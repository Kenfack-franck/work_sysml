"""
Interface abstraite pour les fournisseurs LLM.
Tout nouveau LLM doit implémenter cette interface.
"""

from abc import ABC, abstractmethod


class LLMBase(ABC):
    """Interface commune pour tous les fournisseurs LLM."""

    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.05, max_tokens: int = 8192, response_mime_type: str = None) -> str:
        """
        Envoie un prompt au LLM et retourne la réponse texte.

        Args:
            prompt: Le prompt complet à envoyer
            temperature: Contrôle la créativité (0.0 = déterministe, 1.0 = créatif)
            max_tokens: Nombre maximum de tokens dans la réponse

        Returns:
            La réponse texte du LLM
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Retourne le nom du modèle utilisé."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Retourne le nom du fournisseur (gemini, openai, ollama...)."""
        pass
