"""
Schémas Pydantic pour valider les entrées/sorties API.
Support du workflow MBSE multi-niveaux (Operational, Functional, Logical, Technical).
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum


class GenerateRequest(BaseModel):
    """Requête de génération d'un nouveau système."""
    session_id: Optional[str] = None
    description: str = Field(..., min_length=10)
    use_rag: bool = True


class PatchRequest(BaseModel):
    """Requête de modification d'un système existant."""
    session_id: str = Field(..., min_length=1)
    instruction: str = Field(..., min_length=5)
    use_rag: bool = True


class PortSchema(BaseModel):
    """Schéma d'un port."""
    name: str
    direction: str = Field(..., pattern="^(in|out|inout)$")
    type: str


class ConnectionSchema(BaseModel):
    """Schéma d'une connexion entre ports."""
    from_port: str
    to_port: str
    type: str = Field(..., pattern="^(flow|connection|interface)$")
    item: Optional[str] = None
    description: Optional[str] = None


class RequirementSchema(BaseModel):
    """Schéma d'une exigence."""
    id: str
    text: str
    satisfied_by: Optional[str] = None


class UseCaseSchema(BaseModel):
    """Schéma d'un cas d'utilisation."""
    name: str
    actors: List[str]
    includes: Optional[List[str]] = None


class PartSchema(BaseModel):
    """Schéma d'une partie/composant du système."""
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    ports: List[PortSchema] = Field(default_factory=list)
    children: List["PartSchema"] = Field(default_factory=list)


class SystemModel(BaseModel):
    """Modèle JSON du système complet."""
    system_name: str
    description: str
    warnings: List[str] = Field(default_factory=list)
    parts: List[PartSchema] = Field(default_factory=list)
    connections: List[ConnectionSchema] = Field(default_factory=list)
    requirements: List[RequirementSchema] = Field(default_factory=list)
    use_cases: List[UseCaseSchema] = Field(default_factory=list)


class GenerateResponse(BaseModel):
    """Réponse de génération."""
    session_id: str
    system_model: SystemModel
    sysml_code: str
    rag_sources: List[str]


class PatchResponse(BaseModel):
    """Réponse de modification."""
    session_id: str
    system_model: SystemModel
    sysml_code: str
    changes_summary: str


# ============================================================================
# SCHÉMAS POUR WORKFLOW MBSE MULTI-NIVEAUX
# ============================================================================

class ModelLevel(str, Enum):
    """Niveaux du workflow MBSE."""
    OPERATIONAL = "operational"
    FUNCTIONAL = "functional"
    LOGICAL = "logical"
    TECHNICAL = "technical"


# === MODÈLES PAR NIVEAU ===

class OperationalModel(BaseModel):
    """
    Niveau opérationnel : contexte, acteurs, cas d'utilisation.
    Répond à la question : QUI utilise le système et POURQUOI ?
    """
    system_name: str
    description: str
    warnings: List[str] = Field(default_factory=list)
    stakeholders: List[str] = Field(default_factory=list)  # Parties prenantes
    external_systems: List[str] = Field(default_factory=list)  # Systèmes externes interagissant
    system_boundaries: str = ""  # Périmètre et limites du système
    use_cases: List[UseCaseSchema] = Field(default_factory=list)
    operational_scenarios: List[dict] = Field(default_factory=list)  # {name, description, steps: []}
    requirements: List[RequirementSchema] = Field(default_factory=list)  # Besoins opérationnels


class FunctionalModel(BaseModel):
    """
    Niveau fonctionnel : fonctions, comportements, flux.
    Répond à la question : QUE FAIT le système ?
    """
    system_name: str
    warnings: List[str] = Field(default_factory=list)
    functions: List[dict] = Field(default_factory=list)  # {name, description, inputs: [], outputs: [], sub_functions: []}
    functional_flows: List[dict] = Field(default_factory=list)  # {from_function, to_function, item, description}
    modes: List[dict] = Field(default_factory=list)  # {name, description, active_functions: []}


class LogicalModel(BaseModel):
    """
    Niveau logique : composants, interfaces, architecture.
    Répond à la question : COMMENT le système est-il structuré (indépendamment de l'implémentation) ?
    """
    system_name: str
    warnings: List[str] = Field(default_factory=list)
    parts: List[PartSchema] = Field(default_factory=list)
    connections: List[ConnectionSchema] = Field(default_factory=list)
    requirements: List[RequirementSchema] = Field(default_factory=list)  # Exigences allouées


class TechnicalModel(BaseModel):
    """
    Niveau technique : implémentation physique, technologie.
    Répond à la question : AVEC QUOI le système est-il construit ?
    """
    system_name: str
    warnings: List[str] = Field(default_factory=list)
    technical_parts: List[PartSchema] = Field(default_factory=list)  # Composants physiques
    physical_connections: List[ConnectionSchema] = Field(default_factory=list)
    technology_choices: List[dict] = Field(default_factory=list)  # {component, technology, justification}


# === SESSION AVEC NIVEAUX ===

class LevelData(BaseModel):
    """Données d'un niveau MBSE dans une session."""
    level: ModelLevel
    model: dict = Field(default_factory=dict)  # JSON du modèle (OperationalModel, FunctionalModel, etc.)
    sysml_code: str = ""
    diagrams: List[dict] = Field(default_factory=list)  # [{type, title, plantuml_code, svg}]
    validated: bool = False  # L'utilisateur a validé ce niveau
    history: List[dict] = Field(default_factory=list)  # Historique des modifications


class LLMExchange(BaseModel):
    """Traçabilité d'un échange LLM (prompt envoyé + réponse brute)."""
    id: str = ""
    timestamp: str = ""
    session_id: str = ""
    level: str = ""
    operation: str = ""          # "generate_json" | "generate_sysml" | "patch_json"
    description_input: str = ""  # Description originale fournie par l'utilisateur
    prompt_sent: str = ""        # Prompt complet envoyé au LLM
    llm_response_raw: str = ""   # Réponse brute avant parsing
    llm_model: str = ""
    sysml_code: str = ""         # Code SysML v2 nettoyé (uniquement pour generate_sysml)
    success: bool = True
    error_message: str = ""


class SessionData(BaseModel):
    """Session complète avec workflow multi-niveaux."""
    session_id: str
    session_name: str = ""  # Nom donné par l'utilisateur
    created_at: str
    updated_at: str = ""
    system_name: str = ""
    description: str = ""
    current_level: ModelLevel = ModelLevel.OPERATIONAL
    levels: Dict[str, LevelData] = Field(default_factory=dict)  # Clé = ModelLevel.value
    exchanges: List[dict] = Field(default_factory=list)         # Historique des échanges LLM


# === REQUÊTES API POUR WORKFLOW MULTI-NIVEAUX ===

class GenerateLevelRequest(BaseModel):
    """Demande de génération pour un niveau spécifique."""
    session_id: Optional[str] = None
    session_name: str = ""  # Nom donné par l'utilisateur
    description: str = Field(..., min_length=10)  # Description initiale (operational) ou instructions
    level: ModelLevel = ModelLevel.OPERATIONAL
    use_rag: bool = True


class PatchLevelRequest(BaseModel):
    """Demande de modification d'un niveau."""
    session_id: str = Field(..., min_length=1)
    level: ModelLevel
    instruction: str = Field(..., min_length=5)
    use_rag: bool = True


class ValidateLevelRequest(BaseModel):
    """Valider un niveau pour passer au suivant."""
    session_id: str
    level: ModelLevel


class GenerateDiagramsRequest(BaseModel):
    """Demande de génération de diagrammes pour un niveau."""
    session_id: str
    level: ModelLevel
    diagram_types: Optional[List[str]] = None  # Si None, génère tous les diagrammes du niveau


class RenameSessionRequest(BaseModel):
    """Demande de renommage de session."""
    name: str = Field(..., min_length=1, max_length=100)


# === RÉPONSES API POUR WORKFLOW MULTI-NIVEAUX ===

class LevelResponse(BaseModel):
    """Réponse de génération d'un niveau."""
    session_id: str
    level: ModelLevel
    model: dict
    sysml_code: str
    rag_sources: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    available_diagrams: List[str] = Field(default_factory=list)  # Types de diagrammes disponibles


class PatchLevelResponse(BaseModel):
    """Réponse de modification d'un niveau."""
    session_id: str
    level: ModelLevel
    model: dict
    sysml_code: str
    changes_summary: str


class DiagramsResponse(BaseModel):
    """Réponse de génération de diagrammes."""
    session_id: str
    level: ModelLevel
    diagrams: List[dict]  # [{type, title, plantuml_code, svg}]
