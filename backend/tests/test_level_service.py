"""
Tests unitaires pour LevelService
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from services.level_service import LevelService
from services.state_service import StateService
from services.llm_base import LLMBase


# Mock LLM
class MockLLM(LLMBase):
    """LLM simulé pour les tests"""
    
    def generate(self, prompt, temperature=0.05, max_tokens=8192):
        prompt_lower = prompt.lower()
        
        # D'abord vérifier si c'est une demande de JSON
        # Le prompt JSON dit "TON RÉSULTAT (JSON UNIQUEMENT"
        if "json uniquement" in prompt_lower or "json only" in prompt_lower:
            # Générer du JSON selon le niveau
            if "opérationnel" in prompt_lower or "operational" in prompt_lower:
                return json.dumps({
                    "system_name": "TestSystem",
                    "description": "A test system",
                    "warnings": [],
                    "stakeholders": ["User"],
                    "external_systems": ["External"],
                    "system_boundaries": "The system",
                    "use_cases": [{"name": "UC1", "actors": ["User"], "includes": []}],
                    "operational_scenarios": [],
                    "requirements": [{"id": "REQ1", "text": "Test requirement", "satisfied_by": None}]
                })
            elif "fonctionnel" in prompt_lower or "functional" in prompt_lower:
                return json.dumps({
                    "system_name": "TestSystem",
                    "warnings": [],
                    "functions": [{"name": "F1", "description": "Function 1", "inputs": [], "outputs": [], "sub_functions": []}],
                    "functional_flows": [],
                    "modes": []
                })
            elif "logique" in prompt_lower or "logical" in prompt_lower:
                return json.dumps({
                    "system_name": "TestSystem",
                    "warnings": [],
                    "parts": [{"name": "P1", "type": None, "description": None, "ports": [], "children": []}],
                    "connections": [],
                    "requirements": []
                })
            elif "technique" in prompt_lower or "technical" in prompt_lower:
                return json.dumps({
                    "system_name": "TestSystem",
                    "warnings": [],
                    "technical_parts": [{"name": "TP1", "type": None, "description": None, "ports": [], "children": []}],
                    "physical_connections": [],
                    "technology_choices": []
                })
        
        # Sinon, si c'est une demande de code SysML
        # Le prompt SysML dit "CODE SysML v2 UNIQUEMENT"
        elif "code sysml" in prompt_lower or ("sysml" in prompt_lower and "code" in prompt_lower):
            # Générer du code SysML selon le niveau
            if "opérationnel" in prompt_lower or "operational" in prompt_lower:
                return """package 'TestSystem - Operational' {
    use case def UC1;
    requirement def REQ1;
}"""
            elif "fonctionnel" in prompt_lower or "functional" in prompt_lower:
                return """package 'TestSystem - Functional' {
    action def F1;
}"""
            elif "logique" in prompt_lower or "logical" in prompt_lower:
                return """package 'TestSystem - Logical' {
    part def P1;
}"""
            elif "technique" in prompt_lower or "technical" in prompt_lower:
                return """package 'TestSystem - Technical' {
    part def TP1;
}"""
            else:
                return """package 'TestSystem' {
    // Generic code
}"""
        
        # Sinon, si c'est une demande de modification (patch)
        elif "modifi" in prompt_lower or "patch" in prompt_lower:
            # Pour les patches, retourner un modèle modifié
            if "operational" in prompt_lower or "opérationnel" in prompt_lower:
                return json.dumps({
                    "system_name": "TestSystem Modified",
                    "description": "A modified system",
                    "warnings": [],
                    "stakeholders": ["User", "Admin"],
                    "external_systems": ["External"],
                    "system_boundaries": "The system",
                    "use_cases": [{"name": "UC1", "actors": ["User"], "includes": []}],
                    "operational_scenarios": [],
                    "requirements": [{"id": "REQ1", "text": "Test requirement", "satisfied_by": None}]
                })
            else:
                return json.dumps({
                    "system_name": "TestSystem Modified",
                    "warnings": [],
                    "functions": [],
                    "parts": [],
                    "technical_parts": []
                })
        
        # Default - retour de JSON vide
        return json.dumps({"system_name": "TestSystem", "warnings": []})
    
    def get_model_name(self):
        return "mock"
    
    def get_provider_name(self):
        return "mock"


# Mock RAG
class MockRAG:
    """RAG simulé pour les tests"""
    
    def search(self, query, top_k=8):
        return [
            {"content": "example sysml code", "file": "test.sysml", "score": 0.9}
        ]


# Mock FidelityChecker
class MockFidelityChecker:
    """FidelityChecker simulé pour les tests"""
    
    def check(self, description, model_json):
        return {
            "is_faithful": True,
            "score": 0.95,
            "issues": []
        }
    
    def build_correction_prompt(self, description, model_json, issues):
        return "Correction prompt"


# Mock DiagramService
class MockDiagramService:
    """DiagramService simulé pour les tests"""
    
    def generate_for_level(self, system_model, level):
        return {"diagrams": []}


@pytest.fixture
def temp_dir():
    """Crée un répertoire temporaire pour les tests"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def state_service(temp_dir):
    """Crée un StateService pour les tests"""
    return StateService(state_dir=Path(temp_dir))


@pytest.fixture
def level_service(state_service):
    """Crée un LevelService pour les tests"""
    llm = MockLLM()
    rag = MockRAG()
    fidelity_checker = MockFidelityChecker()
    diagram_service = MockDiagramService()
    
    return LevelService(
        llm=llm,
        rag=rag,
        state=state_service,
        fidelity_checker=fidelity_checker,
        diagram_service=diagram_service
    )


def test_generate_operational(level_service):
    """Test de génération du niveau opérationnel"""
    result = level_service.generate_level(
        description="A test system with users",
        level="operational",
        session_id=None,
        use_rag=True
    )
    
    assert result["session_id"] is not None
    assert result["level"] == "operational"
    assert result["model"]["system_name"] == "TestSystem"
    assert len(result["sysml_code"]) > 0
    assert "available_diagrams" in result


def test_generate_functional_requires_validated_operational(level_service):
    """Test que functional nécessite operational validé"""
    # Créer une session avec operational non validé
    result = level_service.generate_level(
        description="A test system",
        level="operational",
        session_id=None,
        use_rag=False
    )
    
    session_id = result["session_id"]
    
    # Essayer de générer functional sans valider operational
    with pytest.raises(ValueError, match="généré et validé"):
        level_service.generate_level(
            description="Functions",
            level="functional",
            session_id=session_id,
            use_rag=False
        )


def test_generate_functional_after_validation(level_service):
    """Test de génération functional après validation operational"""
    # Générer operational
    result = level_service.generate_level(
        description="A test system",
        level="operational",
        use_rag=False
    )
    
    session_id = result["session_id"]
    
    # Valider operational
    level_service.validate_level(session_id, "operational")
    
    # Générer functional
    result = level_service.generate_level(
        description="Functions",
        level="functional",
        session_id=session_id,
        use_rag=False
    )
    
    assert result["level"] == "functional"
    assert result["model"]["system_name"] == "TestSystem"


def test_patch_level(level_service):
    """Test de modification d'un niveau"""
    # Générer operational
    result = level_service.generate_level(
        description="A test system",
        level="operational",
        use_rag=False
    )
    
    session_id = result["session_id"]
    
    # Patcher
    patch_result = level_service.patch_level(
        session_id=session_id,
        level="operational",
        instruction="Add an admin user",
        use_rag=False
    )
    
    assert patch_result["session_id"] == session_id
    assert patch_result["level"] == "operational"
    assert "changes_summary" in patch_result
    assert len(patch_result["sysml_code"]) > 0


def test_patch_nonexistent_level(level_service):
    """Test de patch d'un niveau non généré"""
    # Créer une session
    result = level_service.generate_level(
        description="A test system",
        level="operational",
        use_rag=False
    )
    
    session_id = result["session_id"]
    
    # Essayer de patcher functional qui n'existe pas
    with pytest.raises(ValueError, match="pas encore été généré"):
        level_service.patch_level(
            session_id=session_id,
            level="functional",
            instruction="Modify something",
            use_rag=False
        )


def test_validate_level(level_service):
    """Test de validation d'un niveau"""
    # Générer operational
    result = level_service.generate_level(
        description="A test system",
        level="operational",
        use_rag=False
    )
    
    session_id = result["session_id"]
    
    # Valider
    validate_result = level_service.validate_level(session_id, "operational")
    
    assert validate_result["session_id"] == session_id
    assert validate_result["level"] == "operational"
    assert validate_result["validated"] is True
    assert validate_result["next_level"] == "functional"


def test_validate_last_level(level_service):
    """Test de validation du dernier niveau (technical)"""
    # Générer tous les niveaux
    result = level_service.generate_level(
        description="A test system",
        level="operational",
        use_rag=False
    )
    session_id = result["session_id"]
    
    # Valider et générer les niveaux suivants
    for level in ["operational", "functional", "logical"]:
        level_service.validate_level(session_id, level)
        next_level = {"operational": "functional", "functional": "logical", "logical": "technical"}[level]
        level_service.generate_level(
            description="Test",
            level=next_level,
            session_id=session_id,
            use_rag=False
        )
    
    # Valider technical
    validate_result = level_service.validate_level(session_id, "technical")
    
    assert validate_result["next_level"] is None


def test_check_coherence_functional(level_service):
    """Test de vérification de cohérence functional"""
    # Générer operational avec un use case
    result = level_service.generate_level(
        description="A test system with UC1",
        level="operational",
        use_rag=False
    )
    session_id = result["session_id"]
    
    level_service.validate_level(session_id, "operational")
    
    # Générer functional
    level_service.generate_level(
        description="Functions",
        level="functional",
        session_id=session_id,
        use_rag=False
    )
    
    # Vérifier la cohérence
    coherence = level_service.check_coherence(session_id, "functional")
    
    assert "coherent" in coherence
    assert "issues" in coherence


def test_get_full_sysml(level_service):
    """Test de récupération du code SysML complet"""
    # Générer operational
    result = level_service.generate_level(
        description="A test system",
        level="operational",
        use_rag=False
    )
    session_id = result["session_id"]
    
    level_service.validate_level(session_id, "operational")
    
    # Générer functional
    level_service.generate_level(
        description="Functions",
        level="functional",
        session_id=session_id,
        use_rag=False
    )
    
    # Récupérer le code complet
    full_code = level_service.get_full_sysml(session_id)
    
    assert len(full_code) > 0
    assert "OPERATIONAL" in full_code
    assert "FUNCTIONAL" in full_code


def test_get_level_status(level_service):
    """Test de récupération du statut des niveaux"""
    # Générer operational
    result = level_service.generate_level(
        description="A test system",
        level="operational",
        use_rag=False
    )
    session_id = result["session_id"]
    
    # Obtenir le statut
    status = level_service.get_level_status(session_id)
    
    assert "operational" in status
    assert status["operational"]["generated"] is True
    assert status["operational"]["validated"] is False
    assert status["functional"]["generated"] is False
    assert status["logical"]["generated"] is False
    assert status["technical"]["generated"] is False
    
    # Valider operational
    level_service.validate_level(session_id, "operational")
    
    # Vérifier le statut mis à jour
    status = level_service.get_level_status(session_id)
    assert status["operational"]["validated"] is True
