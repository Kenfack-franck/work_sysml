"""
Prompts pour le niveau OPÉRATIONNEL (Operational).

Fonctions :
  - build_operational_json_prompt  : sections utilisateur → JSON OperationalModel
  - build_lifecycle_sysml_prompt   : JSON → code SysML v2 (lifecycle)
  - build_usecase_sysml_prompt     : JSON → code SysML v2 (use cases)
  - build_context_sysml_prompt     : JSON → code SysML v2 (context)
  - build_sequence_sysml_prompt    : JSON → code SysML v2 (sequences)
  - build_modes_sysml_prompt       : JSON → code SysML v2 (operating modes)
  - get_operational_sysml_prompts  : JSON → [(diagram_type, prompt), ...] x5
"""

import json
from typing import List, Optional


# ============================================================================
# Blocs de texte réutilisables (prompt JSON)
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
# Blocs réutilisables pour les 5 prompts SysML
# ============================================================================

_SYSML_FIDELITY_BLOCK = """\
=== EXIGENCES DE FIDÉLITÉ ===

F1 — Tu traduis UNIQUEMENT ce qui est dans le JSON. Tu n'inventes aucun élément supplémentaire.
F2 — Tu utilises les noms du JSON pour tous les identifiants SysML v2, convertis en CamelCase ASCII.
F3 — Si un champ est vide, null ou liste vide dans le JSON, tu ne génères PAS de code pour cet élément.
F4 — Les warnings du JSON ne doivent PAS être traduits en code SysML v2.
F5 — AUCUN guillemet simple sauf pour le nom du package. Tous les identifiants en CamelCase sans guillemets."""

_SYSON_RULES_BLOCK = """\
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

_SYSML_FINAL_INSTRUCTION = """\
=== TON RÉSULTAT ===

Génère le code SysML v2 dans un package '{system_name} - {diagram_type}'.
Le code doit être syntaxiquement correct et compatible SysON.
Vérifie que chaque accolade ouvrante a son accolade fermante.
Réponds UNIQUEMENT avec le code SysML v2, sans commentaire ni explication.
Pas de markdown, pas de ```. Uniquement le code SysML v2 brut commençant par 'package'."""


# ============================================================================
# Templates de syntaxe validés (compatibles SysON)
# ============================================================================

_TEMPLATE_LIFECYCLE = """\
=== TEMPLATE DE SYNTAXE : LIFECYCLE (compatible SysON) ===

package 'SystemName - Lifecycle' {

    attribute def StartDevelopment;
    attribute def StartProduction;
    attribute def Deliver;
    attribute def StartOperation;
    attribute def EndOfLife;

    state def SystemLifecycle {
        entry; then ConceptEvaluation;

        state ConceptEvaluation;
        transition StartDev
            first ConceptEvaluation
            accept StartDevelopment
            then Developpement;

        state Developpement;
        transition StartProd
            first Developpement
            accept StartProduction
            then Production;

        state Production {
            entry; then Fabrication;
            state Fabrication;
            state Montage;
            transition first Fabrication then Montage;
            state IntegrationEtEssais;
            transition first Montage then IntegrationEtEssais;
            state StockageInterne;
            transition first IntegrationEtEssais then StockageInterne;
        }
        transition DeliverTransition
            first Production
            accept Deliver
            then Livraison;

        state Livraison {
            entry; then StockageIntermediaire;
            state StockageIntermediaire;
            state Transport;
            transition first StockageIntermediaire then Transport;
        }
        transition FinalAssembly
            first Livraison
            accept StartOperation
            then MontageFinal;

        state MontageFinal;
        transition StartOp
            first MontageFinal
            accept StartOperation
            then Exploitation;

        state Exploitation {
            entry; then Operation;
            state Operation;
            state MaintenanceLRU;
            transition first Operation then MaintenanceLRU;
        }
        transition EndLife
            first Exploitation
            accept EndOfLife
            then Recyclage;

        state Recyclage;
    }
}"""

_RULES_LIFECYCLE = """\
=== RÈGLES DE SYNTAXE SPÉCIFIQUES : LIFECYCLE ===

R-LC1: Tous les noms d'états en CamelCase ASCII sans accents.
       "Concept évaluation" → ConceptEvaluation, "Développement" → Developpement

R-LC2: Les transitions utilisent "transition NomTransition first Source accept Signal then Cible;"

R-LC3: Les états composites contiennent leur propre "entry; then PremierSousEtat;"

R-LC4: Les signaux sont des "attribute def" en CamelCase.

R-LC5: Pas de guillemets simples dans les noms sauf si le nom original contient un espace inévitable."""

_TEMPLATE_USECASES = """\
=== TEMPLATE DE SYNTAXE : USE CASES (compatible SysON) ===

package 'SystemName - Use Cases' {

    part def SystemName {
        doc /* Description du systeme */
    }
    part def Operator {
        doc /* Description de l operateur */
    }
    part def ExternalSystem {
        doc /* Description du systeme externe */
    }

    use case def OperateSystem {
        doc /* Description de l objectif */
        subject system : SystemName;
        actor operator : Operator;
        actor externalSystem : ExternalSystem;
    }

    use case def PerformMaintenance {
        doc /* Description */
        subject system : SystemName;
        actor operator : Operator;
    }

    use case def DiagnoseSystem {
        doc /* Description */
        subject system : SystemName;
        actor operator : Operator;
    }

    use case def MaintainOperationalConditions {
        doc /* Operation generique incluant diagnostic et reparation */
        subject system : SystemName;
        actor operator : Operator;
        include use case DiagnoseSystem;
        include use case PerformMaintenance;
    }
}"""

_RULES_USECASES = """\
=== RÈGLES DE SYNTAXE SPÉCIFIQUES : USE CASES ===

R-UC1: Chaque acteur DOIT avoir un "part def NomActeur;" déclaré AVANT les use cases.

R-UC2: Les noms de use case def sont en CamelCase ASCII sans accents ni apostrophes.
       "Pressuriser les réservoirs" → PressuriserLesReservoirs
       "Être informé de l'état du système" → EtreInformeDeLEtat

R-UC3: Le doc /* ... */ va DIRECTEMENT dans le use case def (PAS dans un bloc objective { }).

R-UC4: Les includes vont dans un use case def composite : "include use case NomUseCaseDef;"

R-UC5: Les acteurs sont typés : "actor nomLocal : NomPartDef;"

R-UC6: Pas de guillemets simples dans les noms de use case def ni d'acteurs."""

_TEMPLATE_CONTEXT = """\
=== TEMPLATE DE SYNTAXE : CONTEXT (compatible SysON) ===

package 'SystemName - Context' {

    port def ControllerPort {
        attribute command;
        attribute status;
        attribute energy;
    }

    port def SourcePort {
        attribute supply;
    }

    port def OutputPort {
        attribute output;
    }

    part def MainSystem {
        port controller : ControllerPort;
        port source : SourcePort;
        port output : OutputPort;
    }

    part def Controller {
        port systemPort : ControllerPort;
    }

    part def Source {
        port systemPort : SourcePort;
    }

    part def Consumer {
        port systemPort : OutputPort;
    }

    part 'System Context' {
        part system : MainSystem;
        part controller : Controller;
        part source : Source;
        part consumer : Consumer;
    }
}"""

_RULES_CONTEXT = """\
=== RÈGLES DE SYNTAXE SPÉCIFIQUES : CONTEXT ===

R-CX1: Les port def contiennent des "attribute nomFlux;" PAS "in item" ni "out item".

R-CX2: PAS de port conjugué (~). Utiliser le même type de port des deux côtés.

R-CX3: PAS de "connect" ni "flow of" dans le code. Déclarer uniquement les parts dans le contexte.
        Les connexions et flux seront créés graphiquement dans SysON.

R-CX4: Chaque système externe a un port def, et chaque part def a un port typé.

R-CX5: Le part 'System Context' instancie tous les parts sans les connecter.

R-CX6: Les noms de ports sont descriptifs du rôle (controllerPort, sourcePort, etc.)

R-CX7: Les attributs dans les port def portent le nom du flux échangé (stateData, energie, consignePT, etc.)"""

_TEMPLATE_SEQUENCES = """\
=== TEMPLATE DE SYNTAXE : OPERATIONAL SEQUENCES (compatible SysON) ===

package 'SystemName - Operational Sequences' {

    item def StartCommand;
    item def StatusReport;
    item def DataPacket;

    occurrence def NominalOperationSequence {
        doc /* Scenario nominal :
               1. Operator envoie StartCommand au System
               2. System traite la commande
               3. System envoie StatusReport a Operator
               4. System envoie DataPacket a Subsystem */
        part operator;
        part system;
        part subsystem;
    }

    occurrence def DegradedOperationSequence {
        doc /* Scenario degrade :
               1. System detecte une anomalie
               2. System envoie Alert a Operator
               3. Operator commande un arret */
        part system;
        part operator;
    }
}"""

_RULES_SEQUENCES = """\
=== RÈGLES DE SYNTAXE SPÉCIFIQUES : OPERATIONAL SEQUENCES ===

R-SQ1: Les séquences utilisent "occurrence def NomSequence { doc /* étapes */ part participants; }".

R-SQ2: NE PAS utiliser "message", "event occurrence", "from", "to".
        SysON ne rend pas les diagrammes de séquence.

R-SQ3: Décrire les étapes du scénario dans le doc /* ... */ de manière numérotée.

R-SQ4: Les participants sont des "part nomParticipant;" simples (sans type).

R-SQ5: Les types de messages échangés sont des "item def NomMessage;" au niveau package.

R-SQ6: Noms en CamelCase ASCII."""

_TEMPLATE_MODES = """\
=== TEMPLATE DE SYNTAXE : OPERATING MODES (compatible SysON) ===

package 'SystemName - Operating Modes' {

    attribute def PowerOnSignal;
    attribute def PowerOffSignal;
    attribute def StartOperationSignal;
    attribute def StopOperationSignal;

    action def MonitorSystem;
    action def NominalOperation;
    action def PerformSelfTest;

    state def SystemModes {
        entry; then ModeOff;

        state ModeOff;
        transition PowerOn
            first ModeOff
            accept PowerOnSignal
            then ModeOn;

        state ModeOn {
            entry; then Standby;

            state Standby {
                entry action : MonitorSystem;
            }
            transition StartOp
                first Standby
                accept StartOperationSignal
                then Operating;

            state Operating {
                entry action : PerformSelfTest;
                do action : NominalOperation;
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

_RULES_MODES = """\
=== RÈGLES DE SYNTAXE SPÉCIFIQUES : OPERATING MODES ===

R-MD1: Noms d'états en CamelCase ASCII : ModeOff, ModeOn, Standby, EnFonctionnement

R-MD2: Les actions sont des "action def NomAction;" au niveau package.

R-MD3: Référence aux actions dans les états : "entry action : NomAction;" ou "do action : NomAction;"
       JAMAIS "do 'Nom Avec Espaces';"

R-MD4: Les signaux de transition sont des "attribute def NomSignal;" en CamelCase.

R-MD5: Les transitions : "transition NomTransition first Source accept Signal then Cible;"

R-MD6: Les états composites ont leur propre "entry; then PremierSousEtat;" """


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
# FONCTIONS SysML v2 — 5 prompts spécialisés par type de diagramme
# ============================================================================

def _build_sysml_prompt(
    diagram_type: str,
    role_suffix: str,
    template: str,
    rules: str,
    filtered_json: dict,
    rag_examples: Optional[List[str]] = None,
) -> str:
    """
    Construit un prompt SysML v2 pour un type de diagramme donné.

    Structure en 8 blocs :
      1. Rôle
      2. Fidélité SysML
      3. Règles SysON
      4. Template de syntaxe
      5. Règles spécifiques
      6. Données JSON
      7. Exemples RAG (optionnel)
      8. Instruction finale

    Args:
        diagram_type: nom du type de diagramme (ex: "Lifecycle")
        role_suffix: complément de rôle spécifique
        template: template de syntaxe validé SysON
        rules: règles spécifiques au diagramme
        filtered_json: sous-ensemble du JSON pertinent
        rag_examples: exemples RAG (optionnel)

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
    parts.append(_SYSML_FIDELITY_BLOCK)

    # --- BLOC 3 : RÈGLES DE COMPATIBILITÉ SysON ---
    parts.append(_SYSON_RULES_BLOCK)

    # --- BLOC 4 : TEMPLATE DE SYNTAXE ---
    parts.append(
        "Voici la syntaxe SysML v2 correcte et compatible SysON pour ce type de diagramme.\n"
        "Tu DOIS utiliser EXACTEMENT ces constructs. Ne PAS inventer d'autre syntaxe.\n\n"
        f"{template}"
    )

    # --- BLOC 5 : RÈGLES DE SYNTAXE SPÉCIFIQUES ---
    parts.append(rules)

    # --- BLOC 6 : DONNÉES À TRADUIRE ---
    json_str = json.dumps(filtered_json, indent=2, ensure_ascii=False)
    parts.append(
        "=== DONNÉES DU MODÈLE JSON À TRADUIRE ===\n\n"
        "Traduis UNIQUEMENT ces données. N'ajoute rien.\n\n"
        f"{json_str}"
    )

    # --- BLOC 7 : EXEMPLES RAG (optionnel) ---
    if rag_examples:
        rag_lines = ["=== EXEMPLES DE SYNTAXE SysML v2 POUR RÉFÉRENCE ==="]
        for i, example in enumerate(rag_examples[:3], 1):
            rag_lines.append(f"\nExemple {i}:\n{example}")
        parts.append("\n".join(rag_lines))

    # --- BLOC 8 : INSTRUCTION FINALE ---
    instruction = _SYSML_FINAL_INSTRUCTION.format(
        system_name=system_name,
        diagram_type=diagram_type,
    )
    parts.append(instruction)

    return "\n\n".join(parts)


# ---- Prompt 1 : Lifecycle ------------------------------------------------

def build_lifecycle_sysml_prompt(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
) -> str:
    """Construit le prompt SysML v2 pour le diagramme Lifecycle."""
    filtered = {
        "system_name": model_json.get("system_name", "System"),
        "lifecycle_phases": model_json.get("lifecycle_phases", []),
    }
    return _build_sysml_prompt(
        diagram_type="Lifecycle",
        role_suffix="Tu modélises les phases de vie du système avec des state def et des transitions.",
        template=_TEMPLATE_LIFECYCLE,
        rules=_RULES_LIFECYCLE,
        filtered_json=filtered,
        rag_examples=rag_examples,
    )


# ---- Prompt 2 : Use Cases ------------------------------------------------

def build_usecase_sysml_prompt(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
) -> str:
    """Construit le prompt SysML v2 pour le diagramme Use Cases."""
    filtered = {
        "system_name": model_json.get("system_name", "System"),
        "stakeholders": model_json.get("stakeholders", []),
        "use_cases": model_json.get("use_cases", []),
    }
    return _build_sysml_prompt(
        diagram_type="Use Cases",
        role_suffix="Tu modélises les cas d'utilisation avec les acteurs, sujets et objectifs.",
        template=_TEMPLATE_USECASES,
        rules=_RULES_USECASES,
        filtered_json=filtered,
        rag_examples=rag_examples,
    )


# ---- Prompt 3 : Context --------------------------------------------------

def build_context_sysml_prompt(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
) -> str:
    """Construit le prompt SysML v2 pour le diagramme de contexte."""
    filtered = {
        "system_name": model_json.get("system_name", "System"),
        "external_interfaces": model_json.get("external_interfaces", []),
        "stakeholders": [
            s for s in model_json.get("stakeholders", [])
            if s.get("type") in ("system", "external")
        ],
    }
    return _build_sysml_prompt(
        diagram_type="Context",
        role_suffix="Tu modélises le système dans son environnement avec ports et parts instanciés.",
        template=_TEMPLATE_CONTEXT,
        rules=_RULES_CONTEXT,
        filtered_json=filtered,
        rag_examples=rag_examples,
    )


# ---- Prompt 4 : Operational Sequences ------------------------------------

def build_sequence_sysml_prompt(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
) -> str:
    """Construit le prompt SysML v2 pour les séquences opérationnelles."""
    filtered = {
        "system_name": model_json.get("system_name", "System"),
        "operational_scenarios": model_json.get("operational_scenarios", []),
    }
    return _build_sysml_prompt(
        diagram_type="Operational Sequences",
        role_suffix="Tu modélises les scénarios opérationnels avec des occurrence def et participants.",
        template=_TEMPLATE_SEQUENCES,
        rules=_RULES_SEQUENCES,
        filtered_json=filtered,
        rag_examples=rag_examples,
    )


# ---- Prompt 5 : Operating Modes ------------------------------------------

def build_modes_sysml_prompt(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
) -> str:
    """Construit le prompt SysML v2 pour les modes de fonctionnement."""
    filtered = {
        "system_name": model_json.get("system_name", "System"),
        "operating_modes": model_json.get("operating_modes", []),
    }
    return _build_sysml_prompt(
        diagram_type="Operating Modes",
        role_suffix="Tu modélises la machine à états des modes opérationnels avec transitions.",
        template=_TEMPLATE_MODES,
        rules=_RULES_MODES,
        filtered_json=filtered,
        rag_examples=rag_examples,
    )


# ============================================================================
# Fonction utilitaire — appelle les 5 prompts
# ============================================================================

OPERATIONAL_DIAGRAMS = [
    ("lifecycle", build_lifecycle_sysml_prompt),
    ("use_cases", build_usecase_sysml_prompt),
    ("context", build_context_sysml_prompt),
    ("sequences", build_sequence_sysml_prompt),
    ("modes", build_modes_sysml_prompt),
]


def get_operational_sysml_prompts(
    model_json: dict,
    rag_examples: Optional[List[str]] = None,
) -> list:
    """
    Retourne une liste de (diagram_type, prompt_text) pour les 5 diagrammes opérationnels.

    Args:
        model_json: le modèle JSON opérationnel (dict, pas string)
        rag_examples: exemples SysML v2 du RAG (optionnel)

    Returns:
        Liste de tuples (diagram_type: str, prompt: str)
    """
    results = []
    for diagram_type, build_fn in OPERATIONAL_DIAGRAMS:
        prompt = build_fn(model_json, rag_examples)
        results.append((diagram_type, prompt))
    return results
