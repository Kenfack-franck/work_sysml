"""
Tests d'intégration pour les endpoints de l'API.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Crée un client de test FastAPI."""
    return TestClient(app)


def test_health_endpoint(client):
    """Teste le endpoint de health check."""
    response = client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert data["status"] == "ok"


def test_health_contains_config(client):
    """Vérifie que le health check contient les informations de configuration."""
    response = client.get("/api/health")
    data = response.json()
    
    assert "llm_provider" in data
    assert "llm_model" in data
    assert "embedding_provider" in data
    assert "embedding_model" in data
    assert "version" in data
    
    # Vérifie les valeurs attendues
    assert data["llm_provider"] == "gemini"
    assert data["embedding_provider"] == "local"


def test_health_check_format(client):
    """Vérifie le format de la réponse du health check."""
    response = client.get("/api/health")
    data = response.json()
    
    # Vérifie les types
    assert isinstance(data["status"], str)
    assert isinstance(data["version"], str)
    assert isinstance(data["sysml_repo_exists"], bool)


def test_rag_stats_endpoint(client):
    """Teste le endpoint des statistiques RAG."""
    # Note: Ce test peut échouer si le RAG n'est pas initialisé
    # mais devrait retourner une erreur 503 propre
    response = client.get("/api/rag/stats")
    
    # Accepte soit 200 (RAG prêt) soit 503 (RAG non initialisé)
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "total_chunks" in data
        assert "unique_files" in data
        assert isinstance(data["total_chunks"], int)
        assert isinstance(data["unique_files"], int)


def test_sessions_endpoint(client):
    """Teste le endpoint de listage des sessions."""
    response = client.get("/api/sessions")
    
    # Peut échouer si le service n'est pas initialisé
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "sessions" in data
        assert "total" in data
        assert isinstance(data["sessions"], list)
        assert isinstance(data["total"], int)


def test_invalid_endpoint(client):
    """Teste un endpoint inexistant."""
    response = client.get("/api/nonexistent")
    assert response.status_code == 404


def test_rag_search_without_query(client):
    """Teste la recherche RAG sans paramètre query."""
    response = client.get("/api/rag/search")
    
    # Doit retourner une erreur (422 pour paramètre manquant)
    assert response.status_code == 422


def test_rag_search_empty_query(client):
    """Teste la recherche RAG avec une query vide."""
    response = client.get("/api/rag/search?query=")
    
    # Doit retourner une erreur 400 (query vide)
    assert response.status_code in [400, 503]


def test_generate_endpoint_missing_description(client):
    """Teste le endpoint generate sans description."""
    response = client.post("/api/generate", json={})
    
    # Doit retourner une erreur de validation
    assert response.status_code == 422


def test_patch_endpoint_missing_fields(client):
    """Teste le endpoint patch sans champs requis."""
    response = client.post("/api/patch", json={})
    
    # Doit retourner une erreur de validation
    assert response.status_code == 422


def test_session_endpoint_invalid_id(client):
    """Teste la récupération d'une session avec un ID invalide."""
    response = client.get("/api/session/nonexistent-session-id")
    
    # Doit retourner 404 ou 503 (selon si le service est initialisé)
    assert response.status_code in [404, 503]


def test_v2_status_no_session(client):
    """Teste le endpoint v2/status avec une session inexistante."""
    response = client.get("/api/v2/status/nonexistent-session")
    
    # Doit retourner une erreur (probablement 500 car la session n'existe pas)
    assert response.status_code in [404, 500, 503]


def test_v2_coherence_no_session(client):
    """Teste le endpoint v2/coherence avec une session inexistante."""
    response = client.get("/api/v2/coherence/nonexistent-session/operational")
    
    # Doit retourner une erreur
    assert response.status_code in [404, 500, 503]


def test_v2_full_sysml_no_session(client):
    """Teste le endpoint v2/full-sysml avec une session inexistante."""
    response = client.get("/api/v2/full-sysml/nonexistent-session")
    
    # Doit retourner une erreur
    assert response.status_code in [404, 500, 503]


def test_v2_generate_missing_fields(client):
    """Teste le endpoint v2/generate sans champs requis."""
    response = client.post("/api/v2/generate", json={})
    
    # Doit retourner une erreur de validation
    assert response.status_code == 422


def test_v2_patch_missing_fields(client):
    """Teste le endpoint v2/patch sans champs requis."""
    response = client.post("/api/v2/patch", json={})
    
    # Doit retourner une erreur de validation
    assert response.status_code == 422


def test_v2_validate_missing_fields(client):
    """Teste le endpoint v2/validate sans champs requis."""
    response = client.post("/api/v2/validate", json={})
    
    # Doit retourner une erreur de validation
    assert response.status_code == 422


def test_v2_diagrams_missing_fields(client):
    """Teste le endpoint v2/diagrams sans champs requis."""
    response = client.post("/api/v2/diagrams", json={})
    
    # Doit retourner une erreur de validation
    assert response.status_code == 422

