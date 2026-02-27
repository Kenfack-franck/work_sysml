"""
Service de gestion des sessions utilisateur.

Utilise l'arborescence par session gérée par FileLogger
et les schémas Pydantic définis dans models/schemas.py.

Structure sur disque :
  data/sessions/{session_id}/
  ├── session.json
  ├── user_inputs/
  ├── prompts/
  └── outputs/
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from config import settings
from models.schemas import ModelLevel
from services.file_logger import FileLogger

logger = logging.getLogger(__name__)

LEVEL_ORDER = [
    ModelLevel.OPERATIONAL.value,
    ModelLevel.FUNCTIONAL.value,
    ModelLevel.LOGICAL.value,
    ModelLevel.TECHNICAL.value,
]


def _empty_level(level: str) -> dict:
    """Structure vide d'un niveau."""
    return {
        "level": level,
        "user_inputs": [],
        "model": {},
        "sysml_code": "",
        "summary": None,
        "warnings": [],
        "validation_result": None,
        "validated": False,
        "history": [],
    }


def _now() -> str:
    return datetime.now().isoformat()


class StateService:
    """Service de gestion de l'état des sessions."""

    def __init__(self, state_dir: Path = None):
        """
        Args:
            state_dir: Répertoire de stockage des sessions.
                       Accepté pour rétrocompatibilité ; la valeur par défaut
                       est config.DATA_DIR / "sessions".
        """
        self.base_dir = Path(state_dir) if state_dir else (settings.DATA_DIR / "sessions")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.file_logger = FileLogger(base_dir=self.base_dir)
        logger.info(f"StateService initialisé : {self.base_dir}")

    # ------------------------------------------------------------------
    # Helpers internes
    # ------------------------------------------------------------------

    def _session_file(self, session_id: str) -> Path:
        return self.base_dir / session_id / "session.json"

    def _write_session(self, session_id: str, data: dict) -> None:
        path = self._session_file(session_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # ------------------------------------------------------------------
    # Création & initialisation
    # ------------------------------------------------------------------

    def create_session(self) -> str:
        """Crée une nouvelle session avec un UUID."""
        session_id = str(uuid4())
        self.file_logger.init_session_dirs(session_id)

        initial_data = {
            "session_id": session_id,
            "session_name": "",
            "created_at": _now(),
            "updated_at": _now(),
            "system_name": "",
            "description": "",
            "current_level": ModelLevel.OPERATIONAL.value,
            "levels": {lv: _empty_level(lv) for lv in LEVEL_ORDER},
            "exchanges": [],
        }
        self._write_session(session_id, initial_data)
        logger.info(f"Session créée : {session_id}")
        return session_id

    def init_session(self, session_id: str, description: str, session_name: str = "") -> None:
        """Initialise la session avec la description et le nom."""
        data = self.load_session(session_id)
        data["description"] = description
        data["session_name"] = session_name
        data["current_level"] = ModelLevel.OPERATIONAL.value
        # Réinitialise les 4 niveaux
        data["levels"] = {lv: _empty_level(lv) for lv in LEVEL_ORDER}
        data["updated_at"] = _now()
        self._write_session(session_id, data)
        logger.info(f"Session initialisée : {session_id}")

    # Rétrocompatibilité : level_service appelle init_session_with_levels
    def init_session_with_levels(self, session_id: str, description: str,
                                 system_name: str = "", session_name: str = "") -> None:
        """Alias rétrocompatible pour init_session."""
        data = self.load_session(session_id)
        data["description"] = description
        data["system_name"] = system_name
        data["session_name"] = session_name
        data["current_level"] = ModelLevel.OPERATIONAL.value
        data["levels"] = {lv: _empty_level(lv) for lv in LEVEL_ORDER}
        data["updated_at"] = _now()
        self._write_session(session_id, data)
        logger.info(f"Session multi-niveaux initialisée : {session_id}")

    # ------------------------------------------------------------------
    # Chargement & sauvegarde générique
    # ------------------------------------------------------------------

    def save_session(self, session_id: str, data: dict) -> None:
        """Merge les données dans session.json existant."""
        try:
            existing = self.load_session(session_id)
        except (FileNotFoundError, ValueError):
            existing = {
                "session_id": session_id,
                "created_at": _now(),
            }
        existing.update(data)
        existing["updated_at"] = _now()
        self._write_session(session_id, existing)
        logger.debug(f"Session sauvegardée : {session_id}")

    def load_session(self, session_id: str) -> dict:
        """Charge session.json depuis le disque."""
        path = self._session_file(session_id)
        if not path.exists():
            raise FileNotFoundError(f"Session {session_id} introuvable")
        data = json.loads(path.read_text(encoding="utf-8"))
        logger.debug(f"Session chargée : {session_id}")
        return data

    def list_sessions(self) -> List[dict]:
        """Liste toutes les sessions, triées par updated_at décroissant."""
        sessions = []
        if not self.base_dir.exists():
            return sessions
        for session_dir in self.base_dir.iterdir():
            if not session_dir.is_dir():
                continue
            session_file = session_dir / "session.json"
            if not session_file.exists():
                continue
            try:
                data = json.loads(session_file.read_text(encoding="utf-8"))
                sessions.append({
                    "session_id": data.get("session_id", session_dir.name),
                    "session_name": data.get("session_name", ""),
                    "created_at": data.get("created_at", ""),
                    "updated_at": data.get("updated_at", ""),
                    "current_level": data.get("current_level", ""),
                    # Rétrocompatibilité : main.py accède à "id" et "name"
                    "id": data.get("session_id", session_dir.name),
                    "name": data.get("session_name", "") or data.get("system_name", ""),
                    "system_name": data.get("system_name", ""),
                })
            except Exception as e:
                logger.warning(f"Erreur lecture session {session_dir.name} : {e}")
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return sessions

    # ------------------------------------------------------------------
    # Gestion des niveaux
    # ------------------------------------------------------------------

    def save_level(self, session_id: str, level: str, level_data: dict) -> None:
        """Sauvegarde les données d'un niveau dans session.json."""
        data = self.load_session(session_id)
        if "levels" not in data:
            data["levels"] = {}
        if level not in data["levels"]:
            data["levels"][level] = _empty_level(level)

        data["levels"][level].update(level_data)
        # Ajouter entrée historique
        data["levels"][level].setdefault("history", [])
        data["levels"][level]["history"].append({
            "action": "save",
            "timestamp": _now(),
        })
        data["updated_at"] = _now()
        self._write_session(session_id, data)
        logger.debug(f"Niveau {level} sauvegardé pour session {session_id}")

    def get_level(self, session_id: str, level: str) -> dict:
        """Retourne les données d'un niveau."""
        data = self.load_session(session_id)
        if "levels" not in data or level not in data["levels"]:
            raise ValueError(f"Niveau {level} introuvable dans la session {session_id}")
        return data["levels"][level]

    def validate_level(self, session_id: str, level: str) -> None:
        """Marque un niveau comme validé et passe au niveau suivant."""
        data = self.load_session(session_id)
        if "levels" in data and level in data["levels"]:
            data["levels"][level]["validated"] = True
            data["levels"][level].setdefault("history", [])
            data["levels"][level]["history"].append({
                "action": "validate",
                "timestamp": _now(),
            })

        try:
            idx = LEVEL_ORDER.index(level)
            if idx < len(LEVEL_ORDER) - 1:
                data["current_level"] = LEVEL_ORDER[idx + 1]
                logger.info(f"Niveau {level} validé, passage à {LEVEL_ORDER[idx + 1]}")
            else:
                logger.info(f"Niveau {level} validé (dernier niveau)")
        except ValueError:
            logger.warning(f"Niveau {level} inconnu")

        data["updated_at"] = _now()
        self._write_session(session_id, data)

    def get_previous_level_data(self, session_id: str, level: str) -> Optional[dict]:
        """Retourne les données du niveau précédent (None pour operational)."""
        previous = {
            ModelLevel.OPERATIONAL.value: None,
            ModelLevel.FUNCTIONAL.value: ModelLevel.OPERATIONAL.value,
            ModelLevel.LOGICAL.value: ModelLevel.FUNCTIONAL.value,
            ModelLevel.TECHNICAL.value: ModelLevel.LOGICAL.value,
        }
        prev = previous.get(level)
        if prev is None:
            return None
        try:
            return self.get_level(session_id, prev)
        except ValueError:
            return None

    def get_level_summary(self, session_id: str, level: str) -> Optional[dict]:
        """Retourne le résumé (LevelSummary) d'un niveau s'il existe."""
        try:
            level_data = self.get_level(session_id, level)
            return level_data.get("summary")
        except ValueError:
            return None

    # ------------------------------------------------------------------
    # Entrées utilisateur
    # ------------------------------------------------------------------

    def save_user_inputs(self, session_id: str, level: str, sections: List[dict]) -> None:
        """Sauvegarde les réponses utilisateur dans session.json ET sur disque."""
        data = self.load_session(session_id)
        if "levels" not in data:
            data["levels"] = {}
        if level not in data["levels"]:
            data["levels"][level] = _empty_level(level)
        data["levels"][level]["user_inputs"] = sections
        data["updated_at"] = _now()
        self._write_session(session_id, data)
        # Sauvegarde fichier
        self.file_logger.save_user_inputs(session_id, level, sections)

    # ------------------------------------------------------------------
    # Échanges LLM
    # ------------------------------------------------------------------

    def save_exchange(self, session_id: str, exchange: dict) -> None:
        """Sauvegarde un échange LLM dans session.json et dans des fichiers."""
        data = self.load_session(session_id)
        data.setdefault("exchanges", [])
        data["exchanges"].append(exchange)
        data["updated_at"] = _now()
        self._write_session(session_id, data)

        # Sauvegarde fichier du prompt et de la réponse
        level = exchange.get("level", "unknown")
        step = exchange.get("operation", "exchange")
        prompt_text = exchange.get("prompt_sent", "") or exchange.get("prompt", "")
        response_text = exchange.get("llm_response_raw", "") or exchange.get("raw_response", "")
        if prompt_text:
            self.file_logger.save_prompt(session_id, level, step, prompt_text)
        if response_text:
            self.file_logger.save_response(session_id, level, step, response_text)
        logger.debug(f"Échange LLM sauvegardé pour session {session_id}")

    def get_exchanges(self, session_id: str, level: str = None) -> List[dict]:
        """Retourne les échanges LLM, optionnellement filtrés par niveau."""
        data = self.load_session(session_id)
        exchanges = data.get("exchanges", [])
        if level is not None:
            exchanges = [e for e in exchanges if e.get("level") == level]
        return exchanges

    # ------------------------------------------------------------------
    # Renommage & suppression
    # ------------------------------------------------------------------

    def rename_session(self, session_id: str, name: str) -> None:
        """Met à jour session_name dans session.json."""
        data = self.load_session(session_id)
        data["session_name"] = name
        data["updated_at"] = _now()
        self._write_session(session_id, data)
        logger.info(f"Session {session_id} renommée : {name}")

    def delete_session(self, session_id: str) -> bool:
        """Supprime tout le dossier de session."""
        session_dir = self.file_logger.get_session_dir(session_id)
        if session_dir.exists():
            self.file_logger.delete_session_files(session_id)
            logger.info(f"Session {session_id} supprimée")
            return True
        return False

    # ------------------------------------------------------------------
    # SysML complet
    # ------------------------------------------------------------------

    def get_full_sysml(self, session_id: str) -> str:
        """Concatène les codes SysML v2 de tous les niveaux validés."""
        data = self.load_session(session_id)
        levels = data.get("levels", {})
        levels_code = {}
        for lv in LEVEL_ORDER:
            lv_data = levels.get(lv, {})
            code = lv_data.get("sysml_code", "")
            if code and lv_data.get("validated", False):
                levels_code[lv] = code
        if levels_code:
            self.file_logger.save_full_sysml(session_id, levels_code)
        return "\n\n".join(levels_code.get(lv, "") for lv in LEVEL_ORDER if lv in levels_code)

    # ------------------------------------------------------------------
    # Rétrocompatibilité : anciennes méthodes
    # ------------------------------------------------------------------

    def add_to_history(self, session_id: str, entry: dict) -> None:
        """Ajoute une entrée à l'historique global de la session."""
        data = self.load_session(session_id)
        data.setdefault("history", [])
        entry["timestamp"] = _now()
        data["history"].append(entry)
        self.save_session(session_id, data)
