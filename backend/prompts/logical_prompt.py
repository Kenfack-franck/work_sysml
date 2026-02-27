"""
Prompts pour le niveau LOGIQUE (Logical).

Deux fonctions :
  - build_logical_json_prompt  : sections utilisateur → JSON LogicalModel
  - build_logical_sysml_prompt : JSON LogicalModel  → code SysML v2
"""

import json
from typing import List, Optional


# ============================================================================
# Blocs de texte réutilisables
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

_SYSML_SYNTAX_RULES = """\
=== RÈGLES DE SYNTAXE SysML v2 (OBLIGATOIRES) ===

RÈGLE S1 — PACKAGE : Tout le code doit être dans un package nommé '{{system_name}} - Logical'.

RÈGLE S2 — ITEM DEFINITIONS : item def pour chaque type de flux.

RÈGLE S3 — PORT DEFINITIONS :
  port def NomPortDef {{
    in item nomFlux : TypeItem;
  }}
Ou avec direction out/inout.

RÈGLE S4 — PART DEFINITIONS (Constituants) :
  part def NomConstituant {{
    doc /* Description et rôle */
    port portEntree : NomPortDef;
    port portSortie : NomPortDef;
  }}

RÈGLE S5 — ALLOCATION (perform) :
  part def NomConstituant {{
    perform action nomFonction : NomFonctionDef;
  }}
L'action def doit avoir été définie au niveau fonctionnel. Si on ne peut pas l'importer, la redéclarer avec un commentaire de référence.

RÈGLE S6 — ARCHITECTURE LOGIQUE (part + connections) :
Instancier les constituants dans un part englobant (le système) et déclarer les connexions :
  part bas : BAS {{
    part ipPort : IPPortDef;
    part vanneNAI : VanneNAIDef;

    connect ipPort.portSortieAir to vanneNAI.portEntreeAir;

    flow of AirChaudHautePression
      from ipPort.portSortieAir
      to vanneNAI.portEntreeAir;
  }}

RÈGLE S7 — SOUS-SYSTÈMES (hiérarchie) :
Si des regroupements existent, imbriquer les parts :
  part def SousSystemeRegulation {{
    part calculateur : CalculateurDef;
    part capteurTemp : CapteurTempDef;
  }}

  part bas : BAS {{
    part regulation : SousSystemeRegulation;
    part pneumatique : SousSystemePneumatique;
  }}

RÈGLE S8 — REQUIREMENTS :
  requirement def 'REQ-LOG-001' {{
    doc /* Texte de l'exigence */
  }}
  satisfy requirement 'REQ-LOG-001' by nomConstituant;

RÈGLE S9 — COMMENTAIRES DE SECTION :
Séparer les grandes parties du code avec des commentaires :
  // ========================================
  // SECTION : Item Definitions
  // ========================================

RÈGLE S10 — IDENTIFIANTS :
Les identifiants avec espaces ou caractères spéciaux doivent être entourés de guillemets simples."""

_SYSML_CODE_STRUCTURE = """\
=== STRUCTURE DU CODE SysML v2 À PRODUIRE ===

Le code doit suivre cette organisation :

1. package '{{system_name}} - Logical' {{
2.   // Item definitions
3.   // Port definitions
4.   // Part definitions (constituants avec ports et perform)
5.   // Part englobant système (instanciation + connections + flows)
6.   // Requirement definitions + satisfy
7. }}"""

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
# FONCTION 2 — Prompt SysML v2 (JSON LogicalModel → code SysML v2)
# ============================================================================

def build_logical_sysml_prompt(
    json_model: str,
    rag_examples: Optional[List[str]] = None,
) -> str:
    """
    Construit le prompt pour traduire le modèle logique JSON
    en code SysML v2 (Logical Architecture Diagram).

    Args:
        json_model: le modèle JSON sérialisé (LogicalModel)
        rag_examples: exemples SysML v2 du RAG (optionnel)

    Returns:
        Le prompt complet (string).
    """
    parts: list[str] = []

    # --- BLOC 1 : RÔLE ---
    parts.append(
        "Tu es un expert SysML v2 (spécification OMG, release 2026-01). "
        "Tu traduis un modèle d'architecture logique JSON en code SysML v2 valide en notation textuelle."
    )

    # --- BLOC 2 : EXIGENCES DE FIDÉLITÉ ---
    parts.append(
        "=== EXIGENCES DE FIDÉLITÉ ===\n\n"
        "- Tu traduis UNIQUEMENT ce qui est dans le JSON. Tu n'inventes aucun élément supplémentaire.\n"
        "- Tu utilises les noms EXACTS du JSON pour tous les identifiants SysML v2.\n"
        "- Si un champ est vide ou null dans le JSON, tu ne génères PAS de code pour cet élément.\n"
        "- Les warnings du JSON ne doivent PAS être traduits en code SysML v2 — ils sont uniquement informatifs."
    )

    # --- BLOC 3 : RÈGLES DE SYNTAXE SysML v2 ---
    parts.append(_SYSML_SYNTAX_RULES)

    # --- BLOC 4 : MODÈLE JSON À TRADUIRE ---
    parts.append(
        "=== MODÈLE JSON À TRADUIRE ===\n\n"
        f"{json_model}"
    )

    # --- BLOC 5 : EXEMPLES RAG (optionnel) ---
    if rag_examples:
        rag_lines = ["=== EXEMPLES DE SYNTAXE SysML v2 POUR RÉFÉRENCE ==="]
        for i, example in enumerate(rag_examples[:5], 1):
            rag_lines.append(f"\nExemple {i}:\n{example}")
        parts.append("\n".join(rag_lines))

    # --- BLOC 6 : STRUCTURE ATTENDUE DU CODE ---
    parts.append(_SYSML_CODE_STRUCTURE)

    # --- BLOC 7 : INSTRUCTION FINALE ---
    parts.append(
        "=== TON RÉSULTAT ===\n"
        "Produis UNIQUEMENT le code SysML v2. Pas de markdown, pas de ```, pas d'explication. "
        "Uniquement le code SysML v2 brut commençant par 'package'."
    )

    return "\n\n".join(parts)
