# Matrice des 15 prompts SysML v2

## Vue d'ensemble

L'agent genere 15 diagrammes SysML v2 repartis sur 4 niveaux d'architecture. Chaque diagramme dispose d'une fonction Python dediee qui construit le prompt de generation, avec des regles syntaxiques specifiques.

## Matrice des prompts

| Niveau | Diagramme | Fonction Python | Regles |
|--------|-----------|-----------------|--------|
| Operationnel | Lifecycle | `build_lifecycle_sysml_prompt` | R-LC1 a R-LC5 |
| Operationnel | Use Cases | `build_use_cases_sysml_prompt` | R-UC1 a R-UC5 |
| Operationnel | Context | `build_context_sysml_prompt` | R-CT1 a R-CT5 |
| Operationnel | Scenarios | `build_scenarios_sysml_prompt` | R-SC1 a R-SC5 |
| Operationnel | Operating Modes | `build_operating_modes_sysml_prompt` | R-OM1 a R-OM5 |
| Fonctionnel | Functional Breakdown | `build_functional_breakdown_sysml_prompt` | R-FB1 a R-FB5 |
| Fonctionnel | Functional Behaviour | `build_functional_behaviour_sysml_prompt` | R-BH1 a R-BH5 |
| Fonctionnel | Functional Modes | `build_functional_modes_sysml_prompt` | R-FM1 a R-FM5 |
| Logique | Logical Breakdown | `build_logical_breakdown_sysml_prompt` | R-LB1 a R-LB5 |
| Logique | Logical Architecture | `build_logical_architecture_sysml_prompt` | R-LA1 a R-LA5 |
| Logique | Logical Sequences | `build_logical_sequences_sysml_prompt` | R-LS1 a R-LS4 |
| Logique | Logical Modes | `build_logical_modes_sysml_prompt` | R-LM1 a R-LM5 |
| Technique | Technical Breakdown | `build_technical_breakdown_sysml_prompt` | R-TB1 a R-TB5 |
| Technique | Technical Architecture | `build_technical_architecture_sysml_prompt` | R-TA1 a R-TA5 |
| Technique | Technical States | `build_technical_states_sysml_prompt` | R-TS1 a R-TS5 |

## Structure commune des prompts

Chaque prompt est assemble par la fonction `build_sysml_prompt` definie dans `prompts/_shared.py`. Cette fonction compose le prompt final a partir de **9 blocs** ordonnes :

### Bloc 1 : Role

Definition du role du LLM. Exemple : "Tu es un expert en ingenierie systeme et en SysML v2. Tu generes du code SysML v2 strictement conforme a la specification OMG."

### Bloc 2 : Contraintes de fidelite (SYSML_FIDELITY_BLOCK)

Les 5 exigences de fidelite F1 a F5 (voir [Exigences de fidelite](fidelite-f1-f5.md)). Ce bloc empeche le LLM d'inventer des elements et l'oblige a signaler les incoherences et les manques.

### Bloc 3 : Regles de compatibilite SysON (SYSON_RULES_BLOCK)

Les 9 regles RS1 a RS9 (voir [Regles de compatibilite SysON](regles-syson.md)). Ce bloc assure que le code genere est directement importable dans l'editeur SysON.

### Bloc 4 : Template syntaxique valide

Un template complet extrait des fichiers de la specification OMG, montrant la syntaxe exacte attendue pour le type de diagramme cible (voir [Templates officiels](templates-officiels.md)).

### Bloc 5 : Regles syntaxiques specifiques

Les regles specifiques au type de diagramme (par exemple R-LC1 a R-LC5 pour le Lifecycle). Ces regles completent le template en precisant les patterns syntaxiques obligatoires et les constructions interdites pour ce diagramme particulier.

### Bloc 6 : Contrainte de nommage (optionnel)

Le bloc de contrainte de nommage genere par `build_naming_constraint_block()`, present uniquement si des packages precedents ont deja ete generes pour le meme niveau (voir [Coherence inter-packages](coherence-inter-packages.md)).

### Bloc 7 : Donnees JSON filtrees

Les donnees JSON extraites des reponses de l'utilisateur, filtrees pour ne contenir que les informations pertinentes au diagramme en cours de generation. Ce filtrage evite de surcharger le contexte du LLM avec des donnees non pertinentes.

### Bloc 8 : Exemples RAG (optionnel)

Des exemples de code SysML v2 valide recuperes par recherche semantique (RAG) dans la base de donnees de templates. Ces exemples fournissent un contexte supplementaire au LLM pour les cas de generation complexes.

### Bloc 9 : Instruction finale

L'instruction finale qui precise le format de sortie attendu (code SysML v2 brut, sans commentaires additionnels, sans blocs markdown) et rappelle les contraintes cles.

## Flux d'assemblage

```
build_sysml_prompt(diagram_type, json_data, identifiers, rag_examples)
    |
    +-- [1] Role
    +-- [2] SYSML_FIDELITY_BLOCK
    +-- [3] SYSON_RULES_BLOCK
    +-- [4] Template specifique au diagram_type
    +-- [5] Regles specifiques au diagram_type
    +-- [6] build_naming_constraint_block(identifiers)  [si non vide]
    +-- [7] json_data filtre
    +-- [8] rag_examples  [si disponibles]
    +-- [9] Instruction finale
    |
    v
    Prompt complet --> LLM --> Code SysML v2
```
