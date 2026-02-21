"""
Implémentation du service LLM pour Google Gemini avec rotation automatique de clés.
"""

from google import genai
from google.genai import types
from services.llm_base import LLMBase


class GeminiLLM(LLMBase):
    """Service LLM utilisant Google Gemini avec rotation automatique de clés."""

    def __init__(self, api_keys: list[str], model_name: str = "gemini-2.5-flash"):
        """
        Initialise le service Gemini avec rotation de clés.
        
        Args:
            api_keys: Liste de clés API Gemini (au moins 1)
            model_name: Nom du modèle Gemini à utiliser
        
        Raises:
            ValueError: Si aucune clé API valide n'est fournie
        """
        # Filtrer les clés vides et les placeholders
        self.api_keys = [k.strip() for k in api_keys if k.strip() and k.strip() != "ta_cle_ici"]
        if not self.api_keys:
            raise ValueError(
                "Aucune clé API Gemini valide fournie. "
                "Modifie le fichier .env avec tes clés : GEMINI_API_KEYS=AIzaSy..."
            )
        
        self.model_name = model_name
        self.current_key_index = 0
        self.failed_keys = set()  # Index des clés qui ont atteint leur quota
        self._init_model()

    def _init_model(self):
        """Initialise le modèle avec la clé courante."""
        key = self.api_keys[self.current_key_index]
        self.client = genai.Client(api_key=key)
        
        # Log discret (ne pas afficher la clé complète)
        key_preview = key[:8] + "..." + key[-4:]
        print(f"[GeminiLLM] Utilisation de la clé {self.current_key_index + 1}/{len(self.api_keys)} "
              f"({key_preview}) avec modèle {self.model_name}")

    def _rotate_key(self) -> bool:
        """
        Passe à la clé suivante disponible.
        
        Returns:
            True si une nouvelle clé est disponible, False si toutes sont épuisées
        """
        self.failed_keys.add(self.current_key_index)
        
        # Chercher la prochaine clé disponible
        for i in range(len(self.api_keys)):
            next_index = (self.current_key_index + 1 + i) % len(self.api_keys)
            if next_index not in self.failed_keys:
                self.current_key_index = next_index
                self._init_model()
                print(f"[GeminiLLM] ⚠️ Quota atteint, rotation vers clé "
                      f"{self.current_key_index + 1}/{len(self.api_keys)}")
                return True
        
        print("[GeminiLLM] ❌ Toutes les clés API ont atteint leur quota !")
        return False

    def generate(self, prompt: str, temperature: float = 0.05, max_tokens: int = 8192, response_mime_type: str = None) -> str:
        """
        Génère du texte avec rotation automatique en cas de quota dépassé.
        
        Args:
            prompt: Le texte d'entrée
            temperature: Température de génération (0.0-1.0)
            max_tokens: Nombre maximum de tokens
            response_mime_type: Format de sortie forcé (ex: "application/json")
        
        Returns:
            Le texte généré
        
        Raises:
            ValueError: Si toutes les clés ont atteint leur quota ou autre erreur
        """
        last_error = None
        attempts = 0
        max_attempts = len(self.api_keys) + 1
        
        while attempts < max_attempts:
            try:
                config_kwargs = dict(temperature=temperature, max_output_tokens=max_tokens)
                if response_mime_type:
                    config_kwargs["response_mime_type"] = response_mime_type
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(**config_kwargs)
                )
                
                if response and response.text:
                    return response.text
                else:
                    raise ValueError("Réponse vide du modèle")
                    
            except Exception as e:
                error_str = str(e)
                last_error = e
                
                # Si c'est une erreur de quota (429, RESOURCE_EXHAUSTED)
                if ("429" in error_str or 
                    "RESOURCE_EXHAUSTED" in error_str or 
                    "quota" in error_str.lower() or
                    "rate limit" in error_str.lower()):
                    
                    if not self._rotate_key():
                        raise ValueError(
                            f"Toutes les clés API ({len(self.api_keys)}) ont atteint leur quota. "
                            f"Dernière erreur : {error_str}"
                        )
                    attempts += 1
                    continue
                
                # Si c'est une autre erreur, on ne fait pas de rotation
                raise
        
        raise ValueError(f"Échec après {attempts} tentatives. Dernière erreur : {last_error}")

    def get_model_name(self) -> str:
        """Retourne le nom du modèle utilisé."""
        return self.model_name

    def get_provider_name(self) -> str:
        """Retourne le nom du fournisseur."""
        return "gemini"

    def get_status(self) -> dict:
        """
        Retourne le statut des clés API.
        
        Returns:
            Dict avec le statut : provider, model, total_keys, active_key, 
            exhausted_keys, available_keys
        """
        return {
            "provider": "gemini",
            "model": self.model_name,
            "total_keys": len(self.api_keys),
            "active_key": self.current_key_index + 1,
            "exhausted_keys": len(self.failed_keys),
            "available_keys": len(self.api_keys) - len(self.failed_keys)
        }
