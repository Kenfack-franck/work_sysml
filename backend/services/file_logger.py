"""
Service de sauvegarde des prompts et résultats dans des fichiers.

Gère l'arborescence de traçabilité par session :
  data/sessions/{session_id}/
  ├── session.json
  ├── user_inputs/
  ├── prompts/
  └── outputs/
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List

from config import settings

logger = logging.getLogger(__name__)


class FileLogger:
    """Service de traçabilité fichier pour les sessions."""

    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or (settings.DATA_DIR / "sessions")
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_session_dir(self, session_id: str) -> Path:
        """Retourne le chemin du dossier de session."""
        return self.base_dir / session_id

    def init_session_dirs(self, session_id: str) -> None:
        """Crée l'arborescence complète de dossiers pour une nouvelle session."""
        session_dir = self.get_session_dir(session_id)
        for sub in ("user_inputs", "prompts", "outputs"):
            (session_dir / sub).mkdir(parents=True, exist_ok=True)
        logger.info(f"Arborescence créée : {session_dir}")

    def save_user_inputs(self, session_id: str, level: str, sections: List[dict]) -> Path:
        """Sauvegarde les réponses brutes de l'utilisateur dans user_inputs/{level}.json."""
        path = self.get_session_dir(session_id) / "user_inputs" / f"{level}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(sections, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.debug(f"User inputs sauvegardés : {path}")
        return path

    def _next_prompt_number(self, session_id: str) -> int:
        """Calcule le prochain numéro séquentiel dans le dossier prompts/."""
        prompts_dir = self.get_session_dir(session_id) / "prompts"
        if not prompts_dir.exists():
            return 1
        existing = list(prompts_dir.glob("*_prompt.txt"))
        if not existing:
            return 1
        numbers = []
        for f in existing:
            try:
                numbers.append(int(f.name.split("_")[0]))
            except ValueError:
                continue
        return max(numbers) + 1 if numbers else 1

    def save_prompt(self, session_id: str, level: str, step: str, prompt: str) -> Path:
        """
        Sauvegarde un prompt envoyé au LLM.

        Args:
            step: "json" ou "sysml"

        Returns:
            Chemin du fichier créé
        """
        num = self._next_prompt_number(session_id)
        prompts_dir = self.get_session_dir(session_id) / "prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{num:03d}_{level}_{step}_prompt.txt"
        path = prompts_dir / filename
        path.write_text(prompt, encoding="utf-8")
        logger.debug(f"Prompt sauvegardé : {path}")
        return path

    def save_response(self, session_id: str, level: str, step: str, response: str) -> Path:
        """
        Sauvegarde la réponse brute du LLM (même numéro séquentiel que le dernier prompt).

        Returns:
            Chemin du fichier créé
        """
        prompts_dir = self.get_session_dir(session_id) / "prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        # Le numéro correspond au dernier prompt sauvegardé
        existing = sorted(prompts_dir.glob("*_prompt.txt"))
        if existing:
            num = int(existing[-1].name.split("_")[0])
        else:
            num = 1
        filename = f"{num:03d}_{level}_{step}_response.txt"
        path = prompts_dir / filename
        path.write_text(response, encoding="utf-8")
        logger.debug(f"Réponse sauvegardée : {path}")
        return path

    def save_sysml_output(self, session_id: str, level: str, sysml_code: str) -> Path:
        """Sauvegarde le code SysML v2 final dans outputs/{level}.sysml."""
        path = self.get_session_dir(session_id) / "outputs" / f"{level}.sysml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(sysml_code, encoding="utf-8")
        logger.debug(f"SysML output sauvegardé : {path}")
        return path

    def save_full_sysml(self, session_id: str, levels_code: Dict[str, str]) -> Path:
        """
        Concatène les codes SysML v2 de tous les niveaux disponibles.
        Ordre : operational, functional, logical, technical.
        """
        order = ["operational", "functional", "logical", "technical"]
        parts = []
        for level in order:
            code = levels_code.get(level, "")
            if not code:
                continue
            parts.append(
                f"// ============================================\n"
                f"// NIVEAU {level.upper()}\n"
                f"// ============================================\n"
                f"{code}"
            )
        full_code = "\n\n".join(parts)
        path = self.get_session_dir(session_id) / "outputs" / "full_system.sysml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(full_code, encoding="utf-8")
        logger.debug(f"Full SysML sauvegardé : {path}")
        return path

    def get_prompt_files(self, session_id: str) -> List[dict]:
        """Retourne la liste de tous les fichiers de prompts/réponses d'une session."""
        prompts_dir = self.get_session_dir(session_id) / "prompts"
        if not prompts_dir.exists():
            return []
        files = []
        for f in sorted(prompts_dir.iterdir()):
            if f.is_file():
                files.append({
                    "filename": f.name,
                    "filepath": str(f),
                    "size_bytes": f.stat().st_size,
                })
        return files

    def delete_session_files(self, session_id: str) -> None:
        """Supprime récursivement tout le dossier de session."""
        session_dir = self.get_session_dir(session_id)
        if session_dir.exists():
            shutil.rmtree(session_dir)
            logger.info(f"Session supprimée : {session_dir}")
