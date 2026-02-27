"""
Service de gestion des sessions utilisateur.
Persiste les modèles et leur historique sur disque.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class StateService:
    """Service de gestion de l'état des sessions."""

    def __init__(self, state_dir: Path):
        """
        Initialise le service de gestion d'état.
        
        Args:
            state_dir: Répertoire où stocker les sessions
        """
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"StateService initialisé : {state_dir}")

    def create_session(self) -> str:
        """
        Crée une nouvelle session.
        
        Returns:
            L'ID de la session (UUID)
        """
        session_id = str(uuid4())
        session_file = self.state_dir / f"{session_id}.json"
        
        initial_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "system_model": None,
            "sysml_code": None,
            "history": []
        }
        
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Session créée : {session_id}")
        return session_id

    def save_session(self, session_id: str, data: Dict) -> None:
        """
        Sauvegarde les données d'une session.
        
        Args:
            session_id: ID de la session
            data: Données à sauvegarder (system_model, sysml_code, history)
        """
        session_file = self.state_dir / f"{session_id}.json"
        
        # Charge les données existantes
        if session_file.exists():
            with open(session_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
            }
        
        # Mise à jour
        existing_data.update(data)
        existing_data["updated_at"] = datetime.now().isoformat()
        
        # Sauvegarde
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Session sauvegardée : {session_id}")

    def load_session(self, session_id: str) -> Dict:
        """
        Charge les données d'une session.
        
        Args:
            session_id: ID de la session
        
        Returns:
            Données de la session
        
        Raises:
            FileNotFoundError: Si la session n'existe pas
        """
        session_file = self.state_dir / f"{session_id}.json"
        
        if not session_file.exists():
            raise FileNotFoundError(f"Session {session_id} introuvable")
        
        with open(session_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        logger.debug(f"Session chargée : {session_id}")
        return data

    def list_sessions(self) -> List[Dict]:
        """
        Liste toutes les sessions existantes.
        
        Returns:
            Liste de sessions avec leurs métadonnées
        """
        sessions = []
        
        for session_file in self.state_dir.glob("*.json"):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                sessions.append({
                    "id": data.get("session_id"),
                    "name": data.get("session_name") or ((data.get("system_model") or {}).get("system_name")),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "system_name": (data.get("system_model") or {}).get("system_name"),
                })
            except Exception as e:
                logger.warning(f"Erreur lors de la lecture de {session_file.name} : {e}")
        
        # Trie par date de mise à jour (plus récent d'abord)
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        return sessions

    def add_to_history(self, session_id: str, entry: Dict) -> None:
        """
        Ajoute une entrée à l'historique d'une session.
        
        Args:
            session_id: ID de la session
            entry: Entrée à ajouter (doit contenir action, timestamp, description ou instruction)
        """
        data = self.load_session(session_id)
        
        if "history" not in data:
            data["history"] = []
        
        entry["timestamp"] = datetime.now().isoformat()
        data["history"].append(entry)
        
        self.save_session(session_id, data)
        logger.debug(f"Historique mis à jour pour session {session_id}")

    # ========================================================================
    # MÉTHODES POUR WORKFLOW MULTI-NIVEAUX
    # ========================================================================

    def init_session_with_levels(self, session_id: str, description: str, system_name: str = "", session_name: str = "") -> None:
        """
        Initialise une session avec la structure multi-niveaux.
        
        Args:
            session_id: ID de la session
            description: Description initiale du système
            system_name: Nom du système (optionnel)
            session_name: Nom de la session donné par l'utilisateur (optionnel)
        """
        from models.schemas import ModelLevel
        
        session_file = self.state_dir / f"{session_id}.json"
        
        # Structure complète avec les 4 niveaux
        initial_data = {
            "session_id": session_id,
            "session_name": session_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "system_name": system_name,
            "description": description,
            "current_level": ModelLevel.OPERATIONAL.value,
            "levels": {
                ModelLevel.OPERATIONAL.value: {
                    "level": ModelLevel.OPERATIONAL.value,
                    "model": {},
                    "sysml_code": "",
                    "diagrams": [],
                    "validated": False,
                    "history": []
                },
                ModelLevel.FUNCTIONAL.value: {
                    "level": ModelLevel.FUNCTIONAL.value,
                    "model": {},
                    "sysml_code": "",
                    "diagrams": [],
                    "validated": False,
                    "history": []
                },
                ModelLevel.LOGICAL.value: {
                    "level": ModelLevel.LOGICAL.value,
                    "model": {},
                    "sysml_code": "",
                    "diagrams": [],
                    "validated": False,
                    "history": []
                },
                ModelLevel.TECHNICAL.value: {
                    "level": ModelLevel.TECHNICAL.value,
                    "model": {},
                    "sysml_code": "",
                    "diagrams": [],
                    "validated": False,
                    "history": []
                }
            }
        }
        
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Session multi-niveaux initialisée : {session_id}")

    def save_level(self, session_id: str, level: str, level_data: Dict) -> None:
        """
        Sauvegarde les données d'un niveau spécifique.
        
        Args:
            session_id: ID de la session
            level: Nom du niveau (operational, functional, logical, technical)
            level_data: Données du niveau à sauvegarder
        """
        session_data = self.load_session(session_id)
        
        if "levels" not in session_data:
            # Migration d'anciennes sessions : créer la structure de niveaux
            session_data["levels"] = {}
        
        # Mettre à jour le niveau
        if level not in session_data["levels"]:
            session_data["levels"][level] = {
                "level": level,
                "model": {},
                "sysml_code": "",
                "diagrams": [],
                "validated": False,
                "history": []
            }
        
        session_data["levels"][level].update(level_data)
        session_data["updated_at"] = datetime.now().isoformat()
        
        # Sauvegarder
        session_file = self.state_dir / f"{session_id}.json"
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Niveau {level} sauvegardé pour session {session_id}")

    def get_level(self, session_id: str, level: str) -> Dict:
        """
        Récupère les données d'un niveau spécifique.
        
        Args:
            session_id: ID de la session
            level: Nom du niveau
        
        Returns:
            Données du niveau
        
        Raises:
            ValueError: Si le niveau n'existe pas
        """
        session_data = self.load_session(session_id)
        
        if "levels" not in session_data or level not in session_data["levels"]:
            raise ValueError(f"Niveau {level} introuvable dans la session {session_id}")
        
        return session_data["levels"][level]

    def validate_level(self, session_id: str, level: str) -> None:
        """
        Marque un niveau comme validé et passe au niveau suivant.
        
        Args:
            session_id: ID de la session
            level: Nom du niveau à valider
        """
        from models.schemas import ModelLevel
        
        session_data = self.load_session(session_id)
        
        # Marquer comme validé
        if "levels" in session_data and level in session_data["levels"]:
            session_data["levels"][level]["validated"] = True
        
        # Déterminer le niveau suivant
        level_order = [
            ModelLevel.OPERATIONAL.value,
            ModelLevel.FUNCTIONAL.value,
            ModelLevel.LOGICAL.value,
            ModelLevel.TECHNICAL.value
        ]
        
        try:
            current_index = level_order.index(level)
            if current_index < len(level_order) - 1:
                next_level = level_order[current_index + 1]
                session_data["current_level"] = next_level
                logger.info(f"Niveau {level} validé, passage au niveau {next_level}")
            else:
                logger.info(f"Niveau {level} validé (dernier niveau)")
        except ValueError:
            logger.warning(f"Niveau {level} inconnu")
        
        session_data["updated_at"] = datetime.now().isoformat()
        
        # Sauvegarder
        session_file = self.state_dir / f"{session_id}.json"
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

    def rename_session(self, session_id: str, name: str) -> None:
        """
        Renomme une session.
        
        Args:
            session_id: ID de la session
            name: Nouveau nom de la session
        """
        session_data = self.load_session(session_id)
        session_data["session_name"] = name
        session_data["updated_at"] = datetime.now().isoformat()
        
        session_file = self.state_dir / f"{session_id}.json"
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Session {session_id} renommée : {name}")

    def delete_session(self, session_id: str) -> bool:
        """
        Supprime une session et toutes ses données.

        Args:
            session_id: ID de la session

        Returns:
            True si supprimée, False si introuvable
        """
        session_file = self.state_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
            logger.info(f"Session {session_id} supprimée")
            return True
        return False

    def get_previous_level_data(self, session_id: str, level: str) -> Optional[Dict]:
        """
        Récupère les données du niveau précédent (pour héritage).
        
        Args:
            session_id: ID de la session
            level: Niveau actuel
        
        Returns:
            Données du niveau précédent ou None si premier niveau
        """
        from models.schemas import ModelLevel
        
        # Mapping des niveaux précédents
        previous_level_map = {
            ModelLevel.OPERATIONAL.value: None,
            ModelLevel.FUNCTIONAL.value: ModelLevel.OPERATIONAL.value,
            ModelLevel.LOGICAL.value: ModelLevel.FUNCTIONAL.value,
            ModelLevel.TECHNICAL.value: ModelLevel.LOGICAL.value
        }
        
        previous_level = previous_level_map.get(level)
        
        if previous_level is None:
            return None
        
        try:
            return self.get_level(session_id, previous_level)
        except ValueError:
            logger.warning(f"Niveau précédent {previous_level} non trouvé")
            return None

    # ========================================================================
    # MÉTHODES POUR LA TRAÇABILITÉ DES ÉCHANGES LLM
    # ========================================================================

    def save_exchange(self, session_id: str, exchange: dict) -> None:
        """
        Sauvegarde un échange LLM dans la session.

        Args:
            session_id: ID de la session
            exchange: Dictionnaire décrivant l'échange (prompt, réponse brute, etc.)
        """
        data = self.load_session(session_id)
        data.setdefault("exchanges", [])
        data["exchanges"].append(exchange)
        self.save_session(session_id, data)
        logger.debug(f"Échange LLM sauvegardé pour session {session_id} (level={exchange.get('level', '?')})")

    def get_exchanges(self, session_id: str, level: str = None) -> list:
        """
        Retourne les échanges LLM d'une session, optionnellement filtrés par niveau.

        Args:
            session_id: ID de la session
            level: Niveau MBSE optionnel pour filtrer les résultats

        Returns:
            Liste des échanges (dicts)
        """
        data = self.load_session(session_id)
        exchanges = data.get("exchanges", [])
        if level is not None:
            exchanges = [e for e in exchanges if e.get("level") == level]
        return exchanges
