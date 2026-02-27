"""
Configuration centralisée du SysML Agent.
Toutes les valeurs sont surchargeables via variables d'environnement ou fichier .env
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration de l'application."""

    # === Chemins ===
    BASE_DIR: Path = Path(__file__).parent
    DATA_DIR: Path = BASE_DIR / "data"
    CHROMA_DIR: Path = DATA_DIR / "chroma"
    STATE_DIR: Path = DATA_DIR / "state"
    SYSML_REPO_PATH: Path = Path(
        os.getenv(
            "SYSML_REPO_PATH",
            "/app/SysML-v2-Release"
        )
    )

    # === LLM ===
    LLM_PROVIDER: str = "gemini"  # Options: "gemini", "openai", "ollama"
    GEMINI_API_KEY: str = ""  # Rétrocompatibilité : clé unique
    GEMINI_API_KEYS: str = ""  # Multi-clés séparées par virgules pour rotation automatique
    LLM_MODEL: str = "gemini-2.5-flash"  # Modèle par défaut, configurable
    LLM_TEMPERATURE: float = 0.05
    LLM_MAX_TOKENS: int = 8192

    # === Embeddings ===
    EMBEDDING_PROVIDER: str = "local"  # Options: "local", "openai", "gemini"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # === RAG ===
    RAG_CHUNK_SIZE: int = 1500
    RAG_CHUNK_OVERLAP: int = 200
    RAG_TOP_K: int = 8

    # === Serveur ===
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Instance unique
settings = Settings()
