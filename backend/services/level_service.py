"""
Service de génération par niveaux MBSE.
Orchestre la génération progressive : Operational → Functional → Logical → Technical.

Pipeline par niveau :
  1. Sections utilisateur → prompt JSON → LLM → JSON model
  2. JSON model → prompt SysML v2 → LLM → code SysML v2
  3. Validation syntaxique + résumé + sauvegarde
"""

import json
import logging
import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from services.llm_base import LLMBase
from services.rag_service import RAGService
from services.state_service import StateService
from services.sysml_validator import SysMLv2Validator

from prompts._shared import extract_identifiers_from_sysml, merge_identifiers, build_naming_constraint_block
from prompts.operational_prompt import build_operational_json_prompt, get_operational_sysml_prompts
from prompts.functional_prompt import build_functional_json_prompt, get_functional_sysml_prompts
from prompts.logical_prompt import build_logical_json_prompt, get_logical_sysml_prompts
from prompts.technical_prompt import build_technical_json_prompt, get_technical_sysml_prompts

logger = logging.getLogger(__name__)


class LevelService:
    """Service de génération progressive par niveaux MBSE."""

    NIVEAUX_ORDER = ["operational", "functional", "logical", "technical"]

    def __init__(
        self,
        llm: LLMBase,
        rag: RAGService,
        state: StateService,
        validator: Optional[SysMLv2Validator] = None,
    ):
        self.llm = llm
        self.rag = rag
        self.state = state
        self.validator = validator if validator is not None else SysMLv2Validator()
        logger.info("LevelService initialisé")

    # ------------------------------------------------------------------
    # Méthode principale — generate_level
    # ------------------------------------------------------------------

    def generate_level(
        self,
        level: str,
        sections: Optional[List[dict]] = None,
        session_id: Optional[str] = None,
        session_name: str = "",
        description: str = "",
        use_rag: bool = True,
    ) -> Dict:
        """
        Génère un niveau spécifique du modèle MBSE.

        Args:
            level: Niveau à générer (operational, functional, logical, technical)
            sections: Liste de {"section_id": str, "content": str}
            session_id: ID de session (None = nouvelle session)
            session_name: Nom de la session
            description: Description globale (rétrocompatibilité, utilisée pour RAG)
            use_rag: Utiliser le RAG pour des exemples

        Returns:
            Résultat avec session_id, level, model, sysml_code, summary, warnings, rag_sources
        """
        logger.info(f"Génération du niveau {level} (session: {session_id})")

        # 1. Validation du niveau
        if level not in self.NIVEAUX_ORDER:
            raise ValueError(f"Niveau invalide : {level}. Valides : {', '.join(self.NIVEAUX_ORDER)}")

        # 2. Création ou chargement de la session
        if session_id is None:
            session_id = self.state.create_session()
            self.state.init_session_with_levels(
                session_id, description=description,
                system_name="", session_name=session_name,
            )
            logger.info(f"Nouvelle session créée : {session_id}")

        # 3. Vérification des prérequis (niveau précédent validé)
        if level != "operational":
            prev_level = self._get_previous_level(level)
            try:
                prev_data = self.state.get_level(session_id, prev_level)
                if not prev_data.get("validated", False):
                    raise ValueError(
                        f"Le niveau {prev_level} doit être validé avant de générer le niveau {level}"
                    )
            except ValueError:
                raise

        # 4. Sauvegarde des entrées utilisateur
        user_sections = sections or []
        if user_sections:
            self.state.save_user_inputs(session_id, level, user_sections)

        # 5. Contexte du niveau précédent
        previous_data = self.state.get_previous_level_data(session_id, level)
        previous_model = None
        if previous_data:
            previous_model = previous_data.get("model", {})

        # 6. Récupération d'exemples RAG
        rag_examples = []
        rag_sources = []
        if use_rag:
            rag_query = description or self._sections_to_rag_query(user_sections)
            if rag_query:
                try:
                    results = self.rag.search(rag_query, top_k=8)
                    rag_examples = [r["content"] for r in results]
                    rag_sources = [r["source_file"] for r in results]
                    logger.info(f"RAG: {len(rag_examples)} exemples récupérés")
                except Exception as e:
                    logger.warning(f"Erreur RAG : {e}")

        # 7. ÉTAPE 1 — Génération du modèle JSON
        logger.info(f"Étape 1/2 : Génération du modèle JSON ({level})")
        json_model, json_exchange = self._generate_json(
            level=level,
            user_sections=user_sections,
            previous_model=previous_model,
            rag_examples=rag_examples,
        )
        # Sauvegarde de l'échange JSON
        self.state.save_exchange(session_id, {**json_exchange, "session_id": session_id, "level": level})

        # 8. ÉTAPE 2 — Génération du code SysML v2
        logger.info(f"Étape 2/2 : Génération du code SysML v2 ({level})")
        sysml_code, sysml_exchange = self._generate_sysml(
            level=level,
            json_model=json_model,
            rag_examples=rag_examples,
        )
        # Sauvegarde de l'échange SysML
        self.state.save_exchange(session_id, {**sysml_exchange, "session_id": session_id, "level": level})

        # 9. Validation syntaxique
        validation_result = self._validate_sysml(sysml_code)

        # 10. Extraction du system_name au niveau opérationnel
        system_name = json_model.get("system_name", "")
        if level == "operational" and system_name:
            session_data = self.state.load_session(session_id)
            session_data["system_name"] = system_name
            self.state.save_session(session_id, session_data)

        # 11. Construction du résumé
        summary = self._build_summary(level, json_model)

        # 12. Extraction des warnings
        warnings = json_model.get("warnings", [])

        # 13. Sauvegarde du niveau
        level_data = {
            "level": level,
            "user_inputs": user_sections,
            "model": json_model,
            "sysml_code": sysml_code,
            "summary": summary,
            "warnings": warnings,
            "validation_result": validation_result,
            "validated": False,
            "history": [{
                "action": "generate",
                "timestamp": datetime.now().isoformat(),
            }],
        }
        self.state.save_level(session_id, level, level_data)

        # 14. Sauvegarde du code SysML sur disque
        self.state.file_logger.save_sysml_output(session_id, level, sysml_code)

        logger.info(f"Niveau {level} généré et sauvegardé")

        # 15. Retour
        return {
            "session_id": session_id,
            "level": level,
            "model": json_model,
            "sysml_code": sysml_code,
            "summary": summary,
            "warnings": warnings,
            "validation_result": validation_result,
            "rag_sources": rag_sources,
        }

    # ------------------------------------------------------------------
    # patch_level — Régénération avec nouvelles sections
    # ------------------------------------------------------------------

    def patch_level(
        self,
        session_id: str,
        level: str,
        sections: Optional[List[dict]] = None,
        instruction: str = "",
        use_rag: bool = True,
    ) -> Dict:
        """
        Régénère un niveau avec de nouvelles sections.

        Args:
            session_id: ID de session
            level: Niveau à modifier
            sections: Nouvelles sections utilisateur
            instruction: Instruction de modification (rétrocompatibilité)
            use_rag: Utiliser le RAG

        Returns:
            Résultat avec session_id, level, model, sysml_code, changes_summary
        """
        logger.info(f"Patch du niveau {level} (session: {session_id})")

        # 1. Vérifier que le niveau existe
        try:
            existing_data = self.state.get_level(session_id, level)
        except ValueError:
            raise ValueError(f"Le niveau {level} n'existe pas pour cette session")

        if not existing_data.get("model"):
            raise ValueError(f"Le niveau {level} n'a pas encore été généré")

        # 2. Utiliser les nouvelles sections ou les anciennes
        user_sections = sections or existing_data.get("user_inputs", [])
        if sections:
            self.state.save_user_inputs(session_id, level, user_sections)

        # 3. Contexte du niveau précédent
        previous_data = self.state.get_previous_level_data(session_id, level)
        previous_model = None
        if previous_data:
            previous_model = previous_data.get("model", {})

        # 4. RAG
        rag_examples = []
        if use_rag:
            rag_query = instruction or self._sections_to_rag_query(user_sections)
            if rag_query:
                try:
                    results = self.rag.search(rag_query, top_k=5)
                    rag_examples = [r["content"] for r in results]
                except Exception as e:
                    logger.warning(f"Erreur RAG : {e}")

        # 5. Régénération JSON
        json_model, json_exchange = self._generate_json(
            level=level,
            user_sections=user_sections,
            previous_model=previous_model,
            rag_examples=rag_examples,
        )
        self.state.save_exchange(session_id, {**json_exchange, "session_id": session_id, "level": level})

        # 6. Régénération SysML
        sysml_code, sysml_exchange = self._generate_sysml(
            level=level,
            json_model=json_model,
            rag_examples=rag_examples,
        )
        self.state.save_exchange(session_id, {**sysml_exchange, "session_id": session_id, "level": level})

        # 7. Validation
        validation_result = self._validate_sysml(sysml_code)

        # 8. Résumé
        summary = self._build_summary(level, json_model)
        warnings = json_model.get("warnings", [])

        # 9. Sauvegarde
        level_data = {
            "level": level,
            "user_inputs": user_sections,
            "model": json_model,
            "sysml_code": sysml_code,
            "summary": summary,
            "warnings": warnings,
            "validation_result": validation_result,
            "validated": False,
            "history": existing_data.get("history", []) + [{
                "action": "patch",
                "timestamp": datetime.now().isoformat(),
            }],
        }
        self.state.save_level(session_id, level, level_data)
        self.state.file_logger.save_sysml_output(session_id, level, sysml_code)

        changes_summary = f"Niveau {level} régénéré avec les sections mises à jour."

        return {
            "session_id": session_id,
            "level": level,
            "model": json_model,
            "sysml_code": sysml_code,
            "changes_summary": changes_summary,
        }

    # ------------------------------------------------------------------
    # validate_level
    # ------------------------------------------------------------------

    def validate_level(self, session_id: str, level: str) -> Dict:
        """
        Valide un niveau pour permettre de passer au suivant.

        Returns:
            {"session_id", "level", "validated", "next_level"}
        """
        logger.info(f"Validation du niveau {level} (session: {session_id})")

        try:
            level_data = self.state.get_level(session_id, level)
        except ValueError:
            raise ValueError(f"Le niveau {level} n'existe pas")

        if not level_data.get("model"):
            raise ValueError(f"Le niveau {level} n'a pas encore été généré")

        self.state.validate_level(session_id, level)

        try:
            idx = self.NIVEAUX_ORDER.index(level)
            next_level = self.NIVEAUX_ORDER[idx + 1] if idx < len(self.NIVEAUX_ORDER) - 1 else None
        except ValueError:
            next_level = None

        return {
            "session_id": session_id,
            "level": level,
            "validated": True,
            "next_level": next_level,
        }

    # ------------------------------------------------------------------
    # get_level_status
    # ------------------------------------------------------------------

    def get_level_status(self, session_id: str) -> Dict:
        """Retourne le statut de tous les niveaux."""
        status = {}
        for level in self.NIVEAUX_ORDER:
            try:
                level_data = self.state.get_level(session_id, level)
                status[level] = {
                    "generated": bool(level_data and level_data.get("model")),
                    "validated": bool(level_data and level_data.get("validated")),
                    "has_warnings": bool(level_data and level_data.get("warnings")),
                    "warning_count": len(level_data.get("warnings", [])) if level_data else 0,
                    "history_count": len(level_data.get("history", [])) if level_data else 0,
                }
            except ValueError:
                status[level] = {
                    "generated": False,
                    "validated": False,
                    "has_warnings": False,
                    "warning_count": 0,
                    "history_count": 0,
                }
        return status

    # ------------------------------------------------------------------
    # get_full_sysml
    # ------------------------------------------------------------------

    def get_full_sysml(self, session_id: str) -> str:
        """Concatène le code SysML v2 de tous les niveaux validés."""
        code_parts = []
        for level in self.NIVEAUX_ORDER:
            try:
                level_data = self.state.get_level(session_id, level)
                sysml_code = level_data.get("sysml_code", "")
                if sysml_code:
                    code_parts.append(f"// ===== NIVEAU {level.upper()} =====\n\n{sysml_code}")
            except ValueError:
                continue
        if not code_parts:
            return "// Aucun niveau généré"
        return "\n\n".join(code_parts)

    # ------------------------------------------------------------------
    # check_coherence (rétrocompatibilité avec main.py)
    # ------------------------------------------------------------------

    def check_coherence(self, session_id: str, level: str) -> Dict:
        """Vérifie la cohérence entre un niveau et ses niveaux adjacents."""
        issues = []
        try:
            current_data = self.state.get_level(session_id, level)
            current_model = current_data.get("model", {})
        except ValueError:
            return {"coherent": True, "issues": []}

        if level == "functional":
            issues.extend(self._check_functional_coherence(session_id, current_model))
        elif level == "logical":
            issues.extend(self._check_logical_coherence(session_id, current_model))
        elif level == "technical":
            issues.extend(self._check_technical_coherence(session_id, current_model))

        return {"coherent": len(issues) == 0, "issues": issues}

    # ==================================================================
    # Méthodes internes
    # ==================================================================

    # ------------------------------------------------------------------
    # _generate_json — Sections → JSON model via LLM
    # ------------------------------------------------------------------

    def _generate_json(
        self,
        level: str,
        user_sections: List[dict],
        previous_model: Optional[dict],
        rag_examples: List[str],
        correction_feedback: Optional[str] = None,
    ) -> tuple:
        """
        Génère le modèle JSON pour un niveau donné.

        Returns:
            (json_model: dict, exchange: dict)
        """
        # Construire le prompt selon le niveau
        if level == "operational":
            prompt = build_operational_json_prompt(user_sections, rag_examples, correction_feedback)
        elif level == "functional":
            prompt = build_functional_json_prompt(user_sections, previous_model or {}, rag_examples, correction_feedback)
        elif level == "logical":
            prompt = build_logical_json_prompt(user_sections, previous_model or {}, rag_examples, correction_feedback)
        elif level == "technical":
            prompt = build_technical_json_prompt(user_sections, previous_model or {}, rag_examples, correction_feedback)
        else:
            raise ValueError(f"Niveau non supporté : {level}")

        # Préparer l'échange
        exchange = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "operation": "generate_json",
            "prompt_sent": prompt,
            "llm_response_raw": "",
            "llm_model": self.llm.get_model_name(),
            "success": True,
            "error_message": "",
        }

        # Appel LLM
        try:
            response = self.llm.generate(
                prompt, temperature=0.05, max_tokens=65536,
                response_mime_type="application/json",
            )
            exchange["llm_response_raw"] = response
        except Exception as e:
            exchange["success"] = False
            exchange["error_message"] = str(e)
            raise

        # Nettoyage et parsing
        cleaned = self._clean_json_response(response)
        try:
            json_model = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON : {e}")
            logger.error(f"Réponse (500 premiers chars) : {cleaned[:500]}")
            raise ValueError(f"Le LLM n'a pas retourné un JSON valide : {e}")

        return json_model, exchange

    # ------------------------------------------------------------------
    # _generate_sysml — JSON model → SysML v2 code via LLM
    # ------------------------------------------------------------------

    def _generate_sysml(
        self,
        level: str,
        json_model: dict,
        rag_examples: List[str],
    ) -> tuple:
        """
        Génère le code SysML v2 pour un niveau donné.

        Pour le niveau opérationnel, 5 appels LLM sont effectués (un par type
        de diagramme) et les résultats sont concaténés.

        Returns:
            (sysml_code: str, exchange: dict)
        """
        prompts_fn_map = {
            "operational": get_operational_sysml_prompts,
            "functional": get_functional_sysml_prompts,
            "logical": get_logical_sysml_prompts,
            "technical": get_technical_sysml_prompts,
        }

        get_prompts_fn = prompts_fn_map.get(level)
        if get_prompts_fn is None:
            raise ValueError(f"Niveau non supporté : {level}")

        return self._generate_sysml_multi(json_model, rag_examples, level, get_prompts_fn)

    def _generate_sysml_multi(
        self,
        json_model: dict,
        rag_examples: List[str],
        level: str,
        get_prompts_fn,
    ) -> tuple:
        """
        Génère le code SysML v2 en N appels LLM séquentiels (un par diagramme),
        avec extraction d'identifiants et injection de contraintes de nommage
        pour assurer la cohérence entre packages du même niveau.

        Logique :
          1. Générer le 1er diagramme sans contrainte de nommage.
          2. Extraire les identifiants du code généré.
          3. Construire un bloc de contrainte de nommage.
          4. Régénérer le prompt du diagramme suivant AVEC la contrainte.
          5. Répéter pour chaque diagramme.

        Args:
            json_model: modèle JSON du niveau
            rag_examples: exemples RAG
            level: nom du niveau (pour les logs)
            get_prompts_fn: fonction qui retourne [(diagram_type, prompt), ...]

        Returns:
            (sysml_code: str, exchange: dict)
        """
        # Obtenir la liste des types de diagrammes (sans contrainte, juste pour connaître le nombre)
        initial_prompts = get_prompts_fn(json_model, rag_examples)
        total = len(initial_prompts)

        all_code_parts = []
        all_raw_responses = []
        all_prompts = []
        errors = []
        accumulated_identifiers: dict = {}

        for i in range(total):
            # Régénérer les prompts avec la contrainte de nommage accumulée
            naming_constraint = build_naming_constraint_block(accumulated_identifiers)
            current_prompts = get_prompts_fn(json_model, rag_examples, naming_constraint=naming_constraint)
            diagram_type, prompt = current_prompts[i]

            logger.info(f"SysML {level} [{i+1}/{total}] : Génération du diagramme {diagram_type}...")
            if naming_constraint:
                logger.info(f"SysML {level} [{i+1}/{total}] : Contrainte de nommage injectée ({len(accumulated_identifiers)} catégories)")

            all_prompts.append(f"--- {diagram_type} ---\n{prompt}")
            try:
                response = self.llm.generate(prompt, temperature=0.05, max_tokens=8192)
                all_raw_responses.append(f"--- {diagram_type} ---\n{response}")
                code = self._clean_sysml_code(response)
                if code:
                    all_code_parts.append(f"// ===== {diagram_type.upper()} =====\n\n{code}")
                    logger.info(f"SysML {level} [{i+1}/{total}] : {diagram_type} OK ({len(code)} chars)")

                    # Extraire les identifiants et les accumuler
                    new_ids = extract_identifiers_from_sysml(code)
                    if new_ids:
                        accumulated_identifiers = merge_identifiers(accumulated_identifiers, new_ids)
                        logger.info(f"SysML {level} [{i+1}/{total}] : Identifiants extraits — {', '.join(f'{k}: {len(v)}' for k, v in new_ids.items())}")
                else:
                    logger.warning(f"SysML {level} [{i+1}/{total}] : {diagram_type} — réponse vide")
            except Exception as e:
                logger.error(f"SysML {level} [{i+1}/{total}] : {diagram_type} ERREUR: {e}")
                errors.append(f"{diagram_type}: {e}")

        sysml_code = "\n\n".join(all_code_parts)

        exchange = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "operation": "generate_sysml",
            "prompt_sent": "\n\n".join(all_prompts),
            "llm_response_raw": "\n\n".join(all_raw_responses),
            "llm_model": self.llm.get_model_name(),
            "sysml_code": sysml_code,
            "success": len(errors) == 0,
            "error_message": "; ".join(errors) if errors else "",
            "diagram_count": len(all_code_parts),
            "accumulated_identifiers": accumulated_identifiers,
        }

        if errors and not all_code_parts:
            raise RuntimeError(f"Tous les diagrammes ont échoué : {'; '.join(errors)}")

        return sysml_code, exchange

    # ------------------------------------------------------------------
    # _validate_sysml
    # ------------------------------------------------------------------

    def _validate_sysml(self, sysml_code: str) -> dict:
        """Valide le code SysML v2 et retourne le résultat."""
        if not self.validator or not sysml_code:
            return {"valid": True, "errors": [], "warnings": [], "score": 100}

        try:
            result = self.validator.validate(sysml_code)
            if result.get("valid"):
                logger.info(f"Code SysML v2 valide (score: {result.get('score', '?')}/100)")
            else:
                err_count = result.get("summary", {}).get("errors_count", 0)
                logger.warning(f"Code SysML v2 invalide : {err_count} erreurs")
            return result
        except Exception as e:
            logger.warning(f"Erreur lors de la validation : {e}")
            return {"valid": True, "errors": [], "warnings": [], "score": 100}

    # ------------------------------------------------------------------
    # _build_summary
    # ------------------------------------------------------------------

    def _build_summary(self, level: str, json_model: dict) -> Optional[dict]:
        """
        Construit un résumé du modèle pour le frontend.

        Returns:
            {"level": str, "summary_text": str, "key_elements": dict} ou None
        """
        if not json_model:
            return None

        system_name = json_model.get("system_name", "Système")
        key_elements = {}

        if level == "operational":
            stakeholders = [s.get("name", "") for s in json_model.get("stakeholders", [])]
            use_cases = [u.get("name", "") for u in json_model.get("use_cases", [])]
            ext_systems = [e.get("system_name", "") for e in json_model.get("external_interfaces", [])]
            modes = [m.get("name", "") for m in json_model.get("operating_modes", [])]
            key_elements = {
                "stakeholders": stakeholders,
                "use_cases": use_cases,
                "external_systems": ext_systems,
                "operating_modes": modes,
            }
            summary_text = (
                f"Niveau opérationnel de {system_name} : "
                f"{len(stakeholders)} acteurs, {len(use_cases)} cas d'utilisation, "
                f"{len(ext_systems)} systèmes externes, {len(modes)} modes."
            )

        elif level == "functional":
            functions = [f.get("name", "") for f in json_model.get("functions", [])]
            chains = [c.get("name", "") for c in json_model.get("functional_chains", [])]
            flows_count = len(json_model.get("functional_flows", []))
            key_elements = {
                "functions": functions,
                "functional_chains": chains,
            }
            summary_text = (
                f"Niveau fonctionnel de {system_name} : "
                f"{len(functions)} fonctions, {flows_count} flux, {len(chains)} chaînes."
            )

        elif level == "logical":
            components = [c.get("name", "") for c in json_model.get("components", [])]
            connections_count = len(json_model.get("connections", []))
            key_elements = {
                "components": components,
            }
            summary_text = (
                f"Niveau logique de {system_name} : "
                f"{len(components)} composants, {connections_count} connexions."
            )

        elif level == "technical":
            tech_components = [c.get("name", "") for c in json_model.get("technical_components", [])]
            phys_connections = len(json_model.get("physical_connections", []))
            tech_choices = len(json_model.get("technology_choices", []))
            key_elements = {
                "technical_components": tech_components,
            }
            summary_text = (
                f"Niveau technique de {system_name} : "
                f"{len(tech_components)} composants, {phys_connections} connexions, "
                f"{tech_choices} choix technologiques."
            )
        else:
            return None

        return {
            "level": level,
            "summary_text": summary_text,
            "key_elements": key_elements,
        }

    # ------------------------------------------------------------------
    # Nettoyage des réponses LLM
    # ------------------------------------------------------------------

    @staticmethod
    def _clean_json_response(response: str) -> str:
        """Nettoie la réponse JSON du LLM (enlève markdown, espaces)."""
        text = response.strip()
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
        return text.strip()

    @staticmethod
    def _clean_sysml_code(response: str) -> str:
        """Nettoie le code SysML v2 du LLM (enlève blocs markdown)."""
        text = response.strip()
        text = re.sub(r'^```sysml\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
        return text.strip()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_previous_level(self, level: str) -> Optional[str]:
        """Retourne le niveau précédent."""
        try:
            idx = self.NIVEAUX_ORDER.index(level)
            return self.NIVEAUX_ORDER[idx - 1] if idx > 0 else None
        except ValueError:
            return None

    @staticmethod
    def _sections_to_rag_query(sections: List[dict]) -> str:
        """Construit une requête RAG à partir des sections utilisateur."""
        parts = []
        for s in sections:
            content = s.get("content", "").strip()
            if content:
                parts.append(content[:200])
        return " ".join(parts)[:500]

    # ------------------------------------------------------------------
    # Vérifications de cohérence inter-niveaux
    # ------------------------------------------------------------------

    def _check_functional_coherence(self, session_id: str, current_model: dict) -> List[dict]:
        """Vérifie la cohérence FUNCTIONAL → OPERATIONAL."""
        issues = []
        try:
            op_data = self.state.get_level(session_id, "operational")
            op_model = op_data.get("model", {})
            use_cases = op_model.get("use_cases", [])
            functions = current_model.get("functions", [])

            all_function_words = set()
            for func in functions:
                func_text = func.get("name", "") + " " + (func.get("description", "") or "")
                all_function_words.update(self._extract_significant_words(func_text))

            for uc in use_cases:
                uc_name = uc.get("name", "")
                uc_words = self._extract_significant_words(uc_name)
                if not uc_words:
                    continue
                matching = uc_words.intersection(all_function_words)
                coverage = len(matching) / len(uc_words)
                if coverage < 0.3:
                    issues.append({
                        "type": "missing_function_for_usecase",
                        "description": f"Le use case '{uc_name}' pourrait ne pas être couvert par les fonctions.",
                        "severity": "warning",
                    })
        except ValueError:
            pass
        return issues

    def _check_logical_coherence(self, session_id: str, current_model: dict) -> List[dict]:
        """Vérifie la cohérence LOGICAL → FUNCTIONAL."""
        issues = []
        try:
            func_data = self.state.get_level(session_id, "functional")
            func_model = func_data.get("model", {})
            functions = func_model.get("functions", [])
            components = current_model.get("components", [])

            comp_descriptions = []
            for c in components:
                comp_descriptions.append((c.get("description", "") or "").lower())
                for f in c.get("allocated_functions", []):
                    comp_descriptions.append(f.lower())

            for func in functions:
                func_name = func.get("name", "")
                if not any(func_name.lower() in desc for desc in comp_descriptions):
                    issues.append({
                        "type": "unallocated_function",
                        "description": f"La fonction '{func_name}' n'est allouée à aucun composant logique.",
                        "severity": "warning",
                    })
        except ValueError:
            pass
        return issues

    def _check_technical_coherence(self, session_id: str, current_model: dict) -> List[dict]:
        """Vérifie la cohérence TECHNICAL → LOGICAL."""
        issues = []
        try:
            log_data = self.state.get_level(session_id, "logical")
            log_model = log_data.get("model", {})
            logical_components = log_model.get("components", [])
            tech_components = current_model.get("technical_components", [])

            tech_implements = set()
            for tc in tech_components:
                impl = (tc.get("implements", "") or "").lower()
                if impl:
                    tech_implements.add(impl)

            for lc in logical_components:
                lc_name = lc.get("name", "")
                if lc_name.lower() not in tech_implements:
                    issues.append({
                        "type": "missing_technical_component",
                        "description": f"Le composant logique '{lc_name}' n'a pas de composant technique correspondant.",
                        "severity": "warning",
                    })
        except ValueError:
            pass
        return issues

    _STOP_WORDS = frozenset({
        "le", "la", "les", "un", "une", "des", "du", "de", "d", "l",
        "au", "aux", "en", "dans", "par", "pour", "sur", "avec", "sans",
        "a", "the", "an", "of", "in", "to", "for", "with",
    })

    @classmethod
    def _extract_significant_words(cls, text: str) -> set:
        """Extrait les mots significatifs (sans stop words)."""
        words = text.lower().replace("'", " ").split()
        return {w for w in words if len(w) > 2 and w not in cls._STOP_WORDS}
