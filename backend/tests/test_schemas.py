"""
Tests pour les schémas Pydantic.
"""

import pytest
from pydantic import ValidationError
from models.schemas import (
    GenerateRequest,
    PatchRequest,
    PortSchema,
    ConnectionSchema,
    RequirementSchema,
    UseCaseSchema,
    PartSchema,
    SystemModel,
    GenerateResponse,
    PatchResponse
)


def test_generate_request_valid():
    """Teste la création d'une requête de génération valide."""
    request = GenerateRequest(
        description="Un système simple de test avec plusieurs composants",
        use_rag=True
    )
    
    assert request.description == "Un système simple de test avec plusieurs composants"
    assert request.use_rag is True
    assert request.session_id is None


def test_generate_request_too_short():
    """Teste qu'une description trop courte est rejetée."""
    with pytest.raises(ValidationError):
        GenerateRequest(description="ab")  # Moins de 10 caractères


def test_generate_request_with_session_id():
    """Teste la création d'une requête avec session_id."""
    request = GenerateRequest(
        description="Un système de test",
        session_id="test-session-123",
        use_rag=False
    )
    
    assert request.session_id == "test-session-123"
    assert request.use_rag is False


def test_patch_request_valid():
    """Teste la création d'une requête de patch valide."""
    request = PatchRequest(
        session_id="session-123",
        instruction="Ajouter un moteur",
        use_rag=True
    )
    
    assert request.session_id == "session-123"
    assert request.instruction == "Ajouter un moteur"


def test_patch_request_instruction_too_short():
    """Teste qu'une instruction trop courte est rejetée."""
    with pytest.raises(ValidationError):
        PatchRequest(session_id="test", instruction="Add")  # Moins de 5 caractères


def test_port_schema():
    """Teste la création d'un port valide."""
    port = PortSchema(name="position_out", direction="out", type="position")
    
    assert port.name == "position_out"
    assert port.direction == "out"
    assert port.type == "position"


def test_port_schema_invalid_direction():
    """Teste qu'une direction invalide est rejetée."""
    with pytest.raises(ValidationError):
        PortSchema(name="test", direction="bidirectional", type="data")


def test_connection_schema():
    """Teste la création d'une connexion valide."""
    connection = ConnectionSchema(
        from_port="GPS.position_out",
        to_port="Controller.position_in",
        type="flow",
        item="position"
    )
    
    assert connection.from_port == "GPS.position_out"
    assert connection.type == "flow"
    assert connection.item == "position"


def test_connection_schema_invalid_type():
    """Teste qu'un type de connexion invalide est rejeté."""
    with pytest.raises(ValidationError):
        ConnectionSchema(
            from_port="A.p1",
            to_port="B.p2",
            type="wireless"  # Type invalide
        )


def test_requirement_schema():
    """Teste la création d'une exigence valide."""
    req = RequirementSchema(
        id="REQ-001",
        text="Le système doit fonctionner à -40°C",
        satisfied_by="Controller"
    )
    
    assert req.id == "REQ-001"
    assert req.satisfied_by == "Controller"


def test_use_case_schema():
    """Teste la création d'un cas d'utilisation valide."""
    use_case = UseCaseSchema(
        name="Navigate to destination",
        actors=["Pilot", "GPS"],
        includes=["GetPosition", "CalculateRoute"]
    )
    
    assert use_case.name == "Navigate to destination"
    assert len(use_case.actors) == 2
    assert len(use_case.includes) == 2


def test_part_schema():
    """Teste la création d'une partie valide."""
    part = PartSchema(
        name="Controller",
        type="FlightController",
        description="Main flight controller",
        ports=[
            PortSchema(name="data_in", direction="in", type="data"),
            PortSchema(name="cmd_out", direction="out", type="command")
        ]
    )
    
    assert part.name == "Controller"
    assert len(part.ports) == 2
    assert part.children == []


def test_system_model_empty():
    """Teste la création d'un modèle système vide."""
    model = SystemModel(
        system_name="SimpleSystem",
        description="A simple test system"
    )
    
    assert model.system_name == "SimpleSystem"
    assert model.parts == []
    assert model.connections == []
    assert model.requirements == []
    assert model.use_cases == []
    assert model.warnings == []


def test_system_model_full():
    """Teste la création d'un modèle système complet."""
    model = SystemModel(
        system_name="DroneSystem",
        description="A complete drone system",
        warnings=["GPS not redundant"],
        parts=[
            PartSchema(
                name="GPS",
                ports=[PortSchema(name="position_out", direction="out", type="position")]
            ),
            PartSchema(
                name="Controller",
                ports=[
                    PortSchema(name="position_in", direction="in", type="position"),
                    PortSchema(name="command_out", direction="out", type="command")
                ]
            ),
            PartSchema(
                name="Motor",
                ports=[PortSchema(name="command_in", direction="in", type="command")]
            )
        ],
        connections=[
            ConnectionSchema(
                from_port="GPS.position_out",
                to_port="Controller.position_in",
                type="flow",
                item="position"
            ),
            ConnectionSchema(
                from_port="Controller.command_out",
                to_port="Motor.command_in",
                type="flow",
                item="command"
            )
        ],
        requirements=[
            RequirementSchema(
                id="REQ-001",
                text="System must maintain stable flight",
                satisfied_by="Controller"
            )
        ],
        use_cases=[
            UseCaseSchema(
                name="AutomaticFlight",
                actors=["Pilot", "Controller"]
            )
        ]
    )
    
    assert len(model.parts) == 3
    assert len(model.connections) == 2
    assert len(model.requirements) == 1
    assert len(model.use_cases) == 1
    assert len(model.warnings) == 1


def test_generate_response():
    """Teste la création d'une réponse de génération."""
    response = GenerateResponse(
        session_id="session-123",
        system_model=SystemModel(system_name="Test", description="Test"),
        sysml_code="package Test { }",
        rag_sources=["source1.sysml", "source2.sysml"]
    )
    
    assert response.session_id == "session-123"
    assert len(response.rag_sources) == 2


def test_patch_response():
    """Teste la création d'une réponse de patch."""
    response = PatchResponse(
        session_id="session-123",
        system_model=SystemModel(system_name="Test", description="Test"),
        sysml_code="package Test { }",
        changes_summary="Added battery component"
    )
    
    assert response.changes_summary == "Added battery component"
