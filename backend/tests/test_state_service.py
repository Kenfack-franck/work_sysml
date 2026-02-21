"""
Tests pour le service de gestion des sessions.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from services.state_service import StateService


@pytest.fixture
def temp_state_service(tmp_path):
    """Crée un StateService temporaire pour les tests."""
    state_dir = tmp_path / "test_state"
    service = StateService(state_dir)
    return service


def test_create_session(temp_state_service):
    """Teste la création d'une nouvelle session."""
    session_id = temp_state_service.create_session()
    
    # Vérifie que l'ID est retourné
    assert session_id is not None
    assert len(session_id) == 36  # UUID format
    
    # Vérifie que le fichier existe
    session_file = temp_state_service.state_dir / f"{session_id}.json"
    assert session_file.exists()
    
    # Vérifie le contenu
    with open(session_file, "r") as f:
        data = json.load(f)
    
    assert data["session_id"] == session_id
    assert "created_at" in data
    assert data["system_model"] is None
    assert data["sysml_code"] is None
    assert data["history"] == []


def test_save_and_load_session(temp_state_service):
    """Teste la sauvegarde et le chargement d'une session."""
    session_id = temp_state_service.create_session()
    
    # Données à sauvegarder
    test_data = {
        "system_model": {"system_name": "Test System", "description": "A test"},
        "sysml_code": "package TestSystem { }",
        "history": [{"action": "generate", "timestamp": "2026-01-01T12:00:00"}]
    }
    
    # Sauvegarde
    temp_state_service.save_session(session_id, test_data)
    
    # Chargement
    loaded_data = temp_state_service.load_session(session_id)
    
    # Vérifications
    assert loaded_data["system_model"] == test_data["system_model"]
    assert loaded_data["sysml_code"] == test_data["sysml_code"]
    assert len(loaded_data["history"]) == 1
    assert loaded_data["history"][0]["action"] == "generate"


def test_load_nonexistent_session(temp_state_service):
    """Tente de charger une session inexistante, doit échouer."""
    with pytest.raises(FileNotFoundError, match="introuvable"):
        temp_state_service.load_session("non-existent-id")


def test_list_sessions(temp_state_service):
    """Teste le listage des sessions."""
    # Crée 3 sessions
    session_ids = []
    for i in range(3):
        session_id = temp_state_service.create_session()
        session_ids.append(session_id)
        
        # Ajoute des données différentes
        temp_state_service.save_session(session_id, {
            "system_model": {"system_name": f"System {i+1}", "description": "Test"}
        })
    
    # Liste les sessions
    sessions = temp_state_service.list_sessions()
    
    # Vérifications
    assert len(sessions) == 3
    assert all("id" in s for s in sessions)
    assert all("created_at" in s for s in sessions)
    assert all("system_name" in s for s in sessions)
    
    # Vérifie que les noms sont présents
    system_names = [s["system_name"] for s in sessions]
    assert "System 1" in system_names
    assert "System 2" in system_names
    assert "System 3" in system_names


def test_add_to_history(temp_state_service):
    """Teste l'ajout d'entrées à l'historique."""
    session_id = temp_state_service.create_session()
    
    # Ajoute 2 entrées
    temp_state_service.add_to_history(session_id, {
        "action": "generate",
        "description": "First generation"
    })
    
    temp_state_service.add_to_history(session_id, {
        "action": "patch",
        "instruction": "Add battery"
    })
    
    # Charge la session
    data = temp_state_service.load_session(session_id)
    
    # Vérifie l'historique
    assert len(data["history"]) == 2
    assert data["history"][0]["action"] == "generate"
    assert data["history"][0]["description"] == "First generation"
    assert "timestamp" in data["history"][0]
    
    assert data["history"][1]["action"] == "patch"
    assert data["history"][1]["instruction"] == "Add battery"
    assert "timestamp" in data["history"][1]


def test_list_sessions_sorted_by_date(temp_state_service):
    """Vérifie que les sessions sont triées par date de mise à jour."""
    # Crée 3 sessions avec des délais
    import time
    
    session1 = temp_state_service.create_session()
    time.sleep(0.1)
    session2 = temp_state_service.create_session()
    time.sleep(0.1)
    session3 = temp_state_service.create_session()
    
    # Modifie la session 1 en dernier
    time.sleep(0.1)
    temp_state_service.save_session(session1, {"test": "data"})
    
    # Liste les sessions
    sessions = temp_state_service.list_sessions()
    
    # La première doit être session1 (mise à jour la plus récente)
    assert sessions[0]["id"] == session1
