"""
Prompts pour le niveau TECHNIQUE (Technical).

Deux fonctions :
  - build_technical_json_prompt  : sections utilisateur → JSON TechnicalModel
  - build_technical_sysml_prompt : JSON TechnicalModel  → code SysML v2
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

_SYSML_SYNTAX_RULES = """\
=== RÈGLES DE SYNTAXE SysML v2 (OBLIGATOIRES) ===

RÈGLE S1 — PACKAGE : Tout le code doit être dans un package nommé '{{system_name}} - Technical'.

RÈGLE S2 — ITEM DEFINITIONS : item def pour chaque type de flux physique.

RÈGLE S3 — PORT DEFINITIONS : ports physiques des composants réels.

RÈGLE S4 — PART DEFINITIONS (Composants techniques) :
  part def NAIV {{
    doc /* Nacelle Anti-Ice Valve — Vanne pneumatique papillon
           Implémente : Vanne NAI (logique)
           Référence : SAE-NAIV-200 */
    port portEntreeAir : PortPneumatiqueIn;
    port portSortieAir : PortPneumatiqueOut;
    port portCommandeElec : PortElectriqueIn;
  }}

RÈGLE S5 — ALLOCATION LOGIQUE→TECHNIQUE :
  allocation def LogicalToTechnical {{
    end logicalPart : LogicalComponentDef;
    end technicalPart : TechnicalComponentDef;
  }}
Ou plus simplement, documenter dans le 'doc' de chaque part def technique quel constituant logique il implémente.

RÈGLE S6 — ARCHITECTURE TECHNIQUE (part + connections) :
  part basPhysique : BASPhysique {{
    part naiv : NAIV;
    part eec : EEC;

    connect naiv.portCommandeElec to eec.portSortieCommande;

    flow of ConsigneOuverture
      from eec.portSortieCommande
      to naiv.portCommandeElec;
  }}
Documenter le medium dans un commentaire ou doc sur chaque connexion.

RÈGLE S7 — CHOIX TECHNOLOGIQUES :
Documenter chaque choix avec un commentaire structuré :
  part def NAIV {{
    doc /* Technologie : vanne papillon
           Justification : meilleure tenue aux hautes températures (500°C) */
  }}

RÈGLE S8 — REQUIREMENTS :
  requirement def 'REQ-TECH-001' {{
    doc /* La NAIV doit résister à 45 PSI et 500°C en continu */
  }}
  satisfy requirement 'REQ-TECH-001' by naiv;

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

1. package '{{system_name}} - Technical' {{
2.   // Item definitions (flux physiques)
3.   // Port definitions (ports physiques)
4.   // Part definitions (composants techniques avec doc allocation + technologie)
5.   // Part englobant (architecture technique + connections + flows)
6.   // Requirement definitions + satisfy
7. }}"""

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
# FONCTION 2 — Prompt SysML v2 (JSON TechnicalModel → code SysML v2)
# ============================================================================

def build_technical_sysml_prompt(
    json_model: str,
    rag_examples: Optional[List[str]] = None,
) -> str:
    """
    Construit le prompt pour traduire le modèle technique JSON
    en code SysML v2 (Technical Architecture Diagram).

    Args:
        json_model: le modèle JSON sérialisé (TechnicalModel)
        rag_examples: exemples SysML v2 du RAG (optionnel)

    Returns:
        Le prompt complet (string).
    """
    parts: list[str] = []

    # --- BLOC 1 : RÔLE ---
    parts.append(
        "Tu es un expert SysML v2 (spécification OMG, release 2026-01). "
        "Tu traduis un modèle d'architecture technique JSON en code SysML v2 valide en notation textuelle."
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
