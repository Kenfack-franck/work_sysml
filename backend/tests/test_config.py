"""
Tests pour la configuration de l'application.
"""

import pytest
from pathlib import Path
from config import settings, Settings


def test_settings_loaded():
    """Vérifie que settings est une instance de Settings."""
    assert isinstance(settings, Settings)


def test_default_values():
    """Vérifie les valeurs par défaut de la configuration."""
    assert settings.LLM_PROVIDER == "gemini"
    assert settings.EMBEDDING_PROVIDER == "local"
    assert settings.PORT == 8000
    assert settings.DEBUG is True


def test_paths_exist_or_configurable():
    """Vérifie que les chemins sont des Path valides."""
    assert isinstance(settings.CHROMA_DIR, Path)
    assert isinstance(settings.STATE_DIR, Path)
    assert isinstance(settings.BASE_DIR, Path)
    assert isinstance(settings.DATA_DIR, Path)


def test_llm_config():
    """Vérifie la configuration du LLM."""
    assert settings.LLM_TEMPERATURE >= 0.0
    assert settings.LLM_TEMPERATURE <= 1.0
    assert settings.LLM_MAX_TOKENS > 0


def test_rag_config():
    """Vérifie la configuration du RAG."""
    assert settings.RAG_CHUNK_SIZE > 0
    assert settings.RAG_CHUNK_OVERLAP >= 0
    assert settings.RAG_TOP_K > 0
    assert settings.RAG_CHUNK_OVERLAP < settings.RAG_CHUNK_SIZE
