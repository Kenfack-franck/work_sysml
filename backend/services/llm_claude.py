"""
Implémentation du service LLM pour Anthropic Claude.
"""

import anthropic
import logging

from services.llm_base import LLMBase

logger = logging.getLogger(__name__)


class ClaudeLLM(LLMBase):
    """Service LLM utilisant Anthropic Claude."""

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001"):
        if not api_key or api_key.strip() == "":
            raise ValueError(
                "Clé API Anthropic manquante. "
                "Configurez ANTHROPIC_API_KEY dans .env"
            )
        self.client = anthropic.Anthropic(api_key=api_key.strip())
        self.model = model
        logger.info(f"[ClaudeLLM] Modèle: {model}")

    def generate(self, prompt: str, temperature: float = 0.05, max_tokens: int = 8192, response_mime_type: str = None) -> str:
        """
        Génère du texte via l'API Anthropic Claude.

        Args:
            prompt: Le texte d'entrée
            temperature: Température de génération (0.0-1.0)
            max_tokens: Nombre maximum de tokens
            response_mime_type: Ignoré (compatibilité avec GeminiLLM)

        Returns:
            Le texte généré

        Raises:
            ValueError: En cas d'erreur API
        """
        try:
            # Haiku supporte max 64000 tokens en sortie
            capped_tokens = min(max_tokens, 64000)

            kwargs = {
                "model": self.model,
                "max_tokens": capped_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            }

            # Si JSON demandé, ajouter un system prompt pour forcer le format
            if response_mime_type and "json" in response_mime_type:
                kwargs["system"] = "Tu dois répondre uniquement en JSON valide, sans texte autour."

            # Streaming obligatoire pour les requêtes longues (>10 min)
            text = ""
            with self.client.messages.stream(**kwargs) as stream:
                for chunk in stream.text_stream:
                    text += chunk

            if not text:
                raise ValueError("Réponse vide du modèle Claude")

            return text

        except anthropic.APIError as e:
            logger.error(f"[ClaudeLLM] Erreur API: {e}")
            raise ValueError(f"Erreur API Claude: {e}")
        except Exception as e:
            logger.error(f"[ClaudeLLM] Erreur: {e}")
            raise

    def get_model_name(self) -> str:
        return self.model

    def get_provider_name(self) -> str:
        return "claude"

    def get_status(self) -> dict:
        return {
            "provider": "claude",
            "model": self.model,
            "total_keys": 1,
            "active_key": 1,
            "exhausted_keys": 0,
            "available_keys": 1,
        }
