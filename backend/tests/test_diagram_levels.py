"""
Tests pour les nouveaux diagrammes par niveau
"""

import pytest
from services.diagram_service import DiagramService
from unittest.mock import patch, MagicMock


@pytest.fixture
def diagram_service():
    """Crée un DiagramService avec SVG mocké"""
    service = DiagramService(plantuml_server_url="http://plantuml:8080")
    return service


@pytest.fixture
def mock_render_svg():
    """Mock pour _render_svg"""
    with patch.object(DiagramService, '_render_svg', return_value="<svg>mock</svg>"):
        yield


def test_generate_for_operational(diagram_service, mock_render_svg):
    """Test génération de diagrammes pour niveau opérationnel"""
    system_model = {
        "system_name": "TestSystem",
        "stakeholders": ["User", "Admin"],
        "external_systems": ["ExternalAPI"],
        "use_cases": [
            {"name": "UC1", "actors": ["User"], "includes": []},
            {"name": "UC2", "actors": ["Admin"], "includes": []}
        ]
    }
    
    result = diagram_service.generate_for_level(system_model, "operational")
    
    assert "diagrams" in result
    diagrams = result["diagrams"]
    
    # Doit contenir context et use_cases
    diagram_types = [d["type"] for d in diagrams]
    assert "context" in diagram_types
    assert "use_cases" in diagram_types


def test_generate_for_functional(diagram_service, mock_render_svg):
    """Test génération de diagrammes pour niveau fonctionnel"""
    system_model = {
        "system_name": "TestSystem",
        "functions": [
            {
                "name": "F1",
                "description": "Function 1",
                "inputs": ["input1"],
                "outputs": ["output1"],
                "sub_functions": [
                    {"name": "F1.1", "description": "Sub function 1.1"}
                ]
            },
            {
                "name": "F2",
                "description": "Function 2",
                "inputs": [],
                "outputs": [],
                "sub_functions": []
            }
        ],
        "functional_flows": [
            {"from_function": "F1", "to_function": "F2", "item": "data", "description": "Data flow"}
        ]
    }
    
    result = diagram_service.generate_for_level(system_model, "functional")
    
    assert "diagrams" in result
    diagrams = result["diagrams"]
    
    # Doit contenir functional_breakdown et functional_behavior
    diagram_types = [d["type"] for d in diagrams]
    assert "functional_breakdown" in diagram_types
    assert "functional_behavior" in diagram_types


def test_generate_for_logical(diagram_service, mock_render_svg):
    """Test génération de diagrammes pour niveau logique"""
    system_model = {
        "system_name": "TestSystem",
        "parts": [
            {
                "name": "Component1",
                "type": "Block",
                "description": "First component",
                "ports": [{"name": "port1", "type": "in"}],
                "children": []
            }
        ],
        "connections": []
    }
    
    result = diagram_service.generate_for_level(system_model, "logical")
    
    assert "diagrams" in result
    diagrams = result["diagrams"]
    
    # Doit contenir bdd et ibd
    diagram_types = [d["type"] for d in diagrams]
    assert "bdd" in diagram_types
    assert "ibd" in diagram_types


def test_generate_functional_breakdown(diagram_service, mock_render_svg):
    """Test génération de functional breakdown (FBS)"""
    system_model = {
        "system_name": "TestSystem",
        "functions": [
            {
                "name": "Main Function",
                "description": "The main function",
                "inputs": [],
                "outputs": [],
                "sub_functions": [
                    {"name": "Sub Function 1", "description": "First sub"},
                    {"name": "Sub Function 2", "description": "Second sub"}
                ]
            }
        ]
    }
    
    result = diagram_service.generate_functional_breakdown(system_model)
    
    assert result is not None
    assert result["type"] == "functional_breakdown"
    assert "plantuml_code" in result
    assert "svg" in result
    
    # Vérifier le contenu PlantUML
    plantuml = result["plantuml_code"]
    assert "Main Function" in plantuml or "Main_Function" in plantuml
    assert "rectangle" in plantuml.lower()


def test_generate_functional_behavior(diagram_service, mock_render_svg):
    """Test génération de functional behavior"""
    system_model = {
        "system_name": "TestSystem",
        "functions": [
            {"name": "Function 1", "description": "First"},
            {"name": "Function 2", "description": "Second"}
        ],
        "functional_flows": [
            {
                "from_function": "Function 1",
                "to_function": "Function 2",
                "item": "data",
                "description": "Data transfer"
            }
        ]
    }
    
    result = diagram_service.generate_functional_behavior(system_model)
    
    assert result is not None
    assert result["type"] == "functional_behavior"
    assert "plantuml_code" in result
    
    plantuml = result["plantuml_code"]
    assert "Function 1" in plantuml or "Function_1" in plantuml
    assert "Function 2" in plantuml or "Function_2" in plantuml
    assert "-->" in plantuml


def test_generate_technical_architecture(diagram_service, mock_render_svg):
    """Test génération de technical architecture"""
    system_model = {
        "system_name": "TestSystem",
        "technical_parts": [
            {
                "name": "Server",
                "type": "Hardware",
                "description": "Application server",
                "ports": [],
                "children": []
            },
            {
                "name": "Database",
                "type": "Software",
                "description": "Data storage",
                "ports": [],
                "children": []
            }
        ],
        "physical_connections": [
            {
                "from_part": "Server",
                "from_port": None,
                "to_part": "Database",
                "to_port": None,
                "description": "Network connection"
            }
        ],
        "technology_choices": [
            {"component": "Server", "technology": "AWS EC2", "justification": "Scalable cloud infrastructure"}
        ]
    }
    
    result = diagram_service.generate_technical_architecture(system_model)
    
    assert result is not None
    assert result["type"] == "technical_architecture"
    assert "plantuml_code" in result
    
    plantuml = result["plantuml_code"]
    assert "Server" in plantuml
    assert "Database" in plantuml
    assert "node" in plantuml.lower()


def test_generate_functional_breakdown_no_functions(diagram_service):
    """Test functional breakdown sans fonctions"""
    system_model = {
        "system_name": "TestSystem",
        "functions": []
    }
    
    result = diagram_service.generate_functional_breakdown(system_model)
    
    assert result is None


def test_generate_functional_behavior_no_flows(diagram_service):
    """Test functional behavior sans flux"""
    system_model = {
        "system_name": "TestSystem",
        "functions": [{"name": "F1"}],
        "functional_flows": []
    }
    
    result = diagram_service.generate_functional_behavior(system_model)
    
    assert result is None


def test_generate_technical_architecture_fallback_to_parts(diagram_service, mock_render_svg):
    """Test technical architecture avec fallback sur parts"""
    system_model = {
        "system_name": "TestSystem",
        "parts": [
            {
                "name": "Component",
                "type": "Block",
                "description": "A component",
                "ports": [],
                "children": []
            }
        ]
    }
    
    result = diagram_service.generate_technical_architecture(system_model)
    
    assert result is not None
    assert result["type"] == "technical_architecture"
    assert "Component" in result["plantuml_code"]


def test_generate_for_level_empty_diagrams(diagram_service, mock_render_svg):
    """Test génération pour un niveau sans données"""
    system_model = {
        "system_name": "TestSystem"
    }
    
    result = diagram_service.generate_for_level(system_model, "operational")
    
    assert "diagrams" in result
    # Peut être vide ou partiel selon les données


def test_generate_for_level_invalid_level(diagram_service):
    """Test génération pour un niveau invalide"""
    system_model = {
        "system_name": "TestSystem"
    }
    
    result = diagram_service.generate_for_level(system_model, "invalid_level")
    
    assert "diagrams" in result
    assert result["diagrams"] == []
