"""
Prompts pour le niveau LOGIQUE (Logical).

Fonctions :
  - build_logical_json_prompt              : sections utilisateur → JSON LogicalModel
  - build_logical_breakdown_sysml_prompt   : JSON → code SysML v2 (Logical Breakdown)
  - build_logical_architecture_sysml_prompt: JSON → code SysML v2 (Logical Architecture)
  - build_logical_sequences_sysml_prompt   : JSON → code SysML v2 (Logical Sequences)
  - build_logical_modes_sysml_prompt       : JSON → code SysML v2 (Logical Modes)
  - get_logical_sysml_prompts              : JSON → [(diagram_type, prompt), ...] x4
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

R1 — CONSTITUANTS AVEC PORTS : Chaque constituant logique doit avoir au moins un port. Si l'utilisateur n'a pas précisé les ports, ajouter un warning "missing_info".

R2 — ALLOCATION COMPLÈTE : Chaque fonction feuille du niveau fonctionnel doit être allouée à exactement un constituant. Si des fonctions ne sont pas allouées, ajouter un warning "missing_info". Si une fonction est allouée à un constituant qui n'existe pas, ajouter un warning "inconsistency".

R3 — COHÉRENCE DES CONNEXIONS : Chaque connexion doit référencer des ports existants sur des constituants existants. Si une connexion référence un port ou constituant inexistant, ajouter un warning "inconsistency".

R4 — TYPAGE DES PORTS : Chaque port doit avoir une direction (in/out/inout) et un flow_type. Le flow_type doit être cohérent avec les flux fonctionnels du niveau précédent.

R5 — REGROUPEMENT : Si l'utilisateur mentionne des sous-systèmes, utiliser la structure children[] récursive de LogicalComponent pour représenter la hiérarchie.

R6 — EXIGENCES : Les exigences logiques doivent avoir un ID au format REQ-LOG-XXX. Le champ satisfied_by doit référencer un constituant existant."""

_JSON_SCHEMA = """\
=== SCHÉMA JSON ATTENDU ===

{
  "system_name": "string",
  "components": [
    {
      "name": "string — Nom du constituant",
      "component_type": "string — calculateur | capteur | vanne | échangeur | port d'interface | ...",
      "description": "string" ou null,
      "ports": [
        {
          "name": "string — Nom du port",
          "direction": "in | out | inout",
          "flow_type": "pneumatic | electric | information | mechanical | thermal | data"
        }
      ],
      "allocated_functions": ["string — Noms des fonctions allouées"],
      "children": ["...même structure récursive..."] ou null
    }
  ],
  "connections": [
    {
      "from_component": "string",
      "from_port": "string",
      "to_component": "string",
      "to_port": "string",
      "flow_type": "pneumatic | electric | ...",
      "item": "string — Nom de l'item transporté",
      "connection_type": "flow | connection | interface",
      "description": "string" ou null
    }
  ],
  "requirements": [
    {
      "id": "REQ-LOG-XXX",
      "text": "string",
      "satisfied_by": "string" ou null
    }
  ],
  "warnings": [
    {
      "type": "inconsistency | missing_info | ambiguity",
      "message": "string",
      "section": "string",
      "suggestion": "string" ou null
    }
  ]
}"""

# Liste ordonnée des 5 sections logiques
_LOGICAL_SECTIONS = [
    "logical_components",
    "function_allocation",
    "internal_connections",
    "logical_grouping",
    "logical_requirements",
]


# ============================================================================
# FONCTION 1 — Prompt JSON (sections utilisateur → LogicalModel)
# ============================================================================

def build_logical_json_prompt(
    user_sections: List[dict],
    previous_level_model: dict,
    rag_examples: Optional[List[str]] = None,
    correction_feedback: Optional[str] = None,
) -> str:
    """
    Construit le prompt pour générer le modèle logique (JSON).

    Args:
        user_sections: liste de {"section_id": str, "content": str}
        previous_level_model: FunctionalModel JSON du niveau précédent validé
        rag_examples: exemples SysML v2 du RAG (optionnel)
        correction_feedback: feedback de correction si retry (optionnel)

    Returns:
        Le prompt complet (string).
    """
    sections_map = {s["section_id"]: s["content"] for s in (user_sections or [])}

    parts: list[str] = []

    # --- BLOC 1 : RÔLE ---
    parts.append(
        "Tu es un ingénieur système expert en architecture logique et en SysML v2. "
        "Tu analyses les réponses structurées d'un utilisateur pour extraire le modèle "
        "d'architecture logique de son système. Tu disposes du modèle fonctionnel validé comme contexte."
    )

    # --- BLOC 2 : EXIGENCES DE FIDÉLITÉ ---
    parts.append(_FIDELITY_RULES)

    # --- BLOC 3 : CONTEXTE DU NIVEAU PRÉCÉDENT ---
    prev_json = json.dumps(previous_level_model, indent=2, ensure_ascii=False) if previous_level_model else "{}"
    parts.append(
        "=== MODÈLE FONCTIONNEL VALIDÉ (CONTEXTE) ===\n\n"
        f"{prev_json}"
    )

    # --- BLOC 4 : RÉPONSES DE L'UTILISATEUR ---
    user_block_lines = ["=== RÉPONSES DE L'UTILISATEUR ==="]
    for section_id in _LOGICAL_SECTIONS:
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

_TEMPLATE_LOGICAL_BREAKDOWN = """\
=== TEMPLATE DE SYNTAXE : LOGICAL BREAKDOWN (compatible SysON) ===

package 'SystemName - Logical Breakdown' {

    // Composants logiques avec hierarchie
    part def Controller {
        doc /* Fonctions allouees : Reguler la vanne, Provide Feedback */
    }

    part def Valve {
        doc /* Fonction allouee : Laisser passer lair */
    }

    part def HeatExchanger {
        doc /* Fonction allouee : Reguler la temperature */
    }

    part def Sensor {
        doc /* Fonction allouee : Mesurer la temperature */
    }

    // Decomposition du systeme
    part def MainSystem {
        part controller : Controller;
        part valve : Valve;
        part heatExchanger : HeatExchanger;
        part sensor : Sensor;
    }
}"""

_RULES_LOGICAL_BREAKDOWN = """\
=== RÈGLES DE SYNTAXE SPÉCIFIQUES : LOGICAL BREAKDOWN ===

R-LB1: Les constituants logiques sont des "part def" au niveau package.
R-LB2: Le doc /* ... */ liste les fonctions allouees a ce constituant.
R-LB3: La decomposition du systeme utilise un "part def MainSystem" contenant les parts instances.
R-LB4: Si des sous-systemes existent, imbriquer : part def SousSysteme { part composant : ComposantDef; }
R-LB5: Tous les noms en CamelCase ASCII sans accents (RS1-RS4)."""

_TEMPLATE_LOGICAL_ARCHITECTURE = """\
=== TEMPLATE DE SYNTAXE : LOGICAL ARCHITECTURE (compatible SysON) ===

package 'SystemName - Logical Architecture' {

    port def ControlPort {
        attribute command;
        attribute feedback;
    }

    port def FluidPort {
        attribute fluid;
    }

    part def Controller {
        port commandOut : ControlPort;
        port sensorIn : ControlPort;
    }

    part def Valve {
        port commandIn : ControlPort;
        port fluidIn : FluidPort;
        port fluidOut : FluidPort;
    }

    part def Sensor {
        port measureOut : ControlPort;
        port fluidIn : FluidPort;
    }

    part 'System Architecture' {
        part controller : Controller;
        part valve : Valve;
        part sensor : Sensor;
    }
}"""

_RULES_LOGICAL_ARCHITECTURE = """\
=== RÈGLES DE SYNTAXE SPÉCIFIQUES : LOGICAL ARCHITECTURE ===

R-LA1: Les port def contiennent des "attribute nomFlux;" PAS "in item" ni "out item".
R-LA2: PAS de port conjugue (~). Utiliser le meme type de port des deux cotes.
R-LA3: PAS de "connect" ni "flow of" dans le code. SysON les cree graphiquement.
        Declarer uniquement les parts dans le contexte d architecture.
R-LA4: Chaque constituant a un "part def" avec ses ports types.
R-LA5: Le part 'System Architecture' instancie tous les parts sans les connecter.
R-LA6: Tous les noms en CamelCase ASCII sans accents (RS1-RS4)."""

_TEMPLATE_LOGICAL_SEQUENCES = """\
=== TEMPLATE DE SYNTAXE : LOGICAL SEQUENCES (compatible SysON) ===

package 'SystemName - Logical Sequences' {

    item def Command;
    item def Measurement;
    item def FluidFlow;

    occurrence def NominalOperationSequence {
        doc /* Sequence nominale :
               1. Controller envoie Command a Valve
               2. Valve laisse passer le fluide
               3. Sensor mesure et envoie Measurement a Controller
               4. Controller ajuste la commande */
        part controller;
        part valve;
        part sensor;
    }

    occurrence def DegradedSequence {
        doc /* Sequence degradee :
               1. Sensor detecte une anomalie
               2. Controller arrete la vanne
               3. Controller envoie alerte */
        part controller;
        part valve;
        part sensor;
    }
}"""

_RULES_LOGICAL_SEQUENCES = """\
=== RÈGLES DE SYNTAXE SPÉCIFIQUES : LOGICAL SEQUENCES ===

R-LS1: Les sequences utilisent "occurrence def NomSequence { doc /* etapes */ part participants; }".
R-LS2: NE PAS utiliser "message", "event occurrence", "from", "to".
        SysON ne rend pas les diagrammes de sequence.
R-LS3: Decrire les etapes du scenario dans le doc /* ... */ de maniere numerotee.
R-LS4: Les participants sont des "part nomParticipant;" simples (sans type).
R-LS5: Les types de messages echanges sont des "item def NomMessage;" au niveau package.
R-LS6: Noms en CamelCase ASCII."""

_TEMPLATE_LOGICAL_MODES = """\
=== TEMPLATE DE SYNTAXE : LOGICAL MODES (compatible SysON) ===

package 'SystemName - Logical Modes' {

    attribute def PowerOnSignal;
    attribute def PowerOffSignal;
    attribute def FaultDetected;
    attribute def FaultCleared;

    state def ControllerStates {
        entry; then Idle;

        state Idle;
        transition Activate
            first Idle
            accept PowerOnSignal
            then Active;

        state Active {
            doc /* Controller regule activement */
        }
        transition Deactivate
            first Active
            accept PowerOffSignal
            then Idle;

        transition Fault
            first Active
            accept FaultDetected
            then Degraded;

        state Degraded;
        transition Recover
            first Degraded
            accept FaultCleared
            then Active;
    }
}"""

_RULES_LOGICAL_MODES = """\
=== RÈGLES DE SYNTAXE SPÉCIFIQUES : LOGICAL MODES ===

R-LM1: Les modes utilisent "state def" avec "entry; then PremierEtat;". JAMAIS "entry state".
R-LM2: Les transitions : "transition Nom first Source accept Signal then Cible;"
R-LM3: Les signaux sont des "attribute def NomSignal;" en CamelCase au niveau package.
R-LM4: Noms d etats en CamelCase ASCII : Idle, Active, Degraded, FailSafe.
R-LM5: Les etats composites contiennent "entry; then" pour leur sous-etat initial.
R-LM6: JAMAIS de "transition Source then Cible if 'texte francais'". Utiliser accept Signal."""


# ============================================================================
# FONCTIONS SysML v2 — 4 prompts spécialisés par type de diagramme
# ============================================================================

def build_logical_breakdown_sysml_prompt(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
    naming_constraint: str = "",
) -> str:
    """Construit le prompt SysML v2 pour le diagramme Logical Breakdown."""
    filtered = {
        "system_name": model_json.get("system_name", "System"),
        "components": model_json.get("components", []),
    }
    return build_sysml_prompt(
        diagram_type="Logical Breakdown",
        role_suffix="Tu modélises la décomposition du système en composants logiques avec leur hiérarchie et les fonctions allouées.",
        template=_TEMPLATE_LOGICAL_BREAKDOWN,
        rules=_RULES_LOGICAL_BREAKDOWN,
        filtered_json=filtered,
        rag_examples=rag_examples,
        naming_constraint=naming_constraint,
    )


def build_logical_architecture_sysml_prompt(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
    naming_constraint: str = "",
) -> str:
    """Construit le prompt SysML v2 pour le diagramme Logical Architecture."""
    filtered = {
        "system_name": model_json.get("system_name", "System"),
        "components": model_json.get("components", []),
        "connections": model_json.get("connections", []),
    }
    return build_sysml_prompt(
        diagram_type="Logical Architecture",
        role_suffix="Tu modélises les composants logiques avec leurs ports et l'instanciation dans l'architecture système.",
        template=_TEMPLATE_LOGICAL_ARCHITECTURE,
        rules=_RULES_LOGICAL_ARCHITECTURE,
        filtered_json=filtered,
        rag_examples=rag_examples,
        naming_constraint=naming_constraint,
    )


def build_logical_sequences_sysml_prompt(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
    naming_constraint: str = "",
) -> str:
    """Construit le prompt SysML v2 pour les séquences logiques."""
    filtered = {
        "system_name": model_json.get("system_name", "System"),
        "components": [{"name": c.get("name")} for c in model_json.get("components", [])],
        "connections": model_json.get("connections", []),
    }
    return build_sysml_prompt(
        diagram_type="Logical Sequences",
        role_suffix="Tu modélises les séquences d'échanges entre composants logiques avec des occurrence def et participants.",
        template=_TEMPLATE_LOGICAL_SEQUENCES,
        rules=_RULES_LOGICAL_SEQUENCES,
        filtered_json=filtered,
        rag_examples=rag_examples,
        naming_constraint=naming_constraint,
    )


def build_logical_modes_sysml_prompt(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
    naming_constraint: str = "",
) -> str:
    """Construit le prompt SysML v2 pour les modes/états logiques."""
    filtered = {
        "system_name": model_json.get("system_name", "System"),
        "components": [{"name": c.get("name")} for c in model_json.get("components", [])],
    }
    return build_sysml_prompt(
        diagram_type="Logical Modes",
        role_suffix="Tu modélises les machines à états des composants logiques avec transitions et signaux.",
        template=_TEMPLATE_LOGICAL_MODES,
        rules=_RULES_LOGICAL_MODES,
        filtered_json=filtered,
        rag_examples=rag_examples,
        naming_constraint=naming_constraint,
    )


# ============================================================================
# Fonction utilitaire — appelle les 4 prompts
# ============================================================================

LOGICAL_DIAGRAMS = [
    ("logical_breakdown", build_logical_breakdown_sysml_prompt),
    ("logical_architecture", build_logical_architecture_sysml_prompt),
    ("logical_sequences", build_logical_sequences_sysml_prompt),
    ("logical_modes", build_logical_modes_sysml_prompt),
]


def get_logical_sysml_prompts(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
    naming_constraint: str = "",
) -> list:
    """
    Retourne une liste de (diagram_type, prompt_text) pour les 4 diagrammes logiques.

    Args:
        model_json: le modèle JSON logique (dict, pas string)
        rag_examples: exemples SysML v2 du RAG (optionnel)
        naming_constraint: contrainte de nommage des packages précédents

    Returns:
        Liste de tuples (diagram_type: str, prompt: str)
    """
    results = []
    for diagram_type, build_fn in LOGICAL_DIAGRAMS:
        prompt = build_fn(model_json, rag_examples, naming_constraint=naming_constraint)
        results.append((diagram_type, prompt))
    return results
