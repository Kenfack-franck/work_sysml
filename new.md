

# 📖 Document de Contexte Complet — Projet SysML v2 Agent

## Date de rédaction : 21 février 2026
## Utilisateur : kenfackfranck (Kenfack Franck)

---

## 1. IDENTITÉ DU PROJET

### 1.1 Contexte contractuel

Ce projet est une mission pour **Safran** (via ENSTA / Junior Entreprise). Le moteur cible est le **Silvercrest**. Le contrat prévoit **2 JEH (Journées d'Étude Homme)** sur **1 semaine**.

**Interlocuteurs côté client :**
- Un contact technique (numéro +33 6 48 03 98 19) qui a clarifié que la visualisation est "un moyen de vérification, pas une fin en soi"
- Un contact contractuel / Benoît (numéro +33 6 49 84 96 29) qui a précisé : "le vrai livrable est un moyen de voir pour vérifier le contenu"
- Un troisième contact (+33 7 45 31 65 23) qui a posé la question sur les livrables

### 1.2 Livrables contractuels

| Livrable | Format | Contenu |
|---|---|---|
| Fichier PDF | Synthèse | Prompts types réutilisables en 2 catégories : prompts de génération du modèle SysML v2 + prompts de visualisation de diagrammes d'architecture |
| Fichier Excel | Export brut | Échanges avec l'IA (colonnes : prompt, réponse IA, commentaires d'analyse) |

### 1.3 Clarification du client sur la visualisation

Le client a dit texto :
> "La visualisation des diagrammes est un moyen de vérification de ce que comprennent les SysML v2. Pas une fin en soi. Surtout si vous avez trouvé des visualisateurs open-source de SysML v2."

Et :
> "Notre besoin : voir en mode diagramme le modèle de SysML v2 afin de vérifier le contenu du modèle. Soit vous livrez des prompts qui permettent de générer les diagrammes. Soit vous trouvez un visualisateur open-source. En synthèse le vrai livrable est un moyen de voir pour vérifier le contenu."

### 1.4 Le système cible pour les tests finaux

Le **système BAS (Bleed Air System) du moteur Silvercrest** — un système de prélèvement et conditionnement d'air intercalé entre la turbomachine et l'avion. Ce système a :
- 6 entités externes (avionique, turbomachine, soufflante, nacelle, système pneumatique avion, SOV)
- 4 fonctions de service (air régulé, dégivrage, diagnostic, communication)
- 3 modes (OFF, Stand-by, Running)
- 5 sous-systèmes (Prélèvement, Dégivrage, Conditionnement, Mesure, Contrôle-Commande)
- ~15 composants physiques (HPV, IPCV, NAIV, PRV, FAV, Exchanger, Filter, capteurs, ports, calculateur EEC)
- 2 scénarios dynamiques (fourniture d'air nominal, dégivrage nacelle)
- 4 exigences chiffrées (température -40°C à +85°C, temps de réponse ≤500ms, pression 20-50 PSI, température sortie 150-230°C)

---

## 2. CE QU'ON A CONSTRUIT

### 2.1 L'idée centrale

Un **agent IA** qui permet à un architecte de :
1. Décrire son système en **langage naturel** (français ou anglais)
2. Obtenir automatiquement du **code SysML v2** syntaxiquement valide
3. Obtenir des **diagrammes d'architecture** dérivés du modèle
4. Le tout en respectant une approche **MBSE progressive** en 4 niveaux

**Contrainte fondamentale** : L'IA TRADUIT, elle ne CONÇOIT PAS. Aucun composant, aucune connexion, aucune exigence ne doit être ajoutée si elle n'est pas dans la description de l'utilisateur.

### 2.2 Architecture technique

| Composant | Technologie | Rôle |
|---|---|---|
| Backend | FastAPI (Python) | API REST, orchestration du pipeline |
| Frontend | Streamlit (Python) | Interface utilisateur web |
| LLM | Google Gemini 2.5 Flash | Compréhension du langage naturel et génération |
| RAG | ChromaDB + sentence-transformers (all-MiniLM-L6-v2) | Base de connaissances SysML v2 officielle |
| Diagrammes | PlantUML Server | Rendu visuel des diagrammes d'architecture |
| SysON | Eclipse SysON v2026.1.0 | Éditeur/visualisateur SysML v2 officiel (ajouté récemment) |
| SysON DB | PostgreSQL 15 | Base de données pour SysON |
| Infrastructure | Docker Compose (5 conteneurs maintenant) | Déploiement local reproductible |

### 2.3 Le pipeline de génération (2 étapes avec JSON intermédiaire)

```
Description en langage naturel
         │
         ▼
    ┌─────────┐     ┌──────────────────┐
    │   RAG   │────▶│ Exemples SysML v2│
    │ Search  │     │   officiels      │
    └─────────┘     └──────────────────┘
         │                   │
         ▼                   ▼
    ┌────────────────────────────────┐
    │  LLM Appel 1 : NL → JSON      │
    │  (Prompt avec règles fidélité) │
    └────────────────────────────────┘
         │
         ▼
      JSON Structuré (format stable, validable)
         │
         ▼
    ┌────────────────────────────────┐
    │  LLM Appel 2 : JSON → SysML   │
    │  (Prompt avec syntaxe SysML)   │
    └────────────────────────────────┘
         │
         ├──▶ Code SysML v2
         ├──▶ Diagrammes PlantUML (générés depuis le JSON, sans LLM)
         └──▶ Import dans SysON (via API GraphQL) ← NOUVEAU
```

**Pourquoi 2 étapes** :
- Le JSON intermédiaire est inspectable (on peut vérifier ce que le LLM a compris)
- Le JSON est modifiable (patch incrémental)
- Le JSON stabilise la sortie (le LLM est moins variable sur du JSON que sur du code)
- Cela sépare la compréhension du langage naturel et la génération syntaxique

### 2.4 Le workflow MBSE en 4 niveaux

```
Niveau 1 — OPÉRATIONNEL (Black Box)
  QUI utilise le système et POURQUOI ?
  → Stakeholders, systèmes externes, cas d'utilisation, scénarios, exigences
  → Diagrammes : Contexte, Use Cases

Niveau 2 — FONCTIONNEL (White Box — Concepts)
  QUE FAIT le système ?
  → Fonctions, sous-fonctions, flux fonctionnels, modes opératoires
  → Diagrammes : FBS, Comportement Fonctionnel

Niveau 3 — LOGIQUE (White Box — Concepts)
  COMMENT est-il structuré ?
  → Composants logiques, ports, interfaces, connexions, exigences allouées
  → Diagrammes : BDD, IBD

Niveau 4 — TECHNIQUE (White Box — Implémentation)
  AVEC QUOI est-il construit ?
  → Composants physiques, technologies, connexions physiques
  → Diagrammes : Architecture Technique
```

Chaque niveau est généré à partir du précédent. Le passage d'un niveau au suivant nécessite une validation humaine.

### 2.5 Le RAG (Retrieval-Augmented Generation)

| Source | Contenu | Statistiques |
|---|---|---|
| Dépôt `Systems-Modeling/SysML-v2-Release` | Fichiers d'entraînement, exemples complets, bibliothèque standard | 197 fichiers indexés, 337 chunks |
| Modèle d'embeddings | `all-MiniLM-L6-v2` (local, pas d'appel API externe) | Recherche sémantique |
| Base vectorielle | ChromaDB (persistée sur disque Docker) | Requêtes < 100ms |

Le dépôt SysML-v2-Release est cloné **à côté** du projet (pas dedans) et monté en volume Docker read-only.

### 2.6 Tous les fichiers du projet

| Composant | Fichier | Lignes | Rôle |
|---|---|---|---|
| Point d'entrée API | `backend/main.py` | ~870+ | Tous les endpoints REST |
| Schémas de données | `backend/models/schemas.py` | ~350 | Modèles Pydantic |
| Service LLM abstrait | `backend/services/llm_base.py` | ~50 | Interface abstraite |
| Implémentation Gemini | `backend/services/llm_gemini.py` | ~150 | Appels Gemini + rotation clés |
| Factory LLM | `backend/services/llm_factory.py` | ~60 | Pattern Factory multi-LLM |
| Service RAG | `backend/services/rag_service.py` | ~257 | ChromaDB + embeddings |
| Gestion des sessions | `backend/services/state_service.py` | ~371 | CRUD sessions JSON sur disque |
| Pipeline v1 (linéaire) | `backend/services/sysml_service.py` | ~300 | Génération linéaire |
| Pipeline v2 (MBSE) | `backend/services/level_service.py` | ~659 | Génération par niveaux |
| Génération diagrammes | `backend/services/diagram_service.py` | ~746 | 7 types PlantUML |
| Fidelity Checker | `backend/services/fidelity_checker.py` | ~349 | Anti-hallucination (Levenshtein) |
| Validateur SysML v2 | `backend/services/sysml_validator.py` | ~626 | Validation syntaxique (5 niveaux, score 0-100) |
| Service SysON | `backend/services/syson_service.py` | ~200+ | Communication GraphQL avec SysON |
| Prompt opérationnel | `backend/prompts/operational_prompt.py` | - | NL → JSON opérationnel + JSON → SysML |
| Prompt fonctionnel | `backend/prompts/functional_prompt.py` | - | JSON op → JSON fonct + JSON → SysML |
| Prompt logique | `backend/prompts/logical_prompt.py` | - | JSON fonct → JSON logique + JSON → SysML |
| Prompt technique | `backend/prompts/technical_prompt.py` | - | JSON logique → JSON technique + JSON → SysML |
| Prompt pipeline v1 | `backend/prompts/json_prompt.py` | - | NL → JSON (linéaire) |
| Prompt pipeline v1 | `backend/prompts/sysml_prompt.py` | - | JSON → SysML (linéaire) |
| Prompt patch | `backend/prompts/patch_prompt.py` | - | Modification incrémentale |
| Interface utilisateur | `frontend/app.py` | ~987+ | Streamlit avec bouton SysON |
| Script expérimentation | `experiments/run_experiment.py` | - | Lancement automatisé des tests |
| Script export | `experiments/export_markdown.py` | - | Export échanges LLM en Markdown |

### 2.7 Les 7 types de diagrammes PlantUML

| Niveau | Diagramme | Méthode Python |
|---|---|---|
| Opérationnel | Diagramme de contexte | `generate_context()` |
| Opérationnel | Diagramme de cas d'utilisation | `generate_use_cases()` |
| Fonctionnel | Arborescence fonctionnelle (FBS) | `generate_functional_breakdown()` |
| Fonctionnel | Comportement fonctionnel | `generate_functional_behavior()` |
| Logique | Block Definition Diagram (BDD) | `generate_bdd()` |
| Logique | Internal Block Diagram (IBD) | `generate_ibd()` |
| Technique | Architecture technique | `generate_technical_architecture()` |

Ces diagrammes sont générés **en Python pur** depuis le JSON (sans appel LLM). Ils sont toujours actifs et fonctionnels.

### 2.8 Endpoints API

| Catégorie | Endpoints |
|---|---|
| Santé | `GET /api/health`, `GET /api/test-llm`, `GET /api/llm-status` |
| RAG | `GET /api/rag/stats`, `GET /api/rag/search` |
| Pipeline v1 | `POST /api/generate`, `POST /api/patch` |
| Pipeline v2 MBSE | `POST /api/v2/generate`, `POST /api/v2/patch`, `POST /api/v2/validate` |
| Sessions | `GET /api/session/{id}`, `GET /api/sessions`, `PUT /api/v2/session/{id}/name` |
| Diagrammes | `POST /api/v2/diagrams`, `GET /api/v2/diagrams/{id}/{level}` |
| Validation | `POST /api/validate-sysml`, `GET /api/validate-sysml/{id}` |
| Cohérence | `GET /api/v2/coherence/{id}/{level}`, `GET /api/v2/status/{id}` |
| Traçabilité | `GET /api/v2/exchanges/{id}`, `GET /api/v2/export/{id}` |
| SysON | `GET /api/syson/status`, `POST /api/syson/push`, `GET /api/syson/project-url/{id}` |

### 2.9 Mécanismes de qualité

| Mécanisme | Description |
|---|---|
| Fidelity Checker | Vérifie que le LLM n'a pas oublié de composants (fuzzy matching Levenshtein) |
| Validateur SysML v2 | Validation syntaxique en 5 niveaux (structure, déclarations, références, naming, complétude) — Score 0-100 |
| Cohérence inter-niveaux | Vérifie que les éléments se propagent correctement entre niveaux |
| Rotation multi-clés API | 5 clés Gemini en rotation automatique sur erreur 429 |
| JSON Mode | Forçage du format JSON dans les réponses Gemini (`response_mime_type`) |

### 2.10 Tests automatisés

**147+ tests passent** (+ 12 tests SysON ajoutés récemment).

| Fichier de tests | Ce qu'il teste |
|---|---|
| `test_api_health.py` | Endpoints de santé |
| `test_config.py` | Configuration et settings |
| `test_schemas.py` | Validation des schémas Pydantic |
| `test_prompts.py` | Construction des prompts |
| `test_state_service.py` | CRUD des sessions JSON |
| `test_fidelity_checker.py` | Extraction de composants + anti faux-positifs |
| `test_diagram_service.py` | Génération PlantUML |
| `test_diagram_levels.py` | Diagrammes par niveau MBSE |
| `test_level_service.py` | Pipeline MBSE complet |
| `test_llm_factory.py` | Factory + multi-clés |
| `test_llm_rotation.py` | Rotation automatique des clés API |
| `test_sysml_validator.py` | Validation syntaxique SysML v2 |
| `test_syson_integration.py` | Communication avec SysON (12 tests) |

---

## 3. L'EXPÉRIMENTATION — CE QU'ON A TESTÉ

### 3.1 Expérience V1 — Contrôle d'accès (4 styles × 4 niveaux)

**Système test** : Contrôle d'accès d'un bâtiment (6 composants, 7 flux, 2 exigences).

**4 styles de description du même système** :

| Style | Caractéristique |
|---|---|
| Formel | Phrases structurées, vocabulaire technique précis |
| Conversationnel | Langage courant, familier |
| Liste à puces | Composants et flux énumérés |
| Narratif | Scénario raconté comme une histoire |

**Résultats V1** :

| Critère (/5) | Formel | Conversationnel | Liste | Narratif |
|---|---|---|---|---|
| Fidélité | 5 | 2 | 3 | 3 |
| Complétude | 3 | 3 | 4 | 3 |
| Absence hallucinations | 5 | 2 | 4 | 3 |
| Cohérence inter-niveaux | 4 | 3 | 5 | 2 |
| Qualité exigences | 5 | 2 | 3 | 3 |
| **TOTAL /25** | **22** | **12** | **19** | **14** |

**6 problèmes identifiés** :

| # | Problème | Styles impactés |
|---|---|---|
| A | Sur-génération d'exigences (8 au lieu de 2) | Conversationnel, Liste |
| B | Confusion stakeholder / système externe | Conversationnel |
| C | Périmètre du système incorrect | Liste |
| D | Modèle logique auto-contradictoire | Narratif |
| E | Composants qui disparaissent entre niveaux | Formel, Narratif |
| F | 0 exigences allouées aux composants | Formel, Conversationnel, Narratif |

### 3.2 Corrections de prompts appliquées (V1 → V2)

| Correction | Fichier modifié | Règle ajoutée |
|---|---|---|
| P1 | `operational_prompt.py` | Un stakeholder est TOUJOURS une personne. Un équipement est un système externe. |
| P2 | `operational_prompt.py` | Les exigences sont UNIQUEMENT des contraintes mesurables (chiffres, SLAs). |
| P3 | `logical_prompt.py` | Toute connexion doit lier deux composants définis dans "parts". |
| P4 | `logical_prompt.py` | Si des exigences existent dans les niveaux précédents, elles DOIVENT être allouées. |

### 3.3 Structure des résultats d'expérience

```
experiments/
├── descriptions/
│   ├── controle_acces/
│   │   ├── style_formel.txt
│   │   ├── style_conversationnel.txt
│   │   ├── style_liste.txt
│   │   └── style_narratif.txt
│   └── bleed_air_system/          ← NOUVEAU
│       └── style_formel.txt
├── results/
│   ├── controle_acces/            ← Résultats V1
│   │   ├── README.md
│   │   ├── ANALYSE_COMPARATIVE.md
│   │   ├── style_formel/
│   │   │   ├── description.md
│   │   │   ├── operational.md     ← Prompt + Réponse LLM + Code SysML v2
│   │   │   ├── functional.md
│   │   │   ├── logical.md
│   │   │   └── technical.md
│   │   ├── style_conversationnel/
│   │   ├── style_liste/
│   │   └── style_narratif/
│   └── bleed_air_system/          ← EN COURS
│       └── style_formel/
├── run_experiment.py
└── export_markdown.py
```

Chaque fichier `.md` de niveau contient :
- Le prompt exact envoyé au LLM
- La réponse brute du LLM (JSON)
- Le code SysML v2 généré
- Les warnings
- Les diagrammes PlantUML

### 3.4 Test parking (test ponctuel SysON)

On a aussi testé un système de **surveillance de parking** pour valider l'intégration SysON. Le code SysML v2 généré a été importé avec succès dans SysON et le modèle était visible dans l'arborescence.

---

## 4. INTÉGRATION ECLIPSE SYSON

### 4.1 Qu'est-ce que SysON

Eclipse SysON est un éditeur web open-source pour SysML v2, développé par **Obeo** et le **CEA**, sous licence Eclipse Public License 2.0. Il est basé sur **Sirius Web**.

| Caractéristique | Détail |
|---|---|
| Image Docker | `eclipsesyson/syson:v2026.1.0` |
| Port | 8085 (sur notre config) |
| Base de données | PostgreSQL 15 |
| API | GraphQL sur `/api/graphql` |
| Stars GitHub | 256 |
| Dernière activité | 20 février 2026 |

### 4.2 Pourquoi SysON

- Vrais diagrammes SysML v2 conformes au standard OMG (pas des approximations PlantUML)
- Validation avec le vrai parser SysML v2
- Édition bidirectionnelle (diagramme ↔ code)
- Compatibilité avec l'écosystème (Papyrus, Capella)
- Le client a dit : "trouvez un visualisateur open-source"

### 4.3 Ce qui a été implémenté

| Fichier | Modification |
|---|---|
| `docker-compose.yml` | +2 services (syson, syson-db), +1 volume, +SYSON_URL dans backend |
| `backend/services/syson_service.py` | NOUVEAU — 9 méthodes GraphQL |
| `backend/main.py` | +3 endpoints `/api/syson/*` |
| `frontend/app.py` | Bouton "Ouvrir dans SysON" + indicateur sidebar |
| `backend/tests/test_syson_integration.py` | 12 tests unitaires |

### 4.4 Corrections apportées au service SysON pendant l'intégration

3 corrections du `syson_service.py` ont été nécessaires :
1. `CreateProjectInput` nécessite `templateId: "sysmlv2-template"` et `libraryIds: []`
2. `CreateDocumentInput` nécessite `stereotypeId: "empty_sysmlv2"` (pas `name`)
3. `get_root_namespace_id` réécrit pour utiliser `createRootObject` (mutation GraphQL) car le `document_id` brut n'est pas un objet SysML valide pour `insertTextualSysMLv2`

### 4.5 Le flux complet avec SysON

1. L'utilisateur décrit son système dans Streamlit
2. Notre LLM génère le code SysML v2 (inchangé)
3. Notre backend envoie automatiquement le code à SysON via l'API GraphQL
4. SysON crée le modèle et les diagrammes
5. Streamlit affiche un bouton "Ouvrir dans SysON"
6. L'utilisateur peut éditer graphiquement dans SysON
7. Les diagrammes PlantUML restent aussi disponibles (fallback)

---

## 5. INFRASTRUCTURE DE DÉPLOIEMENT

### 5.1 Docker Compose actuel (5 conteneurs)

| Service | Image | Port | Rôle |
|---|---|---|---|
| backend | Build local `./backend` | 8000 | API FastAPI |
| frontend | Build local `./frontend` | 8501 | Interface Streamlit |
| plantuml | `plantuml/plantuml-server:tomcat` | 8080 | Rendu diagrammes |
| syson | `eclipsesyson/syson:v2026.1.0` | 8085 | Éditeur SysML v2 |
| syson-db | `postgres:15` | interne | BDD pour SysON |

### 5.2 Dépôts Git

| Plateforme | URL | Usage |
|---|---|---|
| GitHub | `https://github.com/Kenfack-franck/work_sysml` | Partage (60 fichiers, commit 0910904) |
| GitLab | `https://gitlab.com/kenfack-group/work_sysmlv2` | Déploiement CI/CD |

Le mirroring est configuré : `git push origin main` pousse vers les deux.

### 5.3 Déploiement VPS (préparé, pas encore exécuté)

| Élément | Détail |
|---|---|
| VPS | IP 152.228.128.95, utilisateur ubuntu |
| RAM | 7.6 Go total, 5.6 Go disponibles |
| Disque | 72 Go total, 57 Go disponibles |
| Reverse proxy | Caddy dans `~/proxy/` |
| Réseau Docker | `web_net` (externe) |
| Sous-domaines prévus | `sysml-agent.franckkenfack.works` + `api.sysml-agent.franckkenfack.works` |

**Fichiers de déploiement créés mais pas encore exécutés** :
- `docker-compose.prod.yml` — 3 services (backend, frontend, plantuml) pour la prod
- `.gitlab-ci.yml` — Pipeline build + deploy
- `deploy/setup_vps.sh` — Script de setup initial VPS
- `deploy/DEPLOY.md` — Guide de déploiement

**Note** : SysON n'a pas encore été ajouté au déploiement VPS (RAM limitée, à évaluer).

### 5.4 Variables GitLab CI/CD à configurer

| Variable | Valeur |
|---|---|
| SSH_IP | 152.228.128.95 |
| SSH_USER | ubuntu |
| SSH_PRIVATE_KEY | Clé privée encodée en base64 |
| GEMINI_API_KEYS | Clés API Gemini |
| GEMINI_API_KEY | Clé principale |
| LLM_MODEL | gemini-2.5-flash |
| GEMINI_MODEL | gemini-2.0-flash |

---

## 6. ENVIRONNEMENT LOCAL

### 6.1 Machine de développement

| Élément | Détail |
|---|---|
| Machine | Dell 16 DC16250 |
| OS | Linux (Ubuntu) |
| RAM | 15 Go total |
| Chemin projet | `~/Documents/Ensta/Work_safran/sysmlv2/sysml-agent/` |
| Chemin SysML-v2-Release | `~/Documents/Ensta/Work_safran/sysmlv2/SysML-v2-Release/` |
| Python | Conda (base) |
| Docker | Docker Compose installé |

### 6.2 Configuration LLM

Le fichier `.env` (non versionné) contient :
- `GEMINI_API_KEYS` — Plusieurs clés Gemini séparées par des virgules (rotation)
- `GEMINI_API_KEY` — Clé principale
- `LLM_MODEL` — gemini-2.5-flash
- `GEMINI_MODEL` — gemini-2.0-flash

Un fichier `.env.example` est versionné avec des placeholders.

---

## 7. PERSPECTIVE D'ÉVOLUTION — SYSON COMME PLATEFORME

### 7.1 Idée discutée mais non implémentée

On a discuté la possibilité de **réécrire toute notre logique Python dans SysON** (en Java) pour avoir un seul produit. L'architecture cible serait un module Maven `syson-ai-assistant` dans le projet SysON.

**Décision** : reporté. Trop complexe pour le calendrier actuel. Présenté comme perspective V2 au client.

### 7.2 Message envoyé au client

Un message a été rédigé pour présenter l'approche SysON au client. Il explique :
- Ce qu'on a construit (le pipeline NL → SysML v2)
- L'amélioration proposée (intégration SysON pour visualisation)
- Les 8 étapes du flux utilisateur
- Pourquoi c'est la meilleure approche (outil de référence, vrai parser, une seule interface, facilement réalisable)

---

## 8. OÙ ON EN EST — ÉTAT AU 21 FÉVRIER 2026

### 8.1 Ce qui est FAIT et FONCTIONNE

- ✅ Pipeline complet NL → JSON → SysML v2 (4 niveaux MBSE)
- ✅ RAG avec 337 chunks SysML v2 officiels
- ✅ 7 types de diagrammes PlantUML
- ✅ Fidelity Checker anti-hallucination
- ✅ Validateur syntaxique SysML v2
- ✅ Rotation multi-clés API Gemini
- ✅ 147+ tests automatisés passent
- ✅ Expérience V1 contrôle d'accès (4 styles × 4 niveaux) avec analyse comparative
- ✅ Corrections de prompts P1-P4 appliquées
- ✅ Code poussé sur GitHub (60 fichiers, commit 0910904)
- ✅ Intégration SysON fonctionnelle (import via GraphQL, modèle visible)
- ✅ Test parking validé dans SysON
- ✅ 12 tests SysON ajoutés
- ✅ Description BAS Silvercrest créée dans `experiments/descriptions/`

### 8.2 Ce qui est EN COURS

- 🔄 Test BAS Silvercrest sur les 4 niveaux MBSE (prompt Copilot CLI en attente)
- 🔄 Vérification que l'ajout de SysON n'a rien cassé

### 8.3 Ce qui reste À FAIRE

- ⬜ Exécuter le test BAS Silvercrest et exporter les résultats
- ⬜ Pousser le résultat BAS dans SysON et vérifier les diagrammes
- ⬜ Pousser le code mis à jour (intégration SysON) sur GitHub
- ⬜ Générer le livrable PDF (synthèse des prompts)
- ⬜ Générer le livrable Excel (export des échanges)
- ⬜ Déploiement VPS (via GitLab CI/CD)
- ⬜ Lancer les tests V2 (après corrections prompts P1-P4) sur contrôle d'accès

---

## 9. COMMENT REPRENDRE LE TRAVAIL

Si vous perdez le contexte, voici l'ordre pour reprendre :

1. **Relire ce document** pour comprendre tout ce qui a été fait
2. **Vérifier l'état des services** : `docker compose ps` depuis `~/Documents/Ensta/Work_safran/sysmlv2/sysml-agent/`
3. **Lancer les tests** : `docker compose exec backend pytest tests/ -v --tb=short`
4. **Consulter les résultats existants** : `ls experiments/results/`
5. **Le prochain prompt Copilot CLI à exécuter** est celui qui vérifie que rien n'est cassé + lance le test BAS Silvercrest (fourni dans la conversation juste avant ce document)

---

*Document de contexte complet — Projet SysML v2 Agent — 21 février 2026*

