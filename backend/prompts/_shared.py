"""
Constantes et helpers partagés entre les prompts SysML v2 de tous les niveaux.
"""

import json
import re
from typing import List, Optional


# ============================================================================
# Blocs réutilisables pour les prompts SysML (JSON → code)
# ============================================================================

SYSML_FIDELITY_BLOCK = """\
=== EXIGENCES DE FIDÉLITÉ ===

F1 — Tu traduis UNIQUEMENT ce qui est dans le JSON. Tu n'inventes aucun élément supplémentaire.
F2 — Tu utilises les noms du JSON pour tous les identifiants SysML v2, convertis en CamelCase ASCII.
F3 — Si un champ est vide, null ou liste vide dans le JSON, tu ne génères PAS de code pour cet élément.
F4 — Les warnings du JSON ne doivent PAS être traduits en code SysML v2.
F5 — AUCUN guillemet simple sauf pour le nom du package. Tous les identifiants en CamelCase sans guillemets."""

SYSON_RULES_BLOCK = """\
=== RÈGLES DE COMPATIBILITÉ SysON (OBLIGATOIRES) ===

Le code SysML v2 doit être compatible avec l'outil SysON. Respecte ces règles ABSOLUES :

RS1: AUCUN accent dans les identifiants.
     Mauvais: Développement, énergie, régulé
     Bon: Developpement, Energie, Regule

RS2: AUCUN caractère spécial dans les identifiants (pas de parenthèses, slash, virgule, apostrophe).
     Mauvais: 'air régulé (P,T)', 'A/C Pneumatic System', 'l\\'état'
     Bon: AirRegulePT, ACPneumaticSystem, LEtat

RS3: Utiliser CamelCase ASCII pour TOUS les identifiants.
     Mauvais: 'Operation maintenance operator', 'Stockage intermédiaire'
     Bon: MaintenanceOperator, StockageIntermediaire

RS4: AUCUN guillemet simple sauf si absolument nécessaire (nom avec espace inévitable).
     Privilégier les identifiants CamelCase sans guillemets.

RS5: Dans les port def, utiliser "attribute nomFlux;" au lieu de "in item nom : Type;" ou "out item nom : Type;".
     Mauvais: port def X { in item fuel : Fuel; out item status : Status; }
     Bon: port def X { attribute fuel; attribute status; }

RS6: PAS de "connect" ni "flow of" dans le code. SysON les crée graphiquement.
     Dans le part contexte, déclarer uniquement les parts instanciés.

RS7: PAS de port conjugué (~). Utiliser le même type de port des deux côtés.
     Mauvais: port basPort : ~ACAvionicsPort;
     Bon: port basPort : ACAvionicsPort;

RS8: Les actions référencées dans les états utilisent la syntaxe "entry action : NomAction;" ou "do action : NomAction;".
     Mauvais: do 'Communicate the system state';
     Bon: do action : CommunicateSystemState;

RS9: Pour les séquences opérationnelles, NE PAS utiliser message/event occurrence.
     Utiliser occurrence def avec doc /* description */ et des part participants simples.
     SysON ne rend pas les diagrammes de séquence."""

SYSML_FINAL_INSTRUCTION = """\
=== TON RÉSULTAT ===

Génère le code SysML v2 dans un package '{system_name} - {diagram_type}'.
Le code doit être syntaxiquement correct et compatible SysON.
Vérifie que chaque accolade ouvrante a son accolade fermante.
Réponds UNIQUEMENT avec le code SysML v2, sans commentaire ni explication.
Pas de markdown, pas de ```. Uniquement le code SysML v2 brut commençant par 'package'."""


# ============================================================================
# Extraction d'identifiants et contrainte de nommage inter-packages
# ============================================================================

_IDENTIFIER_PATTERNS = {
    "action_defs": r"action\s+def\s+([A-Za-z_]\w*|'[^']+')",
    "part_defs": r"part\s+def\s+([A-Za-z_]\w*|'[^']+')",
    "port_defs": r"port\s+def\s+([A-Za-z_]\w*|'[^']+')",
    "state_defs": r"state\s+def\s+([A-Za-z_]\w*|'[^']+')",
    "item_defs": r"item\s+def\s+([A-Za-z_]\w*|'[^']+')",
    "attribute_defs": r"attribute\s+def\s+([A-Za-z_]\w*|'[^']+')",
    "use_case_defs": r"use\s+case\s+def\s+([A-Za-z_]\w*|'[^']+')",
    "occurrence_defs": r"occurrence\s+def\s+([A-Za-z_]\w*|'[^']+')",
}

_IDENTIFIER_LABELS = {
    "action_defs": "Action definitions",
    "part_defs": "Part definitions",
    "port_defs": "Port definitions",
    "state_defs": "State definitions",
    "item_defs": "Item definitions",
    "attribute_defs": "Attribute definitions",
    "use_case_defs": "Use case definitions",
    "occurrence_defs": "Occurrence definitions",
}


def extract_identifiers_from_sysml(sysml_code: str) -> dict:
    """
    Extrait les identifiants définis dans un code SysML v2.

    Returns:
        Dict avec les listes de noms par type de construct.
    """
    identifiers = {}
    for key, pattern in _IDENTIFIER_PATTERNS.items():
        matches = re.findall(pattern, sysml_code)
        cleaned = [m.strip("'") for m in matches]
        if cleaned:
            identifiers[key] = cleaned
    return identifiers


def merge_identifiers(accumulated: dict, new: dict) -> dict:
    """Fusionne de nouveaux identifiants dans l'accumulateur (sans doublons)."""
    merged = dict(accumulated)
    for key, names in new.items():
        existing = set(merged.get(key, []))
        existing.update(names)
        merged[key] = sorted(existing)
    return merged


def build_naming_constraint_block(identifiers: dict) -> str:
    """
    Construit un bloc de texte à injecter dans un prompt pour forcer
    la réutilisation des noms déjà générés dans les packages précédents.
    """
    if not identifiers:
        return ""

    lines = [
        "=== CONTRAINTE DE NOMMAGE (OBLIGATOIRE) ===",
        "Les packages precedents ont deja defini les identifiants suivants.",
        "Tu DOIS reutiliser EXACTEMENT ces noms. Ne PAS inventer de variantes.",
        "",
    ]

    for key, label in _IDENTIFIER_LABELS.items():
        names = identifiers.get(key, [])
        if names:
            lines.append(f"{label} existantes : {', '.join(names)}")

    lines.append("")
    lines.append("Si tu dois referencer un element deja defini, utilise EXACTEMENT le nom ci-dessus.")

    return "\n".join(lines)


def build_sysml_prompt(
    diagram_type: str,
    role_suffix: str,
    template: str,
    rules: str,
    filtered_json: dict,
    rag_examples: Optional[List[str]] = None,
    naming_constraint: str = "",
) -> str:
    """
    Construit un prompt SysML v2 pour un type de diagramme donné.

    Structure en 9 blocs :
      1. Rôle
      2. Fidélité SysML
      3. Règles SysON
      4. Template de syntaxe
      5. Règles spécifiques
      6. Contrainte de nommage (optionnel)
      7. Données JSON
      8. Exemples RAG (optionnel)
      9. Instruction finale

    Args:
        diagram_type: nom du type de diagramme (ex: "Lifecycle")
        role_suffix: complément de rôle spécifique
        template: template de syntaxe validé SysON
        rules: règles spécifiques au diagramme
        filtered_json: sous-ensemble du JSON pertinent
        rag_examples: exemples RAG (optionnel)
        naming_constraint: bloc de contrainte de nommage inter-packages (optionnel)

    Returns:
        Le prompt complet (string).
    """
    system_name = filtered_json.get("system_name", "System")
    parts: list[str] = []

    # --- BLOC 1 : RÔLE ---
    parts.append(
        f"Tu es un expert SysML v2 (spécification OMG 2025). "
        f"Tu génères du code SysML v2 syntaxiquement correct et compatible SysON "
        f"pour un diagramme de type {diagram_type}. {role_suffix}"
    )

    # --- BLOC 2 : EXIGENCES DE FIDÉLITÉ ---
    parts.append(SYSML_FIDELITY_BLOCK)

    # --- BLOC 3 : RÈGLES DE COMPATIBILITÉ SysON ---
    parts.append(SYSON_RULES_BLOCK)

    # --- BLOC 4 : TEMPLATE DE SYNTAXE ---
    parts.append(
        "Voici la syntaxe SysML v2 correcte et compatible SysON pour ce type de diagramme.\n"
        "Tu DOIS utiliser EXACTEMENT ces constructs. Ne PAS inventer d'autre syntaxe.\n\n"
        f"{template}"
    )

    # --- BLOC 5 : RÈGLES DE SYNTAXE SPÉCIFIQUES ---
    parts.append(rules)

    # --- BLOC 6 : CONTRAINTE DE NOMMAGE (optionnel) ---
    if naming_constraint:
        parts.append(naming_constraint)

    # --- BLOC 7 : DONNÉES À TRADUIRE ---
    json_str = json.dumps(filtered_json, indent=2, ensure_ascii=False)
    parts.append(
        "=== DONNÉES DU MODÈLE JSON À TRADUIRE ===\n\n"
        "Traduis UNIQUEMENT ces données. N'ajoute rien.\n\n"
        f"{json_str}"
    )

    # --- BLOC 8 : EXEMPLES RAG (optionnel) ---
    if rag_examples:
        rag_lines = ["=== EXEMPLES DE SYNTAXE SysML v2 POUR RÉFÉRENCE ==="]
        for i, example in enumerate(rag_examples[:3], 1):
            rag_lines.append(f"\nExemple {i}:\n{example}")
        parts.append("\n".join(rag_lines))

    # --- BLOC 9 : INSTRUCTION FINALE ---
    instruction = SYSML_FINAL_INSTRUCTION.format(
        system_name=system_name,
        diagram_type=diagram_type,
    )
    parts.append(instruction)

    return "\n\n".join(parts)
