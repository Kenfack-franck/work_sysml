"""
Prompts pour le niveau FONCTIONNEL (Functional).

Deux fonctions :
  - build_functional_json_prompt  : sections utilisateur → JSON FunctionalModel
  - build_functional_sysml_prompt : JSON FunctionalModel  → code SysML v2
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

R1 — DÉCOMPOSITION RÉCURSIVE : Les fonctions de service sont décomposées récursivement en sous-fonctions. Une fonction feuille est une fonction élémentaire qui peut être allouée à un seul constituant logique. La profondeur de décomposition est déterminée par l'utilisateur, ne pas en ajouter.

R2 — ENTRÉES/SORTIES OBLIGATOIRES : Chaque fonction (à tout niveau de décomposition) doit avoir au moins une entrée et une sortie. Si l'utilisateur n'a pas précisé les entrées/sorties d'une fonction, ajouter un warning "missing_info" sans les inventer.

R3 — TYPAGE DES FLUX : Chaque flux fonctionnel doit avoir un flow_type parmi : pneumatic, electric, information, mechanical, thermal, data. Si l'utilisateur n'a pas précisé le type, ajouter un warning "missing_info".

R4 — ALLOCATION CONSTITUANT::FONCTION : Si l'utilisateur a précisé la notation "Constituant::Fonction" dans la section functional_behavior, extraire le champ allocated_to de chaque fonction feuille. Si l'allocation n'est pas précisée, laisser allocated_to à null.

R5 — CHAÎNES FONCTIONNELLES : Une chaîne fonctionnelle est un chemin de bout en bout qui réalise une fonction de service. Elle doit lister les fonctions dans l'ordre d'exécution et préciser les entrées/sorties aux frontières du système.

R6 — COHÉRENCE AVEC LE NIVEAU OPÉRATIONNEL : Les fonctions de service du niveau fonctionnel doivent correspondre aux use cases et fonctions mentionnées dans le modèle opérationnel. Si une incohérence est détectée, ajouter un warning "inconsistency".

R7 — MODES FONCTIONNELS : Les modes doivent correspondre aux modes définis au niveau opérationnel. Pour chaque mode, lister les fonctions actives. Ne pas inventer de modes absents du niveau opérationnel."""

_JSON_SCHEMA = """\
=== SCHÉMA JSON ATTENDU ===

{
  "system_name": "string — Nom du système (doit correspondre au niveau opérationnel)",
  "functions": [
    {
      "name": "string — Nom de la fonction (verbe + complément)",
      "description": "string" ou null,
      "inputs": [
        {"name": "string — Nom du flux d'entrée", "flow_type": "pneumatic | electric | information | mechanical | thermal | data"}
      ],
      "outputs": [
        {"name": "string — Nom du flux de sortie", "flow_type": "..."}
      ],
      "sub_functions": [ "...même structure récursive..." ] ou null,
      "allocated_to": "string — Nom du constituant pressenti" ou null
    }
  ],
  "functional_flows": [
    {
      "from_function": "string — Nom de la fonction source",
      "to_function": "string — Nom de la fonction cible",
      "item": "string — Nom de l'item transporté",
      "flow_type": "pneumatic | electric | information | mechanical | thermal | data",
      "description": "string" ou null
    }
  ],
  "functional_chains": [
    {
      "name": "string — Nom de la chaîne fonctionnelle",
      "description": "string" ou null,
      "functions": ["string — Noms des fonctions dans l'ordre"],
      "system_inputs": [{"name": "string", "flow_type": "..."}],
      "system_outputs": [{"name": "string", "flow_type": "..."}]
    }
  ],
  "modes": [
    {
      "name": "string — Nom du mode",
      "description": "string" ou null,
      "active_functions": ["string — Fonctions actives"],
      "transitions": [
        {"from_mode": "string", "to_mode": "string", "trigger": "string"}
      ] ou null
    }
  ],
  "warnings": [
    {
      "type": "inconsistency | missing_info | ambiguity",
      "message": "string",
      "section": "string — section_id concernée",
      "suggestion": "string" ou null
    }
  ]
}"""

_SYSML_SYNTAX_RULES = """\
=== RÈGLES DE SYNTAXE SysML v2 (OBLIGATOIRES) ===

RÈGLE S1 — PACKAGE : Tout le code doit être dans un package nommé '{{system_name}} - Functional'.

RÈGLE S2 — ITEM DEFINITIONS : Chaque type de flux échangé entre fonctions doit avoir un item def. Nommer en PascalCase sans espaces ni accents.

RÈGLE S3 — ACTION DEFINITIONS (Fonctions) :
Chaque fonction est modélisée comme une action def.
Syntaxe :
  action def 'NomFonction' {{
    doc /* Description de la fonction */
    in nomEntree : TypeFlux;
    out nomSortie : TypeFlux;
  }}

RÈGLE S4 — DÉCOMPOSITION FONCTIONNELLE :
Les sous-fonctions sont des actions imbriquées dans l'action parente.
Les flux entre sous-fonctions utilisent 'flow'.
Syntaxe :
  action def 'FonctionParente' {{
    in entreeParente : TypeFlux;
    out sortieParente : TypeFlux;

    action sousFonction1 : SousFonction1Def {{
      in entree;
      out sortie;
    }}
    flow sousFonction1.sortie to sousFonction2.entree;
    action sousFonction2 : SousFonction2Def {{
      in entree;
      out sortie;
    }}
    bind sousFonction1.entree = entreeParente;
    bind sousFonction2.sortie = sortieParente;
  }}

RÈGLE S5 — ALLOCATION CONSTITUANT::FONCTION (Functional Behavior Diagram) :
Si une fonction feuille a un champ allocated_to non null, documenter l'allocation :
  action def 'NomFonction' {{
    doc /* Allouée à : NomConstituant */
  }}
Et dans une section séparée, déclarer l'allocation :
  part def NomConstituant {{
    perform action nomFonction : NomFonctionDef;
  }}

RÈGLE S6 — CHAÎNES FONCTIONNELLES :
Chaque chaîne fonctionnelle est modélisée comme une action def englobante contenant les sous-actions dans l'ordre, avec les flows entre elles et les binds vers les entrées/sorties système.

RÈGLE S7 — MODES (State Def) :
Les modes sont modélisés avec state def, chaque mode contenant des 'perform action' pour les fonctions actives.
Syntaxe :
  state def 'SystemeModes' {{
    state modeOff {{
      // aucune fonction active
    }}
    state modeOperationnel {{
      perform action fonctionA;
      perform action fonctionB;
    }}
    transition modeOff then modeStandby if triggerDemarrage;
  }}

RÈGLE S8 — SUCCESSIONS :
Si un ordre d'exécution est spécifié entre fonctions, utiliser 'first ... then ...' ou le raccourci 'then action'.

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

1. package '{{system_name}} - Functional' {{
2.   // Item definitions (types de flux fonctionnels)
3.   // Action definitions (fonctions élémentaires)
4.   // Action definitions composites (fonctions de service décomposées)
5.   // Functional chains (actions englobantes)
6.   // Part definitions avec perform (allocation Constituant::Fonction)
7.   // State definitions (modes fonctionnels)
8. }}"""

# Liste ordonnée des 5 sections fonctionnelles
_FUNCTIONAL_SECTIONS = [
    "functional_decomposition",
    "functional_flows",
    "functional_behavior",
    "functional_chains",
    "functional_modes",
]


# ============================================================================
# FONCTION 1 — Prompt JSON (sections utilisateur → FunctionalModel)
# ============================================================================

def build_functional_json_prompt(
    user_sections: List[dict],
    previous_level_model: dict,
    rag_examples: Optional[List[str]] = None,
    correction_feedback: Optional[str] = None,
) -> str:
    """
    Construit le prompt pour générer le modèle fonctionnel (JSON).

    Args:
        user_sections: liste de {"section_id": str, "content": str}
        previous_level_model: OperationalModel JSON du niveau précédent validé
        rag_examples: exemples SysML v2 du RAG (optionnel)
        correction_feedback: feedback de correction si retry (optionnel)

    Returns:
        Le prompt complet (string).
    """
    sections_map = {s["section_id"]: s["content"] for s in (user_sections or [])}

    parts: list[str] = []

    # --- BLOC 1 : RÔLE ---
    parts.append(
        "Tu es un ingénieur système expert en architecture fonctionnelle et en SysML v2. "
        "Tu analyses les réponses structurées d'un utilisateur pour extraire le modèle "
        "fonctionnel de son système. Tu disposes également du modèle opérationnel validé comme contexte."
    )

    # --- BLOC 2 : EXIGENCES DE FIDÉLITÉ ---
    parts.append(_FIDELITY_RULES)

    # --- BLOC 3 : CONTEXTE DU NIVEAU PRÉCÉDENT ---
    prev_json = json.dumps(previous_level_model, indent=2, ensure_ascii=False) if previous_level_model else "{}"
    parts.append(
        "=== MODÈLE OPÉRATIONNEL VALIDÉ (CONTEXTE) ===\n\n"
        f"{prev_json}"
    )

    # --- BLOC 4 : RÉPONSES DE L'UTILISATEUR ---
    user_block_lines = ["=== RÉPONSES DE L'UTILISATEUR ==="]
    for section_id in _FUNCTIONAL_SECTIONS:
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
# FONCTION 2 — Prompt SysML v2 (JSON FunctionalModel → code SysML v2)
# ============================================================================

def build_functional_sysml_prompt(
    json_model: str,
    rag_examples: Optional[List[str]] = None,
) -> str:
    """
    Construit le prompt pour traduire le modèle fonctionnel JSON
    en code SysML v2 (Functional Behavior + Functional Chains).

    Args:
        json_model: le modèle JSON sérialisé (FunctionalModel)
        rag_examples: exemples SysML v2 du RAG (optionnel)

    Returns:
        Le prompt complet (string).
    """
    parts: list[str] = []

    # --- BLOC 1 : RÔLE ---
    parts.append(
        "Tu es un expert SysML v2 (spécification OMG, release 2026-01). "
        "Tu traduis un modèle fonctionnel JSON en code SysML v2 valide en notation textuelle."
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
