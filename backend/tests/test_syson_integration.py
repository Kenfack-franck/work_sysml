"""
Tests unitaires pour SysONService.
Ces tests utilisent unittest.mock pour simuler les appels HTTP.
Ils passent sans que SysON soit démarré.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Ajouter le répertoire backend au path pour l'import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.syson_service import SysONService


class TestSysONServiceInit:
    """Tests d'initialisation du service."""

    def test_syson_service_init_default(self):
        """Vérifie que SysONService s'instancie avec les valeurs par défaut."""
        service = SysONService()
        assert service.syson_url == "http://syson:8080"
        assert service.graphql_url == "http://syson:8080/api/graphql"
        assert service.headers == {"Content-Type": "application/json"}

    def test_syson_service_init_custom_url(self):
        """Vérifie que SysONService accepte une URL personnalisée."""
        service = SysONService(syson_url="http://localhost:8085")
        assert service.syson_url == "http://localhost:8085"
        assert service.graphql_url == "http://localhost:8085/api/graphql"

    def test_syson_service_init_env_var(self):
        """Vérifie que SysONService lit la variable d'environnement SYSON_URL."""
        with patch.dict(os.environ, {"SYSON_URL": "http://custom-syson:9090"}):
            service = SysONService()
            assert service.syson_url == "http://custom-syson:9090"


class TestSysONServiceAvailability:
    """Tests de vérification de disponibilité."""

    def test_syson_service_is_available_when_down(self):
        """
        Vérifie que is_available() retourne False quand SysON n'est pas démarré.
        Simule une erreur de connexion.
        """
        service = SysONService(syson_url="http://localhost:8085")
        with patch("requests.get") as mock_get:
            from requests.exceptions import ConnectionError
            mock_get.side_effect = ConnectionError("Connection refused")
            result = service.is_available()
        assert result is False

    def test_syson_service_is_available_when_up(self):
        """Vérifie que is_available() retourne True quand SysON répond 200."""
        service = SysONService(syson_url="http://localhost:8085")
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            result = service.is_available()
        assert result is True

    def test_syson_service_is_available_on_timeout(self):
        """Vérifie que is_available() retourne False en cas de timeout."""
        service = SysONService()
        with patch("requests.get") as mock_get:
            from requests.exceptions import Timeout
            mock_get.side_effect = Timeout("Timeout")
            result = service.is_available()
        assert result is False


class TestPushSysmlToSyson:
    """Tests de la méthode principale push_sysml_to_syson."""

    def _make_graphql_response(self, data: dict):
        """Helper : crée un mock de réponse requests avec du JSON."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": data}
        mock_response.raise_for_status.return_value = None
        return mock_response

    def test_push_sysml_to_syson_creates_project(self):
        """
        Vérifie que push_sysml_to_syson() appelle create_project() et
        retourne un résultat structuré.
        """
        service = SysONService(syson_url="http://localhost:8085")

        with patch.object(service, "create_project") as mock_create, \
             patch.object(service, "get_editing_context") as mock_ctx, \
             patch.object(service, "create_document") as mock_doc, \
             patch.object(service, "get_root_namespace_id") as mock_ns, \
             patch.object(service, "import_sysml_code") as mock_import:

            mock_create.return_value = {"project_id": "proj-123", "success": True, "error": ""}
            mock_ctx.return_value = "ctx-456"
            mock_doc.return_value = "doc-789"
            mock_ns.return_value = "ns-root"
            mock_import.return_value = {"success": True, "error": ""}

            result = service.push_sysml_to_syson("package Test {}", "Mon Projet")

        mock_create.assert_called_once_with("Mon Projet")
        mock_ctx.assert_called_once_with("proj-123")
        mock_doc.assert_called_once_with("ctx-456", "Mon Projet")
        mock_ns.assert_called_once_with("ctx-456", "doc-789")
        mock_import.assert_called_once_with("ctx-456", "ns-root", "package Test {}")

        assert result["success"] is True
        assert result["project_id"] == "proj-123"
        assert "proj-123" in result["syson_url"]
        assert result["error"] == ""

    def test_push_sysml_to_syson_fails_on_project_creation_error(self):
        """Vérifie que push_sysml_to_syson retourne une erreur si create_project échoue."""
        service = SysONService()

        with patch.object(service, "create_project") as mock_create:
            mock_create.return_value = {
                "project_id": None,
                "success": False,
                "error": "GraphQL error"
            }
            result = service.push_sysml_to_syson("package Test {}")

        assert result["success"] is False
        assert "GraphQL error" in result["error"]
        assert result["project_id"] is None

    def test_push_sysml_to_syson_fails_on_editing_context_error(self):
        """Vérifie le comportement si l'editing context ne peut pas être récupéré."""
        service = SysONService()

        with patch.object(service, "create_project") as mock_create, \
             patch.object(service, "get_editing_context") as mock_ctx:

            mock_create.return_value = {"project_id": "proj-abc", "success": True, "error": ""}
            mock_ctx.return_value = None

            result = service.push_sysml_to_syson("package Test {}")

        assert result["success"] is False
        assert "editing context" in result["error"].lower()
        assert result["project_id"] == "proj-abc"


class TestGetProjectUrl:
    """Tests de la méthode get_project_url."""

    def test_get_project_url_format(self):
        """Vérifie que get_project_url() retourne le bon format d'URL."""
        service = SysONService()
        url = service.get_project_url("abc-123-def")
        assert url == "http://localhost:8085/projects/abc-123-def/edit"

    def test_get_project_url_always_uses_localhost(self):
        """Vérifie que l'URL retournée utilise toujours localhost:8085 (accès navigateur)."""
        # Même si le service pointe vers syson:8080 en interne
        service = SysONService(syson_url="http://syson:8080")
        url = service.get_project_url("proj-xyz")
        assert "localhost:8085" in url
        assert "syson:8080" not in url

    def test_get_project_url_contains_project_id(self):
        """Vérifie que l'URL contient bien le project_id."""
        service = SysONService()
        project_id = "12345678-1234-1234-1234-123456789abc"
        url = service.get_project_url(project_id)
        assert project_id in url
        assert "/projects/" in url
        assert "/edit" in url
