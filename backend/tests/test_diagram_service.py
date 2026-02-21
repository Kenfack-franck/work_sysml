"""
Tests pour le service de génération de diagrammes PlantUML.
"""

import pytest
from unittest.mock import patch, MagicMock
from services.diagram_service import DiagramService


@pytest.fixture
def diagram_service():
    """Fixture qui crée une instance de DiagramService avec mock du serveur."""
    return DiagramService(plantuml_server_url="http://mock-plantuml:8080")


@pytest.fixture
def simple_model():
    """Fixture avec un modèle système simple."""
    return {
        "system_name": "DroneSystem",
        "description": "Un système de drone simple",
        "parts": [
            {
                "name": "GPS",
                "type": "Sensor",
                "description": "Capteur GPS",
                "ports": [
                    {"name": "position_out", "direction": "out", "type": "PositionData"}
                ],
                "children": []
            },
            {
                "name": "Controller",
                "type": "Computer",
                "description": "Contrôleur principal",
                "ports": [
                    {"name": "position_in", "direction": "in", "type": "PositionData"},
                    {"name": "command_out", "direction": "out", "type": "ControlSignal"}
                ],
                "children": []
            }
        ],
        "connections": [
            {
                "from_port": "GPS.position_out",
                "to_port": "Controller.position_in",
                "type": "flow",
                "item": "PositionData",
                "description": "Position data flow"
            }
        ],
        "requirements": [],
        "use_cases": []
    }


@pytest.fixture
def complex_model():
    """Fixture avec un modèle complet (requirements, use cases)."""
    return {
        "system_name": "ComplexSystem",
        "description": "Un système complexe avec exigences",
        "parts": [
            {
                "name": "Sensor",
                "type": "Component",
                "description": "Capteur",
                "ports": [],
                "children": []
            },
            {
                "name": "Processor",
                "type": "Component",
                "description": "Processeur",
                "ports": [],
                "children": []
            }
        ],
        "connections": [],
        "requirements": [
            {
                "id": "REQ-001",
                "text": "Le système doit être fiable",
                "satisfied_by": "Sensor"
            },
            {
                "id": "REQ-002",
                "text": "Le système doit être rapide",
                "satisfied_by": "Processor"
            }
        ],
        "use_cases": [
            {
                "name": "Measure",
                "actors": ["User"],
                "includes": ["Calibrate"]
            },
            {
                "name": "Calibrate",
                "actors": [],
                "includes": []
            }
        ]
    }


def test_generate_bdd_basic(diagram_service, simple_model):
    """Test la génération d'un BDD basique."""
    with patch.object(diagram_service, '_render_svg', return_value="<svg>mock bdd</svg>"):
        result = diagram_service.generate_bdd(simple_model)
    
    assert result is not None
    assert result["type"] == "bdd"
    assert result["title"] == "Block Definition Diagram"
    assert "@startuml" in result["plantuml_code"]
    assert "@enduml" in result["plantuml_code"]
    assert "<<block>>" in result["plantuml_code"]
    assert "GPS" in result["plantuml_code"]
    assert "Controller" in result["plantuml_code"]
    assert result["svg"] == "<svg>mock bdd</svg>"


def test_generate_bdd_with_ports(diagram_service, simple_model):
    """Test que le BDD contient les ports."""
    with patch.object(diagram_service, '_render_svg', return_value="<svg>mock</svg>"):
        result = diagram_service.generate_bdd(simple_model)
    
    code = result["plantuml_code"]
    # Vérifier que les ports sont présents
    assert "position_out" in code
    assert "position_in" in code
    assert "command_out" in code


def test_generate_ibd_basic(diagram_service, simple_model):
    """Test la génération d'un IBD basique."""
    with patch.object(diagram_service, '_render_svg', return_value="<svg>mock ibd</svg>"):
        result = diagram_service.generate_ibd(simple_model)
    
    assert result is not None
    assert result["type"] == "ibd"
    assert result["title"] == "Internal Block Diagram"
    assert "@startuml" in result["plantuml_code"]
    assert "component" in result["plantuml_code"].lower()
    assert "GPS" in result["plantuml_code"]
    assert "Controller" in result["plantuml_code"]


def test_generate_ibd_connections(diagram_service, simple_model):
    """Test que l'IBD contient les connexions."""
    with patch.object(diagram_service, '_render_svg', return_value="<svg>mock</svg>"):
        result = diagram_service.generate_ibd(simple_model)
    
    code = result["plantuml_code"]
    # Vérifier qu'il y a des flèches de connexion
    assert "-->" in code or "--" in code


def test_generate_requirements(diagram_service, complex_model):
    """Test la génération du diagramme d'exigences."""
    with patch.object(diagram_service, '_render_svg', return_value="<svg>mock req</svg>"):
        result = diagram_service.generate_requirements(complex_model)
    
    assert result is not None
    assert result["type"] == "requirements"
    assert "<<requirement>>" in result["plantuml_code"]
    assert "REQ-001" in result["plantuml_code"]
    assert "REQ-002" in result["plantuml_code"]
    assert "<<satisfy>>" in result["plantuml_code"]


def test_generate_requirements_empty(diagram_service, simple_model):
    """Test que le diagramme d'exigences n'est pas généré si le modèle n'a pas de requirements."""
    with patch.object(diagram_service, '_render_svg', return_value="<svg>mock</svg>"):
        result = diagram_service.generate_requirements(simple_model)
    
    assert result is None


def test_generate_use_cases(diagram_service, complex_model):
    """Test la génération du diagramme de use cases."""
    with patch.object(diagram_service, '_render_svg', return_value="<svg>mock uc</svg>"):
        result = diagram_service.generate_use_cases(complex_model)
    
    assert result is not None
    assert result["type"] == "use_cases"
    assert "usecase" in result["plantuml_code"].lower()
    assert "Measure" in result["plantuml_code"]
    assert "Calibrate" in result["plantuml_code"]
    assert "User" in result["plantuml_code"]
    assert "<<include>>" in result["plantuml_code"]


def test_generate_use_cases_empty(diagram_service, simple_model):
    """Test que le diagramme de use cases n'est pas généré si le modèle n'en a pas."""
    with patch.object(diagram_service, '_render_svg', return_value="<svg>mock</svg>"):
        result = diagram_service.generate_use_cases(simple_model)
    
    assert result is None


def test_generate_context(diagram_service, simple_model):
    """Test la génération du diagramme de contexte."""
    with patch.object(diagram_service, '_render_svg', return_value="<svg>mock ctx</svg>"):
        result = diagram_service.generate_context(simple_model)
    
    assert result is not None
    assert result["type"] == "context"
    assert "DroneSystem" in result["plantuml_code"]
    assert "rectangle" in result["plantuml_code"].lower()


def test_generate_all(diagram_service, complex_model):
    """Test que generate_all retourne plusieurs diagrammes pour un modèle complet."""
    with patch.object(diagram_service, '_render_svg', return_value="<svg>mock</svg>"):
        result = diagram_service.generate_all(complex_model)
    
    assert "diagrams" in result
    diagrams = result["diagrams"]
    
    # Devrait générer BDD, IBD, context, requirements, use_cases
    assert len(diagrams) >= 3  # Au moins BDD, IBD, context
    
    # Vérifier que chaque diagramme a les bonnes propriétés
    for diagram in diagrams:
        assert "type" in diagram
        assert "title" in diagram
        assert "plantuml_code" in diagram
        assert "svg" in diagram
        assert diagram["svg"] == "<svg>mock</svg>"


def test_generate_all_simple_model(diagram_service, simple_model):
    """Test generate_all avec un modèle simple (sans requirements ni use_cases)."""
    with patch.object(diagram_service, '_render_svg', return_value="<svg>mock</svg>"):
        result = diagram_service.generate_all(simple_model)
    
    diagrams = result["diagrams"]
    diagram_types = [d["type"] for d in diagrams]
    
    # Devrait avoir BDD, IBD, context mais PAS requirements ni use_cases
    assert "bdd" in diagram_types
    assert "ibd" in diagram_types
    assert "context" in diagram_types
    assert "requirements" not in diagram_types
    assert "use_cases" not in diagram_types


def test_sanitize_id(diagram_service):
    """Test la fonction de nettoyage des identifiants."""
    assert diagram_service._sanitize_id("Contrôleur de vol") == "Controleur_de_vol"
    assert diagram_service._sanitize_id("GPS") == "GPS"
    assert diagram_service._sanitize_id("System-v2") == "Systemv2"  # Les tirets sont enlevés
    assert diagram_service._sanitize_id("test@123!") == "test123"  # Les caractères spéciaux sont enlevés
    assert diagram_service._sanitize_id("Moteur électrique") == "Moteur_electrique"


def test_sanitize_id_special_chars(diagram_service):
    """Test que sanitize_id enlève les caractères spéciaux."""
    result = diagram_service._sanitize_id("Test!@#$%Component")
    # Ne devrait contenir que des lettres, chiffres et underscores
    assert all(c.isalnum() or c == '_' for c in result)


def test_sanitize_id_starts_with_letter(diagram_service):
    """Test que sanitize_id assure que l'ID commence par une lettre."""
    # Si commence par un chiffre, devrait ajouter un préfixe
    result = diagram_service._sanitize_id("123Test")
    assert result[0].isalpha() or result.startswith("_")


def test_render_svg_failure(diagram_service, simple_model):
    """Test que le service gère gracieusement l'échec du serveur PlantUML."""
    with patch.object(diagram_service, '_render_svg', return_value=""):
        result = diagram_service.generate_bdd(simple_model)
    
    # Le diagramme devrait quand même être généré, avec un SVG vide
    assert result is not None
    assert result["svg"] == ""
    assert result["plantuml_code"]  # Le code PlantUML devrait être présent


def test_bdd_with_hierarchy(diagram_service):
    """Test le BDD avec des composants hiérarchiques (children)."""
    model = {
        "system_name": "HierarchicalSystem",
        "description": "Système avec hiérarchie",
        "parts": [
            {
                "name": "Parent",
                "type": "System",
                "description": "Composant parent",
                "ports": [],
                "children": [
                    {
                        "name": "Child1",
                        "type": "Component",
                        "description": "Enfant 1",
                        "ports": [],
                        "children": []
                    },
                    {
                        "name": "Child2",
                        "type": "Component",
                        "description": "Enfant 2",
                        "ports": [],
                        "children": []
                    }
                ]
            }
        ],
        "connections": [],
        "requirements": [],
        "use_cases": []
    }
    
    with patch.object(diagram_service, '_render_svg', return_value="<svg>mock</svg>"):
        result = diagram_service.generate_bdd(model)
    
    code = result["plantuml_code"]
    # Vérifier que la relation de composition est présente
    assert "Parent" in code
    assert "Child1" in code
    assert "Child2" in code
    assert "*--" in code or "contient" in code.lower()


def test_ibd_with_multiple_connections(diagram_service):
    """Test l'IBD avec plusieurs connexions."""
    model = {
        "system_name": "ConnectedSystem",
        "description": "Système avec multiples connexions",
        "parts": [
            {"name": "A", "type": "C", "description": "", "ports": [
                {"name": "out1", "direction": "out", "type": "T"},
                {"name": "out2", "direction": "out", "type": "T"}
            ], "children": []},
            {"name": "B", "type": "C", "description": "", "ports": [
                {"name": "in1", "direction": "in", "type": "T"}
            ], "children": []},
            {"name": "C", "type": "C", "description": "", "ports": [
                {"name": "in2", "direction": "in", "type": "T"}
            ], "children": []}
        ],
        "connections": [
            {"from_port": "A.out1", "to_port": "B.in1", "type": "flow", "item": "Data1", "description": ""},
            {"from_port": "A.out2", "to_port": "C.in2", "type": "flow", "item": "Data2", "description": ""}
        ],
        "requirements": [],
        "use_cases": []
    }
    
    with patch.object(diagram_service, '_render_svg', return_value="<svg>mock</svg>"):
        result = diagram_service.generate_ibd(model)
    
    code = result["plantuml_code"]
    # Vérifier que les deux connexions sont présentes
    assert "Data1" in code or "in1" in code
    assert "Data2" in code or "in2" in code
