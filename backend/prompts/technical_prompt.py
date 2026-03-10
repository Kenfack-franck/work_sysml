"""
Prompts pour le niveau TECHNIQUE (Technical).

Fonctions :
  - build_technical_json_prompt               : sections utilisateur → JSON TechnicalModel
  - build_technical_breakdown_sysml_prompt    : JSON → code SysML v2 (Technical Breakdown)
  - build_technical_architecture_sysml_prompt : JSON → code SysML v2 (Technical Architecture)
  - build_technical_states_sysml_prompt       : JSON → code SysML v2 (Technical States)
  - get_technical_sysml_prompts               : JSON → [(diagram_type, prompt), ...] x3
"""

import json
from typing import List, Optional

from prompts._shared import build_sysml_prompt


# ============================================================================
# Blocs de texte réutilisables (prompt JSON uniquement)
# ============================================================================

_FIDELITY_RULES = """\
=== EXIGENCES DE FIDÉLITÉ (CRITIQUES) ===

F1 — ZÉRO INVENTION : Tu ne génères que ce qui est EXPLICITEMENT décrit dans les réponses de l'utilisateur. Si une section est vide ou absente, tu laisses le champ correspondant comme liste vide []. Tu n'inventes JAMAIS d'éléments supplémentaires.

F2 — SIGNALEMENT DES INCOHÉRENCES : Si tu détectes une incohérence (un acteur mentionné dans un use case mais absent de la section stakeholders, un flux référencé sans source, etc.), tu ne la corriges PAS. Tu ajoutes un warning de type "inconsistency" dans le champ "warnings" avec une description précise du problème.

F3 — SIGNALEMENT DES MANQUES : Si une information normalement attendue au niveau opérationnel est absente (par exemple : aucun scénario décrit, aucun mode de fonctionnement, aucune exigence), tu ajoutes un warning de type "missing_info" sans inventer la donnée manquante.

F4 — VOCABULAIRE EXACT : Tu utilises EXACTEMENT les noms, termes et formulations de l'utilisateur. Tu ne renommes pas les éléments, tu ne traduis pas, tu ne reformules pas les noms propres.

F5 — TRAÇABILITÉ : Chaque élément du JSON doit provenir d'une section identifiable des réponses utilisateur."""

_BUSINESS_RULES = """\
=== RÈGLES MÉTIER ===

R1 — ALLOCATION LOGIQUE→TECHNIQUE : Chaque constituant technique doit préciser quel constituant logique il implémente via le champ "implements". Si l'allocation n'est pas précisée, ajouter un warning "missing_info".

R2 — COUVERTURE : Chaque constituant logique du niveau précédent devrait être implémenté par au moins un constituant technique. Si des constituants logiques ne sont pas couverts, ajouter un warning "missing_info".

R3 — CONNEXIONS PHYSIQUES : Chaque connexion doit préciser le medium physique (tuyauterie, câblage, bus de données, etc.).

R4 — CHOIX TECHNOLOGIQUES : Les justifications doivent être factuelles et basées sur ce que l'utilisateur a écrit. Ne pas inventer de justifications.

R5 — EXIGENCES TECHNIQUES : ID au format REQ-TECH-XXX, avec des performances mesurables si l'utilisateur les a précisées."""

_JSON_SCHEMA = """\
=== SCHÉMA JSON ATTENDU ===

{
  "system_name": "string",
  "technical_components": [
    {
      "name": "string — Nom réel du composant",
      "reference": "string — Référence/part number" ou null,
      "technology_type": "string — Type technologique",
      "implements": "string — Nom du constituant logique implémenté",
      "description": "string" ou null,
      "ports": [
        {"name": "string", "direction": "in | out | inout", "flow_type": "..."}
      ]
    }
  ],
  "physical_connections": [
    {
      "from_component": "string",
      "to_component": "string",
      "medium": "string — tuyauterie | câblage | bus de données | ...",
      "description": "string" ou null,
      "flow_type": "pneumatic | electric | ..."
    }
  ],
  "technology_choices": [
    {
      "component": "string",
      "technology": "string",
      "justification": "string"
    }
  ],
  "requirements": [
    {"id": "REQ-TECH-XXX", "text": "string", "satisfied_by": "string" ou null}
  ],
  "warnings": [
    {"type": "inconsistency | missing_info | ambiguity", "message": "string", "section": "string", "suggestion": "string" ou null}
  ]
}"""

# Liste ordonnée des 4 sections techniques
_TECHNICAL_SECTIONS = [
    "technical_components",
    "physical_connections",
    "technology_choices",
    "technical_requirements",
]


# ============================================================================
# FONCTION 1 — Prompt JSON (sections utilisateur → TechnicalModel)
# ============================================================================

def build_technical_json_prompt(
    user_sections: List[dict],
    previous_level_model: dict,
    rag_examples: Optional[List[str]] = None,
    correction_feedback: Optional[str] = None,
) -> str:
    """
    Construit le prompt pour générer le modèle technique (JSON).

    Args:
        user_sections: liste de {"section_id": str, "content": str}
        previous_level_model: LogicalModel JSON du niveau précédent validé
        rag_examples: exemples SysML v2 du RAG (optionnel)
        correction_feedback: feedback de correction si retry (optionnel)

    Returns:
        Le prompt complet (string).
    """
    sections_map = {s["section_id"]: s["content"] for s in (user_sections or [])}

    parts: list[str] = []

    # --- BLOC 1 : RÔLE ---
    parts.append(
        "Tu es un ingénieur système expert en architecture technique et en SysML v2. "
        "Tu analyses les réponses structurées d'un utilisateur pour extraire le modèle "
        "d'architecture technique de son système. Tu disposes du modèle logique validé comme contexte."
    )

    # --- BLOC 2 : EXIGENCES DE FIDÉLITÉ ---
    parts.append(_FIDELITY_RULES)

    # --- BLOC 3 : CONTEXTE DU NIVEAU PRÉCÉDENT ---
    prev_json = json.dumps(previous_level_model, indent=2, ensure_ascii=False) if previous_level_model else "{}"
    parts.append(
        "=== MODÈLE LOGIQUE VALIDÉ (CONTEXTE) ===\n\n"
        f"{prev_json}"
    )

    # --- BLOC 4 : RÉPONSES DE L'UTILISATEUR ---
    user_block_lines = ["=== RÉPONSES DE L'UTILISATEUR ==="]
    for section_id in _TECHNICAL_SECTIONS:
        content = sections_map.get(section_id, "").strip()
        user_block_lines.append(f"\n[SECTION: {section_id}]")
        if content:
            user_block_lines.append(content)
        else:
            user_block_lines.append("(Section non renseignée par l'utilisateur)")
    parts.append("\n".join(user_block_lines))

    # --- BLOC 5 : RÈGLES MÉTIER ---
    parts.append(_BUSINESS_RULES)

    # --- BLOC 6 : SCHÉMA JSON ATTENDU ---
    parts.append(_JSON_SCHEMA)

    # --- BLOC 7 : EXEMPLES RAG (optionnel) ---
    if rag_examples:
        rag_lines = ["=== EXEMPLES DE SYNTAXE SysML v2 POUR RÉFÉRENCE ==="]
        for i, example in enumerate(rag_examples[:5], 1):
            rag_lines.append(f"\nExemple {i}:\n{example}")
        parts.append("\n".join(rag_lines))

    # --- BLOC 8 : CORRECTION (optionnel) ---
    if correction_feedback:
        parts.append(
            "=== CORRECTION REQUISE ===\n"
            f"{correction_feedback}"
        )

    # --- BLOC 9 : INSTRUCTION FINALE ---
    parts.append(
        "=== TON RÉSULTAT ===\n"
        "Produis UNIQUEMENT le JSON conforme au schéma ci-dessus. "
        "Aucun commentaire, aucune explication, aucun markdown. Uniquement le JSON."
    )

    return "\n\n".join(parts)


# ============================================================================
# Templates de syntaxe validés (compatibles SysON)
# ============================================================================

_TEMPLATE_TECHNICAL_BREAKDOWN = """\
=== TEMPLATE DE SYNTAXE : TECHNICAL BREAKDOWN (compatible SysON) ===

package 'SystemName - Technical Breakdown' {

    part def ECU {
        doc /* Realise le composant logique Controller. Technologie : microcontroleur ARM Cortex-M4 */
        attribute manufacturer;
        attribute partNumber;
    }

    part def PneumaticValve {
        doc /* Realise le composant logique Valve. Technologie : vanne pneumatique proportionnelle */
        attribute maxPressure;
        attribute maxTemperature;
    }

    part def TemperatureSensor {
        doc /* Realise le composant logique Sensor. Technologie : thermocouple type K */
        attribute range;
        attribute accuracy;
    }

    // Decomposition physique
    part def PhysicalSystem {
        part ecu : ECU;
        part valve : PneumaticValve;
        part sensor : TemperatureSensor;
    }
}"""

_RULES_TECHNICAL_BREAKDOWN = """\
=== RÈGLES DE SYNTAXE SPÉCIFIQUES : TECHNICAL BREAKDOWN ===

R-TB1: Les composants techniques sont des "part def" au niveau package.
R-TB2: Le doc /* ... */ indique le composant logique realise et la technologie choisie.
R-TB3: Les attributs techniques (manufacturer, partNumber, maxPressure, etc.) sont des "attribute" sans valeur ni unite si non fournis.
R-TB4: La decomposition physique utilise un "part def PhysicalSystem" contenant les parts instances.
R-TB5: Tous les noms en CamelCase ASCII sans accents (RS1-RS4)."""

_TEMPLATE_TECHNICAL_ARCHITECTURE = """\
=== TEMPLATE DE SYNTAXE : TECHNICAL ARCHITECTURE (compatible SysON) ===

package 'SystemName - Technical Architecture' {

    port def ElectricalPort {
        attribute signal;
    }

    port def PneumaticPort {
        attribute fluid;
    }

    part def ECU {
        port commandOut : ElectricalPort;
        port sensorIn : ElectricalPort;
        port powerIn : ElectricalPort;
    }

    part def PneumaticValve {
        port commandIn : ElectricalPort;
        port airIn : PneumaticPort;
        port airOut : PneumaticPort;
    }

    part def TemperatureSensor {
        port measureOut : ElectricalPort;
        port fluidIn : PneumaticPort;
    }

    part 'Physical Architecture' {
        part ecu : ECU;
        part valve : PneumaticValve;
        part sensor : TemperatureSensor;
    }
}"""

_RULES_TECHNICAL_ARCHITECTURE = """\
=== RÈGLES DE SYNTAXE SPÉCIFIQUES : TECHNICAL ARCHITECTURE ===

R-TA1: Les port def contiennent des "attribute nomFlux;" PAS "in item" ni "out item".
R-TA2: PAS de port conjugue (~). Utiliser le meme type de port des deux cotes.
R-TA3: PAS de "connect" ni "flow of" dans le code. SysON les cree graphiquement.
        Declarer uniquement les parts dans le contexte d architecture.
R-TA4: Chaque composant technique a un "part def" avec ses ports types.
R-TA5: Tous les noms en CamelCase ASCII sans accents (RS1-RS4)."""

_TEMPLATE_TECHNICAL_STATES = """\
=== TEMPLATE DE SYNTAXE : TECHNICAL STATES (compatible SysON) ===

package 'SystemName - Technical States' {

    attribute def PowerOnSignal;
    attribute def PowerOffSignal;
    attribute def HardwareFault;
    attribute def HardwareReset;

    state def ECUStates {
        entry; then Off;

        state Off;
        transition BootUp
            first Off
            accept PowerOnSignal
            then Initializing;

        state Initializing {
            doc /* Autotest et initialisation du firmware */
        }
        transition Ready
            first Initializing
            then Running;

        state Running;
        transition Shutdown
            first Running
            accept PowerOffSignal
            then Off;

        transition HWFault
            first Running
            accept HardwareFault
            then FailSafe;

        state FailSafe;
        transition Reset
            first FailSafe
            accept HardwareReset
            then Initializing;
    }
}"""

_RULES_TECHNICAL_STATES = """\
=== RÈGLES DE SYNTAXE SPÉCIFIQUES : TECHNICAL STATES ===

R-TS1: Les etats utilisent "state def" avec "entry; then PremierEtat;". JAMAIS "entry state".
R-TS2: Les transitions : "transition Nom first Source accept Signal then Cible;"
R-TS3: Les signaux sont des "attribute def NomSignal;" en CamelCase au niveau package.
R-TS4: Noms d etats en CamelCase ASCII : Off, Initializing, Running, FailSafe.
R-TS5: JAMAIS de "transition Source then Cible if 'texte francais'". Utiliser accept Signal."""


# ============================================================================
# FONCTIONS SysML v2 — 3 prompts spécialisés par type de diagramme
# ============================================================================

def build_technical_breakdown_sysml_prompt(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
    naming_constraint: str = "",
) -> str:
    """Construit le prompt SysML v2 pour le diagramme Technical Breakdown."""
    filtered = {
        "system_name": model_json.get("system_name", "System"),
        "technical_components": model_json.get("technical_components", []),
        "technology_choices": model_json.get("technology_choices", []),
    }
    return build_sysml_prompt(
        diagram_type="Technical Breakdown",
        role_suffix="Tu modélises la décomposition en composants physiques avec technologies et attributs techniques.",
        template=_TEMPLATE_TECHNICAL_BREAKDOWN,
        rules=_RULES_TECHNICAL_BREAKDOWN,
        filtered_json=filtered,
        rag_examples=rag_examples,
        naming_constraint=naming_constraint,
    )


def build_technical_architecture_sysml_prompt(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
    naming_constraint: str = "",
) -> str:
    """Construit le prompt SysML v2 pour le diagramme Technical Architecture."""
    filtered = {
        "system_name": model_json.get("system_name", "System"),
        "technical_components": model_json.get("technical_components", []),
        "physical_connections": model_json.get("physical_connections", []),
    }
    return build_sysml_prompt(
        diagram_type="Technical Architecture",
        role_suffix="Tu modélises les composants techniques avec leurs ports physiques et l'instanciation dans l'architecture.",
        template=_TEMPLATE_TECHNICAL_ARCHITECTURE,
        rules=_RULES_TECHNICAL_ARCHITECTURE,
        filtered_json=filtered,
        rag_examples=rag_examples,
        naming_constraint=naming_constraint,
    )


def build_technical_states_sysml_prompt(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
    naming_constraint: str = "",
) -> str:
    """Construit le prompt SysML v2 pour les états techniques."""
    filtered = {
        "system_name": model_json.get("system_name", "System"),
        "technical_components": [{"name": c.get("name")} for c in model_json.get("technical_components", [])],
    }
    return build_sysml_prompt(
        diagram_type="Technical States",
        role_suffix="Tu modélises les machines à états des composants techniques avec transitions matérielles.",
        template=_TEMPLATE_TECHNICAL_STATES,
        rules=_RULES_TECHNICAL_STATES,
        filtered_json=filtered,
        rag_examples=rag_examples,
        naming_constraint=naming_constraint,
    )


# ============================================================================
# Fonction utilitaire — appelle les 3 prompts
# ============================================================================

TECHNICAL_DIAGRAMS = [
    ("technical_breakdown", build_technical_breakdown_sysml_prompt),
    ("technical_architecture", build_technical_architecture_sysml_prompt),
    ("technical_states", build_technical_states_sysml_prompt),
]


def get_technical_sysml_prompts(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
    naming_constraint: str = "",
) -> list:
    """
    Retourne une liste de (diagram_type, prompt_text) pour les 3 diagrammes techniques.

    Args:
        model_json: le modèle JSON technique (dict, pas string)
        rag_examples: exemples SysML v2 du RAG (optionnel)
        naming_constraint: contrainte de nommage des packages précédents

    Returns:
        Liste de tuples (diagram_type: str, prompt: str)
    """
    results = []
    for diagram_type, build_fn in TECHNICAL_DIAGRAMS:
        prompt = build_fn(model_json, rag_examples, naming_constraint=naming_constraint)
        results.append((diagram_type, prompt))
    return results
