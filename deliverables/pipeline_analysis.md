# Analyse Exhaustive du Pipeline SysML v2 Agent

> Document généré le 2026-02-25. Destiné à un assistant IA souhaitant modifier ou améliorer le pipeline de génération SysML v2.

---

## Table des matières

1. [Vue d'ensemble du pipeline](#1-vue-densemble-du-pipeline)
2. [Pipeline V1 — sysml_service.py](#2-pipeline-v1--sysml_servicepy)
3. [Pipeline V2 — level_service.py](#3-pipeline-v2--level_servicepy)
4. [Service RAG — rag_service.py](#4-service-rag--rag_servicepy)
5. [Service LLM — llm_factory.py + llm_gemini.py](#5-service-llm--llm_factorypy--llm_geminipy)
6. [Validation — sysml_validator.py + fidelity_checker.py](#6-validation--sysml_validatorpy--fidelity_checkerpy)
7. [Diagrammes — diagram_service.py](#7-diagrammes--diagram_servicepy)
8. [Intégration SysON — syson_service.py](#8-intégration-syson--syson_servicepy)
9. [Gestion des sessions — state_service.py](#9-gestion-des-sessions--state_servicepy)
10. [API Endpoints — main.py](#10-api-endpoints--mainpy)
11. [Frontend — frontend/app.py](#11-frontend--frontendapppy)
12. [Schémas Pydantic — models/schemas.py](#12-schémas-pydantic--modelsschemasy)
13. [Configuration — config.py](#13-configuration--configpy)

---

## 1. Vue d'ensemble du pipeline

```
PIPELINE V1 (linéaire — sysml_service.py)
==========================================

Description NL
    │
    ▼  RAG.search(description, top_k=3)
    │  → exemples SysML v2 pertinents
    ▼
[Étape 1] LLM(build_json_prompt) → JSON SystemModel
    │  température=0.05, max_tokens=4096
    │  Validation Pydantic → SystemModel
    │  FidelityChecker.check() → retry si non fidèle
    ▼
[Étape 2] LLM(build_sysml_prompt) → Code SysML v2
    │  température=0.05, max_tokens=8192
    │  Nettoyage du code (strip markdown)
    ▼
session.save() → {system_model, sysml_code}
    ▼
Réponse: {session_id, system_model, sysml_code, rag_sources}


PIPELINE V2 (MBSE 4 niveaux — level_service.py)
=================================================

Description NL
    │
    ▼
[OPERATIONAL]                [FUNCTIONAL]               [LOGICAL]               [TECHNICAL]
build_operational_json_prompt → LLM → JSON   →   build_functional_json_prompt → LLM → JSON   →   build_logical_json_prompt → LLM → JSON   →   build_technical_json_prompt → LLM → JSON
    │  temp=0.05, max=65536         │  Contexte = modèle opérationnel             │  Contexte = modèle fonctionnel              │  Contexte = modèle logique
    │  response_mime_type=app/json  │  temp=0.05, max=65536                       │  temp=0.05, max=65536                       │  temp=0.05, max=65536
    ▼                               ▼                                              ▼                                             ▼
build_operational_sysml_prompt → LLM → SysML  →  build_functional_sysml_prompt → LLM → SysML  →  build_logical_sysml_prompt → LLM → SysML  →  build_technical_sysml_prompt → LLM → SysML
    │  temp=0.05, max=8192                                                                                                                         │
    ▼                                                                                                                                              ▼
SysMLv2Validator.validate() à chaque niveau                                                                               Code SysML v2 complet = concat des 4 niveaux
    ▼
state.save_level() → {level, model, sysml_code, llm_warnings, validation_result}

Prérequis : chaque niveau doit être VALIDÉ (validate_level) avant de passer au suivant.
```

---

## 2. Pipeline V1 — `sysml_service.py`

### 2.1 Flux d'appels

```
SysMLService.generate(description, session_id, use_rag)
│
├── state.create_session()                        → session_id (UUID)
│
├── rag.search(description, top_k=3)              → [(content, source_file, score), ...]
│
├── build_json_prompt(description, rag_examples, correction_feedback=None)
│     → prompt_string
│
├── llm.generate(prompt, temperature=0.05, max_tokens=4096)
│     → json_response_string
│
├── _parse_json_response(json_response_string)
│     → dict Python
│     Gestion : strip markdown (```json), find("{"), rfind("}")
│     En cas d'échec : retry avec prompt + "ATTENTION : JSON invalide"
│
├── SystemModel(**system_model_dict)             → validation Pydantic
│
├── fidelity_checker.check(description, system_model_dict)
│     → {"is_faithful": bool, "missing_components": [], "extra_components": [], "warnings": []}
│     Si non fidèle :
│       └── build_json_prompt(description, rag_examples, correction_feedback=feedback)
│             → llm.generate() → parse → re-vérifier fidélité → ajouter warnings si persiste
│
├── build_sysml_prompt(system_model_json, rag_examples)
│     → prompt_string
│
├── llm.generate(prompt, temperature=0.05, max_tokens=8192)
│     → sysml_response_string
│
├── _clean_sysml_code(sysml_response_string)
│     → sysml_code (strip ```sysml et ```)
│
└── state.save_session(session_id, {system_model: dict, sysml_code: str})
      state.add_to_history(session_id, {action: "generate", description: ...})

Retourne: {session_id, system_model: SystemModel, sysml_code: str, rag_sources: [str]}
```

### 2.2 Méthode `patch` (V1)

```
SysMLService.patch(session_id, instruction, use_rag)
│
├── state.load_session(session_id)                → session_data avec system_model
│
├── build_patch_prompt(current_model_json, instruction)
│     → prompt_string
│
├── llm.generate(prompt, temperature=0.05, max_tokens=4096)
│
├── _parse_json_response()                        → patched_model_dict
│
├── SystemModel(**patched_model_dict)             → validation Pydantic
│
├── build_sysml_prompt(patched_model_json, rag_examples=[])
│
├── llm.generate(sysml_prompt, temperature=0.05, max_tokens=8192)
│
└── state.save_session() + add_to_history({action: "patch", instruction: ...})

Retourne: {session_id, system_model, sysml_code, changes_summary}
```

### 2.3 Prompt JSON V1 — `build_json_prompt` (code intégral)

```
Tu es un traducteur fidèle. Tu traduis des descriptions de systèmes en JSON structuré. Tu ne conçois PAS, tu TRADUIS.

=== RÈGLES DE FIDÉLITÉ (CRITIQUE) ===
- Tu ne dois RIEN inventer qui n'est pas explicitement décrit
- Tu ne dois RIEN ajouter (pas de composants, ports, connexions non mentionnés)
- Tu ne dois RIEN corriger silencieusement
- Si quelque chose est ambigu ou incohérent, ajoute un warning dans le champ "warnings"
- Utilise le vocabulaire exact de l'utilisateur pour les noms (ne traduis pas, ne reformule pas)
- Si un port n'a pas de direction explicite, utilise "inout" par défaut

=== MÉTHODOLOGIE (OBLIGATOIRE) ===
1. LISTE EXHAUSTIVE : Avant de générer le JSON, fais la liste de TOUS les composants mentionnés dans la description. Chaque composant de cette liste DOIT apparaître dans le JSON.
2. COMPTAGE : Si la description mentionne N composants, ton JSON DOIT contenir exactement N parts (ni plus, ni moins).
3. VÉRIFICATION : Après avoir généré le JSON, relis la description et vérifie que CHAQUE composant, CHAQUE connexion, CHAQUE flux mentionné est bien présent dans ton JSON.

=== SCHÉMA JSON ATTENDU ===
{
  "system_name": "string",
  "description": "string",
  "warnings": ["string"],
  "parts": [
    {
      "name": "string",
      "type": "string (optionnel)",
      "description": "string (optionnel)",
      "ports": [
        {
          "name": "string",
          "direction": "in | out | inout",
          "type": "string"
        }
      ],
      "children": []
    }
  ],
  "connections": [
    {
      "from_port": "PartName.portName",
      "to_port": "PartName.portName",
      "type": "flow | connection | interface",
      "item": "string (optionnel)",
      "description": "string (optionnel)"
    }
  ],
  "requirements": [
    {
      "id": "string",
      "text": "string",
      "satisfied_by": "string (optionnel)"
    }
  ],
  "use_cases": [
    {
      "name": "string",
      "actors": ["string"],
      "includes": ["string (optionnel)"]
    }
  ]
}

=== RÈGLES POUR LES CONNEXIONS ===
- "flow" : pour les flux de données/informations
- "connection" : pour les connexions structurelles/physiques
- "interface" : pour les interfaces de communication
- Le champ "from_port" doit être au format "NomDuComposant.nomDuPort"
- Le champ "to_port" doit être au format "NomDuComposant.nomDuPort"

[si correction_feedback] === CORRECTION REQUISE ===
Un vérificateur automatique a détecté les problèmes suivants...

[si rag_examples] === EXEMPLES DE SYSTÈMES SYSML V2 ===
--- Exemple 1 --- ...

=== INSTRUCTION ===
Traduis cette description en JSON. Retourne UNIQUEMENT le JSON, sans markdown, sans explication, sans ```json.

=== DESCRIPTION À TRADUIRE ===
{description}
```

### 2.4 Prompt SysML V1 — `build_sysml_prompt` (code intégral)

```
Tu es un générateur de code SysML v2 conforme au standard OMG. Tu transformes un modèle JSON en code SysML v2 syntaxiquement valide.

=== RÈGLES SYNTAXIQUES STRICTES ===

1. DÉFINITIONS ET INSTANCES :
   - Utilise "part def NomDuType" pour les définitions de types
   - Utilise "part nomInstance : NomDuType" pour les instances
   - Si pas de type spécifié, juste "part nomInstance"

2. PORTS :
   - Utilise "port def NomPortType { in item TypeDonnée; }" pour les ports d'entrée
   - Utilise "port def NomPortType { out item TypeDonnée; }" pour les ports de sortie
   - Utilise "port nomPort : NomPortType;" dans les parts

3. CONNEXIONS :
   - Pour les flux : "flow nomFlux from composant1.port1 to composant2.port2;"
   - Pour les connexions structurelles : "connect composant1.port1 to composant2.port2;"
   - Pour les interfaces : "interface nomInterface connect composant1.port1 to composant2.port2;"

4. EXIGENCES :
   - Utilise "requirement def IdExigence { doc /* texte */ }"
   - Utilise "satisfy requirement IdExigence by NomComposant;"

5. CAS D'UTILISATION :
   - Utilise "use case def NomCasUsage { actor nomActeur; include use case autreCas; }"

6. ORGANISATION :
   - Tout doit être dans un "package NomDuSystème { }"
   - Les noms avec espaces doivent être entre guillemets simples : 'Nom Avec Espaces'
   - Les commentaires utilisent doc /* ... */ ou // ...

7. BONNES PRATIQUES :
   - Groupe les définitions ensemble (part def, port def, requirement def)
   - Puis les instances
   - Puis les connexions
   - Utilise l'indentation pour la lisibilité

[si rag_examples] === EXEMPLES DE CODE SYSML V2 VALIDE ===
...

=== INSTRUCTION ===
Génère le code SysML v2 pour ce modèle. Retourne UNIQUEMENT le code SysML v2, sans markdown, sans explication, sans ```sysml.

=== MODÈLE JSON À TRANSFORMER ===
{system_model_json}
```

### 2.5 Prompt PATCH V1 — `build_patch_prompt` (code intégral)

```
Tu modifies un modèle JSON existant selon une instruction utilisateur.

=== RÈGLES STRICTES ===
1. Applique UNIQUEMENT la modification demandée dans l'instruction
2. Ne supprime RIEN qui n'est pas explicitement demandé
3. Ne modifie RIEN qui n'est pas concerné par l'instruction
4. Conserve toute la structure existante intacte
5. Retourne le JSON COMPLET mis à jour (pas juste la partie modifiée)
6. Si tu ajoutes un composant, ajoute-le aussi dans les connexions si pertinent
7. Si tu ajoutes une connexion, vérifie que les ports existent ou crée-les

=== TYPES DE CONNEXIONS VALIDES ===
- "flow" : pour les flux de données/informations/énergie
- "connection" : pour les connexions structurelles/physiques
- "interface" : pour les interfaces de communication
IMPORTANT : Utilise "flow" pour les alimentations électriques (batterie → composants).

=== EXEMPLES DE MODIFICATIONS ===
- "Ajouter une batterie" → Ajoute un part "batterie" dans parts[]
- "Ajouter une batterie qui alimente le moteur" → Ajoute le part ET la connexion avec type "flow"
- "Renommer le GPS en Capteur GPS" → Change le name dans le part existant
- "Supprimer le moteur" → Retire le part ET toutes les connexions liées
- "Changer la connexion entre A et B en interface" → Modifie le type de la connexion

=== MODÈLE JSON ACTUEL ===
{current_model_json}

=== INSTRUCTION DE MODIFICATION ===
{instruction}

=== RÉSULTAT ATTENDU ===
Retourne UNIQUEMENT le JSON complet modifié, sans markdown, sans explication, sans ```json.
N'oublie pas : les connexions doivent avoir type "flow", "connection" ou "interface" uniquement.
```

### 2.6 Schéma JSON V1 — `SystemModel`

```json
{
  "system_name": "string",
  "description": "string",
  "warnings": ["string"],
  "parts": [
    {
      "name": "string",
      "type": "string | null",
      "description": "string | null",
      "ports": [
        {
          "name": "string",
          "direction": "in | out | inout",
          "type": "string"
        }
      ],
      "children": [/* PartSchema récursif */]
    }
  ],
  "connections": [
    {
      "from_port": "PartName.portName",
      "to_port": "PartName.portName",
      "type": "flow | connection | interface",
      "item": "string | null",
      "description": "string | null"
    }
  ],
  "requirements": [
    {
      "id": "string",
      "text": "string",
      "satisfied_by": "string | null"
    }
  ],
  "use_cases": [
    {
      "name": "string",
      "actors": ["string"],
      "includes": ["string"] | null
    }
  ]
}
```

---

## 3. Pipeline V2 — `level_service.py`

### 3.1 Ordre des niveaux et prérequis

```
NIVEAUX_ORDER = ["operational", "functional", "logical", "technical"]

Règle de prérequis :
- operational : aucun prérequis
- functional   : operational doit être validated=True
- logical      : functional doit être validated=True
- technical    : logical doit être validated=True
```

### 3.2 Flux complet de `generate_level`

```
LevelService.generate_level(description, level, session_id, session_name, use_rag)
│
├── Validation du niveau (doit être dans NIVEAUX_ORDER)
│
├── Si session_id is None :
│     state.create_session()
│     state.init_session_with_levels(session_id, description, session_name)
│
├── Vérification prérequis (si level != "operational") :
│     state.get_level(session_id, prev_level)
│     Si prev_level.validated == False → raise ValueError
│
├── previous_data = state.get_previous_level_data(session_id, level)
│     → Données du niveau précédent (ou None pour operational)
│
├── RAG : rag.search(description, top_k=8) → rag_examples, rag_sources
│
├── ÉTAPE 1 : _generate_json_for_level(level, description, previous_data, rag_examples)
│     │
│     ├── build_{level}_json_prompt(description, prev_model, rag_examples, correction_feedback)
│     ├── llm.generate(prompt, temperature=0.05, max_tokens=65536, response_mime_type="application/json")
│     ├── state.save_exchange(session_id, exchange)  ← traçabilité complète
│     └── json.loads(response) → json_model : dict
│
├── FidelityChecker (UNIQUEMENT pour logical et technical) :
│     fidelity_checker.check(description, json_model)
│     Si non fidèle :
│       └── retry avec correction_feedback → re-vérification → ajout warnings si persiste
│
├── ÉTAPE 2 : _generate_sysml_for_level(level, json_model, rag_examples)
│     │
│     ├── json.dumps(json_model) → json_str
│     ├── build_{level}_sysml_prompt(json_str, rag_examples)
│     ├── llm.generate(prompt, temperature=0.05, max_tokens=8192)
│     ├── nettoyage (strip ```sysml)
│     └── state.save_exchange(session_id, exchange)  ← traçabilité complète
│
├── Validation syntaxique : SysMLv2Validator.validate(sysml_code)
│     → validation_result {valid, score, errors, warnings, info, summary}
│
├── Filtrage des warnings dupliqués (comparaison avec niveau précédent)
│
├── Extraction et mise à jour system_name (pour operational uniquement)
│
└── state.save_level(session_id, level, level_data)
      → {level, model, sysml_code, llm_warnings, validation_result, diagrams:[], validated:False, history:[...]}

Retourne: {session_id, level, model, sysml_code, llm_warnings, validation_result, rag_sources, warnings, available_diagrams}
```

### 3.3 Diagrammes disponibles par niveau

```python
DIAGRAMMES_PAR_NIVEAU = {
    "operational": ["context", "use_cases", "actors_diagram", "operational_sequence"],
    "functional":  ["functional_breakdown", "functional_behavior", "modes_diagram"],
    "logical":     ["bdd", "ibd"],
    "technical":   ["technical_architecture"]
}
```

---

## 4. Niveau OPÉRATIONNEL

### 4.1 Prompt JSON Opérationnel — `build_operational_json_prompt` (code intégral)

```
Tu es un ingénieur système expert en analyse opérationnelle. Tu analyses une description pour identifier le périmètre opérationnel du système.

=== TON RÔLE ===
- Tu identifies QUI utilise le système (stakeholders, acteurs)
- Tu identifies AVEC QUOI le système interagit (systèmes externes)
- Tu définis le PÉRIMÈTRE du système (ce qui est dedans, ce qui est dehors)
- Tu extrais les CAS D'UTILISATION (use cases)
- Tu identifies les SCÉNARIOS OPÉRATIONNELS (séquences d'interactions)
- Tu formules les BESOINS OPÉRATIONNELS (requirements de haut niveau)

=== RÈGLES DE FIDÉLITÉ (CRITIQUE) ===
- Tu ne dois RIEN inventer qui n'est pas explicitement décrit
- Tu ne dois RIEN ajouter qui n'est pas mentionné
- Si quelque chose est ambigu ou incohérent, ajoute un warning dans le champ "warnings"
- Utilise le vocabulaire exact de l'utilisateur pour les noms
- Si un élément n'est pas clair, marque-le avec un warning
- L'exemple ci-dessous montre uniquement la STRUCTURE attendue. En production, chaque valeur doit provenir EXCLUSIVEMENT de la description fournie par l'utilisateur.
- DISTINCTION STAKEHOLDER / SYSTÈME EXTERNE (P4+P5) : Un stakeholder est soit une PERSONNE/ORGANISATION, soit un SYSTÈME TECHNIQUE qui est ACTEUR dans un cas d'utilisation (c'est-à-dire qui initie des interactions, envoie des commandes, ou reçoit activement des services). En revanche, une frontière physique passive est un external_system. Règle : si une entité est nommée comme acteur dans un use case → "stakeholders". Si frontière passive → "external_systems". Le champ "stakeholders" ne doit JAMAIS être vide si des entités interagissent.
- RÈGLE P5 — FORMAT STAKEHOLDERS : Les stakeholders peuvent être des chaînes ou des objets {"name": "...", "role": "...", "type": "human|system|organization"}.
- PÉRIMÈTRE DU SYSTÈME : Un composant interrogé via réseau ou protocole est un système externe. Un composant physique installé sur site et contrôlé directement est INTERNE.
- EXIGENCES = CONTRAINTES MESURABLES UNIQUEMENT : Ne génère des requirements QUE pour des contraintes explicitement chiffrées ou mesurables (temps de réponse, disponibilité, capacité, température, etc.).
- RÈGLE P8 — DÉCOMPOSITION DES USE CASES : Si un use case est "Fournir/Envoyer X à Y" et que la description mentionne PLUSIEURS destinations distinctes, décompose en sous-use cases séparés par destination.

=== MÉTHODOLOGIE (OBLIGATOIRE) ===
1. IDENTIFICATION : Liste tous les acteurs, systèmes externes et cas d'utilisation mentionnés
2. PÉRIMÈTRE : Définis clairement ce qui est dans le système et ce qui est externe
3. SCÉNARIOS : Pour chaque use case, identifie les étapes principales
4. BESOINS : Formule les besoins opérationnels à partir des use cases
5. VÉRIFICATION : Relis la description et vérifie que tout est bien capturé

=== SCHÉMA JSON ATTENDU (OperationalModel) ===
{
  "system_name": "string",
  "description": "string",
  "warnings": ["string"],
  "stakeholders": [
    {"name": "string", "role": "string", "type": "human|system|organization"}
  ],
  "external_systems": ["string"],
  "system_boundaries": "string",
  "use_cases": [
    {
      "name": "string",
      "actors": ["string"],
      "includes": ["string"]
    }
  ],
  "operational_scenarios": [
    {
      "name": "string",
      "description": "string",
      "steps": ["string"]
    }
  ],
  "requirements": [
    {
      "id": "string (ex: REQ-OP-001)",
      "text": "string",
      "satisfied_by": null
    }
  ]
}

=== EXEMPLE DE STRUCTURE (placeholders) ===
[structure exemple avec des valeurs génériques montrant uniquement le format]

[si rag_examples] === EXEMPLES DE SYNTAXE SysML v2 POUR RÉFÉRENCE ===
...

[si correction_feedback] === CORRECTION REQUISE ===
...

=== DESCRIPTION À ANALYSER ===
{description}

=== TON RÉSULTAT (JSON UNIQUEMENT, SANS COMMENTAIRE) ===
```

### 4.2 Schéma JSON opérationnel (OperationalModel)

```json
{
  "system_name": "string",
  "description": "string",
  "warnings": ["string"],
  "stakeholders": [
    {
      "name": "string",
      "role": "string",
      "type": "human | system | organization"
    }
  ],
  "external_systems": ["string"],
  "system_boundaries": "string",
  "use_cases": [
    {
      "name": "string",
      "actors": ["string"],
      "includes": ["string"]
    }
  ],
  "operational_scenarios": [
    {
      "name": "string",
      "description": "string",
      "steps": ["string"]
    }
  ],
  "requirements": [
    {
      "id": "REQ-OP-001",
      "text": "string",
      "satisfied_by": null
    }
  ]
}
```

### 4.3 Prompt SysML Opérationnel — `build_operational_sysml_prompt` (code intégral)

```
Tu es un expert SysML v2. Tu traduis un modèle opérationnel JSON en code SysML v2 valide.

=== TON RÔLE ===
Génère du code SysML v2 pour le NIVEAU OPÉRATIONNEL qui inclut :
1. Un package pour le niveau opérationnel
2. Les use case definitions
3. Les requirement definitions pour les besoins opérationnels
4. Les action definitions pour les scénarios opérationnels

=== RÈGLES DE SYNTAXE SysML v2 ===
- use case def NomDuUseCase { ... }
- requirement def NomDeLExigence { ... }
- action def NomDuScenario { ... }
- Les noms doivent respecter la casse CamelCase ou snake_case
- Utilise des commentaires /* ... */ pour les descriptions

=== STRUCTURE ATTENDUE ===
```sysml
package '{SystemName} - Operational' {
    use case def {UseCase1} {
        doc /* Description du use case */
        actor {Actor1};
    }
    requirement def {RequirementId} {
        doc /* Texte de l'exigence */
    }
    action def {Scenario1} {
        doc /* Description du scénario */
    }
}
```

=== EXEMPLE ===
```sysml
package 'Drone Surveillance - Operational' {
    use case def SurveillerZone {
        doc /* L'opérateur surveille une zone avec le drone */
        actor Operateur;
    }
    requirement def REQ_OP_001 {
        doc /* Le système doit permettre de surveiller une zone définie */
    }
    action def MissionSurveillance {
        doc /* Scénario nominal d'une mission de surveillance */
    }
}
```

[si rag_examples] === EXEMPLES DE CODE SysML v2 ===
...

=== MODÈLE OPÉRATIONNEL JSON ===
{operational_json}

=== TON RÉSULTAT (CODE SysML v2 UNIQUEMENT, SANS COMMENTAIRE) ===
```

### 4.4 Concepts SysML v2 générés au niveau opérationnel

- `package '{SystemName} - Operational' { ... }`
- `use case def NomUseCase { actor ...; }`
- `requirement def REQ_OP_xxx { doc /* ... */ }`
- `action def NomScenario { doc /* ... */ }`

---

## 5. Niveau FONCTIONNEL

### 5.1 Prompt JSON Fonctionnel — `build_functional_json_prompt` (code intégral)

```
Tu es un ingénieur système expert en analyse fonctionnelle. Tu décomposes les cas d'utilisation en fonctions.

=== TON RÔLE ===
À partir du modèle OPÉRATIONNEL validé, tu identifies :
- Les FONCTIONS que le système doit réaliser (QUE FAIT le système)
- Les FLUX FONCTIONNELS entre ces fonctions (échanges d'informations, d'énergie, de matière)
- Les MODES OPÉRATOIRES (configurations où certaines fonctions sont actives)

=== RÈGLES DE TRAÇABILITÉ ===
- Chaque USE CASE du niveau opérationnel doit être couvert par au moins UNE FONCTION
- Les fonctions peuvent avoir des sous-fonctions (hiérarchie)
- Les flux fonctionnels représentent les échanges entre fonctions
- Les modes permettent de décrire différentes configurations opérationnelles

=== RÈGLES DE FIDÉLITÉ ===
- Tu ne dois RIEN inventer qui ne découle pas du niveau opérationnel
- Chaque fonction doit être justifiable par un ou plusieurs use cases
- Si quelque chose est ambigu, ajoute un warning
- RÈGLE P6 — TYPING DES FLUX (OBLIGATOIRE) : Chaque flux dans "functional_flows" DOIT avoir un champ "flow_type" avec une des valeurs : "pneumatic", "information", "electric", "thermal", "mechanical".
- RÈGLE P7 — NOTATION COMPOSANT::FONCTION (si applicable) : Si une sous-fonction est clairement réalisée par un composant physique nommé dans la description, nomme-la avec le format "NomComposant::NomFonction".

=== MÉTHODOLOGIE ===
1. ANALYSE : Pour chaque use case, identifie les fonctions nécessaires
2. DÉCOMPOSITION : Décompose les fonctions complexes en sous-fonctions
3. FLUX : Identifie les échanges entre fonctions (données, énergie, matière)
4. MODES : Regroupe les fonctions par modes opératoires (nominal, dégradé, maintenance, etc.)
5. VÉRIFICATION : Vérifie que tous les use cases sont couverts

=== SCHÉMA JSON ATTENDU (FunctionalModel) ===
{
  "system_name": "string",
  "warnings": ["string"],
  "functions": [
    {
      "name": "string",
      "description": "string",
      "inputs": ["string"],
      "outputs": ["string"],
      "sub_functions": ["string"]
    }
  ],
  "functional_flows": [
    {
      "from_function": "string",
      "to_function": "string",
      "item": "string",
      "flow_type": "pneumatic|information|electric|thermal|mechanical",  // OBLIGATOIRE
      "description": "string"
    }
  ],
  "modes": [
    {
      "name": "string",
      "description": "string",
      "active_functions": ["string"]
    }
  ]
}

=== MODÈLE OPÉRATIONNEL VALIDÉ (CONTEXTE) ===
{operational_json}

[si rag_examples] === EXEMPLES DE SYNTAXE SysML v2 POUR RÉFÉRENCE ===
...

[si correction_feedback] === CORRECTION REQUISE ===
...

[si description non vide] === INSTRUCTIONS SUPPLÉMENTAIRES ===
{description}

=== TON RÉSULTAT (JSON UNIQUEMENT, SANS COMMENTAIRE) ===
```

### 5.2 Schéma JSON fonctionnel (FunctionalModel)

```json
{
  "system_name": "string",
  "warnings": ["string"],
  "functions": [
    {
      "name": "string",
      "description": "string",
      "inputs": ["string"],
      "outputs": ["string"],
      "sub_functions": ["string"]
    }
  ],
  "functional_flows": [
    {
      "from_function": "string",
      "to_function": "string",
      "item": "string",
      "flow_type": "pneumatic | information | electric | thermal | mechanical",
      "description": "string"
    }
  ],
  "modes": [
    {
      "name": "string",
      "description": "string",
      "active_functions": ["string"]
    }
  ]
}
```

### 5.3 Prompt SysML Fonctionnel — `build_functional_sysml_prompt` (code intégral)

```
Tu es un expert SysML v2. Tu traduis un modèle fonctionnel JSON en code SysML v2 valide.

=== TON RÔLE ===
Génère du code SysML v2 pour le NIVEAU FONCTIONNEL qui inclut :
1. Un package pour le niveau fonctionnel
2. Les action definitions pour chaque fonction
3. Les flow connections pour les flux fonctionnels
4. Les state definitions pour les modes

=== RÈGLES DE SYNTAXE SysML v2 ===
- action def NomDeLaFonction { ... }
- flow NomDuFlux from fonction1.output to fonction2.input;
- state def NomDuMode { ... }
- Les actions peuvent contenir des sous-actions

=== STRUCTURE ATTENDUE ===
```sysml
package '{SystemName} - Functional' {
    action def {Function1} {
        doc /* Description de la fonction */
        in {input1} : {Type};
        out {output1} : {Type};
        action {SubFunction1} { ... }
    }
    flow {FlowName} from {Function1}.{output} to {Function2}.{input};
    state def {Mode1} {
        doc /* Description du mode */
    }
}
```

=== EXEMPLE ===
```sysml
package 'Drone Surveillance - Functional' {
    action def PiloterDrone {
        doc /* Contrôler la trajectoire et l'altitude du drone */
        in commandes : CommandesPilotage;
        in position : PositionGPS;
        out commandesMoteur : SignauxMoteur;
        action Stabiliser { ... }
        action Naviguer { ... }
    }
    action def CapturerImages {
        doc /* Acquérir des images vidéo de la zone */
        in declenchement : Signal;
        out images : FluxVideo;
    }
    action def TransmettreImages {
        doc /* Envoyer les images à la station sol */
        in images : FluxVideo;
        out fluxTransmis : FluxVideo;
    }
    flow FluxImages from CapturerImages.images to TransmettreImages.images;
    state def ModeSurveillance {
        doc /* Mode nominal de surveillance */
        entry / PiloterDrone;
        do / CapturerImages;
        do / TransmettreImages;
    }
    state def ModeRetourBase {
        doc /* Retour automatique à la base */
        do / PiloterDrone;
    }
}
```

=== MODÈLE FONCTIONNEL JSON ===
{functional_json}

=== TON RÉSULTAT (CODE SysML v2 UNIQUEMENT, SANS COMMENTAIRE) ===
```

### 5.4 Concepts SysML v2 générés au niveau fonctionnel

- `package '{SystemName} - Functional' { ... }`
- `action def NomFonction { in ...; out ...; action SubFonction { ... } }`
- `flow NomFlux from FonctionA.output to FonctionB.input;`
- `state def NomMode { entry / ...; do / ...; }`

---

## 6. Niveau LOGIQUE

### 6.1 Prompt JSON Logique — `build_logical_json_prompt` (code intégral)

```
Tu es un ingénieur système expert en conception d'architecture logique. Tu conçois l'architecture en composants logiques.

=== TON RÔLE ===
À partir du modèle FONCTIONNEL validé, tu :
- REGROUPES les fonctions en COMPOSANTS LOGIQUES cohérents
- DÉFINIS les PORTS et INTERFACES de chaque composant
- ÉTABLIS les CONNEXIONS entre composants
- ALLOUES les EXIGENCES aux composants

=== RÈGLES DE TRAÇABILITÉ ===
- Chaque FONCTION du niveau fonctionnel doit être ALLOUÉE à un composant logique
- Les FLUX FONCTIONNELS deviennent des CONNEXIONS entre ports de composants
- L'architecture doit être INDÉPENDANTE de la technologie (pas de choix technique)
- Les composants sont définis par leur RÔLE, pas leur implémentation

=== RÈGLES DE COHÉSION ===
- Regroupe les fonctions fortement couplées dans un même composant
- Minimise les connexions entre composants
- Définis des interfaces claires (ports)
- Chaque composant doit avoir une responsabilité cohérente

=== RÈGLES DE FIDÉLITÉ ===
- Tout doit découler du niveau fonctionnel — Pas de composants sans fonction allouée
- COHÉRENCE DES CONNEXIONS (CRITIQUE) : Toute connexion dans "connections" doit lier EXACTEMENT deux composants définis dans "parts". Connexion vers un élément absent de "parts" = STRICTEMENT INTERDIT.
- COMPOSANTS PHYSIQUES INTERNES : Un composant physiquement présent dans le système (caméra, capteur, serrure, actionneur) DOIT apparaître comme un part même s'il a été classé "externe" au niveau opérationnel.
- ALLOCATION OBLIGATOIRE DES EXIGENCES : Si des exigences existent dans les niveaux précédents, les reprendre dans "requirements" avec "satisfied_by" alloué.

=== MÉTHODOLOGIE ===
1. REGROUPEMENT : Identifie les groupes de fonctions cohérents → composants
2. ALLOCATION : Alloue chaque fonction à un composant
3. INTERFACES : Définis les ports d'entrée/sortie de chaque composant
4. CONNEXIONS : Traduis les flux fonctionnels en connexions entre ports
5. EXIGENCES : Alloue les exigences aux composants qui les satisfont
6. VÉRIFICATION : Vérifie que toutes les fonctions sont allouées

=== SCHÉMA JSON ATTENDU (LogicalModel) ===
{
  "system_name": "string",
  "warnings": ["string"],
  "parts": [
    {
      "name": "string",
      "type": "string (optionnel)",
      "description": "string (fonctions allouées)",
      "ports": [
        {
          "name": "string",
          "direction": "in | out | inout",
          "type": "string"
        }
      ],
      "children": []
    }
  ],
  "connections": [
    {
      "from_port": "ComponentA.portOut",
      "to_port": "ComponentB.portIn",
      "type": "flow | connection | interface",
      "item": "string",
      "description": "string"
    }
  ],
  "requirements": [
    {
      "id": "string",
      "text": "string",
      "satisfied_by": "string (nom du composant)"
    }
  ]
}

=== MODÈLE FONCTIONNEL VALIDÉ (CONTEXTE) ===
{functional_json}

[si rag_examples, correction_feedback, description] → ajoutés en fin de prompt

=== TON RÉSULTAT (JSON UNIQUEMENT, SANS COMMENTAIRE) ===
```

### 6.2 Schéma JSON logique (LogicalModel)

```json
{
  "system_name": "string",
  "warnings": ["string"],
  "parts": [
    {
      "name": "string",
      "type": "string | null",
      "description": "string",
      "ports": [
        {
          "name": "string",
          "direction": "in | out | inout",
          "type": "string"
        }
      ],
      "children": [/* PartSchema récursif */]
    }
  ],
  "connections": [
    {
      "from_port": "ComponentA.portOut",
      "to_port": "ComponentB.portIn",
      "type": "flow | connection | interface",
      "item": "string",
      "description": "string"
    }
  ],
  "requirements": [
    {
      "id": "string",
      "text": "string",
      "satisfied_by": "string"
    }
  ]
}
```

### 6.3 Prompt SysML Logique — `build_logical_sysml_prompt` (code intégral)

```
Tu es un expert SysML v2. Tu traduis un modèle logique JSON en code SysML v2 valide.

=== TON RÔLE ===
Génère du code SysML v2 pour le NIVEAU LOGIQUE qui inclut :
1. Un package pour le niveau logique
2. Les part definitions pour chaque composant
3. Les port definitions pour chaque interface
4. Les connections entre ports
5. Les allocations d'exigences

=== RÈGLES DE SYNTAXE SysML v2 ===
- part def NomDuComposant { ... }
- port def NomDuPort : TypeDuPort;
- port NomDuPort : TypeDuPort [direction];
- flow NomDuFlux from partA.portOut to partB.portIn;
- connect partA.portOut to partB.portIn;
- requirement def NomExigence { ... }

=== STRUCTURE ATTENDUE ===
```sysml
package '{SystemName} - Logical' {
    part def {Component1} {
        doc /* Description et fonctions allouées */
        port {port1} : {Type1} [in];
        port {port2} : {Type2} [out];
    }
    part def {Component2} {
        port {port3} : {Type1} [in];
    }
    part {SystemName} {
        part {component1} : {Component1};
        part {component2} : {Component2};
        flow {flowName} from {component1}.{port2} to {component2}.{port3};
    }
    requirement def {Requirement1} {
        doc /* Texte de l'exigence */
        satisfy by {Component1};
    }
}
```

=== EXEMPLE ===
```sysml
package 'Drone Surveillance - Logical' {
    part def ControleurVol {
        doc /* Fonctions : Piloter, Stabiliser, Naviguer */
        port commandes_in : CommandesPilotage [in];
        port moteur_out : SignauxMoteur [out];
    }
    part def SystemeVideo {
        doc /* Fonctions : Capturer, Transmettre */
        port declenchement_in : Signal [in];
        port video_out : FluxVideo [out];
    }
    part DroneSurveillance {
        part controleur : ControleurVol;
        part camera : SystemeVideo;
        flow DeclenchementFlow from controleur.moteur_out to camera.declenchement_in;
    }
    requirement def REQ_LOG_001 {
        doc /* Le contrôleur de vol doit stabiliser le drone */
        satisfy by ControleurVol;
    }
}
```

=== MODÈLE LOGIQUE JSON ===
{logical_json}

=== TON RÉSULTAT (CODE SysML v2 UNIQUEMENT, SANS COMMENTAIRE) ===
```

### 6.4 Concepts SysML v2 générés au niveau logique

- `package '{SystemName} - Logical' { ... }`
- `part def NomComposant { port ...; }`
- `part SystemName { part comp1 : Type1; ... flow ... from ... to ...; }`
- `requirement def REQ_LOG_xxx { satisfy by NomComposant; }`

---

## 7. Niveau TECHNIQUE

### 7.1 Prompt JSON Technique — `build_technical_json_prompt` (code intégral)

```
Tu es un ingénieur système expert en modélisation SysML v2. Tu traduis les choix techniques en modèle structuré.

=== TON RÔLE ===
À partir du modèle LOGIQUE validé et des instructions de l'utilisateur, tu :
- TRADUIS les choix techniques DÉCRITS par l'utilisateur en modèle JSON structuré
- Si l'utilisateur ne mentionne pas de technologie spécifique, utilise des noms GÉNÉRIQUES (ex: ComposantPhysique1) SANS proposer de marque ou modèle
- DÉFINIS les connexions physiques (câbles, bus, réseaux) tels que décrits
- TRACES chaque composant logique vers son équivalent physique

=== RÈGLES DE TRAÇABILITÉ ===
- Chaque COMPOSANT LOGIQUE doit être RÉALISÉ par un ou plusieurs composants techniques
- Les connexions physiques implémentent les connexions logiques

=== RÈGLES DE CONCEPTION ===
- Les noms de composants reflètent ce que l'utilisateur a décrit
- Si l'utilisateur ne spécifie pas d'attributs physiques, omets-les ou mets des valeurs génériques

=== RÈGLES DE FIDÉLITÉ ===
- Tu ne PROPOSES JAMAIS de marque, modèle ou technologie spécifique non mentionnée par l'utilisateur
- Tu RETRANSCRIS uniquement les justifications FOURNIES ; si absentes, utilise "À spécifier par l'architecte"
- Tout doit découler du niveau logique
- Pas de composants techniques sans composant logique correspondant

=== SCHÉMA JSON ATTENDU (TechnicalModel) ===
{
  "system_name": "string",
  "warnings": ["string"],
  "technical_parts": [
    {
      "name": "string",
      "type": "string",
      "description": "string (composant logique réalisé)",
      "ports": [
        {
          "name": "string",
          "direction": "in | out | inout",
          "type": "string (type physique : CAN, I2C, Ethernet, etc.)"
        }
      ],
      "children": []
    }
  ],
  "physical_connections": [
    {
      "from_port": "CompA.portOut",
      "to_port": "CompB.portIn",
      "type": "connection",
      "item": "string (protocole, bus, câble)",
      "description": "string"
    }
  ],
  "technology_choices": [
    {
      "component": "string (nom du composant logique)",
      "technology": "string (nom du composant technique)",
      "justification": "string"
    }
  ]
}

=== MODÈLE LOGIQUE VALIDÉ (CONTEXTE) ===
{logical_json}

[si rag_examples, correction_feedback, description] → ajoutés en fin de prompt

=== TON RÉSULTAT (JSON UNIQUEMENT, SANS COMMENTAIRE) ===
```

### 7.2 Schéma JSON technique (TechnicalModel)

```json
{
  "system_name": "string",
  "warnings": ["string"],
  "technical_parts": [
    {
      "name": "string",
      "type": "string",
      "description": "string",
      "ports": [
        {
          "name": "string",
          "direction": "in | out | inout",
          "type": "string"
        }
      ],
      "children": [/* récursif */]
    }
  ],
  "physical_connections": [
    {
      "from_port": "CompA.portOut",
      "to_port": "CompB.portIn",
      "type": "connection",
      "item": "string",
      "description": "string"
    }
  ],
  "technology_choices": [
    {
      "component": "string",
      "technology": "string",
      "justification": "string"
    }
  ]
}
```

### 7.3 Prompt SysML Technique — `build_technical_sysml_prompt` (code intégral)

```
Tu es un expert SysML v2. Tu traduis un modèle technique JSON en code SysML v2 valide.

=== TON RÔLE ===
Génère du code SysML v2 pour le NIVEAU TECHNIQUE qui inclut :
1. Un package pour le niveau technique
2. Les part definitions pour chaque composant technique
3. Les attributs techniques (specs matérielles)
4. Les connections physiques
5. Les allocations de composants logiques vers techniques

=== RÈGLES DE SYNTAXE SysML v2 ===
- part def NomComposantTechnique { ... }
- attribute nomAttribut : TypeAttribut = valeur;
- port nomPort : TypeProtocole [direction];
- connect partA.portOut to partB.portIn;
- allocation NomLogique to NomTechnique;

=== STRUCTURE ATTENDUE ===
```sysml
package '{SystemName} - Technical' {
    part def {TechnicalComponent1} {
        doc /* Description et composant logique réalisé */
        attribute fabricant : String = "NomFabricant";
        attribute modele : String = "Reference";
        attribute tension : Real = 5.0 [V];
        attribute masse : Real = 0.1 [kg];
        port {port1} : {ProtocolePhysique} [in];
        port {port2} : {ProtocolePhysique} [out];
    }
    part {SystemName}_Physical {
        part {comp1} : {TechnicalComponent1};
        part {comp2} : {TechnicalComponent2};
        connect {comp1}.{port2} to {comp2}.{port1};
    }
    allocation {LogicalComponent} to {TechnicalComponent1};
}
```

=== EXEMPLE ===
```sysml
package '{SystemName} - Technical' {
    part def {NomComposantTechnique} {
        doc /* Réalise le composant logique {NomComposantLogique} */
        port {port_entree} : {ProtocoleDecritParUtilisateur} [in];
        port {port_sortie} : {ProtocoleDecritParUtilisateur} [out];
    }
    part def {AutreComposantTechnique} {
        doc /* Réalise le composant logique {AutreComposantLogique} */
        port {port_entree} : {ProtocoleDecritParUtilisateur} [in];
    }
    part {SystemName}_Physical {
        part composant1 : {NomComposantTechnique};
        part composant2 : {AutreComposantTechnique};
        connect composant1.{port_sortie} to composant2.{port_entree};
    }
    allocation {NomComposantLogique} to {NomComposantTechnique};
    allocation {AutreComposantLogique} to {AutreComposantTechnique};
}
```

=== MODÈLE TECHNIQUE JSON ===
{technical_json}

=== TON RÉSULTAT (CODE SysML v2 UNIQUEMENT, SANS COMMENTAIRE) ===
```

### 7.4 Concepts SysML v2 générés au niveau technique

- `package '{SystemName} - Technical' { ... }`
- `part def NomComposantTechnique { attribute ...; port ...; }`
- `part {SystemName}_Physical { part comp : Type; connect ... to ...; }`
- `allocation NomLogique to NomTechnique;`

---

## 8. Cohérence inter-niveaux — `check_coherence`

La méthode `LevelService.check_coherence(session_id, level)` vérifie :

### FUNCTIONAL → OPERATIONAL
- Pour chaque use case du niveau opérationnel, vérifier qu'au moins 30% des mots significatifs apparaissent dans les noms/descriptions des fonctions
- Si couverture < 30% → warning `"missing_function_for_usecase"`

### LOGICAL → FUNCTIONAL
- Chaque fonction doit être mentionnée dans la description d'au moins un composant logique
  - Si non → warning `"unallocated_function"`
- `len(functional_flows) > len(connections)` → warning `"missing_connections"`

### TECHNICAL → LOGICAL
- Chaque composant logique (part.name) doit apparaître dans la description d'un composant technique
  - Si non → warning `"missing_technical_component"`

---

## 9. Prompt PATCH V2 — inline dans `patch_level`

```
Tu es un expert en modification de modèles SysML. Tu modifies le modèle JSON du niveau {level}.

=== MODÈLE ACTUEL ===
{current_json}

=== INSTRUCTION DE MODIFICATION ===
{instruction}

=== RÈGLES STRICTES ===
1. Applique UNIQUEMENT la modification demandée
2. Ne supprime RIEN qui n'est pas explicitement demandé
3. Ne modifie RIEN qui n'est pas concerné par l'instruction
4. Conserve TOUTES les autres données inchangées
5. Retourne le JSON COMPLET modifié (pas seulement ce qui a changé)

=== FORMAT DE RÉPONSE ===
Retourne le JSON complet du modèle modifié (sans commentaire, juste le JSON).

[si rag_examples] === EXEMPLES DE SYNTAXE ===
Exemple 1: ...
```

---

## 10. Service RAG — `rag_service.py`

### 10.1 Initialisation

```python
RAGService(
    chroma_dir=settings.CHROMA_DIR,          # backend/data/chroma/
    embedding_model=settings.EMBEDDING_MODEL, # "all-MiniLM-L6-v2"
    sysml_repo_path=settings.SYSML_REPO_PATH  # /app/SysML-v2-Release (volume Docker)
)
```

Actions lors de l'init :
1. Crée le répertoire ChromaDB s'il n'existe pas
2. Charge `SentenceTransformer("all-MiniLM-L6-v2")` → modèle d'embeddings
3. Crée `chromadb.PersistentClient(path=chroma_dir)` avec `anonymized_telemetry=False`
4. Récupère ou crée la collection `"sysml_v2_docs"`

### 10.2 Indexation des fichiers

```python
rag.index_sysml_files(force=False)
```

Répertoires scannés :
- `{SYSML_REPO_PATH}/sysml/src/training/**/*.sysml` → catégorie `"training"`
- `{SYSML_REPO_PATH}/sysml/src/examples/**/*.sysml` → catégorie `"example"`

Algorithme de découpe (`_split_sysml_code`) :
1. Découpe le fichier en lignes
2. Identifie les blocs (séquences terminées par une ligne `}` seule)
3. Regroupe les blocs en chunks de ~1500 caractères
4. Overlap de 200 caractères entre chunks

Pour chaque chunk :
- Calcul d'embedding via `SentenceTransformer.encode()`
- Ajout dans ChromaDB avec métadonnées : `{source_file, chunk_index, category}`

Paramètres :
- `chunk_size = 1500`
- `chunk_overlap = 200`

### 10.3 Recherche

```python
rag.search(query, top_k=8)  # top_k=3 en V1, top_k=8 en V2
```

Algorithme :
1. Encode la query : `embedder.encode([query]).tolist()`
2. Requête ChromaDB : `collection.query(query_embeddings=..., n_results=top_k)`
3. Formatage : `score = 1.0 - distance` (distance cosine → score de similarité)

Retourne :
```python
[
    {
        "content": "code SysML v2 du chunk",
        "source_file": "sysml/src/training/...",
        "score": 0.87
    },
    ...
]
```

**Différence V1 vs V2 :**
- V1 : `top_k=3`, utilise `result["source_file"]`
- V2 : `top_k=8`, utilise `result["file"]` (⚠️ clé différente — incohérence dans le code)

### 10.4 Injection dans les prompts

Les exemples RAG sont injectés dans les prompts de la manière suivante :

**Pour les prompts JSON (V2) :**
```
=== EXEMPLES DE SYNTAXE SysML v2 POUR RÉFÉRENCE ===
Ces exemples te donnent des idées de structure, mais tu dois rester fidèle à la description.

Exemple 1:
```
{chunk SysML v2}
```

Exemple 2: ...
Exemple 3: ...
```
(Maximum 3 exemples injectés parmi les top_k récupérés)

**Pour les prompts SysML (V2) :**
```
=== EXEMPLES DE CODE SysML v2 ===
Exemple 1:
```sysml
{chunk SysML v2}
```
...
```

---

## 11. Service LLM — `llm_factory.py` + `llm_gemini.py`

### 11.1 Factory

```python
create_llm(
    provider="gemini",
    api_key=None,        # clé unique (rétrocompat)
    api_keys=None,       # liste de clés pour rotation
    model=None,          # alias de model_name
    model_name=None      # prioritaire
)
```

Logique de construction des clés :
1. `api_keys` fourni → utiliser directement
2. `api_key` fourni avec virgules → split et utiliser comme liste
3. `api_key` simple → liste à 1 élément

Modèle par défaut : `"gemini-2.5-flash"`

### 11.2 Configuration LLM (config.py)

```python
LLM_PROVIDER   = "gemini"          # fournisseur actif
GEMINI_API_KEY  = ""               # clé unique (compat)
GEMINI_API_KEYS = ""               # multi-clés séparées par virgules
GEMINI_MODEL    = "gemini-2.0-flash"
LLM_MODEL       = "gemini-2.5-flash"  # prioritaire sur GEMINI_MODEL
LLM_TEMPERATURE = 0.05
LLM_MAX_TOKENS  = 8192
```

**En pratique :** le modèle effectif est `LLM_MODEL` (`gemini-2.5-flash`).

### 11.3 GeminiLLM — mécanisme de rotation

```python
GeminiLLM(api_keys=["key1", "key2", ...], model_name="gemini-2.5-flash")
```

État interne :
- `current_key_index` : index de la clé active
- `failed_keys` : ensemble des index des clés épuisées

Méthode `_rotate_key()` :
1. Ajoute `current_key_index` à `failed_keys`
2. Cherche la prochaine clé non épuisée (round-robin)
3. Si toutes épuisées → `False` → exception

Méthode `generate()` :
```python
generate(
    prompt: str,
    temperature: float = 0.05,
    max_tokens: int = 8192,
    response_mime_type: str = None  # ex: "application/json" pour forcer JSON
)
```

Structure de l'appel Gemini :
```python
client.models.generate_content(
    model=model_name,
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
        [response_mime_type=response_mime_type]  # si fourni
    )
)
```

**Important :** Le prompt est passé directement comme `contents` (pas de séparation system/user). Tout le contexte est dans le prompt.

Détection des erreurs de quota : `"429"`, `"RESOURCE_EXHAUSTED"`, `"quota"`, `"rate limit"` dans le message d'erreur.

### 11.4 Paramètres de génération par opération

| Opération | température | max_tokens | mime_type |
|-----------|-------------|------------|-----------|
| V1 JSON   | 0.05        | 4096       | —         |
| V1 SysML  | 0.05        | 8192       | —         |
| V2 JSON   | 0.05        | **65536**  | application/json |
| V2 SysML  | 0.05        | 8192       | —         |
| V2 patch JSON | 0.05   | 65536      | application/json |
| Test LLM  | 0.0         | 64         | —         |

---

## 12. Validation — `sysml_validator.py` + `fidelity_checker.py`

### 12.1 SysMLv2Validator — 5 niveaux de vérification

Le validateur est appelé automatiquement après chaque génération de code SysML v2 (dans `LevelService._generate_sysml_for_level`).

**Niveau 1 — `_check_structure`**
- Accolades équilibrées (ignoring strings et commentaires) → E001, E002
- Déclarations simples sans point-virgule → W001
- Absence de `package` → W002
- Plus de 3 lignes vides consécutives → I001

**Niveau 2 — `_check_declarations`**
- Collecte toutes les `{type} def {Name}` → dictionnaire `definitions`
- Collecte tous les `(part|port|item|attribute) name : Type` → dictionnaire `usages`
- Types référencés mais non déclarés → E003
- Définitions dupliquées → W003

**Niveau 3 — `_check_references`**
- `flow ... from X.port to Y.port` : vérifie que X et Y sont dans `usages` → E004, E005
- `connect X to Y` : vérifie que X et Y sont dans `usages` → E006, E007
- `satisfy/verify req by comp` : vérifie que req existe → W004
- `part def` déclaré mais jamais instancié → W005

**Niveau 4 — `_check_naming`**
- `(part|port|item|attribute) def nom_minuscule` → W006 (devrait être PascalCase)
- `(part|port|item|attribute) NomMajuscule :` → W007 (instances en camelCase)
- `def mot1 mot2` sans guillemets simples → E008

**Niveau 5 — `_check_completeness`**
- Package vide `package Nom {}` → W008
- Part defs sans aucun port → I002
- Ports définis sans flow/connect → W009
- Aucun commentaire doc `/* */` → I003

**Score de qualité :**
```
score = 100 - (errors * 15) - (warnings * 5) - (infos * 1)
score ∈ [0, 100]
```

**Structure de retour :**
```python
{
    "valid": bool,    # True si 0 erreurs
    "score": int,     # 0-100
    "errors": [{"line", "column", "severity": "error", "code": "Exxx", "message": "..."}],
    "warnings": [{"line", "column", "severity": "warning", "code": "Wxxx", "message": "..."}],
    "info": [{"line", "column", "severity": "info", "code": "Ixxx", "message": "..."}],
    "summary": {
        "total_lines": int,
        "definitions": int,
        "usages": int,
        "packages": int,
        "errors_count": int,
        "warnings_count": int
    }
}
```

**Mots-clés SysML v2 reconnus :**
- Définitions : `package`, `part def`, `port def`, `item def`, `attribute def`, `connection def`, `interface def`, `allocation def`, `action def`, `state def`, `requirement def`, `use case def`, etc.
- Usages : `part`, `port`, `item`, `attribute`, `connection`, `interface`, `action`, `state`, `requirement`, `flow`, `ref`, `bind`, `connect`, etc.
- Modificateurs : `abstract`, `readonly`, `derived`, `redefines`, `subsets`, `:>`, `:>>`, etc.
- Types primitifs : `String`, `Integer`, `Real`, `Boolean`, `Natural`, `Positive`, `Number`, `Complex`

### 12.2 FidelityChecker

Appelé uniquement dans les pipelines V1 (toujours) et V2 (niveaux logical et technical uniquement).

**Méthode `check(description, system_model)`**

Entrées :
- `description` : description NL originale
- `system_model` : dict JSON généré

Retourne :
```python
{
    "is_faithful": bool,
    "missing_components": ["noms de composants décrits mais absents du modèle"],
    "extra_components": ["noms de composants dans le modèle mais non décrits"],
    "warnings": ["connexion manquante: A → B (flow)"]
}
```

**Algorithme d'extraction des composants depuis la description :**
1. Supprime les phrases correspondant aux `EXCLUDED_PATTERNS` (exigences, acteurs, flux)
2. Regex : `\b(?:un|une|des|le|la|les|a|an|the)\s+([A-ZÀ-ÿa-z]+(?:\s+[A-ZÀ-ÿa-z]+){0,2})`
3. Normalisation : minuscules, sans accents, sans articles
4. Filtre `EXCLUDED_WORDS` et stop words
5. Filtre les verbes conjugués

**Algorithme d'extraction des composants depuis le modèle :**
- Extraire récursivement `parts[].name` et `parts[].children[].name`

**Matching flou :**
1. Identiques après normalisation → match
2. L'un contient l'autre → match
3. Distance de Levenshtein normalisée < 0.3 → match

**Mots exclus :** `agent`, `administrateur`, `opérateur`, `utilisateur`, `signal`, `flux`, `commande`, `alerte`, `donnée`, `secondes`, `heures`, etc.

---

## 13. Diagrammes — `diagram_service.py`

Tous les diagrammes sont générés en Python pur (pas de LLM). Le rendu SVG est assuré par un appel HTTP POST au serveur PlantUML.

### 13.1 Appel au serveur PlantUML

```python
requests.post(
    f"{plantuml_server_url}/svg/",
    data=plantuml_code.encode("utf-8"),
    headers={"Content-Type": "text/plain"},
    timeout=10
)
```

URL par défaut : `http://plantuml:8080`

### 13.2 7 types de diagrammes — mapping JSON → PlantUML

**BDD (Block Definition Diagram)** — `generate_bdd`
- Source : `parts[]` → `class "NomPart" <<block>> { ports... }`
- Source : `connections[]` de type `connection/interface` → `"A" -- "B" : label`
- Source : `children[]` récursif → `"parent" *-- "child" : contient`

**IBD (Internal Block Diagram)** — `generate_ibd`
- Source : `parts[]` → `component "NomPart" as ID { port "nom" as portID }`
- Source : `connections[]` → `portSrc --> portDst : label`
- Direction : left to right

**Context** — `generate_context`
- Format opérationnel : `stakeholders[]` → acteurs, `external_systems[]` → rectangles
- Format logique : déduit les acteurs externes depuis `connections[]`

**Requirements** — `generate_requirements`
- Source : `requirements[]` → `class "REQ-ID" <<requirement>> { text = "..." }`
- `satisfied_by` → `"component" ..> "REQ-ID" : <<satisfy>>`

**Use Cases** — `generate_use_cases`
- Source : `use_cases[]` → `usecase "nom" as ID`
- `actors[]` → `actor "nom" as ID`
- `includes[]` → `UC1 ..> UC2 : <<include>>`

**Functional Breakdown (FBS)** — `generate_functional_breakdown`
- Source : `functions[]` → `rectangle "nom" as ID`
- `sub_functions[]` → rectangles imbriqués + liens `→`

**Functional Behavior** — `generate_functional_behavior`
- Source : `functions[]` → rectangles
- Source : `functional_flows[]` → `fromID --> toID : item`

**Modes Diagram** — `generate_modes_diagram`
- Source : `modes[]` → `state "nom" as ID { active_functions... }`
- Transitions séquentielles entre modes consécutifs

**Technical Architecture** — `generate_technical_architecture`
- Source : `technical_parts[]` → `node "nom" as ID <<type>>`
- Source : `physical_connections[]` → `from_id --> to_id : description`

### 13.3 Sanitisation des identifiants PlantUML (`_sanitize_id`)

```
1. Normalisation NFD (unicode) → suppression des marques diacritiques
2. Espaces → underscore
3. Suppression de tous les caractères non alphanumériques (sauf _)
4. Si commence par chiffre → préfixer "id_"
```

---

## 14. Intégration SysON — `syson_service.py`

### 14.1 Architecture d'intégration

SysON utilise **GraphQL** (sur `/api/graphql`) et non REST pour les mutations. Un endpoint REST existe pour l'export de projets.

URL par défaut : `http://syson:8080` (container Docker)
URL navigateur : `http://localhost:8085`

### 14.2 Flux complet d'import (`push_sysml_to_syson`)

```
1. createProject(name, templateId="sysmlv2-template")
   → project_id (UUID)

2. viewer.project(projectId).currentEditingContext.id
   → editing_context_id

3. createDocument(editingContextId, stereotypeId="empty_sysmlv2", name="{project_name}.sysml")
   → document_id

4. createRootObject(editingContextId, documentId,
                    domainId="http://www.eclipse.org/syson/sysml",
                    rootObjectCreationDescriptionId="SysMLv2EditService-Package")
   → parent_object_id  (fallback sur document_id si échec)

5. insertTextualSysMLv2(editingContextId, objectId=parent_object_id, textualContent=sysml_code)
   → SuccessPayload ou ErrorPayload
```

### 14.3 Mutations GraphQL

**createProject :**
```graphql
mutation CreateProject($input: CreateProjectInput!) {
  createProject(input: $input) {
    __typename
    ... on CreateProjectSuccessPayload { project { id } }
    ... on ErrorPayload { message }
  }
}
```
Variables : `{ "input": { "id": UUID, "name": str, "templateId": "sysmlv2-template", "libraryIds": [] } }`

**createDocument :**
```graphql
mutation CreateDocument($input: CreateDocumentInput!) {
  createDocument(input: $input) {
    __typename
    ... on CreateDocumentSuccessPayload { document { id } }
    ... on ErrorPayload { message }
  }
}
```
Variables : `{ "input": { "id": UUID, "editingContextId": str, "stereotypeId": "empty_sysmlv2", "name": "{name}.sysml" } }`

**createRootObject :**
```graphql
mutation CreateRootObject($input: CreateRootObjectInput!) {
  createRootObject(input: $input) {
    __typename
    ... on CreateRootObjectSuccessPayload { object { id label } }
    ... on ErrorPayload { message }
  }
}
```
Variables : `{ "input": { "id": UUID, "editingContextId": str, "documentId": str, "domainId": "http://www.eclipse.org/syson/sysml", "rootObjectCreationDescriptionId": "SysMLv2EditService-Package" } }`

**insertTextualSysMLv2 :**
```graphql
mutation InsertTextualSysMLv2($input: InsertTextualSysMLv2Input!) {
  insertTextualSysMLv2(input: $input) {
    __typename
    ... on SuccessPayload { id }
    ... on ErrorPayload { message }
  }
}
```
Variables : `{ "input": { "id": UUID, "editingContextId": str, "objectId": str, "textualContent": sysml_code } }`

### 14.4 Export depuis SysON (`export_sysml_from_syson`)

```
GET /api/projects/{project_id}
Headers: Accept: application/octet-stream
→ ZIP contenant des fichiers .json (format EMF JSON, format propriétaire Eclipse)
```

⚠️ **Important :** SysON v2026.1.0 ne fournit pas d'export SysML v2 textuel via API. Le format retourné est EMF JSON (format interne Eclipse/EMF), pas du SysML v2 lisible.

---

## 15. Gestion des sessions — `state_service.py`

### 15.1 Format de persistance

Chaque session est stockée dans un fichier JSON : `{STATE_DIR}/{session_id}.json`

**Structure complète d'une session multi-niveaux :**
```json
{
  "session_id": "UUID",
  "session_name": "Nom donné par l'utilisateur",
  "created_at": "ISO 8601",
  "updated_at": "ISO 8601",
  "system_name": "Nom du système (extrait du niveau opérationnel)",
  "description": "Description initiale fournie par l'utilisateur",
  "current_level": "operational | functional | logical | technical",
  "levels": {
    "operational": {
      "level": "operational",
      "model": { /* OperationalModel JSON */ },
      "sysml_code": "package '...' { ... }",
      "llm_warnings": ["warning 1", ...],
      "validation_result": {
        "valid": true,
        "score": 85,
        "errors": [...],
        "warnings": [...],
        "info": [...],
        "summary": { "total_lines": ..., "errors_count": ..., ... }
      },
      "diagrams": [
        { "type": "context", "title": "...", "plantuml_code": "..." }
      ],
      "validated": false,
      "history": [
        { "action": "generate", "description": "...", "timestamp": "ISO 8601" },
        { "action": "patch", "instruction": "...", "timestamp": "ISO 8601" }
      ]
    },
    "functional": { /* même structure */ },
    "logical": { /* même structure */ },
    "technical": { /* même structure */ }
  },
  "exchanges": [
    {
      "id": "UUID",
      "timestamp": "ISO 8601",
      "session_id": "UUID",
      "level": "operational",
      "operation": "generate_json | generate_sysml | patch_json",
      "description_input": "description originale",
      "prompt_sent": "prompt complet envoyé au LLM",
      "llm_response_raw": "réponse brute avant parsing",
      "llm_model": "gemini-2.5-flash",
      "sysml_code": "code SysML nettoyé (pour generate_sysml uniquement)",
      "success": true,
      "error_message": ""
    }
  ]
}
```

**Note :** Le SVG des diagrammes n'est PAS sauvegardé dans le fichier de session (trop volumineux). Il est regénéré à la demande depuis le `plantuml_code` stocké.

### 15.2 Méthodes principales

| Méthode | Description |
|---------|-------------|
| `create_session()` | Crée un fichier JSON vide, retourne UUID |
| `init_session_with_levels(session_id, description, session_name)` | Initialise la structure à 4 niveaux |
| `save_session(session_id, data)` | Merge data dans le JSON existant |
| `load_session(session_id)` | Charge le JSON depuis le disque |
| `list_sessions()` | Liste tous les *.json triés par updated_at |
| `save_level(session_id, level, level_data)` | Sauvegarde les données d'un niveau |
| `get_level(session_id, level)` | Retourne les données d'un niveau |
| `validate_level(session_id, level)` | Met `validated=True`, avance `current_level` |
| `get_previous_level_data(session_id, level)` | Retourne les données du niveau précédent |
| `save_exchange(session_id, exchange)` | Ajoute un échange LLM à `exchanges[]` |
| `get_exchanges(session_id, level=None)` | Retourne les échanges (filtrés par niveau) |
| `rename_session(session_id, name)` | Met à jour `session_name` |
| `delete_session(session_id)` | Supprime le fichier JSON |

### 15.3 Cycle de vie d'une session V2

```
Nouvelle session
    │
    ▼
init_session_with_levels() → 4 niveaux vides, validated=False
    │
    ▼
generate_level("operational") → model + sysml_code + validation_result
    │
    ├── [optionnel] patch_level("operational", instruction)
    │
    ▼
validate_level("operational") → validated=True, current_level="functional"
    │
    ▼
generate_level("functional") → utilise operational.model comme contexte
    │
    ▼
validate_level("functional") → validated=True, current_level="logical"
    │
    ▼
generate_level("logical") → utilise functional.model comme contexte
    │
    ▼
validate_level("logical") → validated=True, current_level="technical"
    │
    ▼
generate_level("technical") → utilise logical.model comme contexte
    │
    ▼
get_full_sysml() → concat des 4 niveaux
    │
    ▼
syson.push_sysml_to_syson(sysml_code) → projet SysON
```

---

## 16. API Endpoints — `main.py`

### 16.1 Démarrage (startup)

Ordre d'initialisation des services :
1. `RAGService` + `index_sysml_files(force=False)`
2. `GeminiLLM` (avec toutes les clés API)
3. `StateService`
4. `FidelityChecker`
5. `SysMLService` (V1)
6. `DiagramService`
7. `LevelService` (V2)
8. `SysMLv2Validator`
9. `SysONService`

### 16.2 Table complète des endpoints

| Méthode | URL | Description | Service |
|---------|-----|-------------|---------|
| GET | `/api/health` | Statut + config | — |
| GET | `/api/llm-status` | Statut des clés LLM | llm |
| GET | `/api/test-llm` | Test de connexion LLM | llm |
| GET | `/api/rag/stats` | Stats ChromaDB | rag |
| GET | `/api/rag/search?query=...` | Recherche sémantique | rag |
| POST | `/api/generate` | Génération V1 | sysml_service |
| POST | `/api/patch` | Modification V1 | sysml_service |
| GET | `/api/session/{id}` | Données de session | state |
| GET | `/api/sessions` | Liste des sessions | state |
| DELETE | `/api/session/{id}` | Supprimer session | state |
| POST | `/api/diagrams` | Tous les diagrammes V1 | diagram_service |
| POST | `/api/diagrams/{type}` | Diagramme spécifique V1 | diagram_service |
| POST | `/api/v2/generate` | Génération V2 (niveau) | level_service |
| POST | `/api/v2/patch` | Modification V2 (niveau) | level_service |
| POST | `/api/v2/validate` | Valider un niveau | level_service |
| PUT | `/api/v2/session/{id}/name` | Renommer session | state |
| GET | `/api/v2/coherence/{id}/{level}` | Vérifier cohérence | level_service |
| GET | `/api/v2/status/{id}` | Statut des 4 niveaux | level_service |
| GET | `/api/v2/level/{id}/{level}` | Données d'un niveau | state |
| GET | `/api/v2/full-sysml/{id}` | Code SysML complet | level_service |
| POST | `/api/v2/diagrams` | Diagrammes d'un niveau | diagram_service |
| GET | `/api/v2/diagrams/{id}/{level}` | Diagrammes stockés | diagram_service |
| POST | `/api/validate-sysml` | Validation syntaxique | sysml_validator |
| GET | `/api/validate-sysml/{id}` | Validation session | sysml_validator |
| GET | `/api/v2/exchanges/{id}` | Échanges LLM | state |
| GET | `/api/v2/export/{id}` | Export session | state + level |
| GET | `/api/syson/status` | Statut SysON | syson |
| POST | `/api/syson/push` | Push vers SysON | syson |
| GET | `/api/syson/project-url/{id}` | URL projet SysON | syson |
| GET | `/api/syson/projects` | Liste projets SysON | syson |
| POST | `/api/syson/pull` | Export depuis SysON | syson |

### 16.3 Flux complet de `/api/v2/generate`

```
POST /api/v2/generate
Body: GenerateLevelRequest {
    session_id: null,
    session_name: "Mon projet",
    description: "Le système bleed air...",
    level: "operational",
    use_rag: true
}
    │
    ▼
level_service.generate_level(description, "operational", None, "Mon projet", True)
    │
    ├── create_session() → "abc-123"
    ├── init_session_with_levels("abc-123", description, "Mon projet")
    ├── rag.search(description, top_k=8) → 8 exemples SysML
    ├── build_operational_json_prompt(description, rag_examples[:3])
    ├── llm.generate(prompt, temp=0.05, max=65536, mime="application/json")
    ├── json.loads(response) → json_model
    ├── build_operational_sysml_prompt(json_str, rag_examples[:3])
    ├── llm.generate(prompt, temp=0.05, max=8192)
    ├── SysMLv2Validator.validate(sysml_code)
    └── state.save_level("abc-123", "operational", level_data)
    │
    ▼
Réponse: LevelResponse {
    session_id: "abc-123",
    level: "operational",
    model: { /* OperationalModel JSON */ },
    sysml_code: "package '... - Operational' { ... }",
    rag_sources: [...],
    warnings: [...],
    available_diagrams: ["context", "use_cases", "actors_diagram", "operational_sequence"]
}
```

### 16.4 Flux complet de `/api/v2/patch`

```
POST /api/v2/patch
Body: PatchLevelRequest {
    session_id: "abc-123",
    level: "operational",
    instruction: "Ajouter un acteur MaintenanceTeam",
    use_rag: true
}
    │
    ▼
level_service.patch_level("abc-123", "operational", instruction, True)
    │
    ├── state.get_level("abc-123", "operational") → current_model
    ├── rag.search(instruction, top_k=5) → 5 exemples
    ├── Prompt inline (voir section 9)
    ├── llm.generate(prompt, temp=0.05, max=65536, mime="application/json")
    ├── json.loads(response) → modified_model
    ├── _generate_sysml_for_level("operational", modified_model, rag_examples)
    ├── check_coherence("abc-123", "operational")
    └── state.save_level("abc-123", "operational", updated_level_data)
    │
    ▼
Réponse: PatchLevelResponse {
    session_id: "abc-123",
    level: "operational",
    model: { /* modèle modifié */ },
    sysml_code: "...",
    changes_summary: "Modification appliquée au niveau operational : Ajouter...",
    coherence_warnings: [...]
}
```

---

## 17. Schémas Pydantic — `models/schemas.py`

### 17.1 Requêtes API

```python
class GenerateRequest(BaseModel):
    session_id: Optional[str] = None
    description: str = Field(..., min_length=10)
    use_rag: bool = True

class PatchRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    instruction: str = Field(..., min_length=5)
    use_rag: bool = True

class GenerateLevelRequest(BaseModel):
    session_id: Optional[str] = None
    session_name: str = ""
    description: str = Field(..., min_length=10)
    level: ModelLevel = ModelLevel.OPERATIONAL  # Enum
    use_rag: bool = True

class PatchLevelRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    level: ModelLevel
    instruction: str = Field(..., min_length=5)
    use_rag: bool = True

class ValidateLevelRequest(BaseModel):
    session_id: str
    level: ModelLevel

class GenerateDiagramsRequest(BaseModel):
    session_id: str
    level: ModelLevel
    diagram_types: Optional[List[str]] = None  # None = tous

class RenameSessionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
```

### 17.2 Modèles de données

```python
class ModelLevel(str, Enum):
    OPERATIONAL = "operational"
    FUNCTIONAL  = "functional"
    LOGICAL     = "logical"
    TECHNICAL   = "technical"

class PortSchema(BaseModel):
    name: str
    direction: str = Field(..., pattern="^(in|out|inout)$")
    type: str

class ConnectionSchema(BaseModel):
    from_port: str
    to_port: str
    type: str = Field(..., pattern="^(flow|connection|interface)$")
    item: Optional[str] = None
    description: Optional[str] = None

class RequirementSchema(BaseModel):
    id: str
    text: str
    satisfied_by: Optional[str] = None

class UseCaseSchema(BaseModel):
    name: str
    actors: List[str]
    includes: Optional[List[str]] = None

class PartSchema(BaseModel):
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    ports: List[PortSchema] = []
    children: List["PartSchema"] = []  # récursif

class SystemModel(BaseModel):  # pour V1
    system_name: str
    description: str
    warnings: List[str] = []
    parts: List[PartSchema] = []
    connections: List[ConnectionSchema] = []
    requirements: List[RequirementSchema] = []
    use_cases: List[UseCaseSchema] = []

class OperationalModel(BaseModel):
    system_name: str
    description: str
    warnings: List[str] = []
    stakeholders: List[str] = []
    external_systems: List[str] = []
    system_boundaries: str = ""
    use_cases: List[UseCaseSchema] = []
    operational_scenarios: List[dict] = []  # {name, description, steps: []}
    requirements: List[RequirementSchema] = []

class FunctionalModel(BaseModel):
    system_name: str
    warnings: List[str] = []
    functions: List[dict] = []    # {name, description, inputs, outputs, sub_functions}
    functional_flows: List[dict] = []  # {from_function, to_function, item, flow_type, description}
    modes: List[dict] = []        # {name, description, active_functions}

class LogicalModel(BaseModel):
    system_name: str
    warnings: List[str] = []
    parts: List[PartSchema] = []
    connections: List[ConnectionSchema] = []
    requirements: List[RequirementSchema] = []

class TechnicalModel(BaseModel):
    system_name: str
    warnings: List[str] = []
    technical_parts: List[PartSchema] = []
    physical_connections: List[ConnectionSchema] = []
    technology_choices: List[dict] = []  # {component, technology, justification}

class LevelData(BaseModel):
    level: ModelLevel
    model: dict = {}
    sysml_code: str = ""
    diagrams: List[dict] = []   # [{type, title, plantuml_code}] (SVG non stocké)
    validated: bool = False
    history: List[dict] = []

class LLMExchange(BaseModel):
    id: str = ""
    timestamp: str = ""
    session_id: str = ""
    level: str = ""
    operation: str = ""           # "generate_json" | "generate_sysml" | "patch_json"
    description_input: str = ""
    prompt_sent: str = ""         # prompt COMPLET
    llm_response_raw: str = ""    # réponse brute COMPLÈTE
    llm_model: str = ""
    sysml_code: str = ""          # code nettoyé (generate_sysml uniquement)
    success: bool = True
    error_message: str = ""

class SessionData(BaseModel):
    session_id: str
    session_name: str = ""
    created_at: str
    updated_at: str = ""
    system_name: str = ""
    description: str = ""
    current_level: ModelLevel = ModelLevel.OPERATIONAL
    levels: Dict[str, LevelData] = {}
    exchanges: List[dict] = []
```

### 17.3 Réponses API

```python
class GenerateResponse(BaseModel):   # V1
    session_id: str
    system_model: SystemModel
    sysml_code: str
    rag_sources: List[str]

class PatchResponse(BaseModel):      # V1
    session_id: str
    system_model: SystemModel
    sysml_code: str
    changes_summary: str

class LevelResponse(BaseModel):      # V2
    session_id: str
    level: ModelLevel
    model: dict
    sysml_code: str
    rag_sources: List[str] = []
    warnings: List[str] = []
    available_diagrams: List[str] = []

class PatchLevelResponse(BaseModel): # V2
    session_id: str
    level: ModelLevel
    model: dict
    sysml_code: str
    changes_summary: str

class DiagramsResponse(BaseModel):
    session_id: str
    level: ModelLevel
    diagrams: List[dict]  # [{type, title, plantuml_code, svg}]
```

---

## 18. Configuration — `config.py`

```python
class Settings(BaseSettings):
    # === Chemins ===
    BASE_DIR: Path = Path(__file__).parent          # backend/
    DATA_DIR: Path = BASE_DIR / "data"              # backend/data/
    CHROMA_DIR: Path = DATA_DIR / "chroma"          # backend/data/chroma/
    STATE_DIR: Path = DATA_DIR / "state"            # backend/data/state/
    SYSML_REPO_PATH: Path = Path("/app/SysML-v2-Release")  # surchargeé par env

    # === LLM ===
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""       # clé unique (compat)
    GEMINI_API_KEYS: str = ""      # multi-clés séparées par virgules
    GEMINI_MODEL: str = "gemini-2.0-flash"  # secondaire
    LLM_MODEL: str = "gemini-2.5-flash"     # prioritaire
    LLM_TEMPERATURE: float = 0.05
    LLM_MAX_TOKENS: int = 8192

    # === Embeddings ===
    EMBEDDING_PROVIDER: str = "local"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # === RAG ===
    RAG_CHUNK_SIZE: int = 1500
    RAG_CHUNK_OVERLAP: int = 200
    RAG_TOP_K: int = 8

    # === Serveur PlantUML ===
    PLANTUML_SERVER_URL: str = "http://plantuml:8080"

    # === Serveur API ===
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}
```

Variables d'environnement Docker (docker-compose.yml) :
```yaml
SYSML_REPO_PATH: /app/SysML-v2-Release
PLANTUML_SERVER_URL: http://plantuml:8080
GEMINI_API_KEYS: ${GEMINI_API_KEYS}
GEMINI_API_KEY: ${GEMINI_API_KEY}
LLM_MODEL: ${LLM_MODEL}
GEMINI_MODEL: ${GEMINI_MODEL}
SYSON_URL: http://syson:8080
```

---

## 19. Frontend — `frontend/app.py`

Interface Streamlit multi-onglets accessible sur `http://localhost:8501`.

### 19.1 Variable d'environnement

```python
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
```

### 19.2 Structure de l'interface

**Sidebar :**
- Statut du backend (`GET /api/health`) + statut LLM (`GET /api/llm-status`)
- Stats RAG (`GET /api/rag/stats`) : nb fichiers, nb chunks, stockage estimé
- Liste des sessions récentes (`GET /api/sessions`)
- Paramètres globaux (toggle RAG)

**Onglet 1 — Générer**
- Zone de texte pour la description du système
- Sélecteur de niveau MBSE (opérationnel → technique)
- Option RAG
- Bouton "Générer" → `POST /api/v2/generate`
- Affichage : JSON du modèle, code SysML v2, warnings, score validation
- Bouton "Générer les diagrammes" → `POST /api/v2/diagrams`
- Affichage SVG des diagrammes

**Onglet 2 — Modifier**
- Sélecteur de session
- Sélecteur de niveau
- Zone de texte pour l'instruction de modification
- Bouton "Modifier" → `POST /api/v2/patch`
- Affichage avant/après (code SysML côte à côte)

**Onglet 3 — Historique**
- Liste de toutes les sessions
- Détails d'une session : modèles JSON, code SysML par niveau
- Échanges LLM (`GET /api/v2/exchanges/{id}`) avec prompts et réponses brutes
- Export session (`GET /api/v2/export/{id}`)
- Suppression de session
- Renommage de session (`PUT /api/v2/session/{id}/name`)
- Intégration SysON : push (`POST /api/syson/push`) et pull (`POST /api/syson/pull`)

### 19.3 Appels backend depuis le frontend

Tous les appels passent par la fonction utilitaire `requests.get/post(BACKEND_URL + "/api/...")`.

---

## 20. Points critiques pour modification du pipeline

### 20.1 Incohérence RAG V1 vs V2

En V1 (`sysml_service.py`) :
```python
rag_sources = [result["source_file"] for result in rag_results]  # clé "source_file"
```

En V2 (`level_service.py`) :
```python
rag_sources = [r["file"] for r in results]  # clé "file" ← INCORRECTE !
```

La méthode `rag.search()` retourne `"source_file"`, pas `"file"`. Cela cause un `KeyError` en V2 si `use_rag=True`. (Bug existant)

### 20.2 FidelityChecker — niveaux concernés

- **V1 :** appelé pour TOUS les modèles
- **V2 :** appelé UNIQUEMENT pour `logical` et `technical` (pas pour `operational` et `functional`)

### 20.3 Paramètre `response_mime_type`

Uniquement activé pour la génération JSON (pas pour la génération SysML). Cela force Gemini à retourner du JSON valide directement, contournant ainsi le besoin de parser le markdown.

### 20.4 max_tokens très élevé pour JSON

`max_tokens=65536` pour les générations JSON V2 — valeur très haute pour permettre des modèles complexes mais peut ralentir la génération.

### 20.5 SysML v2 généré par niveau — structure divergente

Chaque niveau génère son propre package indépendant :
- `package '{name} - Operational' { ... }`
- `package '{name} - Functional' { ... }`
- `package '{name} - Logical' { ... }`
- `package '{name} - Technical' { ... }`

Le code complet est la **concaténation** de ces 4 packages. Les types définis dans le package Logical ne sont pas directement réutilisés dans le package Technical — chaque niveau est autonome. Cela peut causer des problèmes de compatibilité SysON.

### 20.6 Syntaxe SysML v2 dans les exemples des prompts

Les prompts montrent des exemples de syntaxe parfois non conformes au standard OMG SysML v2. Par exemple :
- `satisfy by Component;` ← non standard (devrait être `satisfy requirement REQ by Component;`)
- `allocation LogicalComp to TechnicalComp;` ← keyword non standard (allocation en SysML v2 utilise `allocate`)
- Les ports dans les exemples utilisent `[in]`/`[out]` comme modificateurs post-type, ce qui n'est pas la syntaxe standard

Ces inconsistances sont propagées dans le code généré.

---

*Fin du document d'analyse — 2026-02-25*
