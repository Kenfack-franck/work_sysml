"""
Schémas Pydantic pour le projet SysML v2 Agent.

Architecture à 4 descriptions progressives (une par niveau MBSE),
avec sections guidées, exemples de phrases, et warnings structurés.

Organisation du fichier :
  1. Énumérations et types de base
  2. Schémas des sections utilisateur (UserInput)
  3. Schémas des modèles structurés (ce que le LLM produit)
  4. Schémas des sections guidées (métadonnées pour le frontend)
  5. Schémas de requête/réponse API
  6. Schémas de session (pour state_service)
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================================
# PARTIE 1 — Énumérations et types de base
# ============================================================================

class ModelLevel(str, Enum):
    """Niveaux du workflow MBSE."""
    OPERATIONAL = "operational"
    FUNCTIONAL = "functional"
    LOGICAL = "logical"
    TECHNICAL = "technical"


class FlowType(str, Enum):
    """Types de flux échangés entre composants."""
    PNEUMATIC = "pneumatic"
    ELECTRIC = "electric"
    INFORMATION = "information"
    MECHANICAL = "mechanical"
    THERMAL = "thermal"
    DATA = "data"


class WarningType(str, Enum):
    """Types de warnings détectés par le LLM."""
    INCONSISTENCY = "inconsistency"
    MISSING_INFO = "missing_info"
    AMBIGUITY = "ambiguity"


class Direction(str, Enum):
    """Direction d'un port ou d'un flux."""
    IN = "in"
    OUT = "out"
    INOUT = "inout"


class StakeholderType(str, Enum):
    """Type de partie prenante."""
    HUMAN = "human"
    SYSTEM = "system"
    ORGANIZATION = "organization"


class ConnectionType(str, Enum):
    """Type de connexion entre composants."""
    FLOW = "flow"
    CONNECTION = "connection"
    INTERFACE = "interface"


# ============================================================================
# PARTIE 2 — Schémas des sections utilisateur (UserInput)
# ============================================================================

class UserSectionInput(BaseModel):
    """Réponse brute de l'utilisateur pour une section du formulaire."""
    section_id: str = Field(..., description="Identifiant unique de la section")
    content: str = Field(..., description="Texte libre saisi par l'utilisateur")


class OperationalUserInput(BaseModel):
    """Entrées utilisateur pour le niveau opérationnel — 7 sections."""
    system_mission: UserSectionInput = Field(..., description="Mission et périmètre du système")
    lifecycle: UserSectionInput = Field(..., description="Phases de vie du système")
    stakeholders: UserSectionInput = Field(..., description="Parties prenantes et acteurs")
    external_systems: UserSectionInput = Field(..., description="Systèmes et interfaces externes")
    use_cases: UserSectionInput = Field(..., description="Cas d'utilisation")
    operational_scenarios: UserSectionInput = Field(..., description="Scénarios opérationnels")
    operating_modes: UserSectionInput = Field(..., description="Modes de fonctionnement")


class FunctionalUserInput(BaseModel):
    """Entrées utilisateur pour le niveau fonctionnel — 5 sections."""
    functional_decomposition: UserSectionInput = Field(..., description="Décomposition fonctionnelle")
    functional_flows: UserSectionInput = Field(..., description="Flux fonctionnels")
    functional_behavior: UserSectionInput = Field(..., description="Comportement fonctionnel et allocation")
    functional_chains: UserSectionInput = Field(..., description="Chaînes fonctionnelles")
    functional_modes: UserSectionInput = Field(..., description="Modes fonctionnels")


class LogicalUserInput(BaseModel):
    """Entrées utilisateur pour le niveau logique — 5 sections."""
    logical_components: UserSectionInput = Field(..., description="Constituants logiques")
    function_allocation: UserSectionInput = Field(..., description="Allocation des fonctions aux constituants")
    internal_connections: UserSectionInput = Field(..., description="Connexions internes")
    logical_grouping: UserSectionInput = Field(..., description="Regroupement en sous-systèmes")
    logical_requirements: UserSectionInput = Field(..., description="Exigences logiques")


class TechnicalUserInput(BaseModel):
    """Entrées utilisateur pour le niveau technique — 4 sections."""
    technical_components: UserSectionInput = Field(..., description="Constituants techniques réels")
    physical_connections: UserSectionInput = Field(..., description="Connexions physiques")
    technology_choices: UserSectionInput = Field(..., description="Choix technologiques")
    technical_requirements: UserSectionInput = Field(..., description="Exigences techniques")


# ============================================================================
# PARTIE 3 — Schémas des modèles structurés (sortie LLM)
# ============================================================================

# --- Schémas transversaux ---

class Warning(BaseModel):
    """Warning structuré détecté par le LLM."""
    type: WarningType = Field(..., description="Type de warning")
    message: str = Field(..., description="Description du problème détecté")
    section: str = Field(..., description="Identifiant de la section concernée")
    suggestion: Optional[str] = Field(default=None, description="Suggestion de correction pour l'utilisateur")


class Requirement(BaseModel):
    """Exigence traçable."""
    id: str = Field(..., description="Identifiant unique (ex: REQ-OP-001)")
    text: str = Field(..., description="Texte de l'exigence")
    satisfied_by: Optional[str] = Field(default=None, description="Nom du composant qui satisfait l'exigence")


# --- Niveau Opérationnel ---

class Stakeholder(BaseModel):
    """Partie prenante du système."""
    name: str = Field(..., description="Nom de la partie prenante")
    role: str = Field(..., description="Rôle de la partie prenante")
    type: StakeholderType = Field(..., description="Type : humain, système ou organisation")


class ExternalFlow(BaseModel):
    """Flux échangé avec un système externe."""
    name: str = Field(..., description="Nom du flux")
    direction: Direction = Field(..., description="Direction du flux (in/out/inout)")
    flow_type: FlowType = Field(..., description="Nature du flux")
    description: Optional[str] = Field(default=None, description="Description complémentaire")


class ExternalInterface(BaseModel):
    """Système externe en interface avec le système."""
    system_name: str = Field(..., description="Nom du système externe")
    flows: List[ExternalFlow] = Field(default_factory=list, description="Flux échangés avec ce système")


class UseCase(BaseModel):
    """Cas d'utilisation du système."""
    name: str = Field(..., description="Nom du cas d'utilisation")
    actors: List[str] = Field(default_factory=list, description="Acteurs impliqués")
    includes: Optional[List[str]] = Field(default=None, description="Cas d'utilisation inclus")
    description: Optional[str] = Field(default=None, description="Description du cas d'utilisation")


class ScenarioStep(BaseModel):
    """Étape d'un scénario opérationnel."""
    order: int = Field(..., description="Numéro d'ordre dans la séquence")
    source: str = Field(..., description="Entité qui envoie")
    target: str = Field(..., description="Entité qui reçoit")
    action: str = Field(..., description="Description de l'échange")
    flow_type: Optional[FlowType] = Field(default=None, description="Nature du flux échangé")


class OperationalScenario(BaseModel):
    """Scénario opérationnel décrivant une séquence d'échanges."""
    name: str = Field(..., description="Nom du scénario")
    description: str = Field(..., description="Description du scénario")
    steps: List[ScenarioStep] = Field(default_factory=list, description="Étapes ordonnées du scénario")


class LifecyclePhase(BaseModel):
    """Phase de vie du système."""
    name: str = Field(..., description="Nom de la phase")
    sub_phases: Optional[List[str]] = Field(default=None, description="Sous-phases éventuelles")
    description: Optional[str] = Field(default=None, description="Description de la phase")


class ModeTransition(BaseModel):
    """Transition entre deux modes de fonctionnement."""
    from_mode: str = Field(..., description="Mode source")
    to_mode: str = Field(..., description="Mode cible")
    trigger: str = Field(..., description="Événement déclencheur de la transition")


class OperatingMode(BaseModel):
    """Mode de fonctionnement du système."""
    name: str = Field(..., description="Nom du mode")
    description: Optional[str] = Field(default=None, description="Description du mode")
    active_functions: List[str] = Field(default_factory=list, description="Fonctions actives dans ce mode")
    transitions: Optional[List[ModeTransition]] = Field(default=None, description="Transitions depuis ce mode")


class OperationalModel(BaseModel):
    """
    Modèle structuré du niveau opérationnel.
    Répond à : QUI utilise le système et POURQUOI ?
    Diagrammes cibles : Lifecycle, Use Case, Operational Sequence, Context, Operating Modes.
    """
    system_name: str = Field(..., description="Nom du système")
    description: str = Field(..., description="Description de la mission du système")
    system_boundaries: str = Field(default="", description="Périmètre du système (IN vs OUT)")
    lifecycle_phases: List[LifecyclePhase] = Field(default_factory=list, description="Phases de vie")
    stakeholders: List[Stakeholder] = Field(default_factory=list, description="Parties prenantes")
    external_interfaces: List[ExternalInterface] = Field(default_factory=list, description="Interfaces externes")
    use_cases: List[UseCase] = Field(default_factory=list, description="Cas d'utilisation")
    operational_scenarios: List[OperationalScenario] = Field(default_factory=list, description="Scénarios opérationnels")
    operating_modes: List[OperatingMode] = Field(default_factory=list, description="Modes de fonctionnement")
    requirements: List[Requirement] = Field(default_factory=list, description="Exigences opérationnelles")
    warnings: List[Warning] = Field(default_factory=list, description="Warnings détectés")


# --- Niveau Fonctionnel ---

class FunctionPort(BaseModel):
    """Port d'entrée ou de sortie d'une fonction."""
    name: str = Field(..., description="Nom du port/flux")
    flow_type: FlowType = Field(..., description="Nature du flux")


class FunctionDef(BaseModel):
    """Définition d'une fonction (récursive)."""
    name: str = Field(..., description="Nom de la fonction")
    description: Optional[str] = Field(default=None, description="Description de la fonction")
    inputs: List[FunctionPort] = Field(default_factory=list, description="Ports d'entrée")
    outputs: List[FunctionPort] = Field(default_factory=list, description="Ports de sortie")
    sub_functions: Optional[List[FunctionDef]] = Field(default=None, description="Sous-fonctions (décomposition récursive)")
    allocated_to: Optional[str] = Field(default=None, description="Nom du constituant pressenti")


class FunctionalFlow(BaseModel):
    """Flux entre deux fonctions."""
    from_function: str = Field(..., description="Fonction source")
    to_function: str = Field(..., description="Fonction cible")
    item: str = Field(..., description="Nom de l'item transporté")
    flow_type: FlowType = Field(..., description="Nature du flux")
    description: Optional[str] = Field(default=None, description="Description complémentaire")


class FunctionalChain(BaseModel):
    """Chaîne fonctionnelle (enchaînement de bout en bout)."""
    name: str = Field(..., description="Nom de la chaîne fonctionnelle")
    description: Optional[str] = Field(default=None, description="Description de la chaîne")
    functions: List[str] = Field(default_factory=list, description="Noms des fonctions dans l'ordre de la chaîne")
    system_inputs: List[FunctionPort] = Field(default_factory=list, description="Entrées aux frontières du système")
    system_outputs: List[FunctionPort] = Field(default_factory=list, description="Sorties aux frontières du système")


class FunctionalModel(BaseModel):
    """
    Modèle structuré du niveau fonctionnel.
    Répond à : QUE FAIT le système ?
    Diagrammes cibles : Functional Behavior (avec allocation), Functional Chains (AD).
    """
    system_name: str = Field(..., description="Nom du système")
    functions: List[FunctionDef] = Field(default_factory=list, description="Fonctions du système")
    functional_flows: List[FunctionalFlow] = Field(default_factory=list, description="Flux entre fonctions")
    functional_chains: List[FunctionalChain] = Field(default_factory=list, description="Chaînes fonctionnelles")
    modes: List[OperatingMode] = Field(default_factory=list, description="Modes de fonctionnement avec fonctions actives")
    warnings: List[Warning] = Field(default_factory=list, description="Warnings détectés")


# --- Niveau Logique ---

class LogicalPort(BaseModel):
    """Port d'un composant logique."""
    name: str = Field(..., description="Nom du port")
    direction: Direction = Field(..., description="Direction du port")
    flow_type: FlowType = Field(..., description="Nature du flux sur ce port")


class LogicalComponent(BaseModel):
    """Composant logique du système."""
    name: str = Field(..., description="Nom du composant")
    component_type: str = Field(..., description="Type de composant (calculateur, capteur, vanne, échangeur, port d'interface...)")
    description: Optional[str] = Field(default=None, description="Description du composant")
    ports: List[LogicalPort] = Field(default_factory=list, description="Ports du composant")
    allocated_functions: List[str] = Field(default_factory=list, description="Fonctions allouées à ce composant")
    children: Optional[List[LogicalComponent]] = Field(default=None, description="Sous-composants (regroupement en sous-systèmes)")


class LogicalConnection(BaseModel):
    """Connexion entre deux composants logiques."""
    from_component: str = Field(..., description="Composant source")
    from_port: str = Field(..., description="Port source")
    to_component: str = Field(..., description="Composant cible")
    to_port: str = Field(..., description="Port cible")
    flow_type: FlowType = Field(..., description="Nature du flux")
    item: str = Field(..., description="Item transporté")
    connection_type: ConnectionType = Field(..., description="Type de connexion")
    description: Optional[str] = Field(default=None, description="Description complémentaire")


class LogicalModel(BaseModel):
    """
    Modèle structuré du niveau logique.
    Répond à : COMMENT le système est-il structuré ?
    Diagramme cible : Logical Architecture Diagram.
    """
    system_name: str = Field(..., description="Nom du système")
    components: List[LogicalComponent] = Field(default_factory=list, description="Composants logiques")
    connections: List[LogicalConnection] = Field(default_factory=list, description="Connexions internes")
    requirements: List[Requirement] = Field(default_factory=list, description="Exigences logiques")
    warnings: List[Warning] = Field(default_factory=list, description="Warnings détectés")


# --- Niveau Technique ---

class TechnicalComponent(BaseModel):
    """Composant technique réel."""
    name: str = Field(..., description="Nom réel du composant")
    reference: Optional[str] = Field(default=None, description="Référence catalogue ou norme")
    technology_type: str = Field(..., description="Type technologique")
    implements: str = Field(..., description="Nom du constituant logique implémenté")
    description: Optional[str] = Field(default=None, description="Description du composant")
    ports: List[LogicalPort] = Field(default_factory=list, description="Ports du composant")


class PhysicalConnection(BaseModel):
    """Connexion physique entre composants techniques."""
    from_component: str = Field(..., description="Composant source")
    to_component: str = Field(..., description="Composant cible")
    medium: str = Field(..., description="Médium physique (tuyauterie, câblage, bus de données...)")
    description: Optional[str] = Field(default=None, description="Description complémentaire")
    flow_type: FlowType = Field(..., description="Nature du flux")


class TechnologyChoice(BaseModel):
    """Choix technologique justifié."""
    component: str = Field(..., description="Composant concerné")
    technology: str = Field(..., description="Technologie retenue")
    justification: str = Field(..., description="Justification du choix")


class TechnicalModel(BaseModel):
    """
    Modèle structuré du niveau technique.
    Répond à : AVEC QUOI le système est-il construit ?
    Diagramme cible : Technical Architecture Diagram.
    """
    system_name: str = Field(..., description="Nom du système")
    technical_components: List[TechnicalComponent] = Field(default_factory=list, description="Composants techniques")
    physical_connections: List[PhysicalConnection] = Field(default_factory=list, description="Connexions physiques")
    technology_choices: List[TechnologyChoice] = Field(default_factory=list, description="Choix technologiques")
    requirements: List[Requirement] = Field(default_factory=list, description="Exigences techniques")
    warnings: List[Warning] = Field(default_factory=list, description="Warnings détectés")


# ============================================================================
# PARTIE 4 — Schémas des sections guidées (métadonnées pour le frontend)
# ============================================================================

class SectionDefinition(BaseModel):
    """Définition d'une section du formulaire guidé."""
    section_id: str = Field(..., description="Identifiant unique de la section")
    title: str = Field(..., description="Titre affiché à l'utilisateur")
    question: str = Field(..., description="Question guidant l'utilisateur")
    examples: List[str] = Field(default_factory=list, description="Exemples de phrases pour guider l'utilisateur")


class LevelSections(BaseModel):
    """Regroupement des sections d'un niveau MBSE."""
    level: ModelLevel = Field(..., description="Niveau MBSE")
    sections: List[SectionDefinition] = Field(default_factory=list, description="Sections du formulaire")


# Constante contenant toutes les sections, questions et exemples pour les 4 niveaux.
# Utilisée par le frontend pour afficher les formulaires et par le backend pour construire les prompts.

LEVEL_SECTIONS: Dict[str, LevelSections] = {
    # -------------------------------------------------------------------------
    # NIVEAU OPÉRATIONNEL — 7 sections
    # -------------------------------------------------------------------------
    ModelLevel.OPERATIONAL.value: LevelSections(
        level=ModelLevel.OPERATIONAL,
        sections=[
            SectionDefinition(
                section_id="system_mission",
                title="Mission et périmètre du système",
                question="Décrivez le système : quel est son nom, sa mission principale, et ce qui fait partie du système (IN) versus ce qui est externe (OUT) ?",
                examples=[
                    "Le système BAS (Bleed Air System) a pour mission de prélever l'air chaud sur le compresseur du moteur et de le distribuer aux systèmes avion (dégivrage nacelle, pressurisation cabine, démarrage moteur).",
                    "Le périmètre du BAS inclut les vannes de régulation, les capteurs et le calculateur. Le moteur et les systèmes avion destinataires sont hors périmètre.",
                ],
            ),
            SectionDefinition(
                section_id="lifecycle",
                title="Phases de vie du système",
                question="Quelles sont les grandes phases de vie du système, de sa conception à son retrait de service ? Pour chaque phase, y a-t-il des sous-phases ?",
                examples=[
                    "Le BAS passe par les phases suivantes : Conception, Production, Exploitation, Maintenance, Retrait. La phase Production se décompose en : Fabrication, Montage, Intégration & essais, Stockage interne.",
                    "Pendant la phase Exploitation, le système peut être en fonctionnement normal, en mode dégradé, ou à l'arrêt.",
                ],
            ),
            SectionDefinition(
                section_id="stakeholders",
                title="Parties prenantes et acteurs",
                question="Qui utilise le système ou interagit activement avec lui ? Pour chaque acteur, précisez son rôle et s'il s'agit d'une personne, d'une organisation ou d'un système technique actif.",
                examples=[
                    "Le pilote commande le dégivrage nacelle via le cockpit. L'EECS (Electronic Engine Control System) envoie des consignes de régulation au BAS. L'équipe de maintenance intervient pour inspecter et remplacer les composants.",
                    "L'avionique de bord est un système technique qui transmet les commandes de prélèvement d'air au BAS.",
                ],
            ),
            SectionDefinition(
                section_id="external_systems",
                title="Systèmes et interfaces externes",
                question="Quels systèmes ou entités physiques sont en interface avec votre système sans en faire partie ? Pour chaque interface, précisez le nom du flux échangé, sa direction et sa nature.",
                examples=[
                    "Le moteur fournit de l'air chaud haute pression (flux pneumatique, entrée). La nacelle reçoit l'air chaud régulé pour le dégivrage (flux pneumatique, sortie). L'environnement fournit de l'air ambiant (flux pneumatique, entrée) et reçoit l'air tiède rejeté (flux pneumatique, sortie).",
                    "L'avionique transmet la commande de dégivrage nacelle (flux information, entrée) et reçoit les données d'état du système (flux information, sortie).",
                ],
            ),
            SectionDefinition(
                section_id="use_cases",
                title="Cas d'utilisation",
                question="Quels sont les services rendus par le système à ses acteurs ? Pour chaque cas d'utilisation, précisez quels acteurs sont impliqués et s'il inclut d'autres cas d'utilisation.",
                examples=[
                    "Fournir de l'air régulé à l'avion : acteurs impliqués = Pilote, Avionique. Ce use case inclut 'Réguler la pression' et 'Réguler la température'.",
                    "Dégivrer la nacelle : acteur = Pilote. Permettre le démarrage moteur : acteur = Pilote, Système de démarrage.",
                    "Diagnostiquer l'état du système : acteur = Équipe de maintenance. Réparer sous l'aile : acteur = Équipe de maintenance.",
                ],
            ),
            SectionDefinition(
                section_id="operational_scenarios",
                title="Scénarios opérationnels",
                question="Décrivez les séquences d'échanges entre le système et les acteurs/systèmes externes pour les scénarios les plus importants. Précisez l'ordre chronologique, qui envoie quoi à qui.",
                examples=[
                    "Scénario nominal alimentation air : 1. Le pilote active le prélèvement d'air. 2. L'avionique envoie la commande au BAS. 3. Le BAS ouvre la vanne de prélèvement. 4. Le BAS régule la pression et la température. 5. Le BAS envoie l'air régulé vers l'avion. 6. Le BAS communique son état à l'avionique.",
                    "Scénario nominal dégivrage nacelle : 1. Le pilote active le dégivrage. 2. L'avionique envoie la commande de dégivrage au BAS. 3. Le BAS ouvre la vanne NAI. 4. L'air chaud est envoyé à la nacelle. 5. Le capteur de température mesure la température. 6. Le calculateur régule l'ouverture de la vanne.",
                ],
            ),
            SectionDefinition(
                section_id="operating_modes",
                title="Modes de fonctionnement",
                question="Quels sont les différents modes de fonctionnement du système ? Pour chaque mode, quelles fonctions sont actives ? Quels événements provoquent les transitions entre modes ?",
                examples=[
                    "Mode Off : aucune fonction active. Transition vers Stand-by quand le moteur démarre. Mode Stand-by : le système est prêt mais n'envoie pas d'air. Transition vers Opérationnel quand le pilote commande le prélèvement.",
                    "Mode Opérationnel : toutes les fonctions actives (régulation pression, température, communication état). Mode Dégradé : uniquement la communication d'état, régulation désactivée. Transition de Opérationnel vers Dégradé si le calculateur détecte une panne.",
                ],
            ),
        ],
    ),

    # -------------------------------------------------------------------------
    # NIVEAU FONCTIONNEL — 5 sections
    # -------------------------------------------------------------------------
    ModelLevel.FUNCTIONAL.value: LevelSections(
        level=ModelLevel.FUNCTIONAL,
        sections=[
            SectionDefinition(
                section_id="functional_decomposition",
                title="Décomposition fonctionnelle",
                question="Pour chaque fonction de service identifiée au niveau opérationnel, comment se décompose-t-elle en sous-fonctions ? Décomposez récursivement jusqu'aux fonctions élémentaires. Pour chaque fonction, précisez ses entrées et sorties.",
                examples=[
                    "La fonction 'Envoyer de l'air chaud à la nacelle' se décompose en : Prélever l'air (entrée : air chaud haute pression, sortie : air chaud haute pression), Laisser passer l'air (entrée : air chaud HP + consigne ouverture, sortie : air chaud nacelle), Réguler la température nacelle (entrée : air chaud nacelle + air ambiant, sortie : air chaud régulé nacelle + air tiède), Réguler la vanne NAI (entrée : commande dégivrage + mesure température, sortie : consigne ouverture vanne), Mesurer la température (entrée : air chaud nacelle, sortie : mesure température), Fournir l'air à l'interface nacelle (entrée : air chaud régulé, sortie : air chaud nacelle).",
                ],
            ),
            SectionDefinition(
                section_id="functional_flows",
                title="Flux fonctionnels",
                question="Quels flux circulent entre les fonctions ? Pour chaque flux, précisez la fonction source, la fonction cible, le nom de l'item transporté et la nature du flux (pneumatique, électrique, information, mécanique, thermique).",
                examples=[
                    "De 'Prélever l'air' vers 'Laisser passer l'air' : air chaud haute pression (pneumatique). De 'Réguler la vanne NAI' vers 'Laisser passer l'air' : consigne d'ouverture vanne (électrique). De 'Mesurer la température' vers 'Réguler la vanne NAI' : mesure température air (électrique).",
                ],
            ),
            SectionDefinition(
                section_id="functional_behavior",
                title="Comportement fonctionnel et allocation",
                question="Quel constituant logique pressenti réalise chaque fonction élémentaire ? Utilisez la notation 'Constituant::Fonction'. Précisez l'ordre d'exécution entre les fonctions s'il existe.",
                examples=[
                    "IP port::Prélever l'air. Vanne NAI::Laisser passer l'air. ACAC::Réguler la température nacelle. Calculateur::Réguler la vanne NAI. Air Temperature Sensor::Mesurer la température. Nacelle port::Fournir l'air à l'interface nacelle.",
                    "Ordre d'exécution : Prélever l'air → Laisser passer l'air → Réguler la température → Fournir l'air. En parallèle : Mesurer la température → Réguler la vanne (boucle de rétroaction).",
                ],
            ),
            SectionDefinition(
                section_id="functional_chains",
                title="Chaînes fonctionnelles",
                question="Quelles sont les chaînes fonctionnelles principales ? Une chaîne fonctionnelle est un enchaînement de fonctions qui réalise une fonction de service de bout en bout. Précisez les entrées/sorties aux frontières du système.",
                examples=[
                    "Chaîne 'Envoyer de l'air chaud à la nacelle' : entrées système = commande dégivrage nacelle (information, depuis avionique), air chaud haute pression (pneumatique, depuis moteur), air ambiant (pneumatique, depuis environnement). Sorties système = air chaud nacelle (pneumatique, vers nacelle), air tiède (pneumatique, vers environnement).",
                    "Chaîne 'Envoyer de l'air régulé à l'avion' : entrées système = consigne P,T (information, depuis avionique), air chaud haute pression (pneumatique, depuis moteur). Sorties système = air régulé P,T (pneumatique, vers port pneumatique avion), données état (information, vers avionique).",
                ],
            ),
            SectionDefinition(
                section_id="functional_modes",
                title="Modes fonctionnels",
                question="Pour chaque mode de fonctionnement identifié au niveau opérationnel, quelles fonctions sont actives ou inactives dans ce mode ?",
                examples=[
                    "Mode Opérationnel : toutes les fonctions actives. Mode Stand-by : seules 'Déterminer l'état du système' et 'Communiquer' sont actives. Mode Dégradé : 'Communiquer' active, 'Réguler la pression' et 'Réguler la température' inactives.",
                ],
            ),
        ],
    ),

    # -------------------------------------------------------------------------
    # NIVEAU LOGIQUE — 5 sections
    # -------------------------------------------------------------------------
    ModelLevel.LOGICAL.value: LevelSections(
        level=ModelLevel.LOGICAL,
        sections=[
            SectionDefinition(
                section_id="logical_components",
                title="Constituants logiques",
                question="Quels sont les constituants logiques de votre système ? Pour chacun, précisez son nom, son type (calculateur, capteur, vanne, échangeur, port d'interface...), son rôle, et ses ports d'entrée/sortie avec la nature du flux sur chaque port.",
                examples=[
                    "IP port : port d'interface d'entrée. Rôle : point de prélèvement de l'air sur le moteur. Port d'entrée : air chaud haute pression (pneumatique). Port de sortie : air chaud haute pression (pneumatique).",
                    "Calculateur : calculateur numérique. Rôle : traiter les commandes et les mesures pour réguler les vannes. Ports d'entrée : commande dégivrage nacelle (information), mesure température air (électrique), mesure pression air (électrique). Ports de sortie : consigne ouverture vanne NAI (électrique), consigne ouverture vanne PCE (électrique).",
                ],
            ),
            SectionDefinition(
                section_id="function_allocation",
                title="Allocation des fonctions aux constituants",
                question="Quelle(s) fonction(s) chaque constituant réalise-t-il ? Vérifiez que chaque fonction élémentaire du niveau fonctionnel est allouée à exactement un constituant.",
                examples=[
                    "IP port réalise : Prélever l'air. Vanne NAI réalise : Laisser passer l'air. ACAC réalise : Réguler la température nacelle. Calculateur réalise : Réguler la vanne NAI, Réguler la vanne PCE, Déterminer l'état du système. Air Temperature Sensor réalise : Mesurer la température.",
                ],
            ),
            SectionDefinition(
                section_id="internal_connections",
                title="Connexions internes",
                question="Comment les constituants sont-ils connectés entre eux ? Pour chaque connexion, précisez le port source, le port cible, le type de flux et l'item transporté.",
                examples=[
                    "Du port de sortie de IP port vers le port d'entrée de Vanne NAI : air chaud haute pression (flux pneumatique). Du port de sortie consigne du Calculateur vers le port d'entrée commande de Vanne NAI : consigne d'ouverture (flux électrique).",
                ],
            ),
            SectionDefinition(
                section_id="logical_grouping",
                title="Regroupement en sous-systèmes",
                question="Les constituants sont-ils regroupés en sous-systèmes ou modules ? Si oui, quels constituants appartiennent à quel sous-système ?",
                examples=[
                    "Sous-système Régulation : Calculateur, Air Temperature Sensor, Pressure Sensor. Sous-système Pneumatique : IP port, Vanne NAI, Vanne PCE, ACAC, Nacelle port, A/C pneumatic port.",
                ],
            ),
            SectionDefinition(
                section_id="logical_requirements",
                title="Exigences logiques",
                question="Quelles exigences s'appliquent aux constituants logiques ? Pour chaque exigence, précisez son texte, et quel constituant la satisfait.",
                examples=[
                    "REQ-LOG-001 : Le calculateur doit traiter les commandes en moins de 100 ms. Satisfaite par : Calculateur.",
                    "REQ-LOG-002 : La vanne NAI doit pouvoir s'ouvrir et se fermer en moins de 2 secondes. Satisfaite par : Vanne NAI.",
                ],
            ),
        ],
    ),

    # -------------------------------------------------------------------------
    # NIVEAU TECHNIQUE — 4 sections
    # -------------------------------------------------------------------------
    ModelLevel.TECHNICAL.value: LevelSections(
        level=ModelLevel.TECHNICAL,
        sections=[
            SectionDefinition(
                section_id="technical_components",
                title="Constituants techniques réels",
                question="Quels composants réels implémentent chaque constituant logique ? Précisez le nom réel, la référence si applicable, le type technologique, et le constituant logique qu'il implémente.",
                examples=[
                    "NAIV (Nacelle Anti-Ice Valve) : vanne pneumatique papillon, implémente le constituant logique 'Vanne NAI'. Référence : SAE-NAIV-200.",
                    "EEC (Electronic Engine Controller) : calculateur numérique FADEC, implémente le constituant logique 'Calculateur'. Intègre aussi les fonctions de régulation du moteur.",
                ],
            ),
            SectionDefinition(
                section_id="physical_connections",
                title="Connexions physiques",
                question="Comment les composants réels sont-ils physiquement connectés ? Précisez le médium de chaque connexion (tuyauterie, câblage électrique, bus de données, etc.).",
                examples=[
                    "De NAIV vers ACAC : tuyauterie pneumatique haute température (Inconel). De EEC vers NAIV : câblage électrique ARINC 429. De Pressure Sensor vers EEC : liaison analogique 4-20 mA.",
                ],
            ),
            SectionDefinition(
                section_id="technology_choices",
                title="Choix technologiques",
                question="Pour les choix technologiques significatifs, quelle technologie a été retenue et pourquoi ?",
                examples=[
                    "Vanne NAI : technologie papillon plutôt que boisseau car meilleure tenue aux hautes températures (500°C). Bus de données : ARINC 429 plutôt que CAN bus car standard aéronautique certifié DO-254.",
                ],
            ),
            SectionDefinition(
                section_id="technical_requirements",
                title="Exigences techniques",
                question="Quelles exigences techniques s'appliquent aux composants réels ? Précisez les performances mesurables.",
                examples=[
                    "REQ-TECH-001 : La NAIV doit résister à une pression de 45 PSI et une température de 500°C en continu. Satisfaite par : NAIV.",
                    "REQ-TECH-002 : Le capteur de température doit avoir une précision de ±2°C dans la plage 0-600°C. Satisfaite par : Air Temperature Sensor.",
                ],
            ),
        ],
    ),
}


# ============================================================================
# PARTIE 5 — Schémas de requête/réponse API
# ============================================================================

class GenerateLevelRequest(BaseModel):
    """Requête de génération d'un niveau MBSE."""
    session_id: Optional[str] = Field(default=None, description="ID de session (None pour nouvelle session)")
    session_name: str = Field(default="", description="Nom de la session")
    level: ModelLevel = Field(default=ModelLevel.OPERATIONAL, description="Niveau MBSE à générer")
    sections: List[UserSectionInput] = Field(default_factory=list, description="Réponses utilisateur par section")
    use_rag: bool = Field(default=True, description="Utiliser le RAG pour enrichir les prompts")


class LevelSummary(BaseModel):
    """Résumé de ce que le LLM a compris du niveau."""
    level: ModelLevel = Field(..., description="Niveau MBSE")
    summary_text: str = Field(..., description="Résumé en langage naturel")
    key_elements: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Éléments clés extraits (ex: {'stakeholders': ['Pilote', 'EECS'], 'use_cases': ['Dégivrer la nacelle']})",
    )


class LevelResponse(BaseModel):
    """Réponse de génération d'un niveau MBSE."""
    session_id: str = Field(..., description="ID de session")
    level: ModelLevel = Field(..., description="Niveau généré")
    model: dict = Field(default_factory=dict, description="Modèle JSON structuré du niveau")
    sysml_code: str = Field(default="", description="Code SysML v2 généré")
    summary: Optional[LevelSummary] = Field(default=None, description="Résumé de compréhension")
    warnings: List[Warning] = Field(default_factory=list, description="Warnings détectés")
    rag_sources: List[str] = Field(default_factory=list, description="Sources RAG utilisées")


class PatchLevelRequest(BaseModel):
    """Requête de modification d'un niveau MBSE."""
    session_id: str = Field(..., min_length=1, description="ID de session")
    level: ModelLevel = Field(..., description="Niveau à modifier")
    sections: List[UserSectionInput] = Field(default_factory=list, description="Sections modifiées")
    use_rag: bool = Field(default=True, description="Utiliser le RAG")


class PatchLevelResponse(BaseModel):
    """Réponse de modification d'un niveau MBSE."""
    session_id: str = Field(..., description="ID de session")
    level: ModelLevel = Field(..., description="Niveau modifié")
    model: dict = Field(default_factory=dict, description="Modèle JSON mis à jour")
    sysml_code: str = Field(default="", description="Code SysML v2 regénéré")
    changes_summary: str = Field(default="", description="Résumé des modifications appliquées")


class ValidateLevelRequest(BaseModel):
    """Requête de validation d'un niveau pour passer au suivant."""
    session_id: str = Field(..., description="ID de session")
    level: ModelLevel = Field(..., description="Niveau à valider")


class RenameSessionRequest(BaseModel):
    """Requête de renommage de session."""
    name: str = Field(..., min_length=1, max_length=100, description="Nouveau nom de la session")


class LevelStatus(BaseModel):
    """Statut d'un niveau dans une session."""
    level: ModelLevel = Field(..., description="Niveau MBSE")
    status: str = Field(default="empty", description="Statut : empty | generated | validated")
    has_warnings: bool = Field(default=False, description="Présence de warnings")
    warning_count: int = Field(default=0, description="Nombre de warnings")


class SessionStatus(BaseModel):
    """Statut complet d'une session."""
    session_id: str = Field(..., description="ID de session")
    session_name: str = Field(default="", description="Nom de la session")
    created_at: str = Field(default="", description="Date de création")
    updated_at: str = Field(default="", description="Date de dernière modification")
    current_level: ModelLevel = Field(default=ModelLevel.OPERATIONAL, description="Niveau courant")
    levels: Dict[str, LevelStatus] = Field(default_factory=dict, description="Statut de chaque niveau")


# ============================================================================
# PARTIE 6 — Schémas de session (pour state_service)
# ============================================================================

class LevelData(BaseModel):
    """Données complètes d'un niveau dans une session."""
    level: ModelLevel = Field(..., description="Niveau MBSE")
    user_inputs: List[UserSectionInput] = Field(default_factory=list, description="Réponses brutes de l'utilisateur")
    model: dict = Field(default_factory=dict, description="Modèle JSON structuré")
    sysml_code: str = Field(default="", description="Code SysML v2 généré")
    summary: Optional[LevelSummary] = Field(default=None, description="Résumé de compréhension")
    warnings: List[Warning] = Field(default_factory=list, description="Warnings détectés")
    validation_result: Optional[dict] = Field(default=None, description="Résultat de validation syntaxique SysML v2")
    validated: bool = Field(default=False, description="Niveau validé par l'utilisateur")
    history: List[dict] = Field(default_factory=list, description="Historique des actions (generate, patch, validate)")


class LLMExchange(BaseModel):
    """Traçabilité d'un échange LLM (prompt envoyé + réponse brute)."""
    id: str = Field(default="", description="Identifiant unique de l'échange")
    timestamp: str = Field(default="", description="Horodatage ISO")
    session_id: str = Field(default="", description="ID de session")
    level: str = Field(default="", description="Niveau MBSE")
    operation: str = Field(default="", description="Type d'opération (generate_json, generate_sysml, patch_json)")
    description_input: str = Field(default="", description="Entrées utilisateur fournies")
    prompt_sent: str = Field(default="", description="Prompt complet envoyé au LLM")
    llm_response_raw: str = Field(default="", description="Réponse brute du LLM")
    llm_model: str = Field(default="", description="Nom du modèle LLM utilisé")
    sysml_code: str = Field(default="", description="Code SysML v2 nettoyé")
    success: bool = Field(default=True, description="Succès de l'échange")
    error_message: str = Field(default="", description="Message d'erreur si échec")


class SessionData(BaseModel):
    """Session complète avec workflow multi-niveaux."""
    session_id: str = Field(..., description="Identifiant unique de la session")
    session_name: str = Field(default="", description="Nom donné par l'utilisateur")
    created_at: str = Field(default="", description="Date de création ISO")
    updated_at: str = Field(default="", description="Date de dernière modification ISO")
    system_name: str = Field(default="", description="Nom du système modélisé")
    description: str = Field(default="", description="Description globale du système")
    current_level: ModelLevel = Field(default=ModelLevel.OPERATIONAL, description="Niveau courant")
    levels: Dict[str, LevelData] = Field(default_factory=dict, description="Données par niveau (clé = ModelLevel.value)")
    exchanges: List[dict] = Field(default_factory=list, description="Historique des échanges LLM")
