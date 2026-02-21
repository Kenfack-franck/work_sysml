"""
Tests pour la rotation automatique de clés API LLM.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from services.llm_gemini import GeminiLLM


class TestLLMRotation:
    """Tests de rotation de clés API."""
    
    def test_single_key_success(self):
        """Test avec une seule clé, requête réussie."""
        with patch('google.genai.Client') as mock_client_class:
            # Créer un mock de client
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = "Test response"
            mock_client.models.generate_content.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            # Créer le LLM avec une clé
            llm = GeminiLLM(api_keys=["key1"], model_name="gemini-2.5-flash")
            
            # Tester la génération
            result = llm.generate("test prompt")
            
            assert result == "Test response"
            assert llm.get_status()["total_keys"] == 1
            assert llm.get_status()["available_keys"] == 1
            assert llm.get_status()["exhausted_keys"] == 0
    
    def test_rotation_on_quota_error(self):
        """Test rotation vers la 2ème clé quand la 1ère donne erreur 429."""
        with patch('google.genai.Client') as mock_client_class:
            # Créer un mock qui échoue puis réussit
            mock_client = Mock()
            
            # Premier appel : erreur de quota
            quota_error = Exception("429 RESOURCE_EXHAUSTED: quota exceeded")
            # Deuxième appel (après rotation) : succès
            mock_response = Mock()
            mock_response.text = "Success after rotation"
            
            mock_client.models.generate_content.side_effect = [quota_error, mock_response]
            mock_client_class.return_value = mock_client
            
            # Créer le LLM avec 2 clés
            llm = GeminiLLM(api_keys=["key1", "key2"], model_name="gemini-2.5-flash")
            
            # Tester la génération (devrait faire rotation)
            result = llm.generate("test prompt")
            
            assert result == "Success after rotation"
            assert llm.get_status()["exhausted_keys"] == 1
            assert llm.get_status()["available_keys"] == 1
            assert llm.current_key_index == 1  # On est sur la 2ème clé
    
    def test_all_keys_exhausted(self):
        """Test quand toutes les clés ont atteint leur quota."""
        with patch('google.genai.Client') as mock_client_class:
            # Créer un mock qui échoue toujours
            mock_client = Mock()
            quota_error = Exception("429 RESOURCE_EXHAUSTED: quota exceeded")
            mock_client.models.generate_content.side_effect = quota_error
            mock_client_class.return_value = mock_client
            
            # Créer le LLM avec 2 clés
            llm = GeminiLLM(api_keys=["key1", "key2"], model_name="gemini-2.5-flash")
            
            # Tester la génération (devrait lever ValueError)
            with pytest.raises(ValueError) as exc_info:
                llm.generate("test prompt")
            
            assert "Toutes les clés API" in str(exc_info.value)
            assert llm.get_status()["exhausted_keys"] == 2
            assert llm.get_status()["available_keys"] == 0
    
    def test_get_status(self):
        """Test du statut retourné."""
        with patch('google.genai.Client'):
            llm = GeminiLLM(api_keys=["key1", "key2", "key3"], model_name="gemini-3-flash-preview")
            
            status = llm.get_status()
            
            assert status["provider"] == "gemini"
            assert status["model"] == "gemini-3-flash-preview"
            assert status["total_keys"] == 3
            assert status["active_key"] == 1
            assert status["exhausted_keys"] == 0
            assert status["available_keys"] == 3
    
    def test_invalid_keys_filtered(self):
        """Test que les clés vides et 'ta_cle_ici' sont ignorées."""
        with pytest.raises(ValueError) as exc_info:
            GeminiLLM(api_keys=["", "ta_cle_ici", "  "])
        
        assert "Aucune clé API Gemini valide" in str(exc_info.value)
    
    def test_valid_and_invalid_keys_mixed(self):
        """Test avec un mélange de clés valides et invalides."""
        with patch('google.genai.Client'):
            llm = GeminiLLM(
                api_keys=["", "valid_key1", "ta_cle_ici", "valid_key2", "  "],
                model_name="gemini-2.5-flash"
            )
            
            # Seulement les 2 clés valides devraient être gardées
            assert llm.get_status()["total_keys"] == 2
            assert llm.api_keys == ["valid_key1", "valid_key2"]
    
    def test_model_name_configurable(self):
        """Test que le nom du modèle est configurable."""
        with patch('google.genai.Client'):
            llm = GeminiLLM(api_keys=["key1"], model_name="gemini-3-flash-preview")
            
            assert llm.get_model_name() == "gemini-3-flash-preview"
            assert llm.get_provider_name() == "gemini"
    
    def test_non_quota_error_no_rotation(self):
        """Test qu'une erreur non-quota ne déclenche pas de rotation."""
        with patch('google.genai.Client') as mock_client_class:
            mock_client = Mock()
            # Erreur qui n'est PAS de quota
            other_error = Exception("Invalid API key")
            mock_client.models.generate_content.side_effect = other_error
            mock_client_class.return_value = mock_client
            
            llm = GeminiLLM(api_keys=["key1", "key2"], model_name="gemini-2.5-flash")
            
            # L'erreur devrait être propagée sans rotation
            with pytest.raises(Exception) as exc_info:
                llm.generate("test prompt")
            
            assert "Invalid API key" in str(exc_info.value)
            # Pas de rotation (toujours sur la clé 0)
            assert llm.current_key_index == 0
            assert llm.get_status()["exhausted_keys"] == 0
    
    def test_empty_response_raises_error(self):
        """Test qu'une réponse vide lève une ValueError."""
        with patch('google.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = ""  # Réponse vide
            mock_client.models.generate_content.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            llm = GeminiLLM(api_keys=["key1"], model_name="gemini-2.5-flash")
            
            with pytest.raises(ValueError) as exc_info:
                llm.generate("test prompt")
            
            assert "Réponse vide" in str(exc_info.value)
    
    def test_multiple_rotations(self):
        """Test de rotations multiples à travers toutes les clés."""
        with patch('google.genai.Client') as mock_client_class:
            mock_client = Mock()
            quota_error = Exception("429 quota exceeded")
            success_response = Mock()
            success_response.text = "Success"
            
            # Erreur sur key1, key2, succès sur key3
            mock_client.models.generate_content.side_effect = [
                quota_error, quota_error, success_response
            ]
            mock_client_class.return_value = mock_client
            
            llm = GeminiLLM(
                api_keys=["key1", "key2", "key3"],
                model_name="gemini-2.5-flash"
            )
            
            result = llm.generate("test prompt")
            
            assert result == "Success"
            assert llm.current_key_index == 2  # Sur la 3ème clé
            assert llm.get_status()["exhausted_keys"] == 2
            assert llm.get_status()["available_keys"] == 1
