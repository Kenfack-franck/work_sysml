"""
Prompts pour le niveau FONCTIONNEL (Functional).

Fonctions :
  - build_functional_json_prompt           : sections utilisateur → JSON FunctionalModel
  - build_functional_breakdown_sysml_prompt : JSON → code SysML v2 (Functional Breakdown)
  - build_functional_behaviour_sysml_prompt : JSON → code SysML v2 (Functional Behaviour)
  - build_functional_modes_sysml_prompt     : JSON → code SysML v2 (Functional Modes)
  - get_functional_sysml_prompts            : JSON → [(diagram_type, prompt), ...] x3
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
# Templates de syntaxe validés (compatibles SysON)
# ============================================================================

_TEMPLATE_FUNCTIONAL_BREAKDOWN = """\
=== TEMPLATE DE SYNTAXE : FUNCTIONAL BREAKDOWN (compatible SysON) ===

package 'SystemName - Functional Breakdown' {

    // Types des items echanges
    item def Scene;
    item def Image;
    item def Picture;

    // Definitions des fonctions feuilles
    action def Focus {
        doc /* Description de la sous-fonction */
        in scene : Scene;
        out image : Image;
    }

    action def Shoot {
        doc /* Description */
        in image : Image;
        out picture : Picture;
    }

    // Fonction composite avec decomposition
    action def TakePicture {
        doc /* Fonction de service principale */
        in scene : Scene;
        out picture : Picture;

        // Sous-actions
        action focus : Focus {
            in scene;
            out image;
        }
        action shoot : Shoot {
            in image;
            out picture;
        }

        // Liaison aux parametres parents
        bind focus.scene = scene;
        bind shoot.picture = picture;
    }

    // Allocation aux constituants logiques
    part def AutoFocus {
        doc /* Constituant logique */
        perform action focus : Focus;
    }

    part def Imager {
        doc /* Constituant logique */
        perform action shoot : Shoot;
    }
}"""

_RULES_FUNCTIONAL_BREAKDOWN = """\
=== RÈGLES DE SYNTAXE SPÉCIFIQUES : FUNCTIONAL BREAKDOWN ===

R-FB1: Les fonctions de service sont des "action def" avec "in" et "out" items.
R-FB2: Les sous-fonctions sont des "action" (usages) imbriquees dans l action def parente.
R-FB3: Les liaisons aux parametres parents utilisent "bind subAction.param = parentParam;"
R-FB4: L allocation aux constituants utilise "part def Constituant { perform action nom : ActionDef; }"
R-FB5: Tous les noms en CamelCase ASCII sans accents (RS1-RS4).
R-FB6: Les item def pour les types de flux sont declares au niveau package.
R-FB7: Si une fonction n est pas decomposee dans le document, la declarer comme action def simple sans sous-actions."""

_TEMPLATE_FUNCTIONAL_BEHAVIOUR = """\
=== TEMPLATE DE SYNTAXE : FUNCTIONAL BEHAVIOUR (compatible SysON) ===

package 'SystemName - Functional Behaviour' {

    // Types des items echanges
    item def Scene;
    item def Image;
    item def Picture;

    // Definitions des fonctions avec entrees/sorties
    action def Focus {
        in scene : Scene;
        out image : Image;
    }

    action def Shoot {
        in image : Image;
        out picture : Picture;
    }

    // Chaine fonctionnelle complete avec flux
    action def TakePictureChain {
        doc /* Chaine fonctionnelle de bout en bout */
        in scene : Scene;
        out picture : Picture;

        action focus : Focus {
            in scene;
            out image;
        }

        action shoot : Shoot {
            in image;
            out picture;
        }

        // Flux entre sous-fonctions
        flow focus.image to shoot.image;

        // Succession (ordre d execution)
        first focus then shoot;

        // Liaison aux bornes du systeme
        bind focus.scene = scene;
        bind shoot.picture = picture;
    }
}"""

_RULES_FUNCTIONAL_BEHAVIOUR = """\
=== RÈGLES DE SYNTAXE SPÉCIFIQUES : FUNCTIONAL BEHAVIOUR ===

R-BH1: Les flux entre sous-fonctions utilisent "flow source.output to target.input;"
R-BH2: L ordre d execution utilise "first action1 then action2;" ou le raccourci "then action"
R-BH3: Les chaines fonctionnelles sont des action def composites contenant les sous-actions et leurs flux.
R-BH4: Les liaisons aux bornes du systeme utilisent "bind subAction.param = chainParam;"
R-BH5: Chaque flux du JSON devient un "flow" entre deux sous-actions.
R-BH6: Les item def sont declares au niveau package avec des noms CamelCase ASCII.
R-BH7: Pour les boucles de retroaction, utiliser "flow" sans "first/then" (flux continu pendant l execution)."""

_TEMPLATE_FUNCTIONAL_MODES = """\
=== TEMPLATE DE SYNTAXE : FUNCTIONAL MODES (compatible SysON) ===

package 'SystemName - Functional Modes' {

    // Signaux de transition
    attribute def PowerOnSignal;
    attribute def PowerOffSignal;
    attribute def StartOperationSignal;
    attribute def StopOperationSignal;

    // References aux fonctions (action def declarees dans Functional Breakdown)
    action def MonitorSystem;
    action def ProcessData;
    action def TransmitData;

    state def FunctionalModes {
        entry; then ModeOff;

        state ModeOff {
            doc /* Aucune fonction active */
        }
        transition PowerOn
            first ModeOff
            accept PowerOnSignal
            then ModeOn;

        state ModeOn {
            entry; then Standby;

            state Standby {
                doc /* Seules les fonctions de surveillance sont actives */
                perform action monitorSystem : MonitorSystem;
            }
            transition StartOp
                first Standby
                accept StartOperationSignal
                then Operating;

            state Operating {
                doc /* Toutes les fonctions sont actives */
                perform action monitorSystem : MonitorSystem;
                perform action processData : ProcessData;
                perform action transmitData : TransmitData;
            }
            transition StopOp
                first Operating
                accept StopOperationSignal
                then Standby;
        }
        transition PowerOff
            first ModeOn
            accept PowerOffSignal
            then ModeOff;
    }
}"""

_RULES_FUNCTIONAL_MODES = """\
=== RÈGLES DE SYNTAXE SPÉCIFIQUES : FUNCTIONAL MODES ===

R-FM1: Les modes utilisent "state def" avec "entry; then PremierEtat;". JAMAIS "entry state".
R-FM2: Les fonctions actives dans un mode utilisent "perform action nomLocal : ActionDef;"
R-FM3: Les transitions : "transition Nom first Source accept Signal then Cible;"
R-FM4: Les action def references dans les perform doivent etre declares au niveau package (meme si ce sont des stubs).
R-FM5: Noms CamelCase ASCII pour tout (etats, signaux, actions).
R-FM6: Les etats composites contiennent "entry; then" pour leur sous-etat initial.
R-FM7: JAMAIS de "transition Source then Cible if 'texte francais'". Utiliser accept Signal."""


# ============================================================================
# FONCTIONS SysML v2 — 3 prompts spécialisés par type de diagramme
# ============================================================================

def build_functional_breakdown_sysml_prompt(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
    naming_constraint: str = "",
) -> str:
    """Construit le prompt SysML v2 pour le diagramme Functional Breakdown."""
    filtered = {
        "system_name": model_json.get("system_name", "System"),
        "functions": model_json.get("functions", []),
        "functional_behavior": model_json.get("functional_behavior", []),
    }
    return build_sysml_prompt(
        diagram_type="Functional Breakdown",
        role_suffix="Tu modélises l'arborescence fonctionnelle : fonctions de service décomposées en sous-fonctions, avec allocation aux constituants logiques.",
        template=_TEMPLATE_FUNCTIONAL_BREAKDOWN,
        rules=_RULES_FUNCTIONAL_BREAKDOWN,
        filtered_json=filtered,
        rag_examples=rag_examples,
        naming_constraint=naming_constraint,
    )


def build_functional_behaviour_sysml_prompt(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
    naming_constraint: str = "",
) -> str:
    """Construit le prompt SysML v2 pour le diagramme Functional Behaviour (flows)."""
    filtered = {
        "system_name": model_json.get("system_name", "System"),
        "functions": model_json.get("functions", []),
        "functional_flows": model_json.get("functional_flows", []),
        "functional_chains": model_json.get("functional_chains", []),
    }
    return build_sysml_prompt(
        diagram_type="Functional Behaviour",
        role_suffix="Tu modélises les flux entre sous-fonctions avec entrées/sorties et chaînes fonctionnelles de bout en bout.",
        template=_TEMPLATE_FUNCTIONAL_BEHAVIOUR,
        rules=_RULES_FUNCTIONAL_BEHAVIOUR,
        filtered_json=filtered,
        rag_examples=rag_examples,
        naming_constraint=naming_constraint,
    )


def build_functional_modes_sysml_prompt(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
    naming_constraint: str = "",
) -> str:
    """Construit le prompt SysML v2 pour le diagramme Functional Modes."""
    filtered = {
        "system_name": model_json.get("system_name", "System"),
        "modes": model_json.get("modes", []),
        "functions": [{"name": f.get("name")} for f in model_json.get("functions", [])],
    }
    return build_sysml_prompt(
        diagram_type="Functional Modes",
        role_suffix="Tu modélises la machine à états des modes fonctionnels avec les fonctions actives/inactives dans chaque mode.",
        template=_TEMPLATE_FUNCTIONAL_MODES,
        rules=_RULES_FUNCTIONAL_MODES,
        filtered_json=filtered,
        rag_examples=rag_examples,
        naming_constraint=naming_constraint,
    )


# ============================================================================
# Fonction utilitaire — appelle les 3 prompts
# ============================================================================

FUNCTIONAL_DIAGRAMS = [
    ("functional_breakdown", build_functional_breakdown_sysml_prompt),
    ("functional_behaviour", build_functional_behaviour_sysml_prompt),
    ("functional_modes", build_functional_modes_sysml_prompt),
]


def get_functional_sysml_prompts(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
    naming_constraint: str = "",
) -> list:
    """
    Retourne une liste de (diagram_type, prompt_text) pour les 3 diagrammes fonctionnels.

    Args:
        model_json: le modèle JSON fonctionnel (dict, pas string)
        rag_examples: exemples SysML v2 du RAG (optionnel)
        naming_constraint: contrainte de nommage des packages précédents

    Returns:
        Liste de tuples (diagram_type: str, prompt: str)
    """
    results = []
    for diagram_type, build_fn in FUNCTIONAL_DIAGRAMS:
        prompt = build_fn(model_json, rag_examples, naming_constraint=naming_constraint)
        results.append((diagram_type, prompt))
    return results
