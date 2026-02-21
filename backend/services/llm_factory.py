"""
Factory pour créer le bon service LLM selon la configuration.
Pour ajouter un nouveau LLM :
  1. Créer llm_nouveau.py qui implémente LLMBase
  2. Ajouter un cas dans create_llm()
"""

from services.llm_base import LLMBase


def create_llm(
    provider: str = "gemini", 
    api_key: str = None, 
    api_keys: list[str] = None, 
    model: str = None,
    model_name: str = None
) -> LLMBase:
    """
    Crée une instance du service LLM selon le fournisseur.

    Args:
        provider: "gemini", "openai", "ollama"
        api_key: Clé API unique (rétrocompatibilité)
        api_keys: Liste de clés API pour rotation automatique
        model: Nom du modèle (alias de model_name)
        model_name: Nom du modèle

    Returns:
        Instance de LLMBase

    Raises:
        ValueError: Si le fournisseur n'est pas supporté ou si aucune clé valide
    """
    if provider == "gemini":
        from services.llm_gemini import GeminiLLM
        
        # Construire la liste de clés
        keys = []
        if api_keys:
            keys = api_keys
        elif api_key:
            # Si c'est une chaîne avec des virgules, la splitter
            if "," in api_key:
                keys = [k.strip() for k in api_key.split(",")]
            else:
                keys = [api_key]
        
        # Validation
        if not keys or all(not k or k == "ta_cle_ici" for k in keys):
            raise ValueError(
                "Aucune clé API Gemini valide fournie. "
                "Configurez GEMINI_API_KEYS dans .env"
            )
        
        # Déterminer le modèle (priorité à model_name)
        selected_model = model_name or model or "gemini-2.5-flash"
        
        return GeminiLLM(api_keys=keys, model_name=selected_model)

    # === Ajouter ici les futurs fournisseurs ===
    # elif provider == "openai":
    #     from services.llm_openai import OpenAILLM
    #     return OpenAILLM(api_key=kwargs["api_key"], model=kwargs.get("model"))
    #
    # elif provider == "ollama":
    #     from services.llm_ollama import OllamaLLM
    #     return OllamaLLM(model=kwargs.get("model", "llama3"))

    else:
        supported = ["gemini"]
        raise ValueError(
            f"Fournisseur LLM '{provider}' non supporté. "
            f"Options disponibles : {supported}"
        )
