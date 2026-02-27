"""
Prompts pour le niveau OPÉRATIONNEL (Operational).

Deux fonctions :
  - build_operational_json_prompt  : sections utilisateur → JSON OperationalModel
  - build_operational_sysml_prompt : JSON OperationalModel  → code SysML v2
"""

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

R1 — DISTINCTION STAKEHOLDER / SYSTÈME EXTERNE : Un stakeholder est soit une PERSONNE/ORGANISATION, soit un SYSTÈME TECHNIQUE ACTIF qui est ACTEUR dans un cas d'utilisation (il initie des interactions, envoie des commandes, ou reçoit activement des services). Une entité physique passive (une vanne, un connecteur, une frontière) est un external_system, pas un stakeholder. Le champ "stakeholders" ne doit JAMAIS être vide si des entités interagissent activement avec le système.

R2 — FORMAT DES STAKEHOLDERS : Chaque stakeholder doit avoir un name, un role, et un type parmi "human", "system", "organization".

R3 — INTERFACES EXTERNES AVEC FLUX : Chaque système externe doit lister les flux échangés avec le système, en précisant le nom, la direction (in/out/inout), et le type de flux (pneumatic/electric/information/mechanical/thermal/data).

R4 — DÉCOMPOSITION DES USE CASES : Si un use case est "Fournir/Envoyer X à Y" et que la description mentionne PLUSIEURS destinations distinctes, décompose en sous-use cases séparés par destination.

R5 — SCÉNARIOS STRUCTURÉS : Chaque scénario doit avoir des steps structurés avec un order, un source (qui envoie), un target (qui reçoit), une action (description de l'échange), et optionnellement un flow_type.

R6 — MODES AVEC TRANSITIONS : Chaque mode doit lister les fonctions actives. Les transitions entre modes doivent préciser from_mode, to_mode, et le trigger (événement déclencheur).

R7 — LIFECYCLE : Les phases de vie doivent être extraites uniquement de la section lifecycle. Si la section est vide, laisser lifecycle_phases comme liste vide.

R8 — EXIGENCES : Les exigences opérationnelles doivent être formulées avec la structure "condition d'application + ce que le système doit faire/être + paramètres mesurables". L'ID doit suivre le format REQ-OP-XXX. Ne les inventer que si l'utilisateur les mentionne explicitement."""

_JSON_SCHEMA = """\
=== SCHÉMA JSON ATTENDU ===

{
  "system_name": "string — Nom exact du système tel que donné par l'utilisateur",
  "description": "string — Description de la mission du système",
  "system_boundaries": "string — Ce qui est IN et OUT du périmètre",
  "lifecycle_phases": [
    {
      "name": "string — Nom de la phase",
      "sub_phases": ["string"] ou null,
      "description": "string" ou null
    }
  ],
  "stakeholders": [
    {
      "name": "string — Nom exact de l'acteur",
      "role": "string — Son rôle vis-à-vis du système",
      "type": "human | system | organization"
    }
  ],
  "external_interfaces": [
    {
      "system_name": "string — Nom du système externe",
      "flows": [
        {
          "name": "string — Nom du flux",
          "direction": "in | out | inout",
          "flow_type": "pneumatic | electric | information | mechanical | thermal | data",
          "description": "string" ou null
        }
      ]
    }
  ],
  "use_cases": [
    {
      "name": "string — Verbe + complément",
      "actors": ["string — Noms des acteurs impliqués"],
      "includes": ["string — Noms des use cases inclus"] ou null,
      "description": "string" ou null
    }
  ],
  "operational_scenarios": [
    {
      "name": "string — Nom du scénario",
      "description": "string",
      "steps": [
        {
          "order": 1,
          "source": "string — Qui envoie",
          "target": "string — Qui reçoit",
          "action": "string — Description de l'échange",
          "flow_type": "pneumatic | electric | information | ..." ou null
        }
      ]
    }
  ],
  "operating_modes": [
    {
      "name": "string — Nom du mode",
      "description": "string" ou null,
      "active_functions": ["string — Fonctions actives dans ce mode"],
      "transitions": [
        {
          "from_mode": "string",
          "to_mode": "string",
          "trigger": "string — Événement déclencheur"
        }
      ] ou null
    }
  ],
  "requirements": [
    {
      "id": "REQ-OP-XXX",
      "text": "string — Texte structuré de l'exigence",
      "satisfied_by": "string" ou null
    }
  ],
  "warnings": [
    {
      "type": "inconsistency | missing_info | ambiguity",
      "message": "string — Description du problème détecté",
      "section": "string — section_id concernée",
      "suggestion": "string — Suggestion pour l'utilisateur" ou null
    }
  ]
}"""

_SYSML_SYNTAX_RULES = """\
=== RÈGLES DE SYNTAXE SysML v2 (OBLIGATOIRES) ===

RÈGLE S1 — PACKAGE : Tout le code doit être dans un package nommé '{system_name} - Operational'.

RÈGLE S2 — LIFECYCLE (Lifecycle Diagram) :
Utiliser des state def et state pour modéliser les phases de vie.
Syntaxe :
  state def LifecycleStates {{
    entry state phase1 : Phase1;
    state phase2 : Phase2;
    transition phase1 then phase2;
  }}
Chaque phase est un state. Les sous-phases sont des states imbriqués.
Les transitions entre phases utilisent 'transition ... then ...'.

RÈGLE S3 — USE CASES (Use Case Diagram) :
Utiliser use case def pour les définitions et use case pour les usages.
Syntaxe :
  use case def 'Nom du use case' {{
    doc /* Description */
    actor acteurRef : ActeurDef;
  }}
Les acteurs sont définis comme des part def avec un commentaire ou metadata.
Les liens include sont des 'include use case'.

RÈGLE S4 — CONTEXT (Context Diagram) :
Utiliser part def pour le système et les systèmes externes.
Définir des port def pour les interfaces.
Utiliser des connection def ou interface def pour les liens entre le système et ses systèmes externes.
Syntaxe pour les ports :
  port def NomPort {{
    in item nomFlux : TypeFlux;
    // ou out item ...
  }}
Les flux aux interfaces doivent être typés avec des item def correspondant aux types de flux.

RÈGLE S5 — SCÉNARIOS OPÉRATIONNELS (Operational Sequence Diagram) :
Utiliser des action def pour modéliser les séquences d'interactions.
Chaque participant (système, acteur, système externe) est une lifeline.
Les échanges sont modélisés avec des send/accept actions.
Syntaxe :
  action def 'NomScénario' {{
    // Participants
    ref part système : SystemDef;
    ref part acteur : ActeurDef;

    // Séquence
    action step1 send message1 via système {{ ... }}
    then action step2 accept message1 via acteur {{ ... }}
  }}
Pour les séquences simples, des successions d'actions avec flow sont acceptables :
  action def 'NomScénario' {{
    action step1 : Step1Def {{ out message1; }}
    flow step1.message1 to step2.message1;
    then action step2 : Step2Def {{ in message1; }}
  }}

RÈGLE S6 — MODES (Operating Mode Chart Diagram) :
Utiliser state def pour le diagramme de modes.
Syntaxe :
  state def 'NomSysteme Modes' {{
    entry state modeOff : ModeOff;
    state modeStandby : ModeStandby;
    state modeOperationnel : ModeOperationnel;
    transition modeOff then modeStandby if trigger1;
    transition modeStandby then modeOperationnel if trigger2;
  }}
Les fonctions actives dans chaque mode sont documentées avec 'doc' ou des 'perform' à l'intérieur de chaque state.

RÈGLE S7 — EXIGENCES :
Utiliser requirement def pour les exigences.
Syntaxe :
  requirement def 'REQ-OP-001' {{
    doc /* Texte de l'exigence */
  }}
Les liens de satisfaction utilisent :
  satisfy requirement 'REQ-OP-001' by nomElement;

RÈGLE S8 — ITEMS DEF POUR LES FLUX :
Chaque type de flux échangé doit avoir un item def :
  item def AirChaudHautePression;
  item def CommandeDegivrageNacelle;
Les noms des item def doivent correspondre aux noms de flux du JSON (en PascalCase sans espaces ni accents).

RÈGLE S9 — COMMENTAIRES :
Utiliser 'doc /* ... */' pour documenter les éléments.
Ajouter un commentaire de section entre les grandes parties du code :
  // ========================================
  // SECTION : Lifecycle
  // ========================================

RÈGLE S10 — IDENTIFIANTS :
Les identifiants SysML v2 avec des espaces ou caractères spéciaux doivent être entourés de guillemets simples : 'Nom avec espaces'.
Les identifiants sans espaces ni caractères spéciaux peuvent être écrits sans guillemets."""

_SYSML_CODE_STRUCTURE = """\
=== STRUCTURE DU CODE SysML v2 À PRODUIRE ===

Le code doit suivre cette organisation :

1. package '{system_name} - Operational' {{
2.   // Item definitions (types de flux)
3.   // Part definitions (acteurs, systèmes externes, système principal)
4.   // Port definitions (interfaces)
5.   // Use case definitions
6.   // Lifecycle states
7.   // Operating modes
8.   // Requirement definitions
9.   // Operational scenarios (action definitions)
10.  // Connections et flows (contexte)
11. }}"""

# Liste ordonnée des 7 sections opérationnelles attendues
_OPERATIONAL_SECTIONS = [
    "system_mission",
    "lifecycle",
    "stakeholders",
    "external_systems",
    "use_cases",
    "operational_scenarios",
    "operating_modes",
]


# ============================================================================
# FONCTION 1 — Prompt JSON (sections utilisateur → OperationalModel)
# ============================================================================

def build_operational_json_prompt(
    user_sections: List[dict],
    rag_examples: Optional[List[str]] = None,
    correction_feedback: Optional[str] = None,
) -> str:
    """
    Construit le prompt pour générer le modèle opérationnel (JSON)
    à partir des réponses sectionnées de l'utilisateur.

    Args:
        user_sections: liste de {"section_id": str, "content": str}
        rag_examples: exemples SysML v2 du RAG (optionnel)
        correction_feedback: feedback de correction si retry (optionnel)

    Returns:
        Le prompt complet (string).
    """
    # Index rapide section_id → content
    sections_map = {s["section_id"]: s["content"] for s in (user_sections or [])}

    parts: list[str] = []

    # --- BLOC 1 : RÔLE ---
    parts.append(
        "Tu es un ingénieur système expert en analyse opérationnelle et en SysML v2. "
        "Tu analyses les réponses structurées d'un utilisateur pour extraire le modèle "
        "opérationnel de son système."
    )

    # --- BLOC 2 : EXIGENCES DE FIDÉLITÉ ---
    parts.append(_FIDELITY_RULES)

    # --- BLOC 3 : RÉPONSES DE L'UTILISATEUR ---
    user_block_lines = ["=== RÉPONSES DE L'UTILISATEUR ==="]
    for section_id in _OPERATIONAL_SECTIONS:
        content = sections_map.get(section_id, "").strip()
        user_block_lines.append(f"\n[SECTION: {section_id}]")
        if content:
            user_block_lines.append(content)
        else:
            user_block_lines.append("(Section non renseignée par l'utilisateur)")
    parts.append("\n".join(user_block_lines))

    # --- BLOC 4 : RÈGLES MÉTIER ---
    parts.append(_BUSINESS_RULES)

    # --- BLOC 5 : SCHÉMA JSON ATTENDU ---
    parts.append(_JSON_SCHEMA)

    # --- BLOC 6 : EXEMPLES RAG (optionnel) ---
    if rag_examples:
        rag_lines = ["=== EXEMPLES DE SYNTAXE SysML v2 POUR RÉFÉRENCE ==="]
        for i, example in enumerate(rag_examples[:5], 1):
            rag_lines.append(f"\nExemple {i}:\n{example}")
        parts.append("\n".join(rag_lines))

    # --- BLOC 7 : CORRECTION (optionnel) ---
    if correction_feedback:
        parts.append(
            "=== CORRECTION REQUISE ===\n"
            f"{correction_feedback}"
        )

    # --- BLOC 8 : INSTRUCTION FINALE ---
    parts.append(
        "=== TON RÉSULTAT ===\n"
        "Produis UNIQUEMENT le JSON conforme au schéma ci-dessus. "
        "Aucun commentaire, aucune explication, aucun markdown. Uniquement le JSON."
    )

    return "\n\n".join(parts)


# ============================================================================
# FONCTION 2 — Prompt SysML v2 (JSON OperationalModel → code SysML v2)
# ============================================================================

def build_operational_sysml_prompt(
    json_model: str,
    rag_examples: Optional[List[str]] = None,
) -> str:
    """
    Construit le prompt pour traduire le modèle opérationnel JSON
    en code SysML v2 couvrant les 5 diagrammes opérationnels.

    Args:
        json_model: le modèle JSON sérialisé (OperationalModel)
        rag_examples: exemples SysML v2 du RAG (optionnel)

    Returns:
        Le prompt complet (string).
    """
    parts: list[str] = []

    # --- BLOC 1 : RÔLE ---
    parts.append(
        "Tu es un expert SysML v2 (spécification OMG, release 2026-01). "
        "Tu traduis un modèle opérationnel JSON en code SysML v2 valide en notation textuelle."
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
