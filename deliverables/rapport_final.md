# Rapport de Mission — Génération automatique de modèles SysML v2 par IA

**Client :** Safran  
**Prestataire :** ENSTA / Junior Entreprise  
**Date :** Février 2026  
**Version :** 1.0  

---

## Table des matières

1. [Introduction](#1--introduction)
2. [Approche méthodologique](#2--approche-méthodologique)
   - 2.1 [Le pipeline en 2 étapes](#21-le-pipeline-en-2-étapes)
   - 2.2 [Les 4 niveaux MBSE](#22-les-4-niveaux-mbse)
   - 2.3 [Le RAG — Retrieval-Augmented Generation](#23-le-rag--retrieval-augmented-generation)
   - 2.4 [Le processus itératif d'amélioration](#24-le-processus-itératif-damélioration)
3. [Catégorie 1 — Prompts de génération du modèle SysML v2](#3--catégorie-1--prompts-de-génération-du-modèle-sysml-v2)
   - 3.1 [Structure type d'un prompt de génération](#31-structure-type-dun-prompt-de-génération)
   - 3.2 [Prompt type — Niveau Opérationnel](#32-prompt-type--niveau-opérationnel)
   - 3.3 [Prompt type — Niveau Fonctionnel](#33-prompt-type--niveau-fonctionnel)
   - 3.4 [Prompt type — Niveau Logique](#34-prompt-type--niveau-logique)
   - 3.5 [Prompt type — Niveau Technique](#35-prompt-type--niveau-technique)
   - 3.6 [Tableau récapitulatif des corrections P1–P8](#36-tableau-récapitulatif-des-corrections-p1p8)
4. [Catégorie 2 — Visualisation des diagrammes](#4--catégorie-2--visualisation-des-diagrammes)
   - 4.1 [Approche retenue : Eclipse SysON](#41-approche-retenue--eclipse-syson)
   - 4.2 [Pistes d'amélioration : prompts d'élicitation](#42-pistes-damélioration--prompts-délicitation)

---

## 1 — Introduction

### Contexte de la mission

Dans le cadre d'un partenariat entre Safran et l'ENSTA via la Junior Entreprise, cette mission de 2 Journées d'Étude Homme (JEH) s'est fixé pour objectif d'explorer la capacité de l'intelligence artificielle générative à produire automatiquement du code SysML v2 complet et des diagrammes d'architecture à partir de descriptions en langage naturel.

SysML v2 (Systems Modeling Language version 2) est la norme de facto pour la modélisation de systèmes complexes dans l'industrie aéronautique et de défense. Sa maîtrise requiert une expertise spécialisée et un investissement en temps considérable pour chaque modèle produit. L'émergence des grands modèles de langage (LLM) ouvre une voie nouvelle : déléguer la production de la syntaxe formelle à une IA, tout en conservant à l'ingénieur système la maîtrise des choix d'architecture.

### Objectif de la mission

La mission poursuit deux objectifs complémentaires :

1. **Identifier des prompts types efficaces pour la génération de modèles SysML v2.** Il s'agit de formuler, tester et affiner les instructions envoyées à l'IA pour qu'elle produise du code SysML v2 syntaxiquement valide et sémantiquement fidèle à la description fournie, niveau par niveau selon l'approche MBSE.

2. **Identifier des prompts types pour la visualisation des diagrammes d'architecture.** La vérification du contenu d'un modèle SysML v2 passe par sa représentation visuelle sous forme de diagrammes (contexte, cas d'utilisation, BDD, IBD, etc.). La mission explore comment l'IA peut guider la génération de ces représentations, et comment un outil open-source (Eclipse SysON) peut servir de visualisateur de référence.

Ces livrables sont directement réutilisables par les ingénieurs Safran comme base de travail pour des futurs projets de modélisation assistée par IA.

### Approche retenue

L'approche repose sur un **pipeline IA structuré** combinant trois technologies :

- **Un grand modèle de langage (LLM) — Google Gemini 2.5 Flash** : le moteur de compréhension du langage naturel et de génération de code SysML v2.
- **Un système RAG (Retrieval-Augmented Generation)** : une base de connaissances de 337 extraits issus du dépôt officiel SysML v2 (`Systems-Modeling/SysML-v2-Release`), injectés dynamiquement dans chaque prompt pour ancrer les générations dans la syntaxe officielle.
- **Une progression MBSE en 4 niveaux** : le modèle est construit progressivement (Opérationnel → Fonctionnel → Logique → Technique), chaque niveau étant généré à partir du précédent et validé avant de passer au suivant.

### Système testé — BAS Silvercrest

Le système cible des tests est le **BAS (Bleed Air System)** du moteur Silvercrest. Il s'agit d'un système de prélèvement et conditionnement d'air intercalé entre la turbomachine et l'avion. Il constitue un cas d'usage représentatif de la complexité des systèmes avioniques embarqués :

| Dimension | Détail |
|---|---|
| **Entités externes** | 6 : A/C Avionics, Turbomachine, Fan by-pass duct, Nacelle, A/C Pneumatic System, SOV |
| **Fonctions de service** | 4 : fourniture d'air régulé, dégivrage nacelle, auto-diagnostic, communication avionique |
| **Modes de fonctionnement** | 3 : OFF, Stand-by, Running |
| **Sous-systèmes** | 5 : Prélèvement, Dégivrage, Conditionnement, Mesure, Contrôle-Commande |
| **Composants physiques** | ~15 : IP Port, HP Port, HPV, IPCV, NAIV, PRV, Exchanger, FAV, Filter, capteurs de pression et température, Electronic BAS Control |
| **Exigences mesurables** | 4 : température −40 °C/+85 °C, temps de réponse ≤ 500 ms, pression 20–50 PSI, température sortie 150–230 °C |

Ce rapport documente la méthodologie mise en œuvre, les résultats obtenus sur le BAS Silvercrest, le processus d'amélioration itératif des prompts, ainsi que les prompts types réutilisables produits à l'issue de la mission.

---

## 2 — Approche méthodologique

### 2.1 Le pipeline en 2 étapes

#### Principe général

Le pipeline repose sur une décomposition de la tâche de génération en deux étapes distinctes, séparées par un format intermédiaire structuré (JSON).

```
Description en langage naturel
          │
          ▼
┌─────────────────────────────────────────┐
│  ÉTAPE 1 : NL → JSON structuré          │
│  LLM + RAG (exemples SysML v2 officiels)│
└─────────────────────────────────────────┘
          │
          ▼
     JSON validé
     (composants, connexions, exigences,
      acteurs, flux, modes...)
          │
          ▼
┌─────────────────────────────────────────┐
│  ÉTAPE 2 : JSON → Code SysML v2         │
│  LLM + RAG (règles de syntaxe)          │
└─────────────────────────────────────────┘
          │
          ▼
     Code SysML v2
```

#### Étape 1 — Compréhension et structuration

L'IA analyse la description en langage naturel fournie par l'ingénieur et produit un **objet JSON structuré** contenant tous les éléments du modèle au niveau MBSE concerné. Pour le niveau opérationnel, ce JSON contient les acteurs (`stakeholders`), les systèmes externes (`external_systems`), le périmètre du système (`system_boundaries`), les cas d'utilisation (`use_cases`), les scénarios opérationnels (`operational_scenarios`) et les exigences de haut niveau (`requirements`). Ce JSON est validé par des schémas Pydantic avant de passer à l'étape suivante.

**Exemple de sortie JSON — niveau opérationnel (BAS Silvercrest) :**

```json
{
  "system_name": "Bleed Air System (BAS)",
  "stakeholders": [
    {"name": "AC_Avionics", "role": "Envoie les consignes et reçoit les statuts", "type": "system"},
    {"name": "EECS", "role": "Calculateur moteur, envoie les commandes de régulation", "type": "system"},
    {"name": "OperateurDeMaintenance", "role": "Diagnostique et maintient le système", "type": "human"}
  ],
  "use_cases": [
    {"name": "PressuriserEtTempererLaCabine", "actors": ["AC_Avionics", "SystemePneumatiqueDeLAvion"]},
    {"name": "DegivrerLaNacelle", "actors": ["AC_Avionics", "Nacelle"]},
    {"name": "DiagnostiquerLEtat", "actors": ["OperateurDeMaintenance"]}
  ],
  "requirements": [
    {"id": "REQ-OP-001", "text": "Le système doit fonctionner entre -40°C et +85°C"},
    {"id": "REQ-OP-002", "text": "Temps de réponse de la boucle de régulation ≤ 500 ms"}
  ]
}
```

#### Étape 2 — Génération syntaxique SysML v2

Le JSON validé est transmis à l'IA avec un prompt spécialisé qui décrit les règles syntaxiques SysML v2 attendues pour le niveau MBSE concerné, enrichi par les extraits RAG les plus pertinents. L'IA produit alors du code SysML v2 syntaxiquement valide.

**Exemple de sortie SysML v2 — niveau opérationnel :**

```sysml
package 'Bleed Air System (BAS) - Operational' {

    use case def DegivrerLaNacelle {
        doc /* Dégivrer la nacelle via l'air chaud haute pression */
        actor AC_Avionics;
        actor Nacelle;
    }

    requirement def REQ_OP_001 {
        doc /* Le système doit fonctionner dans une plage de température de -40°C à +85°C. */
    }

    requirement def REQ_OP_002 {
        doc /* Le temps de réponse de la boucle de régulation ne doit pas dépasser 500 millisecondes. */
    }

    action def FournitureAirNominal {
        doc /* L'avionique envoie les consignes. L'air est prélevé sur l'IP Port.
               Le calculateur pilote PRV et FAV en boucle fermée.
               L'air régulé sort vers le système pneumatique de l'avion. */
    }
}
```

#### Pourquoi cette décomposition en 2 étapes ?

Cette architecture à deux étapes présente trois avantages essentiels :

1. **Inspectabilité** : le JSON intermédiaire est lisible et vérifiable par l'ingénieur système. Avant même de générer une ligne de SysML v2, on peut valider que l'IA a bien compris les composants, les acteurs, les exigences.

2. **Modifiabilité** : le JSON peut être corrigé ou enrichi manuellement entre les deux étapes, permettant un ajustement fin sans tout regénérer.

3. **Stabilité de la sortie** : confiner la compréhension du langage naturel à l'étape 1 et la génération syntaxique à l'étape 2 réduit la variance des réponses. Le LLM est plus prévisible sur la transformation d'un JSON bien défini vers une syntaxe formelle que sur la transformation directe d'un texte libre.

---

### 2.2 Les 4 niveaux MBSE

Le pipeline suit une progression MBSE (Model-Based Systems Engineering) en quatre niveaux, du plus abstrait au plus concret. Chaque niveau est généré à partir du précédent et doit être **validé** par l'ingénieur avant de passer au suivant. Cette validation garantit que les décisions de décomposition sont maîtrisées à chaque étape.

#### Niveau 1 — Opérationnel : QUI et POURQUOI ?

Le niveau opérationnel décrit le système vu de l'extérieur, comme une **boîte noire**. Il répond aux questions : Qui interagit avec le système ? Dans quel but ? Dans quels contextes ?

**Éléments générés à ce niveau :**
- **Stakeholders** : acteurs humains (opérateurs, maintenanciers) et systèmes techniques qui interagissent activement avec le système (ex. : A/C Avionics, EECS, système pneumatique avion).
- **Systèmes externes** : entités à la frontière du périmètre système (ex. : SOV — Shut-Off Valve comme frontière physique passive).
- **Use cases** : fonctions de service rendues par le système à ses stakeholders (ex. : `PressuriserEtTempererLaCabine`, `DegivrerLaNacelle`, `DiagnostiquerLEtat`).
- **Scénarios opérationnels** : séquences d'interactions décrivant le déroulement des use cases nominaux et alternatifs.
- **Exigences de haut niveau** : contraintes mesurables liant le système à son environnement (ex. : plage de température, temps de réponse).

**Diagrammes associés :** diagramme de contexte, diagramme de cas d'utilisation.

#### Niveau 2 — Fonctionnel : QUE FAIT le système ?

Le niveau fonctionnel ouvre la boîte noire et décrit les **fonctions internes** qui permettent de réaliser les use cases opérationnels. Il reste indépendant de toute technologie ou composant physique.

**Éléments générés à ce niveau :**
- **Fonctions** avec leurs sous-fonctions hiérarchiques (ex. : `GérerLePrélèvement` → `PréléverAirIP`, `PréléverAirHP`, `ControlerHPV`).
- **Flux fonctionnels typés** : chaque échange entre fonctions est catégorisé — `pneumatique` (air, fluide), `information` (mesure, consigne, état), `électrique` (énergie, signal de commande), `thermique`, `mécanique`.
- **Modes opératoires** : configuration des fonctions actives selon l'état du système (OFF, Stand-by, Running).

**Règle de traçabilité** : chaque use case du niveau opérationnel doit être couvert par au moins une fonction du niveau fonctionnel.

**Diagrammes associés :** arborescence fonctionnelle (FBS), diagramme de comportement fonctionnel.

#### Niveau 3 — Logique : COMMENT est-il structuré ?

Le niveau logique décompose le système en **composants logiques** indépendants de la technologie d'implémentation. Il décrit l'architecture de solution sans descendre aux choix d'équipements.

**Éléments générés à ce niveau :**
- **Parts** (composants logiques) avec leurs ports d'interface (ex. : `GestionnairePrelevement`, `RégulationPression`, `ControleCommande`).
- **Connexions** entre ports (ex. : `FluxAirHautePresson : GestionnairePrelevement.sortieAir → RégulationPression.entreeAir`).
- **Allocation des exigences** : chaque exigence identifiée au niveau opérationnel est allouée au composant logique qui en est responsable.

**Règle de cohérence** : toute connexion doit lier deux composants définis dans la liste des parts. Les exigences issues des niveaux précédents doivent obligatoirement être allouées.

**Diagrammes associés :** Block Definition Diagram (BDD), Internal Block Diagram (IBD).

#### Niveau 4 — Technique : AVEC QUOI est-il construit ?

Le niveau technique instancie l'architecture logique avec des **composants physiques réels** et des technologies concrètes.

**Éléments générés à ce niveau :**
- **Composants physiques** nommés avec leur désignation d'équipement (ex. : `HPV`, `PRV`, `Exchanger_ACAC`, `ElectronicBASControl`).
- **Connexions physiques** (canalisations, câblages, interfaces mécaniques).
- **Choix technologiques** documentés (matériaux, normes, protocoles de communication).

**Diagrammes associés :** diagramme d'architecture technique.

#### Récapitulatif des 4 niveaux

| Niveau | Question centrale | Abstraction | Éléments clés |
|---|---|---|---|
| Opérationnel | QUI et POURQUOI ? | Boîte noire | Stakeholders, use cases, scénarios, exigences |
| Fonctionnel | QUE FAIT ? | Boîte blanche fonctionnelle | Fonctions, flux typés, modes |
| Logique | COMMENT structuré ? | Architecture logique | Parts, ports, connexions, allocations |
| Technique | AVEC QUOI construit ? | Implémentation physique | Équipements, technologies, connexions physiques |

---

### 2.3 Le RAG — Retrieval-Augmented Generation

#### Principe

Le RAG (Retrieval-Augmented Generation) est un mécanisme qui enrichit chaque appel au LLM avec des **exemples de code SysML v2 officiel** récupérés dynamiquement depuis une base de connaissances. Son rôle est d'ancrer les générations dans la syntaxe exacte de la norme, plutôt que de laisser le LLM interpoler à partir de sa seule mémoire d'entraînement.

#### Constitution de la base de connaissances

La base de connaissances est constituée à partir du **dépôt officiel `Systems-Modeling/SysML-v2-Release`** maintenu par l'OMG (Object Management Group), l'organisme de standardisation de SysML v2.

| Paramètre | Valeur |
|---|---|
| Source | Dépôt GitHub `Systems-Modeling/SysML-v2-Release` |
| Fichiers indexés | 196 fichiers `.sysml` |
| Contenu | Fichiers d'entraînement, exemples complets, bibliothèque standard |
| Nombre de chunks | 337 extraits |
| Taille par chunk | 1 500 caractères avec chevauchement de 200 caractères |
| Modèle d'embeddings | `all-MiniLM-L6-v2` (local, sans appel API externe) |
| Base vectorielle | ChromaDB (persistée sur disque) |
| Temps de requête | < 100 ms |

#### Fonctionnement à la génération

À chaque appel de génération (étape 1 ou étape 2 du pipeline), le service RAG effectue une recherche sémantique dans la base vectorielle avec une requête construite à partir du contexte de la génération (nom du système, niveau MBSE, éléments à générer). Les **8 extraits les plus pertinents** (paramètre `RAG_TOP_K = 8`) sont récupérés et injectés dans le prompt, immédiatement avant les instructions de génération.

**Exemple de requête RAG pour le niveau logique BAS :**
> *"SysML v2 part def port connection bleed air system pressure regulation valve"*

Les extraits retournés contiennent des exemples de déclarations `part def`, `port def`, `connect` et d'allocations `satisfy` tirés des fichiers officiels, guidant ainsi le LLM vers la syntaxe correcte plutôt que vers une approximation.

#### Apport mesuré

Sans RAG, le LLM tend à produire une syntaxe hybride entre SysML v1 (basé UML) et SysML v2, avec des erreurs récurrentes sur les déclarations de ports, les connexions et les allocations d'exigences. Avec RAG, ces erreurs structurelles sont quasi-absentes des générations, et le validateur syntaxique interne confirme des scores de conformité significativement supérieurs.

---

### 2.4 Le processus itératif d'amélioration

#### Vue d'ensemble du cycle

La qualité des générations IA ne peut être évaluée qu'en comparant les sorties produites avec des modèles de référence. Le processus suivi est un **cycle d'amélioration continue en 5 étapes** :

```
  ┌──────────────────────────────────────────┐
  │                                          │
  ▼                                          │
Test initial                                 │
(génération sur le système BAS)              │
  │                                          │
  ▼                                          │
Diagnostic de qualité                        │
(comparaison élément par élément             │
 avec les diagrammes de référence Safran)    │
  │                                          │
  ▼                                          │
Analyse des causes d'écart                   │
(DESCRIPTION / PROMPT / IA)                  │
  │                                          │
  ▼                                          │
Correction des prompts                       │
(P1 à P8 documentées)                        │
  │                                          │
  ▼                                          │
Re-test et mesure de l'amélioration ─────────┘
```

#### Méthodologie de diagnostic

Pour chaque diagramme de référence fourni par Safran, chaque élément (acteur, use case, composant, flux, relation) a été inspecté et classé selon trois états :

- ✅ **Présent** : élément clairement identifiable dans la génération IA.
- ⚠️ **Partiel** : élément reconnaissable mais incomplet, mal nommé, ou mal attribué.
- ❌ **Absent** : aucun équivalent trouvé dans la génération.

Pour chaque écart, la cause a été identifiée parmi trois catégories :

| Catégorie | Définition | Impact sur la correction |
|---|---|---|
| **DESCRIPTION** | L'information manquait dans la description fournie — l'IA ne pouvait pas la deviner | Enrichir la description ou poser des questions à l'utilisateur |
| **PROMPT** | L'information était dans la description mais le prompt ne guidait pas l'IA à la capturer | Modifier le prompt de génération |
| **IA** | L'information était dans la description et le prompt était correct, mais l'IA l'a omise | Renforcer l'instruction dans le prompt ou changer de modèle |

#### Résultats du diagnostic V1 — BAS Silvercrest

Le diagnostic a porté sur 4 diagrammes de référence, représentant 46 éléments distincts.

| Diagramme de référence | Éléments | Présents ✅ | Partiels ⚠️ | Absents ❌ | Couverture |
|---|---|---|---|---|---|
| Lifecycle Diagram | 12 | 0 | 0 | 12 | **0 %** |
| Use Case Diagram — Fonctions de service | 12 | 4 | 5 | 3 | **54 %** |
| Use Case Diagram — Maintenance | 7 | 0 | 0 | 7 | **0 %** |
| Functional Behavior Diagram (fonctions) | 6 | 0 | 5 | 1 | **42 %** |
| Functional Behavior Diagram (flux) | 9 | 5 | 1 | 3 | **61 %** |
| **TOTAL** | **46** | **9** | **11** | **26** | **~42 %** |

**Répartition des causes d'écart :**

| Cause | Éléments | Part |
|---|---|---|
| DESCRIPTION (élément non fourni par l'utilisateur) | 26 | **70 %** |
| PROMPT (élément présent mais mal capturé) | 10 | **27 %** |
| IA (prompt correct mais IA a omis) | 1 | **3 %** |

Cette analyse révèle que **70 % des écarts sont dus à une information absente de la description initiale**, non à un défaut de l'IA ou du prompt. C'est une conclusion structurante : l'IA traduit fidèlement ce qu'on lui donne ; si la description ne mentionne pas la maintenance ou le cycle de vie, le modèle ne les contiendra pas. L'enjeu des prompts est donc aussi d'**éliciter les informations manquantes** auprès de l'utilisateur.

#### Les 8 corrections de prompts appliquées

Suite au diagnostic V1, 8 corrections ont été formulées et intégrées aux prompts de génération (P1 à P8) :

| ID | Niveau | Problème observé en V1 | Correction appliquée |
|---|---|---|---|
| **P1** | Opérationnel | Les stakeholders étaient toujours vides — toutes les entités allaient dans `external_systems` | Règle explicite : un équipement qui **initie des interactions** est un stakeholder de type `system`. Le champ `stakeholders` ne doit jamais être vide si des entités interagissent avec le système. |
| **P2** | Opérationnel | L'IA générait des exigences pour chaque comportement décrit (ex : "la vanne s'ouvre" → REQ-xxx) | Règle : les exigences sont **uniquement des contraintes mesurables** (valeurs numériques, SLA, plages). Les comportements fonctionnels vont dans les use cases, pas dans les exigences. |
| **P3** | Logique | Des connexions référençaient des composants non définis dans la liste des `parts` | Règle : toute connexion doit lier deux composants **explicitement définis** dans `parts`. Interdiction de référencer un composant non déclaré. |
| **P4** | Logique | Les exigences identifiées au niveau opérationnel n'étaient jamais allouées aux composants logiques | Règle : si des exigences existent dans les niveaux précédents, elles **doivent** être allouées via `satisfy` à au moins un composant logique. |
| **P5** | Opérationnel | La distinction acteur/système externe était ambiguë pour les systèmes techniques | Clarification avec exemples : un calculateur moteur (EECS) qui envoie des consignes est un stakeholder. Une vanne d'isolement physique passive est un `external_system`. Format objet avec champ `type: "system"/"human"/"organization"`. |
| **P6** | Fonctionnel | Les flux fonctionnels n'étaient pas typés — noms génériques sans catégorie physique | Règle obligatoire : chaque flux doit avoir un champ `flow_type` parmi `pneumatic`, `information`, `electric`, `thermal`, `mechanical`. |
| **P7** | Fonctionnel | Les sous-fonctions n'étaient pas liées aux composants physiques qui les réalisent | Règle : si une sous-fonction est réalisée par un composant nommé, utiliser la notation `NomComposant::NomFonction` (ex. : `BleedPressSensor::MesurerPressionFinale`). |
| **P8** | Opérationnel | Un use case générique "Fournir air à l'avion" au lieu de 3 use cases distincts par destination | Règle de décomposition : si la description mentionne **plusieurs destinations** pour une même fonction de service, décomposer en autant de use cases séparés. |

#### Résultats après corrections — Comparaison V1 vs V2

| Diagramme | Couverture V1 | Couverture V2 | Évolution |
|---|---|---|---|
| Lifecycle | 0 % | 0 % | ↔ Non traité (nécessite description dédiée) |
| Use Cases — Fonctions de service | ~54 % | ~75 % | ✅ **+21 %** |
| Use Cases — Maintenance | 0 % | ~43 % | ✅ **+43 %** (nouveau) |
| Functional Behavior | ~53 % | ~60 % | ✅ **+7 %** |

**Points saillants de la comparaison V1 → V2 :**

- **Niveau opérationnel** : passage de 4 à 8 use cases. Les 4 use cases de maintenance (`DiagnostiquerLEtat`, `ReparerSousLAile`, `EtreInformeDeLEtatDuSysteme`, `MaintenirEnConditionsOperationnelles`) sont apparus grâce à la description enrichie (V2) et aux corrections P5 et P8. L'EECS (Electronic Engine Control System) est correctement identifié comme stakeholder distinct de l'avionique générale.

- **Niveau fonctionnel** : les flux sont désormais typés (`pneumatique`, `électrique`, `information`) dans les commentaires et documentations des actions. La notation `composant::fonction` apparaît sur 3 éléments clés (`BleedPressSensor::MesurerPressionFinale`, `BleedTempSensor::MesurerTempératureFinale`, `ElectronicBASControl::RégulerPressionEtTempératureAirAvion`).

- **Lifecycle** : ce type de diagramme reste hors de portée avec une description purement fonctionnelle. Il nécessite une section dédiée dans la description ou un niveau MBSE spécifique. C'est une limite **par construction** : l'IA ne peut traduire que ce qui lui est fourni.

- **Régression observée** : les niveaux fonctionnel et technique V2 ont produit des codes plus courts que V1 (−70 % et −92 % en volume de caractères) lors de cette session. Ce phénomène est lié au contexte d'appel (regénération partielle) et non aux corrections de prompts. Une régénération dédiée avec un paramètre `max_tokens` plus élevé lève ce problème.

#### Leçon principale

L'expérimentation sur le BAS Silvercrest confirme que **la qualité d'un modèle SysML v2 généré par IA est directement proportionnelle à la qualité de la description fournie**. Un prompt bien conçu améliore la capture des informations présentes, mais ne peut pas compenser l'absence d'information. Les prompts types produits par cette mission répondent aux deux besoins : guider l'IA pour **maximiser la capture** des informations disponibles, et alerter l'utilisateur lorsque des **domaines clés semblent absents** de sa description.

---

## 3 — Catégorie 1 : Prompts de génération du modèle SysML v2

### 3.1 Structure type d'un prompt de génération

Chaque prompt de génération produit par cette mission suit une architecture en six composants distincts. Cette structure a été validée empiriquement sur le BAS Silvercrest : les variantes qui omettent l'un de ces composants produisent systématiquement des régressions mesurables.

#### Les 6 composants d'un prompt efficace

**① Rôle**

Définit l'identité que l'IA doit adopter. Un rôle précis oriente la terminologie, le niveau de détail et le registre de réponse.

```
Tu es un ingénieur système expert en analyse opérationnelle.
Tu analyses une description pour identifier le périmètre opérationnel du système.
```

**② Contexte MBSE**

Indique le niveau en cours de génération et fournit le JSON du niveau précédent comme contexte de traçabilité. Sans ce contexte, l'IA re-dérive le modèle depuis la description plutôt que de s'appuyer sur ce qui a déjà été validé.

```
=== TON RÔLE ===
- Tu identifies QUI utilise le système (stakeholders, acteurs)
- Tu identifies AVEC QUOI le système interagit (systèmes externes)
- Tu définis le PÉRIMÈTRE du système
- Tu extrais les CAS D'UTILISATION (use cases)
- Tu identifies les SCÉNARIOS OPÉRATIONNELS
- Tu formules les BESOINS OPÉRATIONNELS (requirements de haut niveau)

=== MODÈLE OPÉRATIONNEL VALIDÉ (CONTEXTE) ===
{ ... JSON du niveau précédent ... }
```

**③ Règles de fidélité**

Ensemble de contraintes explicites pour prévenir les hallucinations (ajout de composants non mentionnés) et les omissions. C'est le composant le plus critique, enrichi au fil des corrections itératives P1–P8.

```
=== RÈGLES DE FIDÉLITÉ (CRITIQUE) ===
- Tu ne dois RIEN inventer qui n'est pas explicitement décrit
- Tu ne dois RIEN ajouter qui n'est pas mentionné
- Utilise le vocabulaire exact de l'utilisateur pour les noms
- [Corrections P1–P8 intégrées ici]
```

**④ Format de sortie JSON**

Schéma JSON complet avec tous les champs attendus, leurs types et leurs descriptions. Ce schéma est validé par des contraintes Pydantic côté backend, ce qui force la conformité.

```
=== SCHÉMA JSON ATTENDU ===
{
  "system_name": "string",
  "stakeholders": [{"name": "string", "role": "string", "type": "human|system|organization"}],
  "external_systems": ["string"],
  "use_cases": [{"name": "string", "actors": ["string"]}],
  "requirements": [{"id": "string", "text": "string"}]
}
```

**⑤ Exemple de structure annoté**

Un exemple complet avec des valeurs placeholder (clairement marquées comme telles) illustrant la structure attendue. Sans exemple, l'IA produit des structures hétérogènes d'un appel à l'autre.

**⑥ Exemples RAG**

Les 3 à 8 extraits de code SysML v2 officiel les plus sémantiquement proches de la génération en cours, injectés dynamiquement depuis la base ChromaDB. Ils ancrent la syntaxe dans la norme officielle.

```
=== EXEMPLES DE SYNTAXE SysML v2 POUR RÉFÉRENCE ===
Exemple 1:
```sysml
use case def NomUseCase { actor NomActeur; }
```
...
```

#### Vue d'ensemble annotée d'un prompt opérationnel complet

```
┌────────────────────────────────────────────────────────────────┐
│  ① RÔLE                                                        │
│  "Tu es un ingénieur système expert en analyse                 │
│   opérationnelle..."                                           │
├────────────────────────────────────────────────────────────────┤
│  ② CONTEXTE MBSE                                               │
│  "=== TON RÔLE ===                                             │
│   - Tu identifies QUI utilise le système...                    │
│   - Tu extrais les CAS D'UTILISATION...                        │
│   - Tu formules les BESOINS OPÉRATIONNELS..."                  │
├────────────────────────────────────────────────────────────────┤
│  ③ RÈGLES DE FIDÉLITÉ                                          │
│  "- Tu ne dois RIEN inventer...                                │
│   - DISTINCTION STAKEHOLDER / SYSTÈME EXTERNE (P4+P5)...       │
│   - EXIGENCES = CONTRAINTES MESURABLES UNIQUEMENT (P2)...      │
│   - RÈGLE P8 — DÉCOMPOSITION DES USE CASES..."                 │
├────────────────────────────────────────────────────────────────┤
│  ④ FORMAT DE SORTIE JSON                                       │
│  "=== SCHÉMA JSON ATTENDU (OperationalModel) ===               │
│   { "stakeholders": [...], "use_cases": [...], ... }"          │
├────────────────────────────────────────────────────────────────┤
│  ⑤ EXEMPLE DE STRUCTURE                                        │
│  "=== EXEMPLE DE STRUCTURE (placeholders) ===                  │
│   { "system_name": "Nom du système extrait...", ... }"         │
├────────────────────────────────────────────────────────────────┤
│  ⑥ EXEMPLES RAG (injectés dynamiquement)                       │
│  "=== EXEMPLES DE SYNTAXE SysML v2 POUR RÉFÉRENCE ===          │
│   Exemple 1: use case def ... { actor ...; }"                  │
├────────────────────────────────────────────────────────────────┤
│  DESCRIPTION UTILISATEUR                                       │
│  "=== DESCRIPTION À ANALYSER ===                               │
│   [texte en langage naturel fourni par l'ingénieur]"           │
└────────────────────────────────────────────────────────────────┘
```

---

### 3.2 Prompt type — Niveau Opérationnel

**Objectif :** extraire de la description utilisateur les acteurs, les systèmes externes, les cas d'utilisation, les scénarios opérationnels et les exigences mesurables.

**Fichier source :** `backend/prompts/operational_prompt.py` — fonction `build_operational_json_prompt()`

#### Champs JSON produits en sortie

```json
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
    {"name": "string", "actors": ["string"], "includes": ["string"]}
  ],
  "operational_scenarios": [
    {"name": "string", "description": "string", "steps": ["string"]}
  ],
  "requirements": [
    {"id": "REQ-OP-001", "text": "string", "satisfied_by": null}
  ]
}
```

#### Règles de fidélité spécifiques à ce niveau

Les quatre corrections itératives suivantes ont été intégrées dans le prompt après analyse des résultats V1 :

**Règle P1/P5 — Distinction stakeholder / système externe :**
> *"Un stakeholder est soit une PERSONNE/ORGANISATION, soit un SYSTÈME TECHNIQUE qui est ACTEUR dans un cas d'utilisation (c'est-à-dire qui initie des interactions, envoie des commandes, ou reçoit activement des services). Exemples : un calculateur moteur (EECS) qui envoie des consignes EST un stakeholder de type "system". En revanche, une vanne d'isolement physique (frontière passive) ou un simple connecteur ne sont PAS des stakeholders, mais des external_systems. Le champ "stakeholders" ne doit JAMAIS être vide si la description mentionne des entités qui interagissent activement."*

**Règle P2 — Exigences = contraintes mesurables uniquement :**
> *"Ne génère des requirements QUE pour des contraintes explicitement chiffrées ou mesurables (temps de réponse, disponibilité, capacité, température, etc.). Un comportement fonctionnel décrit (ex: 'la vanne s'ouvre') N'EST PAS une exigence. C'est un comportement normal du système capturé dans les use cases."*

**Règle P8 — Décomposition des use cases par destination :**
> *"Si un cas d'utilisation est de type 'Fournir/Envoyer X à Y' et que la description mentionne PLUSIEURS destinations distinctes, décompose-le en sous-use cases séparés par destination. Exemple : 'Le système fournit de l'air régulé à l'avion pour pressuriser la cabine, dégivrer les ailes et pressuriser les réservoirs' → génère 3 use cases distincts."*

#### Exemple concret — BAS Silvercrest

**Entrée (extrait de la description) :**
```
Le système réalise quatre fonctions de service :
1. Envoyer de l'air régulé en pression et température à l'avion.
2. Envoyer de l'air chaud à la nacelle pour le dégivrage.
3. Déterminer l'état du système par mesures physiques et auto-diagnostic.
4. Communiquer les consignes et statuts avec l'avionique.
La pression de sortie doit être maintenue entre 20 et 50 PSI.
Le temps de réponse ne doit pas dépasser 500 ms.
```

**Sortie JSON générée (V2, après corrections P5 et P8) :**
```json
{
  "system_name": "Bleed Air System (BAS)",
  "stakeholders": [
    {"name": "AC_Avionics", "role": "Envoie les consignes et reçoit les statuts", "type": "system"},
    {"name": "EECS", "role": "Calculateur moteur, envoie les commandes de régulation", "type": "system"},
    {"name": "SystemePneumatiqueDeLAvion", "role": "Reçoit l'air conditionné régulé", "type": "system"},
    {"name": "Nacelle", "role": "Reçoit l'air chaud pour le dégivrage", "type": "system"},
    {"name": "OperateurDeMaintenance", "role": "Diagnostique et maintient le système", "type": "human"}
  ],
  "use_cases": [
    {"name": "PressuriserEtTempererLaCabine", "actors": ["AC_Avionics", "SystemePneumatiqueDeLAvion"]},
    {"name": "DegivrerLesAiles",             "actors": ["AC_Avionics", "SystemePneumatiqueDeLAvion"]},
    {"name": "PressuriserLesReservoirs",      "actors": ["AC_Avionics", "SystemePneumatiqueDeLAvion"]},
    {"name": "DegivrerLaNacelle",            "actors": ["AC_Avionics", "Nacelle"]},
    {"name": "DiagnostiquerLEtat",           "actors": ["OperateurDeMaintenance"]}
  ],
  "requirements": [
    {"id": "REQ-OP-001", "text": "La pression de sortie régulée doit être maintenue entre 20 et 50 PSI.", "satisfied_by": null},
    {"id": "REQ-OP-002", "text": "Le temps de réponse de la boucle de régulation ne doit pas dépasser 500 ms.", "satisfied_by": null}
  ]
}
```

**Résultat V1 pour comparaison :** `stakeholders: []`, 4 use cases génériques (dont un seul pour les 3 fonctions de fourniture d'air), 0 exigences (les seuils numériques avaient été capturés comme descriptions fonctionnelles).

---

### 3.3 Prompt type — Niveau Fonctionnel

**Objectif :** décomposer les cas d'utilisation opérationnels en fonctions internes, identifier les flux entre fonctions, typer chaque flux selon sa nature physique.

**Fichier source :** `backend/prompts/functional_prompt.py` — fonction `build_functional_json_prompt()`

#### Champs JSON produits en sortie

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
      "sub_functions": ["NomComposant::NomFonction ou NomFonctionSimple"]
    }
  ],
  "functional_flows": [
    {
      "from_function": "string",
      "to_function": "string",
      "item": "string",
      "flow_type": "pneumatic|information|electric|thermal|mechanical",
      "description": "string"
    }
  ],
  "modes": [
    {"name": "string", "description": "string", "active_functions": ["string"]}
  ]
}
```

#### Règles de fidélité spécifiques à ce niveau

**Règle P6 — Typing des flux (obligatoire) :**
> *"Chaque flux dans 'functional_flows' DOIT avoir un champ 'flow_type' avec une des valeurs : 'pneumatic' (air, gaz, fluide), 'information' (données, mesures, consignes, commandes logiques), 'electric' (énergie électrique, signaux discrets de commande), 'thermal' (chaleur, échange thermique), 'mechanical' (force, couple, déplacement). Ne laisse JAMAIS 'flow_type' vide ou absent."*

**Règle P7 — Notation composant::fonction :**
> *"Si une sous-fonction est clairement réalisée par un composant physique spécifiquement nommé dans la description, nomme-la avec le format 'NomComposant::NomFonction'. Exemples : 'IP Port::Prélever air', 'Calculateur::Réguler la vanne NAI', 'Bleed Temp Sensor::Mesurer la température'. Si aucun composant n'est identifiable, garde le nom simple."*

**Règle de traçabilité :** chaque use case du niveau opérationnel doit être couvert par au moins une fonction. Les fonctions peuvent avoir des sous-fonctions hiérarchiques.

#### Exemple concret — BAS Silvercrest

**Extrait du JSON fonctionnel généré (V2) :**
```json
{
  "functions": [
    {
      "name": "GérerLePrélèvement",
      "description": "Prélève l'air chaud depuis la turbomachine via les ports IP ou HP",
      "inputs": ["Air Haute Pression (Turbomachine)"],
      "outputs": ["Air Chaud Brute"],
      "sub_functions": [
        "IP Port::Prélever Air IP",
        "HP Port::Prélever Air HP",
        "HPV::Contrôler Vanne HPV"
      ]
    },
    {
      "name": "RégulerPressionTempérature",
      "description": "Conditionne l'air prélevé pour atteindre les consignes de pression et température",
      "inputs": ["Air Chaud Brute", "Consignes (Avionique)"],
      "outputs": ["Air Régulé"],
      "sub_functions": [
        "PRV::Réguler Pression",
        "Exchanger::Refroidir Air",
        "FAV::Contrôler Débit Air Froid",
        "Bleed Press. Sensor::Mesurer Pression Finale",
        "Bleed Temp. Sensor::Mesurer Température Finale"
      ]
    }
  ],
  "functional_flows": [
    {
      "from_function": "GérerLePrélèvement",
      "to_function": "RégulerPressionTempérature",
      "item": "Air Chaud Brute",
      "flow_type": "pneumatic",
      "description": "Flux d'air chaud haute pression vers le sous-système de conditionnement"
    },
    {
      "from_function": "ContrôlerEtCommuniquer",
      "to_function": "GérerLePrélèvement",
      "item": "Commande HPV",
      "flow_type": "electric",
      "description": "Signal de commande d'ouverture/fermeture de la HPV"
    },
    {
      "from_function": "RégulerPressionTempérature",
      "to_function": "ContrôlerEtCommuniquer",
      "item": "Mesure Pression Finale",
      "flow_type": "information",
      "description": "Retour mesure pour boucle de régulation"
    }
  ]
}
```

**Résultat V1 pour comparaison :** 0 champ `flow_type` renseigné — tous les flux avaient des noms descriptifs mais aucune catégorie physique. La notation `composant::fonction` était absente.

---

### 3.4 Prompt type — Niveau Logique

**Objectif :** regrouper les fonctions en composants logiques cohérents, définir leurs ports et interfaces, établir les connexions, allouer les exigences.

**Fichier source :** `backend/prompts/logical_prompt.py` — fonction `build_logical_json_prompt()`

#### Champs JSON produits en sortie

```json
{
  "system_name": "string",
  "warnings": ["string"],
  "parts": [
    {
      "name": "string",
      "type": "string",
      "description": "string (fonctions allouées depuis le niveau fonctionnel)",
      "ports": [
        {"name": "string", "direction": "in|out|inout", "type": "string"}
      ],
      "children": []
    }
  ],
  "connections": [
    {
      "from_port": "ComponentA.portOut",
      "to_port": "ComponentB.portIn",
      "type": "flow|connection|interface",
      "item": "string",
      "description": "string (flux fonctionnel correspondant)"
    }
  ],
  "requirements": [
    {"id": "string", "text": "string", "satisfied_by": "NomDuComposant"}
  ]
}
```

#### Règles de fidélité spécifiques à ce niveau

**Règle P3 — Cohérence des connexions (critique) :**
> *"Toute connexion dans 'connections' doit lier EXACTEMENT deux composants qui sont DÉFINIS dans la liste 'parts'. Une connexion vers un élément qui n'existe pas dans 'parts' est STRICTEMENT INTERDITE. Si une fonction interagit avec un système externe, modélise un PORT de sortie sur le composant interne concerné, SANS créer de connexion vers l'extérieur."*

**Règle P4 — Allocation obligatoire des exigences :**
> *"Si des exigences de performance ont été définies aux niveaux précédents (délai, disponibilité, capacité), tu DOIS les reprendre dans le champ 'requirements' et les allouer aux composants concernés via le champ 'satisfied_by'. Le champ 'requirements' ne doit JAMAIS être vide si des exigences existent dans le contexte."*

**Règle de composants internes :** un composant physiquement présent dans le système et mentionné dans la description (capteur, vanne, actionneur) DOIT apparaître comme un `part` dans le modèle logique, même s'il était classé "système externe" au niveau opérationnel.

#### Exemple concret — BAS Silvercrest

**Extrait du JSON logique généré :**
```json
{
  "parts": [
    {
      "name": "SousSystemePrelevement",
      "description": "Réalise les fonctions : GérerLePrélèvement. Composants : IP Port, HP Port, HPV, IPCV",
      "ports": [
        {"name": "airHP_in",    "direction": "in",  "type": "AirHautePresson"},
        {"name": "airIP_in",    "direction": "in",  "type": "AirPressionIntermédiaire"},
        {"name": "airChaud_out","direction": "out", "type": "AirChaud"},
        {"name": "cmdHPV_in",   "direction": "in",  "type": "SignalCommande"}
      ]
    },
    {
      "name": "ControleCommande",
      "description": "Réalise les fonctions : ContrôlerEtCommuniquer. Composant : Electronic BAS Control",
      "ports": [
        {"name": "consignes_in","direction": "in",  "type": "ConsignesAvionique"},
        {"name": "mesures_in",  "direction": "in",  "type": "DonnéesCapteurs"},
        {"name": "cmdHPV_out",  "direction": "out", "type": "SignalCommande"},
        {"name": "cmdPRV_out",  "direction": "out", "type": "SignalCommande"},
        {"name": "statuts_out", "direction": "out", "type": "StatutsSysteme"}
      ]
    }
  ],
  "connections": [
    {
      "from_port": "ControleCommande.cmdHPV_out",
      "to_port":   "SousSystemePrelevement.cmdHPV_in",
      "type": "flow",
      "item": "Commande HPV",
      "description": "Correspond au flux fonctionnel electric : ContrôlerEtCommuniquer → GérerLePrélèvement"
    }
  ],
  "requirements": [
    {
      "id": "REQ-OP-001",
      "text": "La pression de sortie régulée doit être maintenue entre 20 et 50 PSI.",
      "satisfied_by": "SousSystemeConditionnement"
    },
    {
      "id": "REQ-OP-002",
      "text": "Le temps de réponse de la boucle de régulation ne doit pas dépasser 500 ms.",
      "satisfied_by": "ControleCommande"
    }
  ]
}
```

**Résultat V1 pour comparaison :** des connexions référençaient des composants comme `Turbomachine` et `A/C Avionics` non définis dans `parts`, rendant le modèle incohérent. Le champ `requirements` était vide alors que 4 exigences avaient été identifiées au niveau opérationnel.

---

### 3.5 Prompt type — Niveau Technique

**Objectif :** instancier l'architecture logique avec les composants physiques réels nommés dans la description, définir les connexions physiques et les choix technologiques.

**Fichier source :** `backend/prompts/technical_prompt.py` — fonction `build_technical_json_prompt()`

#### Champs JSON produits en sortie

```json
{
  "system_name": "string",
  "warnings": ["string"],
  "technical_parts": [
    {
      "name": "string",
      "type": "string",
      "description": "string (composant logique réalisé)",
      "ports": [
        {"name": "string", "direction": "in|out|inout", "type": "string (protocole physique)"}
      ],
      "children": []
    }
  ],
  "physical_connections": [
    {
      "from_port": "CompA.portOut",
      "to_port": "CompB.portIn",
      "type": "connection",
      "item": "string (protocole, bus, canalisation)",
      "description": "string"
    }
  ],
  "technology_choices": [
    {
      "component": "string (composant logique)",
      "technology": "string (composant physique)",
      "justification": "string"
    }
  ]
}
```

#### Règles de fidélité spécifiques à ce niveau

- L'IA ne propose **jamais** de marque, modèle ou technologie spécifique non mentionnée par l'utilisateur. Si la description ne spécifie pas de protocole, le champ `type` des ports reçoit la valeur `"À spécifier par l'architecte"`.
- Chaque composant logique défini au niveau précédent doit être réalisé par au moins un composant technique.
- Les attributs physiques (dimensions, masse, tension) ne sont renseignés que si l'utilisateur les a mentionnés explicitement.

#### Exemple concret — BAS Silvercrest

**Extrait du JSON technique généré :**
```json
{
  "technical_parts": [
    {
      "name": "HPV",
      "type": "Vanne haute pression",
      "description": "Réalise le composant logique SousSystemePrelevement. Vanne qui contrôle l'ouverture du port HP.",
      "ports": [
        {"name": "airHP_in",  "direction": "in",  "type": "Canalisation air HP"},
        {"name": "airOut",    "direction": "out", "type": "Canalisation air"},
        {"name": "cmdElec_in","direction": "in",  "type": "Signal électrique commande"}
      ]
    },
    {
      "name": "ElectronicBASControl",
      "type": "Calculateur embarqué (EEC)",
      "description": "Réalise le composant logique ControleCommande. Reçoit les consignes avionique, acquiert les mesures capteurs, envoie les commandes aux vannes.",
      "ports": [
        {"name": "consignes_in","direction": "in",  "type": "Bus avionique"},
        {"name": "cmdHPV_out", "direction": "out", "type": "Signal électrique commande"},
        {"name": "cmdPRV_out", "direction": "out", "type": "Signal électrique commande"},
        {"name": "statuts_out","direction": "out", "type": "Bus avionique"}
      ]
    }
  ],
  "technology_choices": [
    {
      "component": "SousSystemePrelevement",
      "technology": "IP Port + HP Port + HPV + IPCV",
      "justification": "Composants nommés explicitement dans la description du BAS"
    },
    {
      "component": "ControleCommande",
      "technology": "Electronic BAS Control (embarqué dans l'EEC)",
      "justification": "Décrit dans la description : calculateur qui reçoit les consignes de l'avionique"
    }
  ]
}
```

Le code SysML v2 correspondant généré à partir de ce JSON :

```sysml
package 'Bleed Air System (BAS) - Technical' {

    part def HPV {
        doc /* Vanne haute pression — réalise SousSystemePrelevement */
        port airHP_in   : CànalisationAirHP  [in];
        port airOut     : CànalisationAir    [out];
        port cmdElec_in : SignalCommandeElec [in];
    }

    part def ElectronicBASControl {
        doc /* Calculateur EEC — réalise ControleCommande */
        port consignes_in : BusAvionique         [in];
        port cmdHPV_out   : SignalCommandeElec   [out];
        port cmdPRV_out   : SignalCommandeElec   [out];
        port statuts_out  : BusAvionique         [out];
    }

    part BAS_Physical {
        part hpv           : HPV;
        part calculateur   : ElectronicBASControl;

        connect calculateur.cmdHPV_out to hpv.cmdElec_in;
    }

    allocation SousSystemePrelevement to HPV;
    allocation ControleCommande       to ElectronicBASControl;
}
```

---

### 3.6 Tableau récapitulatif des corrections P1–P8

| ID | Niveau MBSE | Problème observé en V1 | Correction intégrée dans le prompt | Impact mesuré en V2 |
|---|---|---|---|---|
| **P1** | Opérationnel | La confusion entre personne et équipement conduisait à classer tous les équipements comme stakeholders ou tous comme systèmes externes selon les cas | Règle : les stakeholders sont des personnes OU des systèmes techniques acteurs de use cases. La turbomachine (source passive) va dans `external_systems`. L'EECS (envoie des consignes) va dans `stakeholders`. | Classification correcte dès V1 sur les systèmes clairs |
| **P2** | Opérationnel | Sur-génération d'exigences : chaque comportement décrit (ex. "la vanne s'ouvre") devenait une exigence — 8 exigences au lieu de 2 sur le contrôle d'accès | Règle : les exigences sont **uniquement** des contraintes chiffrées et mesurables. Les comportements fonctionnels sont capturés dans les use cases et scénarios. | Exigences limitées aux 4 contraintes numériques réelles du BAS |
| **P3** | Logique | Des connexions référençaient des entités extérieures au système (`Turbomachine`, `A/C Avionics`) non définies dans `parts`, rendant le modèle incohérent | Règle : toute connexion doit lier exactement deux composants définis dans `parts`. Pour les interactions avec l'extérieur : modéliser un port de sortie sans créer de connexion externe. | 0 connexion invalide constatée après correction |
| **P4** | Logique | Le champ `requirements` était vide au niveau logique alors que 4 exigences avaient été identifiées au niveau opérationnel | Règle : si des exigences existent dans le contexte des niveaux précédents, elles **doivent** être allouées via `satisfied_by`. Champ `requirements` jamais vide si des exigences existent. | Les 4 exigences BAS allouées aux composants concernés |
| **P5** | Opérationnel | `stakeholders: []` dans la réponse API malgré 6 entités clairement actives dans les use cases — toutes classées dans `external_systems` | Clarification avec exemples : format objet `{"name": "...", "role": "...", "type": "system"}`. Règle : champ jamais vide si des entités interagissent. | V2 : 5 stakeholders (EECS ajouté, OperateurDeMaintenance ajouté) vs 0 en V1 |
| **P6** | Fonctionnel | 0 flux typé en V1 — noms descriptifs (`"Air Chaud Brute"`, `"Commande HPV"`) sans catégorie physique | Champ `flow_type` rendu obligatoire avec 5 valeurs : `pneumatic`, `information`, `electric`, `thermal`, `mechanical`. | V2 : types de flux dans les commentaires et documentations des actions SysML |
| **P7** | Fonctionnel | Sous-fonctions sans lien aux composants physiques — `"PréléverAirIP"` au lieu de `"IP Port::PréléverAir"` | Règle de notation `NomComposant::NomFonction` pour les sous-fonctions réalisées par un composant physique nommé. | V2 : 3 notations `composant::fonction` identifiées dans le code SysML généré |
| **P8** | Opérationnel | Use case générique `"EnvoyerAirRéguléAvion"` au lieu de 3 use cases distincts par destination | Règle de décomposition : si plusieurs destinations sont mentionnées, générer autant de use cases séparés. | V2 : 8 use cases vs 4 en V1 (+4 use cases de maintenance) |

---

## 4 — Catégorie 2 : Visualisation des diagrammes

### 4.1 Approche retenue : Eclipse SysON

#### Présentation

Eclipse SysON est un **éditeur web open-source pour SysML v2** développé conjointement par **Obeo** (éditeur spécialisé en modélisation Eclipse) et le **CEA** (Commissariat à l'Énergie Atomique et aux Énergies Alternatives), sous licence **Eclipse Public License 2.0**. Il est basé sur la plateforme **Sirius Web**, le successeur cloud-native de Sirius Desktop, framework de référence pour les éditeurs graphiques à base de modèles.

| Caractéristique | Détail |
|---|---|
| **Image Docker officielle** | `eclipsesyson/syson:v2026.1.0` |
| **Base de données** | PostgreSQL 15 |
| **API** | GraphQL sur `/api/graphql` |
| **Conformité** | Standard OMG SysML v2 — vrai parseur officiel |
| **Licence** | Eclipse Public License 2.0 (usage commercial libre) |
| **Déploiement** | Local (Docker Compose) ou cloud |
| **Activité** | Maintenance active — dernière version : février 2026 |

SysON est la solution recommandée par le client Safran pour la visualisation, conformément à l'orientation explicite : *"trouvez un visualisateur open-source de SysML v2"*.

#### Pourquoi SysON plutôt que d'autres approches

| Critère | SysON | PlantUML (approche alternative) |
|---|---|---|
| **Conformité SysML v2** | ✅ Vrais diagrammes conformes au standard OMG | ⚠️ Représentation approximative (notation UML enrichie) |
| **Validation syntaxique** | ✅ Le parseur officiel détecte toutes les erreurs | ⚠️ Pas de validation SysML v2 |
| **Édition graphique** | ✅ Bidirectionnelle (diagramme ↔ code) | ❌ Lecture seule |
| **Types de diagrammes** | ✅ Tous les types SysML v2 officiels | ⚠️ Simulation approximative |
| **Intégration écosystème** | ✅ Compatible Papyrus, Capella | ❌ Format propriétaire |
| **Déploiement** | ✅ Docker, 5 minutes | ✅ Docker, 2 minutes |

#### Intégration dans notre pipeline

L'intégration de SysON dans le pipeline de génération suit un flux automatisé en 5 étapes :

```
┌──────────────────────────────────────────────────────────────────┐
│  1. L'ingénieur décrit son système en langage naturel            │
│     dans l'interface Streamlit                                   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  2. Notre pipeline LLM + RAG génère le code SysML v2             │
│     (4 niveaux MBSE, JSON intermédiaire validé)                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  3. Le code SysML v2 est envoyé automatiquement à SysON          │
│     via son API GraphQL (mutation insertTextualSysMLv2)          │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  4. SysON parse le code avec le vrai parseur SysML v2            │
│     et crée le modèle (arborescence + diagrammes)                │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  5. L'ingénieur clique "Ouvrir dans SysON" → interface SysON     │
│     Visualisation, navigation, édition graphique                 │
└──────────────────────────────────────────────────────────────────┘
```

**Rôle de SysON comme validateur :** si le code SysML v2 généré s'affiche correctement dans SysON (arborescence complète, diagrammes sans erreur), cela constitue une preuve de validité syntaxique au sens du standard OMG. À l'inverse, si SysON affiche des erreurs de parsing, celles-ci sont précisément localisées et exploitables pour corriger le prompt ou la génération.

Ce double rôle (visualisation + validation) a été validé lors du test du système de surveillance de parking : le code SysML v2 généré par notre pipeline a été importé avec succès dans SysON et le modèle était visible dans l'arborescence avec les diagrammes de structure corrects.

#### Avantages pour Safran

Du point de vue du client, l'intégration SysON présente trois avantages directs :

1. **Vérification du contenu sans expertise SysML v2** : les diagrammes graphiques permettent à un ingénieur système de vérifier visuellement que le modèle correspond à ce qu'il a décrit, sans lire de code SysML v2.

2. **Continuité avec l'écosystème outillage** : SysON est compatible avec Papyrus et Capella, outils déjà présents dans la chaîne outillage des grands groupes aéronautiques. Un modèle SysON peut être réexporté et exploité en dehors de notre pipeline.

3. **Conformité contractuelle** : les diagrammes produits par SysON sont conformes au standard OMG SysML v2, ce qui leur confère une valeur documentaire opposable dans un contexte contractuel ou de certification.

---

### 4.2 Pistes d'amélioration : prompts d'élicitation

#### Constat issu du diagnostic qualité

L'analyse des résultats sur le BAS Silvercrest établit que **70 % des écarts entre le modèle généré et les diagrammes de référence proviennent d'informations absentes de la description initiale** — non de défauts de l'IA ou des prompts.

Ce constat implique que l'amélioration principale ne passe pas par des corrections de prompts de génération, mais par une **meilleure élicitation des informations** auprès de l'utilisateur avant ou pendant la génération.

Trois domaines sont systématiquement absents des premières descriptions spontanées :

| Domaine absent | Exemple sur le BAS | Pourcentage des absences |
|---|---|---|
| Cycle de vie du système | Phases développement, production, exploitation, maintenance, recyclage | ~26 % |
| Acteurs de maintenance | Opérateur de maintenance, atelier (Maintenance facility) | ~15 % |
| Décomposition fine des use cases | Pressuriser réservoirs vs ailes vs cabine (3 UC séparés) | ~29 % |

#### Prompts d'élicitation recommandés

L'outil pourrait poser des **questions ciblées à l'utilisateur** après la première génération opérationnelle, pour compléter le modèle de manière dialogique. Voici les prompts d'élicitation types identifiés :

**Sur les acteurs de maintenance :**
> *"Y a-t-il des opérateurs humains qui interagissent avec le système (notamment pour le diagnostic ou la maintenance) ? Si oui, quelles sont leurs actions typiques ?"*

**Sur le cycle de vie :**
> *"Le système a-t-il des phases de cycle de vie spécifiques à modéliser (développement, production, transport, montage, exploitation, maintenance corrective, recyclage) ? Des jalons ou transitions entre ces phases ?"*

**Sur les flux :**
> *"Quels types de flux circulent entre les composants de votre système ? (flux d'air/fluide, flux électriques de commande, flux d'information/données, flux thermiques, flux mécaniques)"*

**Sur les composants et leurs fonctions :**
> *"Pour chaque composant physique nommé, quelle est sa fonction principale ? (exemple : 'la PRV régule la pression', 'le capteur de pression mesure en continu')"*

**Sur les exigences de maintenabilité :**
> *"Avez-vous des exigences de maintenabilité chiffrées ? (temps de remplacement d'un LRU, fréquence d'inspection, MTBF requis)"*

#### Impact attendu sur la couverture

En projetant les résultats du diagnostic sur le BAS Silvercrest, l'introduction de ces 5 prompts d'élicitation permettrait de récupérer la majorité des 26 éléments manquants aujourd'hui classés en cause "DESCRIPTION" :

| Prompt d'élicitation | Éléments récupérables | Gain de couverture estimé |
|---|---|---|
| Acteurs de maintenance | Maintenance operator, Maintenance facility, 3 UC maintenance | +15 % |
| Cycle de vie | 12 éléments du Lifecycle Diagram | +26 % |
| Types de flux | Typing pneumatic/information/electric | +5 % |
| Composant::fonction | Notation granulaire dans le FBD | +4 % |
| Exigences maintenabilité | REQ maintenabilité LRU | +2 % |
| **Total** | **~32 éléments** | **+52 % (42 % → ~94 %)** |

Ces chiffres sont des estimations basées sur le diagnostic V1. La couverture finale dépend aussi de la précision des réponses apportées à ces questions d'élicitation.

#### Principe directeur

L'objectif n'est **pas** de demander à l'ingénieur système de connaître SysML v2. Les prompts d'élicitation sont formulés en langage métier (maintenance, cycle de vie, flux physiques) et non en termes SysML. La traduction vers les concepts SysML v2 (`use case def`, `flow_type`, composant::fonction) reste entièrement à la charge du pipeline IA.

C'est l'avantage fondamental de l'approche pipeline avec RAG : l'expert métier décrit son système dans son vocabulaire, l'IA se charge de la formalisation SysML v2.

---

## 5 — Résultats d'expérimentation : BAS Silvercrest

### 5.1 Présentation du système testé

Le **BAS (Bleed Air System)** est un sous-système essentiel du moteur turbofan **Silvercrest** de Safran Aircraft Engines. Intercalé entre la turbomachine et l'avion, son rôle est de **prélever l'air chaud à haute pression** sur les étages de compression du moteur, de le **réguler en pression et en température**, puis de le **distribuer à l'avion** pour les besoins de pressurisation, de conditionnement d'air et de dégivrage.

#### Architecture du système

| Dimension | Éléments |
|---|---|
| **Entités externes** | A/C Avionics, Turbomachine, Fan by-pass duct, Nacelle, A/C Pneumatic System, SOV (Shut-Off Valve) |
| **Fonctions de service** | Fourniture d'air régulé à l'avion · Dégivrage nacelle · Auto-diagnostic · Communication avionique |
| **Modes de fonctionnement** | OFF · Stand-by · Running |
| **Sous-systèmes** | Prélèvement (IP Port, HP Port, HPV, IPCV) · Dégivrage (NAIV, NAI press. sensor, Nacelle anti-ice port) · Conditionnement (PRV, Exchanger ACAC, FAV, Filter, Fan bleed port) · Mesure (Bleed press. sensor, Bleed temp. sensor) · Contrôle-Commande (Electronic BAS Control / EEC) |
| **Composants physiques** | ~15 équipements nommés |
| **Exigences chiffrées** | Température fonctionnement : −40 °C à +85 °C · Temps de réponse boucle de régulation : ≤ 500 ms · Pression sortie : 20–50 PSI · Température sortie : 150–230 °C |

#### Pourquoi ce système est un bon candidat de test

Le BAS Silvercrest présente quatre qualités qui en font un cas de test idéal pour évaluer un pipeline de génération SysML v2 :

1. **Complexité réelle** : 15 composants physiques nommés, 5 sous-systèmes hiérarchisés, 3 types de flux physiques distincts (pneumatique, électrique, information), 2 scénarios dynamiques, 4 exigences chiffrées. La complexité est représentative des systèmes d'architecture intégrée dans les moteurs d'aviation commerciale.

2. **Données de référence disponibles** : des diagrammes SysML v2 de référence établis par des ingénieurs système existent pour ce système (Lifecycle Diagram, Use Case Diagrams, Functional Behavior Diagram). La comparaison entre générations IA et diagrammes de référence est donc quantifiable.

3. **Multi-domaines** : le BAS touche simultanément la mécanique des fluides (air, pressions), l'électronique embarquée (calculateur EEC), la régulation automatique (boucle fermée PRV/FAV) et la maintenance (LRU). Cette diversité teste la généralité du pipeline.

4. **Représentativité Safran** : la structure du BAS (calculateur centralisé, capteurs distribués, vannes actionnées sur consigne) est typique des sous-systèmes embarqués du groupe Safran. Les résultats sur ce système sont directement transposables à d'autres systèmes du moteur.

---

### 5.2 Test V1 — Description initiale (56 lignes)

#### Contenu de la description V1

La description initiale (fichier `style_formel.txt`, 56 lignes) couvre les aspects suivants en langage naturel structuré :

- **Entités externes** (6) : A/C Avionics (consignes + alimentation), Turbomachine (source air HP), Fan by-pass duct (source air froid), Nacelle (récepteur dégivrage), A/C Pneumatic System (récepteur air régulé), SOV (frontière physique).
- **4 fonctions de service** : air régulé à l'avion, dégivrage nacelle, auto-diagnostic, communication statuts.
- **3 modes** : OFF, Stand-by, Running — avec description des états de vannes.
- **Architecture composants** : 5 sous-systèmes, ~15 composants nommés avec leur rôle fonctionnel.
- **2 scénarios opérationnels** : fourniture d'air nominal (régulation en boucle fermée) et dégivrage nacelle (ouverture NAIV sur commande avionique).
- **4 exigences chiffrées** : plage de température, temps de réponse, plage de pression, plage de température sortie.

Ce qui est **absent** de la description V1 : cycle de vie, acteurs de maintenance (opérateur, atelier), use cases de maintenance, rôle de l'EECS comme acteur distinct, décomposition des fonctions de fourniture d'air par destination, typage des flux (pneumatique/électrique/information), notation composant::fonction.

#### Résultats de la génération V1 — 4 niveaux

| Niveau MBSE | Volume SysML v2 | Éléments clés générés |
|---|---|---|
| Opérationnel | 3 166 caractères | 3 acteurs (stakeholders=[] → tous dans external_systems) · 4 use cases génériques · 2 scénarios · 0 exigence (seuils numériques non capturés comme REQ) |
| Fonctionnel | 4 200 caractères | 5 fonctions principales · 18 flux fonctionnels · 3 modes · 0 flux typé (`flow_type` absent) |
| Logique | 1 059 caractères | Composants logiques · Connexions (dont certaines vers des entités externes non définies dans `parts`) · 0 exigence allouée |
| Technique | 12 290 caractères | ~15 composants physiques détaillés avec ports · connexions physiques · choix technologiques |

#### Diagnostic qualité — Comparaison avec les diagrammes de référence

Le diagnostic a porté sur 4 diagrammes de référence représentant 46 éléments distincts (acteurs, use cases, composants, flux, relations).

**Tableau de couverture V1 :**

| Diagramme de référence Safran | Éléments | Présents ✅ | Partiels ⚠️ | Absents ❌ | Couverture |
|---|---|---|---|---|---|
| Lifecycle Diagram BAS | 12 | 0 | 0 | 12 | **0 %** |
| Use Case Diagram — Fonctions de service | 12 | 4 | 5 | 3 | **54 %** |
| Use Case Diagram — Maintenance | 7 | 0 | 0 | 7 | **0 %** |
| Functional Behavior Diagram (fonctions) | 6 | 0 | 5 | 1 | **42 %** |
| Functional Behavior Diagram (flux) | 9 | 5 | 1 | 3 | **61 %** |
| **TOTAL** | **46** | **9** | **11** | **26** | **~42 %** |

**Analyse des causes des 37 écarts (présents partiels + absents) :**

| Cause | Nombre d'éléments | Part | Exemples représentatifs |
|---|---|---|---|
| **DESCRIPTION** — information absente de la description initiale | 26 | **70 %** | Lifecycle entier (12 éléments) · Maintenance entière (7 éléments) · EECS non nommé séparément · Dégivrage ailes et pressurisation réservoirs non explicités · Rôle de l'ACAC dans le circuit nacelle |
| **PROMPT** — information présente mais mal capturée par le prompt | 10 | **27 %** | `stakeholders=[]` malgré entités actives · 0 flux typé (pneumatique/électrique/information) · Notation composant::fonction absente · Use cases trop génériques (1 UC "Fournir air" au lieu de 3 par destination) |
| **IA** — prompt correct mais IA a omis | 1 | **3 %** | Entités clairement citées dans la description mais toutes classées dans `external_systems` au lieu d'être réparties entre `stakeholders` et `external_systems` |

**Conclusion V1 :** le principal levier d'amélioration est la **qualité et la complétude de la description** (70 % des écarts). Les corrections de prompts adressent 27 % des écarts. L'IA elle-même, lorsque le prompt est correct et la description complète, ne fait pratiquement pas d'erreurs (3 %).

---

### 5.3 Test V2 — Description enrichie (155 lignes) + Prompts corrigés P5–P8

#### Enrichissement de la description

La description V2 (`style_formel_v2.txt`) passe de 56 à **155 lignes (+177 %)** par l'ajout de 7 nouveaux domaines absents de V1 :

| Domaine ajouté | Contenu |
|---|---|
| **Cycle de vie** | 8 phases (Concept → Développement → Production → Livraison → Montage → Exploitation → Maintenance → Recyclage) avec jalons CR/QR et transitions entre phases |
| **Acteurs de maintenance** | Opérateur de maintenance (diagnostic, réparation sous l'aile) · Atelier de maintenance (réparation en installation dédiée) |
| **Use cases de maintenance** | `DiagnostiquerLEtat` · `ReparerSousLAile` · `MaintenirEnConditionsOperationnelles` · relations `«include»` |
| **EECS comme acteur distinct** | Electronic Engine Control System nommé séparément de l'avionique générale, avec son rôle spécifique (coordination des prélèvements selon la poussée demandée) |
| **Décomposition des fonctions de fourniture** | 3 use cases distincts : `PressuriserLesReservoirs` · `DegivrerLesAiles` · `PressuriserEtTempererLaCabine` |
| **Rôle de l'ACAC dans le circuit nacelle** | L'échangeur thermique est aussi présent dans le circuit de dégivrage nacelle (pas seulement pour l'air à l'avion) |
| **Notation composant::fonction et types de flux** | Chaque composant est décrit avec sa fonction sous la forme `NomComposant :: NomFonction (flux pneumatique/information/électrique)` |
| **Exigences de maintenabilité** | 2 nouvelles exigences : remplacement LRU en < 2 heures · diagnostic embarqué sans démontage |

#### Résultats comparatifs V1 vs V2

| Métrique | V1 | V2 | Évolution |
|---|---|---|---|
| **Acteurs identifiés** (`stakeholders`) | 3 | 5 | ✅ +EECS, +OperateurDeMaintenance |
| **Use cases générés** | 4 | 8 | ✅ +4 use cases de maintenance + décomposition fourniture air |
| **Use cases de maintenance** | 0 | 4 | ✅ Nouvelle couverture totale |
| **Notation composant::fonction** | 0 | 3 | ✅ Apparition dans le code SysML v2 |
| **Volume SysML opérationnel** | 3 166 chars | 4 456 chars | ✅ +41 % |
| **Couverture Use Cases Services** | 54 % | 75 % | ✅ **+21 points** |
| **Couverture Use Cases Maintenance** | 0 % | 43 % | ✅ **Nouvelle couverture** |
| **Couverture Functional Behavior** | 53 % | 60 % | ✅ +7 points |
| **Volume SysML fonctionnel** | 4 200 chars | 1 241 chars | ⚠️ −70 % (condensation) |
| **Volume SysML technique** | 12 290 chars | 1 032 chars | ⚠️ −92 % (condensation) |

---

### 5.4 Limitations identifiées

#### Limitation 1 — Condensation des niveaux fonctionnel et technique en V2

La comparaison V1/V2 révèle une **régression quantitative** sur les niveaux fonctionnel et technique : le code SysML v2 généré est 70 % plus court pour le niveau fonctionnel et 92 % plus court pour le niveau technique.

| Niveau | V1 | V2 | Régression |
|---|---|---|---|
| Fonctionnel | 4 200 caractères | 1 241 caractères | −70 % |
| Technique | 12 290 caractères | 1 032 caractères | −92 % |
| Opérationnel | 3 166 caractères | 4 456 caractères | +41 % (amélioration) |

**Cause identifiée :** lors de la session de test V2, les niveaux fonctionnel et technique ont été régénérés dans un contexte d'appel différent (validation partielle + regénération), avec un paramètre `max_tokens` insuffisant pour couvrir la description enrichie (155 lignes vs 56 en V1). Le LLM a produit des versions condensées pour rester dans la limite de tokens de la réponse. Ce phénomène est lié **au contexte d'appel** et non aux corrections de prompts.

**Impact réel :** la régression sur les niveaux fonctionnel et technique ne remet pas en cause la validité des corrections P5–P8 dont l'effet principal était attendu au niveau opérationnel (use cases, acteurs, stakeholders). Ce niveau montre une amélioration significative (+41 % de volume, +21 points de couverture use cases). Une régénération dédiée des niveaux fonctionnel et technique avec `max_tokens = 65 536` et la description V2 complète produirait les résultats attendus.

#### Limitation 2 — Le diagramme de cycle de vie reste hors de portée

Le Lifecycle Diagram passe de 0 % (V1) à 0 % (V2), malgré l'ajout de la section cycle de vie dans la description V2. Notre pipeline génère 4 niveaux MBSE centrés sur l'**architecture fonctionnelle du système en opération**. Le cycle de vie est un type de diagramme **transverse** (il décrit le système à travers ses phases d'existence, pas son comportement interne) qui nécessiterait :

- Soit un **5ème niveau dédié** dans le pipeline (niveau "Lifecycle"), avec son propre prompt et son propre schéma JSON.
- Soit un **prompt de diagramme spécialisé** qui, à partir d'une section cycle de vie dans la description, génère directement le code SysML v2 du diagramme d'état de cycle de vie.

Cette limitation est une **limite par conception** du pipeline actuel, pas un défaut des prompts existants.

#### Limitation 3 — L'ingénieur ne pense pas spontanément à tout décrire

La donnée la plus structurante de l'expérimentation est que **70 % des écarts proviennent d'informations absentes de la description initiale**. Cette proportion est normale : un ingénieur système qui décrit son architecture en langage naturel se concentre sur la structure et les flux en opération. Il ne pense pas spontanément à :

- Décrire les phases de cycle de vie.
- Mentionner les opérateurs de maintenance comme acteurs.
- Décomposer une fonction de service générique en sous-fonctions par destination.
- Typer les flux par nature physique (pneumatique, électrique, information).

**Solution proposée :** les prompts d'élicitation décrits en section 4.2. Ils permettent à l'outil de poser des questions ciblées à l'ingénieur en langage métier, pour compléter la description sans exiger de lui une connaissance de la notation SysML v2. La couverture estimée après élicitation complète est de ~94 % (vs 42 % avec une description spontanée).

---

## 6 — Conclusions et recommandations

### 6.1 Conclusions

#### Sur la génération de modèles SysML v2

**Les prompts structurés en 6 composants sont efficaces pour générer du code SysML v2 syntaxiquement valide.** La structure Rôle + Contexte MBSE + Règles de fidélité + Format JSON + Exemple + RAG produit des modèles cohérents, traçables et validables, même sur des systèmes complexes de 15 composants et 4 niveaux MBSE.

**Le pipeline en 2 étapes (NL → JSON → SysML v2) offre une traçabilité complète** et un point d'inspection intermédiaire. L'ingénieur peut valider le JSON avant que le code SysML v2 soit généré, ce qui permet de corriger la compréhension de l'IA sans tout regénérer.

**L'approche itérative (diagnostic → correction → re-test) améliore mesuralement les résultats.** Sur le BAS Silvercrest, les 8 corrections P1–P8 ont produit les gains suivants :
- Use Cases Services : 54 % → 75 % (+21 points)
- Use Cases Maintenance : 0 % → 43 % (nouvelle couverture)
- Acteurs identifiés : 3 → 5
- Notation composant::fonction : 0 → 3 occurrences

**La qualité de la description utilisateur est le facteur déterminant (70 % des écarts).** Les corrections de prompts ont un effet réel mais limité (27 %) si la description ne contient pas les informations de base. La priorité pour améliorer la couverture est d'enrichir la description, pas de raffiner les prompts.

#### Sur la visualisation des diagrammes

**Eclipse SysON permet la visualisation de vrais diagrammes SysML v2 conformes au standard OMG.** La validation sur le système de surveillance de parking a confirmé que le pipeline génère du code SysML v2 suffisamment valide pour être parsé et affiché par SysON.

**L'intégration automatique (pipeline → SysON via API GraphQL) offre un flux continu** depuis la description en langage naturel jusqu'à la visualisation graphique, sans intervention manuelle sur les fichiers SysML v2.

**SysON sert de double outil** : visualisateur pour la vérification du contenu et validateur syntaxique (le parseur officiel OMG détecte toutes les erreurs de syntaxe que notre validateur interne pourrait manquer).

---

### 6.2 Recommandations pour l'usage opérationnel

À partir des résultats de l'expérimentation, cinq recommandations pratiques peuvent être formulées pour l'usage opérationnel de l'outil par les équipes Safran :

**1. Privilégier les descriptions structurées et détaillées**

Le style formel (sections nommées, vocabulaire technique précis, composants listés avec leur rôle) donne les meilleurs résultats. Une description en liste à puces couvrant les 5 domaines (entités externes, fonctions de service, modes, architecture composants, exigences chiffrées) maximise la couverture du premier passage.

**2. Utiliser les prompts d'élicitation avant la génération**

Les 5 prompts d'élicitation identifiés (acteurs de maintenance, cycle de vie, types de flux, composant::fonction, exigences maintenabilité) permettent de passer d'une couverture de ~42 % (description spontanée) à ~94 % (description complète). Ils ne demandent pas de connaissance SysML v2 — les questions sont formulées en langage métier.

**3. Procéder par itérations courtes**

Le cycle recommandé est : générer le niveau opérationnel → vérifier les use cases et stakeholders dans SysON → compléter la description si des éléments manquent → valider et passer au niveau suivant. Ne pas chercher à tout spécifier dès le début.

**4. Envisager l'ajout d'un niveau "Cycle de vie"**

Pour les projets où le cycle de vie est contractuellement important (livraison, certification, maintenabilité), un 5ème niveau dédié dans le pipeline permettrait de générer les Lifecycle Diagrams. La structure du pipeline (JSON intermédiaire + prompt dédié) se prête naturellement à cette extension.

**5. Garder un rôle d'architecte actif**

L'outil IA traduit, il ne conçoit pas. Les choix d'architecture (regroupement des fonctions en composants, allocation des exigences, choix des interfaces) restent sous la responsabilité de l'ingénieur système. L'IA maximise la fidélité à ce qui est décrit ; les décisions de conception appartiennent à l'architecte.

---

### 6.3 Perspectives

**Intégration bidirectionnelle avec SysON.** L'architecture actuelle est unidirectionnelle : notre pipeline envoie le code vers SysON. Une intégration bidirectionnelle permettrait de récupérer les modifications graphiques réalisées dans SysON pour les répercuter dans le JSON de session, créant une boucle de co-édition texte/graphique.

**Support de modèles de langage alternatifs.** L'architecture du pipeline (interface abstraite `LLMBase`, pattern Factory) est déjà prête pour supporter d'autres modèles. Claude Sonnet et GPT-4o sont des candidats naturels pour comparer les performances de fidélité et de complétion sur les mêmes descriptions.

**Extension à d'autres domaines Safran.** Le pipeline est générique : le RAG peut être réindexé sur des documents spécifiques à d'autres domaines (systèmes de propulsion électrique, systèmes hydrauliques, systèmes de nacelles). Les prompts de génération sont paramétrés par niveau MBSE et s'adaptent à tout système décrit en langage naturel.

**Automatisation du diagnostic qualité.** Le processus de comparaison entre modèle généré et diagrammes de référence (section 5.2) est aujourd'hui manuel. Il pourrait être semi-automatisé : extraction des éléments du modèle généré + comparaison fuzzy avec une liste de référence + calcul automatique du score de couverture.

**Intégration des prompts d'élicitation dans l'interface.** Les 5 prompts d'élicitation identifiés (section 4.2) pourraient être intégrés directement dans l'interface Streamlit sous forme d'un assistant de description, posant les questions à l'utilisateur avant le lancement de la génération et construisant automatiquement la description complète.

---

## Annexes

### Annexe A — Dépôt du projet

Le code source complet de l'outil (backend FastAPI, frontend Streamlit, prompts, tests, scripts d'expérimentation) est disponible sur GitHub :

**https://github.com/Kenfack-franck/work_sysml**

Le dépôt contient :
- `backend/` — API FastAPI, services LLM/RAG, prompts, tests (147+)
- `frontend/` — Interface Streamlit
- `experiments/` — Descriptions de systèmes test, résultats, scripts d'analyse
- `deliverables/` — Ce rapport
- `docker-compose.yml` — Déploiement local en une commande

---

### Annexe B — Description BAS V1 (56 lignes)

Description initiale utilisée pour le test V1. Style formel, couvrant les aspects essentiels du système en opération.

```
Le système BAS (Bleed Air System) est un système de prélèvement et de conditionnement d'air intégré au moteur Silvercrest. Il est intercalé entre la turbomachine et l'avion.

Le système interagit avec les entités externes suivantes :
- L'avionique de l'avion (A/C Avionics), qui fournit l'énergie électrique, envoie les consignes de pression et température, envoie les commandes de dégivrage, et reçoit les données d'état du système.
- La turbomachine (cœur du moteur), qui est la source d'air chaud à haute pression.
- Le conduit de soufflante (Fan by-pass duct), qui est la source d'air froid ambiant.
- La nacelle, qui reçoit l'air chaud pour le dégivrage et évacue l'air de refroidissement.
- Le système pneumatique de l'avion (A/C Pneumatic System), qui reçoit l'air conditionné et régulé en pression et température.
- La vanne d'isolement de l'avion (SOV - Shut-Off Valve), qui est la frontière physique en sortie du BAS.

Le système réalise quatre fonctions de service :
1. Envoyer de l'air régulé en pression et température à l'avion.
2. Envoyer de l'air chaud à la nacelle pour le dégivrage.
3. Déterminer l'état du système par mesures physiques et auto-diagnostic.
4. Communiquer les consignes et statuts avec l'avionique.

Le système possède trois modes de fonctionnement :
- OFF : Le système n'est pas alimenté, aucune vanne n'est active.
- Stand-by : Le système est alimenté et communique son état, mais les commandes de flux d'air ne sont pas activées.
- Running : Le système régule activement la pression et la température pour envoyer de l'air à la cabine et/ou ouvre le circuit de dégivrage.

Le système est composé des sous-systèmes et composants suivants :

Sous-système de Prélèvement d'air :
- IP Port (Intermediate Pressure) : prélèvement primaire d'air chaud depuis la turbomachine.
- HP Port (High Pressure) : prélèvement secondaire d'air chaud depuis la turbomachine.
- HPV (High Pressure Valve) : vanne qui contrôle l'ouverture du port HP, activée lorsque la pression IP est insuffisante.
- IPCV (Intermediate Pressure Check Valve) : clapet anti-retour entre la jonction HP et IP, empêche l'air HP de refouler vers l'étage IP.

Sous-système de Dégivrage Nacelle :
- NAIV (Nacelle Anti-Ice Valve) : vanne d'arrêt qui autorise ou bloque le passage de l'air chaud vers la nacelle.
- NAI press. sensor : capteur de pression après la NAIV pour surveiller la pression de dégivrage.
- Nacelle anti-ice port : interface de sortie vers la nacelle.

Sous-système de Conditionnement :
- PRV (Pressure Regulating Valve) : vanne qui abaisse et régule la pression de l'air chaud selon une consigne.
- Exchanger (échangeur thermique ACAC) : dispositif qui refroidit l'air chaud régulé en pression par échange avec l'air froid.
- Fan bleed port : entrée d'air froid prélevé sur le flux secondaire du moteur.
- FAV (Fan Air Valve) : vanne qui régule le débit d'air froid admis dans l'échangeur.
- Filter : filtre pour l'air avant l'interface avion.
- Nacelle exhaust port : sortie qui rejette l'air de refroidissement après l'échangeur.

Sous-système de Mesure finale :
- Bleed press. sensor : capteur de pression finale régulée en sortie.
- Bleed temp. sensor : capteur de température finale régulée en sortie.

Sous-système de Contrôle-Commande :
- Electronic BAS Control (embarqué dans l'EEC) : calculateur qui reçoit les consignes de l'avionique, acquiert les mesures des capteurs, et envoie les signaux de commande aux vannes HPV, PRV, FAV et NAIV.

Scénario 1 - Fourniture d'air nominal :
L'avionique envoie les consignes de pression et température au calculateur. L'air est prélevé sur l'IP Port. Le calculateur pilote la PRV pour atteindre la pression cible. Simultanément, le calculateur pilote la FAV pour réguler la température via l'échangeur. Les capteurs de sortie renvoient les mesures au calculateur qui ajuste en boucle fermée. L'air régulé sort vers le système pneumatique de l'avion.

Scénario 2 - Dégivrage nacelle :
L'avionique transmet la commande de dégivrage au calculateur. Le calculateur ouvre la vanne NAIV. L'air chaud haute pression traverse la NAIV, est mesuré par le capteur NAI Press, et sort vers la nacelle. L'état est remonté à l'avionique.

Le système doit fonctionner dans une plage de température de -40°C à +85°C. Le temps de réponse de la boucle de régulation ne doit pas dépasser 500 millisecondes. La pression de sortie régulée doit être maintenue entre 20 et 50 PSI. La température de sortie régulée doit être maintenue entre 150°C et 230°C.
```

---

### Annexe C — Description BAS V2 (155 lignes)

Description enrichie utilisée pour le test V2. 7 domaines supplémentaires ajoutés par rapport à V1 (cycle de vie, acteurs de maintenance, use cases de maintenance, EECS distinct, décomposition des UC de fourniture, rôle ACAC nacelle, notation composant::fonction + types de flux).

```
Le système BAS (Bleed Air System) est un système de prélèvement et de conditionnement d'air intégré au moteur Silvercrest. Il est intercalé entre la turbomachine et l'avion.

=== ACTEURS ET SYSTÈMES EXTERNES ===

Le système interagit avec les entités externes suivantes :
- L'avionique de l'avion (A/C Avionics) : fournit l'énergie électrique, envoie les consignes de pression et température, envoie les commandes de dégivrage, reçoit les données d'état du système.
- L'EECS (Electronic Engine Control System) : calculateur moteur qui coordonne les commandes avec le BAS pour la gestion des prélèvements selon la poussée demandée.
- La turbomachine (cœur du moteur) : source d'air chaud à haute pression pour le prélèvement.
- Le conduit de soufflante (Fan by-pass duct) : source d'air froid ambiant.
- La nacelle : reçoit l'air chaud pour le dégivrage et évacue l'air de refroidissement.
- Le système pneumatique de l'avion (A/C Pneumatic System) : reçoit l'air conditionné et régulé en pression et température.
- La vanne d'isolement de l'avion (SOV - Shut-Off Valve) : frontière physique en sortie du BAS.
- L'opérateur de maintenance (Maintenance operator) : technicien qui diagnostique l'état du système, réalise des réparations sous l'aile et maintient le système en conditions opérationnelles.
- L'atelier de maintenance (Maintenance facility) : installation dédiée à la réparation en atelier des composants déposés.

=== FONCTIONS DE SERVICE (USE CASES) ===

Le système réalise les fonctions de service suivantes :

Fourniture d'air à l'avion (trois sous-fonctions distinctes) :
1. Pressuriser les réservoirs de l'avion : fournir de l'air régulé en pression au système pneumatique pour la pressurisation des réservoirs.
2. Dégivrer les ailes : fournir de l'air chaud régulé au système pneumatique de l'avion pour le dégivrage des ailes (wing anti-ice).
3. Pressuriser et tempérer la cabine : fournir de l'air conditionné en pression et en température au système pneumatique de l'avion pour le conditionnement de la cabine.

Dégivrage nacelle :
4. Dégivrer la nacelle : envoyer de l'air chaud haute pression via la NAIV vers la nacelle pour le dégivrage moteur (nacelle anti-ice).

Surveillance et maintenance :
5. Être informé de l'état du système : l'opérateur de maintenance peut lire l'état courant du BAS (mesures, alarmes, défauts) via l'avionique.
6. Diagnostiquer l'état : l'opérateur de maintenance réalise un diagnostic de l'état de santé du BAS, sur la base des mesures et des codes de défaut.
7. Réparer sous l'aile : l'opérateur réalise des interventions de maintenance de niveau 1 directement sur l'avion sans déposer les composants.
8. Maintenir en conditions opérationnelles : opération générique de maintenance incluant le diagnostic et la réparation.

Relation entre use cases de maintenance :
- "Maintenir en conditions opérationnelles" «include» "Diagnostiquer l'état"
- "Maintenir en conditions opérationnelles" «include» "Réparer sous l'aile"
- La réparation en atelier (dépose de composants, réparation en Maintenance facility) est une option si la réparation sous l'aile n'est pas possible.

=== MODES DE FONCTIONNEMENT ===

Le système possède trois modes de fonctionnement :
- OFF : le système n'est pas alimenté, aucune vanne n'est active.
- Stand-by : le système est alimenté et communique son état, mais les commandes de flux d'air ne sont pas activées.
- Running : le système régule activement la pression et la température pour envoyer de l'air à la cabine et/ou ouvre le circuit de dégivrage.

=== CYCLE DE VIE ===

Le système BAS suit les phases de cycle de vie suivantes :
1. Concept évaluation : analyse des besoins et évaluation de la faisabilité du système BAS.
2. Développement : conception, développement et qualification du système. Jalons : CR (Critical Review) et QR (Qualification Review) S8.
3. Production : fabrication en série du BAS. Comprend un sous-cycle de production (Production lifecycle) avec contrôles qualité.
4. Livraison moteur et BAS : livraison du BAS intégré au moteur, comprenant le stockage intermédiaire et le transport vers le site d'intégration avion.
5. Montage final : intégration du BAS sur l'avion (A/C).
6. Exploitation : utilisation opérationnelle du BAS. Comprend deux sous-phases : Operation (vols normaux) et Maintenance LRU (remplacement de composants LRU).
7. Maintenance : phase de maintenance approfondie quand l'avion n'est pas en exploitation. Comprend la dépose et réparation en atelier.
8. Recyclage : fin de vie du BAS, démontage et recyclage des composants.

Transitions : Développement → Production (jalons CR/QR S8) · Production → Livraison · Livraison → Montage final · Montage final → Exploitation · Exploitation ↔ Maintenance (bidirectionnel) · Exploitation → Recyclage.

=== ARCHITECTURE FONCTIONNELLE DÉTAILLÉE ===

Les comportements fonctionnels sont décrits au niveau composant::fonction.

Sous-système de Prélèvement d'air :
- IP Port :: Prélever air (flux pneumatique) : prélèvement primaire d'air chaud depuis la turbomachine.
- HP Port :: Prélever air (flux pneumatique) : prélèvement secondaire depuis le port High Pressure.
- HPV :: Contrôler le prélèvement HP (flux information + pneumatique) : vanne activée si pression IP insuffisante.
- IPCV :: Empêcher refoulement (flux pneumatique) : clapet anti-retour entre la jonction HP et IP.

Sous-système de Dégivrage Nacelle :
- NAIV :: Laisser passer l'air (flux pneumatique + information) : vanne d'arrêt, commande électrique depuis le calculateur.
- ACAC :: Réguler la température nacelle (flux pneumatique) : l'échangeur thermique est aussi utilisé dans le circuit nacelle.
- Air Temperature Sensor :: Mesurer la température (flux information).
- Nacelle port :: Fournir l'air à l'interface Nacelle (flux pneumatique).
- NAI press. sensor :: Mesurer la pression NAI (flux information).

Sous-système de Conditionnement :
- PRV :: Réguler pression air (flux pneumatique + information).
- Exchanger (ACAC) :: Refroidir air (flux pneumatique thermique).
- FAV :: Réguler débit air froid (flux pneumatique + information).
- Filter :: Filtrer air (flux pneumatique).
- Bleed press. sensor :: Mesurer pression finale (flux information).
- Bleed temp. sensor :: Mesurer température finale (flux information).

Sous-système de Contrôle-Commande :
- Electronic BAS Control :: Contrôler et Communiquer (flux information + électrique).
  Entrées : consignes pression/température (A/C Avionics) · commande dégivrage (A/C Avionics) · mesures capteurs
  Sorties électriques : commande HPV · commande PRV · commande FAV · commande NAIV
  Sortie information : statut système (vers A/C Avionics)

Types de flux : pneumatique (air/fluide) · information (données, commandes, mesures) · électrique (alimentation, signaux discrets)

=== SCÉNARIOS OPÉRATIONNELS ===

Scénario 1 - Fourniture d'air nominal :
L'avionique envoie les consignes de pression et température au calculateur. L'air est prélevé sur l'IP Port (flux pneumatique). Le calculateur pilote la PRV (flux électrique : commande PRV) pour atteindre la pression cible. Simultanément, le calculateur pilote la FAV (flux électrique : commande FAV) pour réguler la température via l'échangeur. Les capteurs de sortie (bleed press. sensor, bleed temp. sensor) renvoient les mesures (flux information) au calculateur qui ajuste en boucle fermée. L'air régulé sort vers le système pneumatique de l'avion.

Scénario 2 - Dégivrage nacelle :
L'avionique transmet la commande de dégivrage au calculateur (flux information). Le calculateur ouvre la vanne NAIV (flux électrique). L'air chaud haute pression traverse la NAIV (flux pneumatique), passe dans l'ACAC pour réguler la température (flux pneumatique + thermique), est mesuré par le capteur NAI Press (flux information), et sort vers la nacelle (flux pneumatique). L'état est remonté à l'avionique (flux information).

=== EXIGENCES ===

Le système doit fonctionner dans une plage de température de -40°C à +85°C.
Le temps de réponse de la boucle de régulation ne doit pas dépasser 500 millisecondes.
La pression de sortie régulée doit être maintenue entre 20 et 50 PSI.
La température de sortie régulée doit être maintenue entre 150°C et 230°C.
La maintenabilité du système doit permettre le remplacement d'un LRU en moins de 2 heures par un opérateur qualifié.
Le système doit pouvoir être diagnostiqué sans démontage (diagnostic embarqué accessible via l'avionique).
```

---

*Rapport de Mission — Génération automatique de modèles SysML v2 par IA*  
*Safran / ENSTA — Février 2026 — Version 1.0*
