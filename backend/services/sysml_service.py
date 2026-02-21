"""
Service principal d'orchestration du pipeline de génération SysML v2.
Coordonne le LLM, le RAG et la gestion d'état.
"""

import json
import logging
import re
from typing import Dict, Optional

from services.llm_base import LLMBase
from services.rag_service import RAGService
from services.state_service import StateService
from services.fidelity_checker import FidelityChecker
from models.schemas import SystemModel
from prompts.json_prompt import build_json_prompt
from prompts.sysml_prompt import build_sysml_prompt
from prompts.patch_prompt import build_patch_prompt

logger = logging.getLogger(__name__)


class SysMLService:
    """Service d'orchestration du pipeline de génération SysML v2."""

    def __init__(self, llm: LLMBase, rag: RAGService, state: StateService):
        """
        Initialise le service SysML.
        
        Args:
            llm: Service LLM pour la génération
            rag: Service RAG pour la recherche d'exemples
            state: Service de gestion d'état des sessions
        """
        self.llm = llm
        self.rag = rag
        self.state = state
        self.fidelity_checker = FidelityChecker()
        logger.info("SysMLService initialisé")

    def generate(self, description: str, session_id: Optional[str] = None, use_rag: bool = True) -> Dict:
        """
        Génère un modèle SysML v2 à partir d'une description en langage naturel.
        
        Pipeline en 2 étapes :
        1. Description NL → JSON structuré
        2. JSON → Code SysML v2
        
        Args:
            description: Description du système en langage naturel
            session_id: ID de session (optionnel, créé si None)
            use_rag: Utiliser le RAG pour récupérer des exemples
        
        Returns:
            Dictionnaire avec session_id, system_model, sysml_code, rag_sources
        """
        logger.info("=== Début génération ===")
        
        # Étape 0 : Créer ou récupérer la session
        if session_id is None:
            session_id = self.state.create_session()
            logger.info(f"Nouvelle session créée : {session_id}")
        
        # Étape 1 : Récupération d'exemples via RAG (optionnel)
        rag_examples = []
        rag_sources = []
        if use_rag:
            logger.info("Recherche d'exemples pertinents via RAG...")
            rag_results = self.rag.search(description, top_k=3)
            rag_examples = [result["content"] for result in rag_results]
            rag_sources = [result["source_file"] for result in rag_results]
            logger.info(f"  → {len(rag_examples)} exemples trouvés")
        
        # Étape 2 : Génération du JSON structuré
        logger.info("Étape 1/2 : Génération du modèle JSON...")
        json_prompt = build_json_prompt(description, rag_examples)
        json_response = self.llm.generate(json_prompt, temperature=0.05, max_tokens=4096)
        
        # Parse et validation du JSON
        try:
            system_model_dict = self._parse_json_response(json_response)
            system_model = SystemModel(**system_model_dict)
            logger.info(f"  ✓ JSON valide : {system_model.system_name}")
        except json.JSONDecodeError as e:
            logger.error(f"  ✗ JSON invalide : {e}")
            # Retry avec un prompt corrigé
            logger.info("  → Retry avec correction...")
            retry_prompt = f"{json_prompt}\n\nATTENTION : Ta précédente réponse n'était pas un JSON valide. Erreur : {e}\nRetourne UNIQUEMENT le JSON valide, sans texte avant ou après."
            json_response = self.llm.generate(retry_prompt, temperature=0.0, max_tokens=4096)
            system_model_dict = self._parse_json_response(json_response)
            system_model = SystemModel(**system_model_dict)
            logger.info(f"  ✓ Retry réussi : {system_model.system_name}")
        
        # Vérification de la fidélité
        logger.info("Vérification de la fidélité...")
        fidelity_result = self.fidelity_checker.check(description, system_model_dict)
        
        if not fidelity_result["is_faithful"]:
            logger.warning(f"  ⚠ Problèmes de fidélité détectés")
            logger.warning(f"    - Composants manquants : {fidelity_result['missing_components']}")
            logger.warning(f"    - Composants en trop : {fidelity_result['extra_components']}")
            
            # Construire le feedback de correction
            feedback_parts = []
            if fidelity_result["missing_components"]:
                feedback_parts.append(f"Composants manquants : {', '.join(fidelity_result['missing_components'])}")
            if fidelity_result["extra_components"]:
                feedback_parts.append(f"Composants en trop (non mentionnés dans la description) : {', '.join(fidelity_result['extra_components'])}")
            
            correction_feedback = ". ".join(feedback_parts)
            
            # Retry avec correction (maximum 1 fois)
            logger.info("  → Retry avec correction de fidélité...")
            corrected_json_prompt = build_json_prompt(description, rag_examples, correction_feedback)
            json_response = self.llm.generate(corrected_json_prompt, temperature=0.05, max_tokens=4096)
            
            try:
                system_model_dict = self._parse_json_response(json_response)
                system_model = SystemModel(**system_model_dict)
                
                # Re-vérifier la fidélité
                fidelity_result = self.fidelity_checker.check(description, system_model_dict)
                
                if fidelity_result["is_faithful"]:
                    logger.info("  ✓ Fidélité corrigée avec succès")
                else:
                    logger.warning("  ⚠ Problèmes de fidélité persistent, ajout aux warnings")
                    # Ajouter les problèmes aux warnings du modèle
                    if fidelity_result["missing_components"]:
                        system_model_dict["warnings"].append(
                            f"Composants possiblement manquants : {', '.join(fidelity_result['missing_components'])}"
                        )
                    if fidelity_result["extra_components"]:
                        system_model_dict["warnings"].append(
                            f"Composants possiblement non décrits : {', '.join(fidelity_result['extra_components'])}"
                        )
                    system_model = SystemModel(**system_model_dict)
            except Exception as e:
                logger.error(f"  ✗ Erreur lors de la correction : {e}")
                # Garder le modèle original avec warnings
                if fidelity_result["missing_components"]:
                    system_model_dict["warnings"].append(
                        f"Composants possiblement manquants : {', '.join(fidelity_result['missing_components'])}"
                    )
                if fidelity_result["extra_components"]:
                    system_model_dict["warnings"].append(
                        f"Composants possiblement non décrits : {', '.join(fidelity_result['extra_components'])}"
                    )
                system_model = SystemModel(**system_model_dict)
        else:
            logger.info("  ✓ Fidélité vérifiée : tous les composants sont présents")
        
        # Étape 3 : Génération du code SysML v2
        logger.info("Étape 2/2 : Génération du code SysML v2...")
        system_model_json = json.dumps(system_model_dict, indent=2, ensure_ascii=False)
        sysml_prompt = build_sysml_prompt(system_model_json, rag_examples)
        sysml_response = self.llm.generate(sysml_prompt, temperature=0.05, max_tokens=8192)
        
        # Nettoyage du code SysML
        sysml_code = self._clean_sysml_code(sysml_response)
        logger.info(f"  ✓ Code généré : {len(sysml_code)} caractères")
        
        # Étape 4 : Sauvegarde de la session
        self.state.save_session(session_id, {
            "system_model": system_model_dict,
            "sysml_code": sysml_code,
        })
        self.state.add_to_history(session_id, {
            "action": "generate",
            "description": description[:100] + "..." if len(description) > 100 else description,
        })
        
        logger.info("=== Génération terminée ===")
        
        return {
            "session_id": session_id,
            "system_model": system_model,
            "sysml_code": sysml_code,
            "rag_sources": rag_sources,
        }

    def patch(self, session_id: str, instruction: str, use_rag: bool = True) -> Dict:
        """
        Modifie un système existant selon une instruction.
        
        Args:
            session_id: ID de la session à modifier
            instruction: Instruction de modification
            use_rag: Utiliser le RAG (non utilisé pour patch actuellement)
        
        Returns:
            Dictionnaire avec session_id, system_model, sysml_code, changes_summary
        """
        logger.info(f"=== Début patch (session {session_id}) ===")
        
        # Étape 1 : Charger la session existante
        session_data = self.state.load_session(session_id)
        if not session_data.get("system_model"):
            raise ValueError("Session sans modèle existant")
        
        current_model_json = json.dumps(session_data["system_model"], indent=2, ensure_ascii=False)
        logger.info(f"Modèle actuel chargé : {session_data['system_model']['system_name']}")
        
        # Étape 2 : Modification du JSON
        logger.info("Modification du modèle JSON...")
        patch_prompt = build_patch_prompt(current_model_json, instruction)
        patched_response = self.llm.generate(patch_prompt, temperature=0.05, max_tokens=4096)
        
        # Parse et validation
        try:
            patched_model_dict = self._parse_json_response(patched_response)
            patched_model = SystemModel(**patched_model_dict)
            logger.info(f"  ✓ Modèle modifié validé")
        except json.JSONDecodeError as e:
            logger.error(f"  ✗ JSON invalide : {e}")
            # Retry
            retry_prompt = f"{patch_prompt}\n\nATTENTION : Ta réponse n'était pas un JSON valide. Erreur : {e}\nRetourne UNIQUEMENT le JSON complet modifié."
            patched_response = self.llm.generate(retry_prompt, temperature=0.0, max_tokens=4096)
            patched_model_dict = self._parse_json_response(patched_response)
            patched_model = SystemModel(**patched_model_dict)
        
        # Étape 3 : Régénération du code SysML v2
        logger.info("Régénération du code SysML v2...")
        patched_model_json = json.dumps(patched_model_dict, indent=2, ensure_ascii=False)
        sysml_prompt = build_sysml_prompt(patched_model_json)
        sysml_response = self.llm.generate(sysml_prompt, temperature=0.05, max_tokens=8192)
        sysml_code = self._clean_sysml_code(sysml_response)
        logger.info(f"  ✓ Code régénéré : {len(sysml_code)} caractères")
        
        # Étape 4 : Sauvegarde
        self.state.save_session(session_id, {
            "system_model": patched_model_dict,
            "sysml_code": sysml_code,
        })
        self.state.add_to_history(session_id, {
            "action": "patch",
            "instruction": instruction,
        })
        
        changes_summary = f"Modification appliquée : {instruction}"
        logger.info("=== Patch terminé ===")
        
        return {
            "session_id": session_id,
            "system_model": patched_model,
            "sysml_code": sysml_code,
            "changes_summary": changes_summary,
        }

    def _parse_json_response(self, response: str) -> Dict:
        """
        Parse une réponse LLM en JSON.
        Gère les cas où le LLM ajoute du markdown ou du texte autour.
        
        Args:
            response: Réponse du LLM
        
        Returns:
            Dictionnaire parsé
        """
        # Nettoie les balises markdown
        cleaned = response.strip()
        
        # Enlève ```json et ``` si présents
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        
        # Trouve le premier { et le dernier }
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        
        if start == -1 or end == 0:
            raise json.JSONDecodeError("Pas de JSON trouvé", cleaned, 0)
        
        json_str = cleaned[start:end]
        return json.loads(json_str)

    def _clean_sysml_code(self, response: str) -> str:
        """
        Nettoie le code SysML généré.
        
        Args:
            response: Réponse du LLM
        
        Returns:
            Code SysML nettoyé
        """
        cleaned = response.strip()
        
        # Enlève les balises markdown si présentes
        if cleaned.startswith("```sysml"):
            cleaned = cleaned[8:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        return cleaned.strip()
