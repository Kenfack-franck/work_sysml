"""
Service de génération par niveaux MBSE.
Orchestre la génération progressive : Operational → Functional → Logical → Technical.
"""

import json
import logging
import re
import time
import uuid
from datetime import datetime
from typing import Dict, Optional, List

from services.llm_base import LLMBase
from services.rag_service import RAGService
from services.state_service import StateService
from services.fidelity_checker import FidelityChecker
from services.diagram_service import DiagramService
from services.sysml_validator import SysMLv2Validator

from prompts.operational_prompt import build_operational_json_prompt, build_operational_sysml_prompt
from prompts.functional_prompt import build_functional_json_prompt, build_functional_sysml_prompt
from prompts.logical_prompt import build_logical_json_prompt, build_logical_sysml_prompt
from prompts.technical_prompt import build_technical_json_prompt, build_technical_sysml_prompt

logger = logging.getLogger(__name__)


class LevelService:
    """Service de génération progressive par niveaux MBSE."""
    
    # Ordre des niveaux
    NIVEAUX_ORDER = ["operational", "functional", "logical", "technical"]
    
    # Diagrammes disponibles par niveau
    DIAGRAMMES_PAR_NIVEAU = {
        "operational": ["context", "use_cases", "actors_diagram", "operational_sequence"],
        "functional": ["functional_breakdown", "functional_behavior", "modes_diagram"],
        "logical": ["bdd", "ibd"],
        "technical": ["technical_architecture"]
    }

    def __init__(
        self,
        llm: LLMBase,
        rag: RAGService,
        state: StateService,
        fidelity_checker: FidelityChecker,
        diagram_service: DiagramService,
        validator: Optional[SysMLv2Validator] = None
    ):
        """
        Initialise le service de génération par niveaux.
        
        Args:
            llm: Service LLM
            rag: Service RAG
            state: Service de gestion d'état
            fidelity_checker: Vérificateur de fidélité
            diagram_service: Service de génération de diagrammes
            validator: Validateur syntaxique SysML v2 (optionnel)
        """
        self.llm = llm
        self.rag = rag
        self.state = state
        self.fidelity_checker = fidelity_checker
        self.diagram_service = diagram_service
        self.validator = validator if validator is not None else SysMLv2Validator()
        logger.info("LevelService initialisé")

    def generate_level(
        self,
        description: str,
        level: str,
        session_id: Optional[str] = None,
        session_name: str = "",
        use_rag: bool = True
    ) -> Dict:
        """
        Génère un niveau spécifique du modèle MBSE.
        
        Args:
            description: Description initiale ou instructions
            level: Niveau à générer (operational, functional, logical, technical)
            session_id: ID de session (None = nouvelle session)
            session_name: Nom de la session (utilisé uniquement lors de la création)
            use_rag: Utiliser le RAG pour des exemples
        
        Returns:
            Résultat avec model, sysml_code, rag_sources, warnings, available_diagrams
        """
        logger.info(f"Génération du niveau {level} (session: {session_id})")
        
        # Validation du niveau
        if level not in self.NIVEAUX_ORDER:
            raise ValueError(f"Niveau invalide : {level}. Niveaux valides : {', '.join(self.NIVEAUX_ORDER)}")
        
        # 1. Création de session si nécessaire
        if session_id is None:
            session_id = self.state.create_session()
            self.state.init_session_with_levels(session_id, description, session_name=session_name)
            logger.info(f"Nouvelle session créée : {session_id}")
        
        # 2. Vérification des prérequis (niveau précédent validé)
        if level != "operational":
            prev_level = self._get_previous_level(level)
            try:
                prev_data = self.state.get_level(session_id, prev_level)
                if not prev_data.get("validated", False):
                    raise ValueError(
                        f"Le niveau {prev_level} doit être validé avant de générer le niveau {level}"
                    )
            except ValueError:
                raise ValueError(
                    f"Le niveau {prev_level} doit être généré et validé avant le niveau {level}"
                )
        
        # 3. Récupération du contexte du niveau précédent
        previous_data = self.state.get_previous_level_data(session_id, level)
        
        # 4. Récupération d'exemples RAG
        rag_examples = []
        rag_sources = []
        if use_rag:
            try:
                results = self.rag.search(description, top_k=8)
                rag_examples = [r["content"] for r in results]
                rag_sources = [r["file"] for r in results]
                logger.info(f"RAG: {len(rag_examples)} exemples récupérés")
            except Exception as e:
                logger.warning(f"Erreur RAG : {e}")
        
        # 5. ÉTAPE 1 — Génération du JSON
        logger.info(f"Étape 1/2 : Génération du modèle JSON ({level})")
        json_model = self._generate_json_for_level(
            level, description, previous_data, rag_examples,
            session_id=session_id, orig_description=description
        )
        
        # 6. Vérification de fidélité (UNIQUEMENT pour logical et technical, pas operational/functional)
        if level in ["logical", "technical"]:
            fidelity_result = self.fidelity_checker.check(description, json_model)
            if not fidelity_result["is_faithful"]:
                logger.warning(f"Fidélité non respectée : {fidelity_result}")
                # Retry avec feedback
                feedback = f"Composants manquants : {fidelity_result['missing_components']}. "
                feedback += f"Composants en trop : {fidelity_result['extra_components']}."
                
                logger.info("Retry avec correction de fidélité")
                json_model = self._generate_json_for_level(
                    level, description, previous_data, rag_examples, feedback,
                    session_id=session_id, orig_description=description
                )
                
                # Re-vérification
                fidelity_result = self.fidelity_checker.check(description, json_model)
                if not fidelity_result["is_faithful"]:
                    # Ajouter les warnings au modèle
                    if "warnings" not in json_model:
                        json_model["warnings"] = []
                    json_model["warnings"].extend([
                        f"Composant manquant : {comp}" for comp in fidelity_result['missing_components']
                    ])
                    json_model["warnings"].extend([
                        f"Composant non décrit : {comp}" for comp in fidelity_result['extra_components']
                    ])
        
        # 7. ÉTAPE 2 — Génération du code SysML v2
        logger.info(f"Étape 2/2 : Génération du code SysML v2 ({level})")
        sysml_code = self._generate_sysml_for_level(
            level, json_model, rag_examples,
            session_id=session_id, orig_description=description
        )
        
        # 7.5. Validation syntaxique du code SysML v2 généré
        validation_result = None
        if self.validator:
            logger.info(f"Validation syntaxique du code SysML v2 ({level})")
            validation_result = self.validator.validate(sysml_code)
            
            # NE PAS ajouter de warning dans le modèle JSON
            # Le résultat de validation est stocké séparément
            if not validation_result["valid"]:
                error_count = validation_result["summary"]["errors_count"]
                logger.warning(f"Code SysML v2 invalide : {error_count} erreurs détectées")
            else:
                logger.info(f"Code SysML v2 validé avec succès (score: {validation_result['score']}/100)")
        
        # 7.6. Filtrer les warnings dupliqués des niveaux précédents
        # Les warnings du LLM sont dans json_model["warnings"]
        llm_warnings = []
        if previous_data:
            prev_model = previous_data.get("model", {})
            prev_warnings = set(prev_model.get("warnings", []))
            current_warnings = json_model.get("warnings", [])
            
            # Ne garder que les nouveaux warnings
            new_warnings = [w for w in current_warnings if w not in prev_warnings]
            llm_warnings = new_warnings
            
            if len(current_warnings) > len(new_warnings):
                logger.info(f"Filtrage de {len(current_warnings) - len(new_warnings)} warnings dupliqués")
        else:
            llm_warnings = json_model.get("warnings", [])
        
        # Filtrer les warnings qui parlent de validation syntaxique (ajoutés par erreur dans les anciennes versions)
        llm_warnings = [w for w in llm_warnings if "erreur(s) syntaxique(s)" not in w and "syntaxique" not in w.lower()]
        
        # 8. Extraction du system_name
        system_name = json_model.get("system_name", "")
        if level == "operational" and system_name:
            # Mettre à jour le system_name de la session
            session_data = self.state.load_session(session_id)
            session_data["system_name"] = system_name
            self.state.save_session(session_id, session_data)
        
        # 9. Sauvegarde du niveau
        level_data = {
            "level": level,
            "model": json_model,
            "sysml_code": sysml_code,
            "llm_warnings": llm_warnings,  # Warnings du LLM séparés
            "validation_result": validation_result if validation_result else {"valid": True, "errors": [], "warnings": [], "score": 100},  # Résultat de validation
            "diagrams": [],
            "validated": False,
            "history": [{
                "action": "generate",
                "description": description[:100],
                "timestamp": None  # sera ajouté par save_level
            }]
        }
        self.state.save_level(session_id, level, level_data)
        logger.info(f"Niveau {level} sauvegardé")
        
        # 10. Retour
        return {
            "session_id": session_id,
            "level": level,
            "model": json_model,
            "sysml_code": sysml_code,
            "llm_warnings": llm_warnings,  # Warnings LLM séparés
            "validation_result": validation_result if validation_result else {"valid": True, "errors": [], "warnings": [], "score": 100},
            "rag_sources": rag_sources,
            "warnings": llm_warnings,  # Pour compatibilité avec ancien code
            "available_diagrams": self.DIAGRAMMES_PAR_NIVEAU.get(level, [])
        }

    def _generate_json_for_level(
        self,
        level: str,
        description: str,
        previous_data: Optional[Dict],
        rag_examples: List[str],
        correction_feedback: Optional[str] = None,
        session_id: Optional[str] = None,
        orig_description: str = ""
    ) -> Dict:
        """Génère le modèle JSON pour un niveau donné."""
        
        # Construire le prompt selon le niveau
        if level == "operational":
            prompt = build_operational_json_prompt(description, rag_examples, correction_feedback)
        elif level == "functional":
            prev_model = previous_data["model"] if previous_data else {}
            prompt = build_functional_json_prompt(description, prev_model, rag_examples, correction_feedback)
        elif level == "logical":
            prev_model = previous_data["model"] if previous_data else {}
            prompt = build_logical_json_prompt(description, prev_model, rag_examples, correction_feedback)
        elif level == "technical":
            prev_model = previous_data["model"] if previous_data else {}
            prompt = build_technical_json_prompt(description, prev_model, rag_examples, correction_feedback)
        else:
            raise ValueError(f"Niveau non supporté : {level}")
        
        # Appel au LLM (avec traçabilité si session_id fourni)
        exchange_id = str(uuid.uuid4())
        exchange = {
            "id": exchange_id,
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id or "",
            "level": level,
            "operation": "generate_json",
            "description_input": orig_description or description,
            "prompt_sent": prompt,
            "llm_response_raw": "",
            "llm_model": self.llm.get_model_name(),
            "sysml_code": "",
            "success": True,
            "error_message": ""
        }
        try:
            response = self.llm.generate(prompt, temperature=0.05, max_tokens=65536, response_mime_type="application/json")
            exchange["llm_response_raw"] = response
        except Exception as e:
            exchange["success"] = False
            exchange["error_message"] = str(e)
            if session_id:
                self.state.save_exchange(session_id, exchange)
        
        # Nettoyage et parsing
        response = response.strip()
        # Enlever les blocs markdown
        response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
        response = re.sub(r'^```\s*$', '', response, flags=re.MULTILINE)
        response = response.strip()
        
        # Parser le JSON
        try:
            json_model = json.loads(response)
            return json_model
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON : {e}")
            logger.error(f"Réponse : {response[:500]}")
            raise ValueError(f"Le LLM n'a pas retourné un JSON valide : {e}")

    def _generate_sysml_for_level(
        self,
        level: str,
        json_model: Dict,
        rag_examples: List[str],
        session_id: Optional[str] = None,
        orig_description: str = ""
    ) -> str:
        """Génère le code SysML v2 pour un niveau donné."""
        
        # Sérialiser le JSON
        json_str = json.dumps(json_model, indent=2, ensure_ascii=False)
        
        # Construire le prompt selon le niveau
        if level == "operational":
            prompt = build_operational_sysml_prompt(json_str, rag_examples)
        elif level == "functional":
            prompt = build_functional_sysml_prompt(json_str, rag_examples)
        elif level == "logical":
            prompt = build_logical_sysml_prompt(json_str, rag_examples)
        elif level == "technical":
            prompt = build_technical_sysml_prompt(json_str, rag_examples)
        else:
            raise ValueError(f"Niveau non supporté : {level}")
        
        # Appel au LLM (avec traçabilité si session_id fourni)
        exchange_id = str(uuid.uuid4())
        exchange = {
            "id": exchange_id,
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id or "",
            "level": level,
            "operation": "generate_sysml",
            "description_input": orig_description,
            "prompt_sent": prompt,
            "llm_response_raw": "",
            "llm_model": self.llm.get_model_name(),
            "sysml_code": "",
            "success": True,
            "error_message": ""
        }
        try:
            response = self.llm.generate(prompt, temperature=0.05, max_tokens=8192)
            exchange["llm_response_raw"] = response
        except Exception as e:
            exchange["success"] = False
            exchange["error_message"] = str(e)
            if session_id:
                self.state.save_exchange(session_id, exchange)
            raise
        
        # Nettoyage
        response = response.strip()
        response = re.sub(r'^```sysml\s*', '', response, flags=re.MULTILINE)
        response = re.sub(r'^```\s*$', '', response, flags=re.MULTILINE)
        response = response.strip()
        
        exchange["sysml_code"] = response
        if session_id:
            self.state.save_exchange(session_id, exchange)
        
        return response

    def patch_level(
        self,
        session_id: str,
        level: str,
        instruction: str,
        use_rag: bool = True
    ) -> Dict:
        """
        Modifie un niveau existant.
        
        Args:
            session_id: ID de session
            level: Niveau à modifier
            instruction: Instruction de modification
            use_rag: Utiliser le RAG
        
        Returns:
            Résultat avec model, sysml_code, changes_summary
        """
        logger.info(f"Patch du niveau {level} (session: {session_id})")
        
        # 1. Charger les données actuelles
        try:
            level_data = self.state.get_level(session_id, level)
        except ValueError:
            raise ValueError(f"Le niveau {level} n'existe pas pour cette session")
        
        if not level_data.get("model"):
            raise ValueError(f"Le niveau {level} n'a pas encore été généré")
        
        current_model = level_data["model"]
        
        # 2. Récupérer des exemples RAG
        rag_examples = []
        if use_rag:
            try:
                results = self.rag.search(instruction, top_k=5)
                rag_examples = [r["content"] for r in results]
            except Exception as e:
                logger.warning(f"Erreur RAG : {e}")
        
        # 3. Construire le prompt de patch
        current_json = json.dumps(current_model, indent=2, ensure_ascii=False)
        
        prompt = f"""Tu es un expert en modification de modèles SysML. Tu modifies le modèle JSON du niveau {level}.

=== MODÈLE ACTUEL ===
{current_json}

=== INSTRUCTION DE MODIFICATION ===
{instruction}

=== RÈGLES STRICTES ===
1. Applique UNIQUEMENT la modification demandée
2. Ne supprime RIEN qui n'est pas explicitement demandé
3. Ne modifie RIEN qui n'est pas concerné par l'instruction
4. Conserve TOUTES les autres données inchangées
5. Retourne le JSON COMPLET modifié (pas seulement ce qui a changé)

=== FORMAT DE RÉPONSE ===
Retourne le JSON complet du modèle modifié (sans commentaire, juste le JSON).
"""
        
        if rag_examples:
            prompt += "\n\n=== EXEMPLES DE SYNTAXE ===\n"
            for i, ex in enumerate(rag_examples[:3], 1):
                prompt += f"Exemple {i}:\n```\n{ex}\n```\n\n"
        
        # 4. Appel au LLM (avec traçabilité)
        patch_exchange_id = str(uuid.uuid4())
        patch_exchange = {
            "id": patch_exchange_id,
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "level": level,
            "operation": "patch_json",
            "description_input": instruction,
            "prompt_sent": prompt,
            "llm_response_raw": "",
            "llm_model": self.llm.get_model_name(),
            "sysml_code": "",
            "success": True,
            "error_message": ""
        }
        try:
            response = self.llm.generate(prompt, temperature=0.05, max_tokens=65536, response_mime_type="application/json")
            patch_exchange["llm_response_raw"] = response
        except Exception as e:
            patch_exchange["success"] = False
            patch_exchange["error_message"] = str(e)
            self.state.save_exchange(session_id, patch_exchange)
            raise
        self.state.save_exchange(session_id, patch_exchange)
        
        response = response.strip()
        response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
        response = re.sub(r'^```\s*$', '', response, flags=re.MULTILINE)
        response = response.strip()
        
        # 5. Parser le JSON modifié
        try:
            modified_model = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing : {e}")
            raise ValueError(f"Le LLM n'a pas retourné un JSON valide : {e}")
        
        # 6. Régénérer le code SysML v2
        logger.info("Régénération du code SysML v2")
        sysml_code = self._generate_sysml_for_level(
            level, modified_model, rag_examples,
            session_id=session_id, orig_description=instruction
        )
        
        # 7. Vérifier la cohérence
        coherence = self.check_coherence(session_id, level)
        warnings = []
        if not coherence["coherent"]:
            warnings = [f"{issue['severity'].upper()}: {issue['description']}" for issue in coherence["issues"]]
        
        # 8. Sauvegarder
        level_data["model"] = modified_model
        level_data["sysml_code"] = sysml_code
        if "history" not in level_data:
            level_data["history"] = []
        level_data["history"].append({
            "action": "patch",
            "instruction": instruction,
            "timestamp": None  # sera ajouté par save_level
        })
        self.state.save_level(session_id, level, level_data)
        
        # 9. Résumé des changements
        changes_summary = f"Modification appliquée au niveau {level} : {instruction}"
        
        return {
            "session_id": session_id,
            "level": level,
            "model": modified_model,
            "sysml_code": sysml_code,
            "changes_summary": changes_summary,
            "coherence_warnings": warnings
        }

    def validate_level(self, session_id: str, level: str) -> Dict:
        """
        Valide un niveau pour permettre de passer au suivant.
        
        Args:
            session_id: ID de session
            level: Niveau à valider
        
        Returns:
            Résultat avec session_id, level, validated, next_level
        """
        logger.info(f"Validation du niveau {level} (session: {session_id})")
        
        # Vérifier que le niveau a un modèle
        try:
            level_data = self.state.get_level(session_id, level)
        except ValueError:
            raise ValueError(f"Le niveau {level} n'existe pas")
        
        if not level_data.get("model"):
            raise ValueError(f"Le niveau {level} n'a pas encore été généré")
        
        # Valider
        self.state.validate_level(session_id, level)
        
        # Déterminer le niveau suivant
        try:
            current_index = self.NIVEAUX_ORDER.index(level)
            next_level = self.NIVEAUX_ORDER[current_index + 1] if current_index < len(self.NIVEAUX_ORDER) - 1 else None
        except ValueError:
            next_level = None
        
        return {
            "session_id": session_id,
            "level": level,
            "validated": True,
            "next_level": next_level
        }

    def check_coherence(self, session_id: str, level: str) -> Dict:
        """
        Vérifie la cohérence entre un niveau et ses niveaux adjacents.
        Ne propose PAS de corrections, signale seulement les incohérences.
        
        Args:
            session_id: ID de session
            level: Niveau à vérifier
        
        Returns:
            {"coherent": bool, "issues": [{"type": str, "description": str, "severity": str}]}
        """
        issues = []
        
        try:
            current_data = self.state.get_level(session_id, level)
            current_model = current_data.get("model", {})
        except ValueError:
            return {"coherent": True, "issues": []}
        
        # Vérification FUNCTIONAL → OPERATIONAL
        if level == "functional":
            try:
                op_data = self.state.get_level(session_id, "operational")
                op_model = op_data.get("model", {})
                use_cases = op_model.get("use_cases", [])
                functions = current_model.get("functions", [])
                
                # Stop words pour le matching sémantique
                STOP_WORDS = {"le", "la", "les", "un", "une", "des", "du", "de", "d", "l", "au", "aux", 
                              "en", "dans", "par", "pour", "sur", "avec", "sans", "a", "the", "an", "of", 
                              "in", "to", "for", "with"}
                
                def extract_significant_words(text: str):
                    """Extrait les mots significatifs (sans stop words)."""
                    words = text.lower().replace("'", " ").split()
                    return set(w for w in words if len(w) > 2 and w not in STOP_WORDS)
                
                # Collecter tous les mots des fonctions
                all_function_words = set()
                for func in functions:
                    func_text = func.get("name", "") + " " + func.get("description", "")
                    all_function_words.update(extract_significant_words(func_text))
                
                # Vérifier chaque use case
                for use_case in use_cases:
                    uc_name = use_case.get("name", "")
                    uc_words = extract_significant_words(uc_name)
                    
                    if not uc_words:
                        continue
                    
                    # Matching : au moins 30% des mots du use case doivent apparaître dans les fonctions
                    matching_words = uc_words.intersection(all_function_words)
                    coverage = len(matching_words) / len(uc_words) if uc_words else 0
                    
                    if coverage < 0.3:
                        issues.append({
                            "type": "missing_function_for_usecase",
                            "description": f"Le use case '{uc_name}' pourrait ne pas être entièrement couvert par les fonctions actuelles. Vérifiez la couverture.",
                            "severity": "warning"
                        })
            except ValueError:
                pass  # Pas de niveau opérationnel
        
        # Vérification LOGICAL → FUNCTIONAL
        elif level == "logical":
            try:
                func_data = self.state.get_level(session_id, "functional")
                func_model = func_data.get("model", {})
                functions = func_model.get("functions", [])
                parts = current_model.get("parts", [])
                
                # Chaque fonction doit être mentionnée dans la description d'un composant
                function_names = [f.get("name", "") for f in functions]
                part_descriptions = [p.get("description", "") for p in parts]
                
                for func_name in function_names:
                    if not any(func_name.lower() in desc.lower() for desc in part_descriptions):
                        issues.append({
                            "type": "unallocated_function",
                            "description": f"La fonction '{func_name}' n'est allouée à aucun composant logique",
                            "severity": "warning"
                        })
                
                # Vérifier les flux fonctionnels vs connexions
                functional_flows = func_model.get("functional_flows", [])
                connections = current_model.get("connections", [])
                
                if len(functional_flows) > len(connections):
                    issues.append({
                        "type": "missing_connections",
                        "description": f"{len(functional_flows)} flux fonctionnels mais seulement {len(connections)} connexions logiques",
                        "severity": "warning"
                    })
            except ValueError:
                pass  # Pas de niveau fonctionnel
        
        # Vérification TECHNICAL → LOGICAL
        elif level == "technical":
            try:
                log_data = self.state.get_level(session_id, "logical")
                log_model = log_data.get("model", {})
                logical_parts = log_model.get("parts", [])
                technical_parts = current_model.get("technical_parts", [])
                
                # Chaque composant logique doit avoir un composant technique correspondant
                logical_names = [p.get("name", "") for p in logical_parts]
                tech_descriptions = [p.get("description", "") for p in technical_parts]
                
                for log_name in logical_names:
                    if not any(log_name.lower() in desc.lower() for desc in tech_descriptions):
                        issues.append({
                            "type": "missing_technical_component",
                            "description": f"Le composant logique '{log_name}' n'a pas de composant technique correspondant",
                            "severity": "warning"
                        })
            except ValueError:
                pass  # Pas de niveau logique
        
        coherent = len(issues) == 0
        return {"coherent": coherent, "issues": issues}

    def get_full_sysml(self, session_id: str) -> str:
        """
        Retourne le code SysML v2 complet en concaténant tous les niveaux validés.
        
        Args:
            session_id: ID de session
        
        Returns:
            Code SysML v2 complet
        """
        code_parts = []
        
        for level in self.NIVEAUX_ORDER:
            try:
                level_data = self.state.get_level(session_id, level)
                sysml_code = level_data.get("sysml_code", "")
                if sysml_code:
                    code_parts.append(f"// ===== NIVEAU {level.upper()} =====\n\n{sysml_code}")
            except ValueError:
                continue  # Niveau pas encore généré
        
        if not code_parts:
            return "// Aucun niveau généré"
        
        return "\n\n".join(code_parts)

    def get_level_status(self, session_id: str) -> Dict:
        """
        Retourne le statut de tous les niveaux.
        
        Args:
            session_id: ID de session
        
        Returns:
            Dictionnaire avec le statut de chaque niveau
        """
        status = {}
        
        for level in self.NIVEAUX_ORDER:
            try:
                level_data = self.state.get_level(session_id, level)
                status[level] = {
                    "generated": bool(level_data and level_data.get("model")),
                    "validated": bool(level_data and level_data.get("validated")),
                    "has_diagrams": bool(level_data and level_data.get("diagrams")),
                    "history_count": len(level_data.get("history", [])) if level_data else 0
                }
            except ValueError:
                status[level] = {
                    "generated": False,
                    "validated": False,
                    "has_diagrams": False,
                    "history_count": 0
                }
        
        return status

    def _get_previous_level(self, level: str) -> Optional[str]:
        """Retourne le niveau précédent."""
        try:
            index = self.NIVEAUX_ORDER.index(level)
            return self.NIVEAUX_ORDER[index - 1] if index > 0 else None
        except ValueError:
            return None
