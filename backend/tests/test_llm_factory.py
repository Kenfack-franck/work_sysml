"""
Tests pour la factory de création de LLM.
"""

import pytest
from services.llm_factory import create_llm
from services.llm_base import LLMBase
from config import settings


def test_create_gemini_invalid_key():
    """Tente de créer un LLM Gemini avec une clé vide, doit échouer."""
    with pytest.raises(ValueError, match="Aucune clé API Gemini valide"):
        create_llm("gemini", api_key="")


def test_create_gemini_placeholder_key():
    """Tente de créer un LLM Gemini avec une clé placeholder, doit échouer."""
    with pytest.raises(ValueError, match="Aucune clé API Gemini valide"):
        create_llm("gemini", api_key="ta_cle_ici")


def test_create_unsupported_provider():
    """Tente de créer un LLM avec un fournisseur non supporté, doit échouer."""
    with pytest.raises(ValueError, match="non supporté"):
        create_llm("gpt4all", api_key="test_key")


@pytest.mark.skipif(
    not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "ta_cle_ici",
    reason="Clé API Gemini non configurée"
)
def test_create_gemini_returns_llmbase():
    """Vérifie que create_llm retourne une instance de LLMBase."""
    llm = create_llm("gemini", api_key=settings.GEMINI_API_KEY, model="gemini-2.5-flash")
    
    assert isinstance(llm, LLMBase)
    assert llm.get_provider_name() == "gemini"
    assert llm.get_model_name() == "gemini-2.5-flash"


def test_create_gemini_with_custom_model():
    """Vérifie que le modèle personnalisé est bien pris en compte."""
    # Skip si pas de clé valide
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "ta_cle_ici":
        pytest.skip("Clé API Gemini non configurée")
    
    llm = create_llm("gemini", api_key=settings.GEMINI_API_KEY, model="gemini-3-pro-preview")
    assert llm.get_model_name() == "gemini-3-pro-preview"


def test_create_gemini_with_api_keys_list():
    """Vérifie que create_llm supporte une liste de clés."""
    # Skip si pas de clé valide
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "ta_cle_ici":
        pytest.skip("Clé API Gemini non configurée")
    
    llm = create_llm("gemini", api_keys=[settings.GEMINI_API_KEY], model_name="gemini-2.5-flash")
    
    assert isinstance(llm, LLMBase)
    assert llm.get_model_name() == "gemini-2.5-flash"
    # Vérifier que get_status() fonctionne
    status = llm.get_status()
    assert status["total_keys"] >= 1
    assert status["provider"] == "gemini"


def test_create_gemini_comma_separated_keys():
    """Vérifie que create_llm split les clés séparées par virgule."""
    # Skip si pas de clé valide
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "ta_cle_ici":
        pytest.skip("Clé API Gemini non configurée")
    
    # Passer 2 clés séparées par virgule
    keys_str = f"{settings.GEMINI_API_KEY},{settings.GEMINI_API_KEY}"
    llm = create_llm("gemini", api_key=keys_str, model_name="gemini-2.5-flash")
    
    status = llm.get_status()
    assert status["total_keys"] == 2
