# Cartographie complète du projet SysML v2 Agent

> **Date** : 27 février 2026
> **Statut** : Investigation pure — aucun fichier modifié
> **Objectif** : État précis du code avant restructuration

---

## TABLE DES MATIÈRES

1. [Arborescence complète avec tailles](#1-arborescence-complète-avec-tailles)
2. [Inventaire des services backend](#2-inventaire-des-services-backend)
3. [Inventaire des endpoints API](#3-inventaire-des-endpoints-api)
4. [Inventaire des schémas Pydantic](#4-inventaire-des-schémas-pydantic)
5. [Inventaire des prompts LLM](#5-inventaire-des-prompts-llm)
6. [Configuration Docker Compose](#6-configuration-docker-compose)
7. [Dépendances Python](#7-dépendances-python)
8. [Structure du frontend](#8-structure-du-frontend)
9. [Fichiers de données et expériences](#9-fichiers-de-données-et-expériences)
10. [Classification de chaque fichier](#10-classification-de-chaque-fichier)
11. [Anomalies et points d'attention](#11-anomalies-et-points-dattention)
12. [État Git — fichiers non commités](#12-état-git--fichiers-non-commités)

---

## 1. Arborescence complète avec tailles

```
sysml-agent/                              (racine du projet)
├── .env                                  [NON VERSIONNÉ — clés API, config locale]
├── CONTEXT.md                            (468 lignes) — Document de contexte étendu (21/02/2026)
├── README.md                             — Documentation principale
├── docker-compose.yml                    (77 lignes) — Orchestration 5 services Docker
├── rebuild.sh                            (18 lignes) — Script rebuild Docker complet
├── check_access.py                       (71 lignes) — Script de diagnostic Gemini (liste tous les modèles)
├── list_models.py                        (33 lignes) — Script simple liste modèles Gemini disponibles
├── new.md                                (525 lignes) — Document de contexte alternatif/complémentaire
│
├── backend/                              [Service FastAPI — cœur applicatif]
│   ├── __init__.py                       (0 ligne) — Package marker
│   ├── main.py                           (1 127 lignes) — Point d'entrée API, tous les endpoints
│   ├── config.py                         (61 lignes) — Configuration centralisée (pydantic-settings)
│   ├── conftest.py                       (7 lignes) — Configuration pytest (ajout au sys.path)
│   ├── Dockerfile                        — Image Docker backend
│   ├── .dockerignore                     — Fichiers exclus du build Docker
│   ├── requirements.txt                  (28 lignes) — Dépendances Python
│   │
│   ├── models/
│   │   ├── __init__.py                   (0 ligne) — Package marker
│   │   └── schemas.py                    (261 lignes) — Tous les schémas Pydantic
│   │
│   ├── prompts/                          [Prompts LLM par niveau MBSE]
│   │   ├── __init__.py                   (0 ligne) — Package marker
│   │   ├── json_prompt.py                (108 lignes) — Pipeline V1 : NL → JSON
│   │   ├── sysml_prompt.py               (71 lignes) — Pipeline V1 : JSON → SysML v2
│   │   ├── patch_prompt.py               (60 lignes) — Pipeline V1 : modification incrémentale
│   │   ├── operational_prompt.py         (223 lignes) — Pipeline V2 : niveau Opérationnel (2 fonctions)
│   │   ├── functional_prompt.py          (250 lignes) — Pipeline V2 : niveau Fonctionnel (2 fonctions)
│   │   ├── logical_prompt.py             (288 lignes) — Pipeline V2 : niveau Logique (2 fonctions)
│   │   └── technical_prompt.py           (281 lignes) — Pipeline V2 : niveau Technique (2 fonctions)
│   │
│   ├── services/                         [Services métier]
│   │   ├── __init__.py                   (0 ligne) — Package marker
│   │   ├── llm_base.py                   (35 lignes) — Classe abstraite LLMBase (interface)
│   │   ├── llm_gemini.py                 (151 lignes) — Client Gemini + rotation multi-clés
│   │   ├── llm_factory.py                (74 lignes) — Factory pattern instanciation LLM
│   │   ├── rag_service.py                (257 lignes) — RAG : indexation + recherche ChromaDB
│   │   ├── state_service.py              (424 lignes) — Persistence sessions JSON sur disque
│   │   ├── sysml_service.py              (306 lignes) — Pipeline V1 : orchestration linéaire
│   │   ├── level_service.py              (747 lignes) — Pipeline V2 : orchestration MBSE 4 niveaux
│   │   ├── diagram_service.py            (890 lignes) — Génération diagrammes PlantUML (10 types)
│   │   ├── fidelity_checker.py           (349 lignes) — Anti-hallucination (Levenshtein)
│   │   ├── sysml_validator.py            (626 lignes) — Validation syntaxique SysML v2 (5 niveaux)
│   │   └── syson_service.py              (511 lignes) — [NON COMMITÉ] Communication GraphQL SysON
│   │
│   ├── scripts/
│   │   └── index_sysml.py                (62 lignes) — Script ré-indexation manuelle RAG
│   │
│   └── tests/
│       ├── __init__.py                   (0 ligne)
│       ├── test_api_health.py            (186 lignes) — Tests endpoints santé
│       ├── test_config.py                (43 lignes) — Tests configuration
│       ├── test_schemas.py               (246 lignes) — Tests validation schémas Pydantic
│       ├── test_prompts.py               (142 lignes) — Tests construction prompts
│       ├── test_state_service.py         (150 lignes) — Tests CRUD sessions
│       ├── test_fidelity_checker.py      (260 lignes) — Tests anti-hallucination (16 tests)
│       ├── test_diagram_service.py       (359 lignes) — Tests génération PlantUML
│       ├── test_diagram_levels.py        (287 lignes) — Tests diagrammes par niveau MBSE
│       ├── test_llm_factory.py           (79 lignes) — Tests factory LLM
│       ├── test_llm_rotation.py          (181 lignes) — Tests rotation clés API (10 tests)
│       ├── test_sysml_validator.py       (436 lignes) — Tests validateur syntaxique (23 tests)
│       ├── test_syson_integration.py     (176 lignes) — [NON COMMITÉ] Tests SysON (12 tests)
│       └── [test_level_service.py]       ← SUPPRIMÉ (D dans git status) — Tests pipeline V2
│
├── frontend/
│   ├── app.py                            (1 100 lignes) — Interface Streamlit complète
│   ├── Dockerfile                        — Image Docker frontend
│   └── requirements.txt                  (2 lignes) — streamlit==1.42.0, requests==2.32.3
│
├── deliverables/                         [NON COMMITÉ — livrables projet]
│   ├── pipeline_analysis.md              (2 327 lignes) — Analyse exhaustive du pipeline
│   ├── rapport_final.md                  — Rapport final Safran
│   ├── rapport_interactif.html           — Rapport interactif HTML
│   ├── echanges_ia.xlsx                  — Export Excel échanges LLM
│   └── generate_excel.py                 — Script génération Excel
│
├── docs/                                 [NON COMMITÉ]
│   └── LLM_PROBLEMES_ET_CORRECTIONS.md  — Documentation des 6 problèmes LLM et corrections P1-P4
│
├── experiments/                          [Scripts et résultats d'expériences]
│   ├── run_experiment.py                 — Script lancement automatisé des expériences
│   ├── export_markdown.py                — Script export échanges LLM en Markdown
│   ├── descriptions/
│   │   ├── controle_acces/               — 4 styles description contrôle d'accès
│   │   │   ├── style_conversationnel.txt
│   │   │   ├── style_formel.txt
│   │   │   ├── style_liste.txt
│   │   │   └── style_narratif.txt
│   │   └── bleed_air_system/             [NON COMMITÉ] — 2 versions description BAS Silvercrest
│   │       ├── style_formel.txt
│   │       └── style_formel_v2.txt
│   └── results/
│       ├── COMPARAISON_V1_V2.md         — Comparaison pipeline V1 vs V2
│       ├── controle_acces/              — Résultats exp. V1 (4 styles × 4 niveaux)
│       │   ├── README.md
│       │   ├── ANALYSE_COMPARATIVE.md
│       │   └── style_{formel,conversationnel,liste,narratif}/
│       │       ├── description.md
│       │       ├── operational.md        — Prompt + réponse LLM + code SysML v2
│       │       ├── functional.md
│       │       ├── logical.md
│       │       └── technical.md
│       ├── controle_acces_v2/           — Résultats exp. V2 (corrections P1-P4)
│       │   ├── README.md
│       │   ├── ANALYSE_COMPARATIVE.md
│       │   └── style_conversationnel/   (5 fichiers md)
│       └── bleed_air_system/            — Résultats BAS Silvercrest
│           ├── COMPARAISON_V1_V2.md
│           ├── DIAGNOSTIC_QUALITE.md
│           └── style_formel{,_v2}/      (4 fichiers md chacun)
│
├── LIVRABLES_v1/                         [NON COMMITÉ]
│   ├── presentation (1).pdf             — Présentation PDF Safran
│   ├── rapport_interactif.html          — Rapport interactif v1
│   └── readme_important_a_lire.md       — README v1
│
└── LIVRABLES_v1.zip                      [NON COMMITÉ] — Archive des livrables v1

TOTAL CODE SOURCE : ~10 684 lignes (services + prompts + tests + frontend + backend/main.py)
```

---

## 2. Inventaire des services backend

### 2.1 `llm_base.py` — Interface abstraite LLM (35 lignes)

| Élément | Type | Signature |
|---------|------|-----------|
| `LLMBase` | Classe abstraite (ABC) | — |
| `generate()` | Méthode abstraite | `(prompt: str, temperature: float, max_tokens: int, response_mime_type: str) → str` |
| `get_model_name()` | Méthode abstraite | `() → str` |
| `get_provider_name()` | Méthode abstraite | `() → str` |

**Imports :** `abc.ABC`, `abc.abstractmethod`

---

### 2.2 `llm_gemini.py` — Client Gemini avec rotation multi-clés (151 lignes)

| Élément | Type | Description |
|---------|------|-------------|
| `GeminiLLM` | Classe | Implémentation LLMBase pour Google Gemini |
| `__init__()` | Constructeur | `(api_keys: list[str], model_name: str, temperature: float, max_tokens: int)` — initialise les clients Gemini par clé |
| `_rotate_key()` | Méthode privée | Sélectionne la prochaine clé disponible (round-robin, ignore `failed_keys`) |
| `generate()` | Méthode publique | Envoie le prompt, gère les erreurs 429/quota → rotation automatique |
| `get_model_name()` | Méthode publique | Retourne le nom du modèle |
| `get_provider_name()` | Méthode publique | Retourne `"gemini"` |

**Attributs clés :**
- `self.clients` : liste de clients `google.genai.Client` (un par clé)
- `self.failed_keys` : `set` des index de clés épuisées
- `self.current_key_index` : index courant (rotation)

**Imports :** `from google import genai`, `logging`

**Déclencheurs de rotation :** erreur contenant `"429"`, `"RESOURCE_EXHAUSTED"`, `"quota"`, `"rate limit"`, `"rateLimitExceeded"`

---

### 2.3 `llm_factory.py` — Factory pattern LLM (74 lignes)

| Élément | Type | Description |
|---------|------|-------------|
| `LLMFactory` | Classe | Factory pour instanciation LLM |
| `create_llm()` | Méthode statique | `(provider: str, api_keys: list, model_name: str, ...) → LLMBase` |

**Imports :** `services.llm_base`, `services.llm_gemini`

**Providers supportés :** `"gemini"` (implémenté) ; `"openai"` et `"ollama"` prévus mais non implémentés (raise `ValueError`)

---

### 2.4 `rag_service.py` — Service RAG ChromaDB (257 lignes)

| Élément | Type | Description |
|---------|------|-------------|
| `RAGService` | Classe | Service RAG avec ChromaDB |
| `__init__()` | Constructeur | `(chroma_dir: Path, embedding_model: str, sysml_repo_path: Path)` |
| `index_sysml_files()` | Méthode publique | `(force: bool) → dict` — Indexe tous les `.sysml` du dépôt SysML-v2-Release |
| `_split_sysml_code()` | Méthode privée | Découpe un fichier SysML en chunks de `RAG_CHUNK_SIZE` (1500) avec overlap 200 |
| `search()` | Méthode publique | `(query: str, n_results: int) → list[dict]` — Recherche sémantique ChromaDB |
| `get_stats()` | Méthode publique | `() → dict` — Statistiques collection (total_chunks, unique_files, files) |

**Retour de `search()`** : `[{"content": str, "source_file": str, "score": float}, ...]`
⚠️ **La clé retournée est `"source_file"`, PAS `"file"`** (voir Anomalies §11)

**Imports :** `chromadb`, `sentence_transformers.SentenceTransformer`, `pathlib.Path`

**Modèle d'embeddings :** `all-MiniLM-L6-v2` (local, ~80 MB)

---

### 2.5 `state_service.py` — Persistence sessions JSON (424 lignes)

| Élément | Type | Description |
|---------|------|-------------|
| `StateService` | Classe | CRUD sessions JSON sur disque |
| `__init__()` | Constructeur | `(state_dir: Path)` — répertoire `data/state/` |
| `create_session()` | Méthode | `(description: str, system_name: str) → SessionData` |
| `init_session_with_levels()` | Méthode | Crée la session + initialise les 4 `LevelData` vides |
| `get_session()` | Méthode | `(session_id: str) → SessionData \| None` |
| `list_sessions()` | Méthode | `() → list[dict]` — liste résumée des sessions |
| `save_level()` | Méthode | `(session_id, level, model_dict, sysml_code, diagrams)` |
| `get_level()` | Méthode | `(session_id, level) → LevelData \| None` |
| `validate_level()` | Méthode | `(session_id, level) → bool` — marque un niveau comme validé |
| `save_exchange()` | Méthode | `(session_id, exchange: LLMExchange)` — trace un échange LLM |
| `get_exchanges()` | Méthode | `(session_id) → list[LLMExchange]` |
| `delete_session()` | Méthode | `(session_id) → bool` — supprime le fichier JSON |
| `rename_session()` | Méthode | `(session_id, name) → bool` |

**Format de stockage :** `data/state/{session_id}.json` — sérialisé via `.model_dump()` / `.model_validate()`

**Imports :** `json`, `pathlib`, `uuid`, `datetime`, `models.schemas.*`

---

### 2.6 `sysml_service.py` — Pipeline V1 linéaire (306 lignes)

| Élément | Type | Description |
|---------|------|-------------|
| `SysMLService` | Classe | Orchestration pipeline V1 |
| `__init__()` | Constructeur | `(llm, rag, state)` — injection de dépendances |
| `generate()` | Méthode | `(request: GenerateRequest) → GenerateResponse` — NL → JSON → SysML |
| `patch()` | Méthode | `(request: PatchRequest) → PatchResponse` — modification incrémentale |
| `_parse_json_response()` | Méthode privée | Parse et valide la réponse JSON du LLM |
| `_clean_sysml_code()` | Méthode privée | Supprime markdown, blocs de code, nettoie le code SysML |

**Flux `generate()` :**
1. Recherche RAG (`rag.search(description)`) → `rag_sources` (clé `"source_file"`)
2. Construit prompt JSON (`build_json_prompt(description, rag_context)`)
3. Appel LLM → parse JSON → valide `SystemModel`
4. Construit prompt SysML (`build_sysml_prompt(model_json)`)
5. Appel LLM → nettoie code SysML
6. Sauvegarde session (`state.create_session()`)

**Imports :** `prompts.json_prompt`, `prompts.sysml_prompt`, `prompts.patch_prompt`, `models.schemas`

---

### 2.7 `level_service.py` — Pipeline V2 MBSE 4 niveaux (747 lignes)

| Élément | Type | Description |
|---------|------|-------------|
| `LevelService` | Classe | Orchestration pipeline V2 MBSE |
| `__init__()` | Constructeur | `(llm, rag, state, diagram_service, fidelity_checker)` |
| `generate_level()` | Méthode principale | `(request: GenerateLevelRequest) → LevelResponse` |
| `_generate_json_for_level()` | Méthode privée | NL/JSON précédent → JSON du niveau courant |
| `_generate_sysml_for_level()` | Méthode privée | JSON → SysML v2 du niveau |
| `patch_level()` | Méthode | `(request: PatchLevelRequest) → PatchLevelResponse` |
| `validate_level()` | Méthode | `(request: ValidateLevelRequest) → dict` |
| `check_coherence()` | Méthode | `(session_id, level) → dict` — vérifie cohérence inter-niveaux |
| `get_full_sysml()` | Méthode | `(session_id) → str` — concatène les SysML des 4 niveaux |
| `get_level_status()` | Méthode | `(session_id) → dict` — statut de chaque niveau |
| `_validate_json_for_level()` | Méthode privée | Valide le JSON selon le modèle Pydantic du niveau |
| `_get_previous_level_context()` | Méthode privée | Récupère le JSON du niveau précédent pour le passer au LLM |

**Flux `generate_level()` :**
1. Création/récupération session
2. Recherche RAG → `rag_sources = [r["file"] for r in results]` ← **BUG : clé "source_file" ≠ "file"**
3. Construction prompt JSON selon le niveau (`operational_prompt`, `functional_prompt`, etc.)
4. Appel LLM (JSON mode) → validation Pydantic
5. Si niveau `logical`/`technical` : FidelityChecker → retry si composants manquants
6. Construction prompt SysML → appel LLM → nettoyage code
7. Sauvegarde session + échange LLM

**Imports :** `prompts.operational_prompt`, `prompts.functional_prompt`, `prompts.logical_prompt`, `prompts.technical_prompt`, `services.fidelity_checker`, `services.state_service`, `models.schemas`

---

### 2.8 `diagram_service.py` — Génération diagrammes PlantUML (890 lignes)

| Élément | Type | Description |
|---------|------|-------------|
| `DiagramService` | Classe | Génération diagrammes PlantUML (sans LLM) |
| `__init__()` | Constructeur | `(plantuml_url: str)` |
| `generate_for_level()` | Méthode | Dispatcher → appelle les méthodes selon le niveau |
| `generate_context()` | Méthode | Opérationnel : diagramme de contexte |
| `generate_use_cases()` | Méthode | Opérationnel : cas d'utilisation |
| `generate_actors_diagram()` | Méthode | Opérationnel : diagramme d'acteurs |
| `generate_operational_sequence()` | Méthode | Opérationnel : séquence opérationnelle |
| `generate_functional_breakdown()` | Méthode | Fonctionnel : arborescence (FBS) |
| `generate_functional_behavior()` | Méthode | Fonctionnel : comportement fonctionnel |
| `generate_modes_diagram()` | Méthode | Fonctionnel : modes opératoires |
| `generate_bdd()` | Méthode | Logique : Block Definition Diagram |
| `generate_ibd()` | Méthode | Logique : Internal Block Diagram |
| `generate_requirements()` | Méthode | Logique : diagramme d'exigences |
| `generate_technical_architecture()` | Méthode | Technique : architecture technique |
| `_render_svg()` | Méthode privée | POST HTTP vers serveur PlantUML → SVG |
| `_sanitize_id()` | Méthode privée | Nettoie les noms pour PlantUML (enlève accents, espaces) |

**Imports :** `httpx`, `base64`, `re`, `models.schemas`, `logging`

---

### 2.9 `fidelity_checker.py` — Anti-hallucination LLM (349 lignes)

| Élément | Type | Description |
|---------|------|-------------|
| `FidelityChecker` | Classe | Vérifie fidélité du modèle généré vs description |
| `check()` | Méthode principale | `(description, model_dict, level) → dict{ok, missing, correction_feedback}` |
| `_extract_components_from_description()` | Méthode privée | Extraction composants via regex + filtrage |
| `_extract_components_from_model()` | Méthode privée | Extraction composants du JSON généré |
| `_fuzzy_match()` | Méthode privée | Matching approximatif (Levenshtein ≤ 2) |
| `_levenshtein_distance()` | Méthode privée | Calcul distance d'édition |
| `_contains_conjugated_verb()` | Méthode privée | Filtre expressions verbales conjuguées |

**Constantes :**
- `EXCLUDED_PATTERNS` : 7 regex (phrases types "les parties prenantes sont…")
- `EXCLUDED_WORDS` : 27 mots filtrés (stakeholder, acteur, système, verbes, unités…)

**Actif sur :** niveaux `logical` et `technical` uniquement

**Imports :** `re`, `logging`

---

### 2.10 `sysml_validator.py` — Validateur syntaxique SysML v2 (626 lignes)

| Élément | Type | Description |
|---------|------|-------------|
| `SysMLv2Validator` | Classe | Validation syntaxique multi-niveaux |
| `validate()` | Méthode principale | `(code: str) → {score: int, errors: list, warnings: list, info: list, valid: bool}` |
| `_check_structure()` | Méthode | Accolades équilibrées, points-virgules, mots-clés |
| `_check_declarations()` | Méthode | Types définis vs référencés, doublons |
| `_check_references()` | Méthode | Flux, connexions, satisfy/verify |
| `_check_naming()` | Méthode | PascalCase (types), camelCase (instances) |
| `_check_completeness()` | Méthode | Packages vides, définitions inutilisées |
| `_calculate_score()` | Méthode | Score 0-100 basé sur erreurs/warnings |

**Imports :** `re`, `logging`

**Note :** Validateur basé sur regex uniquement — ANTLR4 (grammaire officielle) commenté dans `requirements.txt`

---

### 2.11 `syson_service.py` — Communication GraphQL SysON (511 lignes) [NON COMMITÉ]

| Élément | Type | Description |
|---------|------|-------------|
| `SysONService` | Classe | Client HTTP GraphQL vers Eclipse SysON |
| `__init__()` | Constructeur | `(syson_url: str)` |
| `is_available()` | Méthode | `() → bool` — ping SysON (GET `/api/graphql`) |
| `push_sysml_to_syson()` | Méthode | Flux complet : create_project + import_sysml |
| `create_project()` | Méthode | Mutation GraphQL `createProject` (`templateId: "sysmlv2-template"`) |
| `get_editing_context()` | Méthode | Query GraphQL `editingContext` |
| `create_document()` | Méthode | Mutation `createDocument` (`stereotypeId: "empty_sysmlv2"`) |
| `get_root_namespace_id()` | Méthode | Mutation `createRootObject` → récupère l'ID namespace racine |
| `import_sysml_code()` | Méthode | Mutation `insertTextualSysMLv2` |
| `export_sysml_from_syson()` | Méthode | Récupère le code SysML depuis SysON |
| `list_projects()` | Méthode | Liste tous les projets SysON |

**Imports :** `httpx`, `json`, `logging`

---

## 3. Inventaire des endpoints API

**Fichier :** `backend/main.py` (1 127 lignes)
**Initialisation :** à la racine `main.py`, les 5 services sont instanciés (LLM, RAG, State, Diagram, Fidelity, Level, Sysml, SysON, Validator)

### Groupe : Santé & Diagnostic

| Méthode | Route | Description | Service utilisé |
|---------|-------|-------------|-----------------|
| GET | `/api/health` | Statut global (LLM, RAG, SysON) | all |
| GET | `/api/test-llm` | Test rapide LLM avec prompt simple | llm |
| GET | `/api/llm-status` | État de chaque clé API (rotation) | llm |
| GET | `/api/rag/stats` | Statistiques ChromaDB | rag |
| GET | `/api/rag/search` | Recherche dans la base RAG (`?q=...`) | rag |

### Groupe : Pipeline V1 (linéaire)

| Méthode | Route | Description | Schéma requête | Schéma réponse |
|---------|-------|-------------|----------------|----------------|
| POST | `/api/generate` | Génère un système complet (NL → JSON → SysML) | `GenerateRequest` | `GenerateResponse` |
| POST | `/api/patch` | Modifie un système existant | `PatchRequest` | `PatchResponse` |
| GET | `/api/session/{id}` | Récupère une session V1 | — | `SessionData` |
| GET | `/api/sessions` | Liste toutes les sessions | — | `{sessions: list}` |
| POST | `/api/diagrams` | Génère tous les diagrammes (V1) | `{session_id}` | `DiagramsResponse` |
| POST | `/api/diagrams/{type}` | Génère un diagramme spécifique | `{session_id}` | `{svg}` |

### Groupe : Pipeline V2 MBSE (actif)

| Méthode | Route | Description | Schéma requête | Schéma réponse |
|---------|-------|-------------|----------------|----------------|
| POST | `/api/v2/generate` | Génère un niveau MBSE | `GenerateLevelRequest` | `LevelResponse` |
| POST | `/api/v2/patch` | Modifie un niveau MBSE | `PatchLevelRequest` | `PatchLevelResponse` |
| POST | `/api/v2/validate` | Valide un niveau (→ passage suivant) | `ValidateLevelRequest` | `{validated: bool}` |
| PUT | `/api/v2/session/{id}/name` | Renomme une session | `RenameSessionRequest` | `{ok: bool}` |
| GET | `/api/v2/coherence/{session_id}/{level}` | Cohérence inter-niveaux | — | `{ok, issues, warnings}` |
| GET | `/api/v2/status/{session_id}` | Statut de tous les niveaux | — | `{operational: {generated, validated}, ...}` |
| GET | `/api/v2/level/{session_id}/{level}` | Données complètes d'un niveau | — | `LevelData` |
| GET | `/api/v2/full-sysml/{session_id}` | SysML v2 complet (4 niveaux concaténés) | — | `{sysml_code: str}` |
| POST | `/api/v2/diagrams` | Génère diagrammes d'un niveau | `GenerateDiagramsRequest` | `DiagramsResponse` |
| GET | `/api/v2/diagrams/{session_id}/{level}` | Diagrammes sauvegardés d'un niveau | — | `DiagramsResponse` |

### Groupe : Validation SysML v2

| Méthode | Route | Description | Schéma |
|---------|-------|-------------|--------|
| POST | `/api/validate-sysml` | Valide du code SysML v2 brut | `{sysml_code: str}` → `{score, errors, warnings, valid}` |
| GET | `/api/validate-sysml/{session_id}` | Valide le SysML d'une session | — → `{score, errors, warnings, valid}` |

### Groupe : Traçabilité LLM

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/v2/exchanges/{session_id}` | Historique de tous les échanges LLM de la session |
| GET | `/api/v2/export/{session_id}` | Export complet de la session (JSON) |

### Groupe : SysON

| Méthode | Route | Description | Retour |
|---------|-------|-------------|--------|
| GET | `/api/syson/status` | SysON disponible ? | `{available: bool, url: str}` |
| POST | `/api/syson/push` | Importe SysML dans SysON | `{project_id, project_url, ok}` |
| GET | `/api/syson/project-url/{session_id}` | URL du projet SysON d'une session | `{url: str}` |

**Total : 28 endpoints actifs**

---

## 4. Inventaire des schémas Pydantic

**Fichier :** `backend/models/schemas.py` (261 lignes)

### Schémas de base (partagés V1 et V2)

| Schéma | Champs principaux | Usage |
|--------|-------------------|-------|
| `PortSchema` | `name`, `direction` (in/out/inout), `type` | Ports sur les parts |
| `ConnectionSchema` | `from_port`, `to_port`, `type` (flow/connection/interface), `item?`, `description?` | Connexions entre ports |
| `RequirementSchema` | `id`, `text`, `satisfied_by?` | Exigences |
| `UseCaseSchema` | `name`, `actors`, `includes?` | Cas d'utilisation |
| `PartSchema` | `name`, `type?`, `description?`, `ports[]`, `children[]` | Composants/sous-composants (récursif) |

### Modèles par niveau MBSE

| Modèle | Champs spécifiques | Niveau |
|--------|-------------------|--------|
| `OperationalModel` | `stakeholders[]`, `external_systems[]`, `system_boundaries`, `use_cases[]`, `operational_scenarios[]`, `requirements[]` | Niveau 1 |
| `FunctionalModel` | `functions[]` (avec `sub_functions`, `inputs`, `outputs`), `functional_flows[]`, `modes[]` | Niveau 2 |
| `LogicalModel` | `parts[]`, `connections[]`, `requirements[]` | Niveau 3 |
| `TechnicalModel` | `technical_parts[]`, `physical_connections[]`, `technology_choices[]` | Niveau 4 |
| `SystemModel` | `parts[]`, `connections[]`, `requirements[]`, `use_cases[]` | Pipeline V1 uniquement |

### Schémas de session

| Schéma | Description |
|--------|-------------|
| `ModelLevel` | Enum : `OPERATIONAL`, `FUNCTIONAL`, `LOGICAL`, `TECHNICAL` |
| `LevelData` | `level`, `model` (dict), `sysml_code`, `diagrams[]`, `validated`, `history[]` |
| `LLMExchange` | `id`, `timestamp`, `session_id`, `level`, `operation`, `description_input`, `prompt_sent`, `llm_response_raw`, `llm_model`, `sysml_code`, `success`, `error_message` |
| `SessionData` | `session_id`, `session_name`, `created_at`, `updated_at`, `system_name`, `description`, `current_level`, `levels` (dict), `exchanges[]` |

### Schémas de requêtes/réponses API

| Schéma | Usage |
|--------|-------|
| `GenerateRequest` / `GenerateResponse` | Pipeline V1 — génération |
| `PatchRequest` / `PatchResponse` | Pipeline V1 — modification |
| `GenerateLevelRequest` | Pipeline V2 — génération d'un niveau |
| `PatchLevelRequest` / `PatchLevelResponse` | Pipeline V2 — modification d'un niveau |
| `ValidateLevelRequest` | Pipeline V2 — validation |
| `GenerateDiagramsRequest` / `DiagramsResponse` | Génération diagrammes |
| `LevelResponse` | Réponse génération niveau (model, sysml_code, rag_sources, warnings, available_diagrams) |
| `RenameSessionRequest` | Renommage session |

---

## 5. Inventaire des prompts LLM

### Prompts Pipeline V1

#### `json_prompt.py` — `build_json_prompt(description, rag_context)` (108 lignes)

**Rôle :** Description en langage naturel → JSON `SystemModel` (pipeline linéaire)
**Contexte injecté :** exemples SysML v2 du RAG
**Format de sortie :** JSON strict avec champs `system_name`, `description`, `parts[]`, `connections[]`, `requirements[]`, `use_cases[]`

#### `sysml_prompt.py` — `build_sysml_prompt(model_json)` (71 lignes)

**Rôle :** JSON `SystemModel` → code SysML v2 syntaxiquement valide
**Format de sortie :** code SysML v2 pur (sans markdown)

#### `patch_prompt.py` — `build_patch_prompt(current_model_json, instruction)` (60 lignes)

**Rôle :** Modification incrémentale du JSON existant selon instruction utilisateur
**Règles clés :** appliquer UNIQUEMENT la modification demandée, conserver toute la structure existante, types de connexions valides (flow/connection/interface)

---

### Prompts Pipeline V2 — Opérationnel

#### `operational_prompt.py` — 2 fonctions (223 lignes)

**`build_operational_json_prompt(description, rag_context)`**
→ Description NL → JSON `OperationalModel`
Règles clés injectées :
- Un stakeholder est TOUJOURS une personne humaine (pas un équipement)
- Les exigences sont UNIQUEMENT des contraintes mesurables (avec chiffres/SLA)
- `external_systems` = équipements/logiciels en interaction (pas des personnes)

**`build_operational_sysml_prompt(model_json)`**
→ JSON `OperationalModel` → SysML v2 (packages `OperationalContext`, `StakeholderAnalysis`, `UseCaseModel`, `OperationalRequirements`)

---

### Prompts Pipeline V2 — Fonctionnel

#### `functional_prompt.py` — 2 fonctions (250 lignes)

**`build_functional_json_prompt(operational_json, rag_context)`**
→ JSON opérationnel → JSON `FunctionalModel`
**`build_functional_sysml_prompt(model_json)`**
→ JSON `FunctionalModel` → SysML v2 (packages `FunctionalBreakdown`, `FunctionalBehavior`, `OperatingModes`)

---

### Prompts Pipeline V2 — Logique

#### `logical_prompt.py` — 2 fonctions (288 lignes)

**`build_logical_json_prompt(functional_json, rag_context)`**
→ JSON fonctionnel → JSON `LogicalModel`
Règles clés injectées (corrections P3-P4) :
- Toute connexion doit lier deux composants définis dans `parts`
- Si des exigences existent dans les niveaux précédents, elles DOIVENT être allouées

**`build_logical_sysml_prompt(model_json)`**
→ JSON `LogicalModel` → SysML v2 (packages `LogicalArchitecture`, `ComponentInterfaces`, `RequirementAllocation`)

---

### Prompts Pipeline V2 — Technique

#### `technical_prompt.py` — 2 fonctions (281 lignes)

**`build_technical_json_prompt(logical_json, rag_context)`**
→ JSON logique → JSON `TechnicalModel`
**`build_technical_sysml_prompt(model_json)`**
→ JSON `TechnicalModel` → SysML v2 (packages `PhysicalArchitecture`, `TechnologyChoices`, `PhysicalInterfaces`)

---

### Récapitulatif des fonctions de prompt

| Fichier | Fonctions | Pipeline | Total lignes |
|---------|-----------|----------|-------------|
| `json_prompt.py` | `build_json_prompt` | V1 | 108 |
| `sysml_prompt.py` | `build_sysml_prompt` | V1 | 71 |
| `patch_prompt.py` | `build_patch_prompt` | V1 | 60 |
| `operational_prompt.py` | `build_operational_json_prompt`, `build_operational_sysml_prompt` | V2 | 223 |
| `functional_prompt.py` | `build_functional_json_prompt`, `build_functional_sysml_prompt` | V2 | 250 |
| `logical_prompt.py` | `build_logical_json_prompt`, `build_logical_sysml_prompt` | V2 | 288 |
| `technical_prompt.py` | `build_technical_json_prompt`, `build_technical_sysml_prompt` | V2 | 281 |

**Total : 11 fonctions de prompt**

---

## 6. Configuration Docker Compose

**Fichier :** `docker-compose.yml` (77 lignes)

### Services

| Service | Image | Port externe | Rôle | Dépendances |
|---------|-------|-------------|------|-------------|
| `backend` | Build `./backend/Dockerfile` | `8000` | API FastAPI | `plantuml` |
| `frontend` | Build `./frontend/Dockerfile` | `8501` | Interface Streamlit | `backend` |
| `plantuml` | `plantuml/plantuml-server:tomcat` | `8080` | Rendu SVG diagrammes | — |
| `syson-db` | `postgres:15` | interne | Base de données SysON | — |
| `syson` | `eclipsesyson/syson:v2026.1.0` | `8085` | Éditeur SysML v2 graphique | `syson-db` |

### Volumes

| Volume | Type | Montage | Usage |
|--------|------|---------|-------|
| `backend_data` | Volume Docker nommé | `/app/data` (backend) | Persistence sessions + ChromaDB |
| `syson_db_data` | Volume Docker nommé | `/var/lib/postgresql/data` (syson-db) | Données PostgreSQL SysON |
| `../SysML-v2-Release` | Bind mount (read-only) | `/app/SysML-v2-Release` (backend) | Source RAG |

### Variables d'environnement clés

| Service | Variable | Source | Usage |
|---------|----------|--------|-------|
| backend | `GEMINI_API_KEYS` | `.env` | Rotation multi-clés Gemini |
| backend | `GEMINI_API_KEY` | `.env` | Clé unique (rétrocompat) |
| backend | `LLM_MODEL` | `.env` | Modèle LLM (`gemini-2.5-flash`) |
| backend | `GEMINI_MODEL` | `.env` | Rétrocompat (`gemini-2.0-flash`) |
| backend | `SYSML_REPO_PATH` | compose | `/app/SysML-v2-Release` |
| backend | `PLANTUML_SERVER_URL` | compose | `http://plantuml:8080` |
| backend | `SYSON_URL` | compose | `http://syson:8080` |
| frontend | `BACKEND_URL` | compose | `http://backend:8000` |
| syson | `SPRING_DATASOURCE_URL` | compose | `jdbc:postgresql://syson-db/syson` |

### Commandes opérationnelles

```bash
docker compose up --build -d          # Démarrer (rebuild obligatoire si code modifié)
docker compose exec backend pytest tests/ -v  # Tests
./rebuild.sh                          # Rebuild complet (down + rmi + build + up)
docker compose logs backend -f        # Logs backend
```

⚠️ **Le code backend est COPIÉ dans l'image** (pas de volume de dev). Tout changement = rebuild Docker.

---

## 7. Dépendances Python

### Backend `backend/requirements.txt`

| Librairie | Version | Rôle |
|-----------|---------|------|
| `fastapi` | 0.115.6 | Framework API REST |
| `uvicorn[standard]` | 0.34.0 | Serveur ASGI |
| `pydantic` | 2.10.4 | Validation des données |
| `pydantic-settings` | 2.7.1 | Configuration via `.env` |
| `chromadb` | 0.6.3 | Base vectorielle RAG |
| `sentence-transformers` | 3.4.1 | Embeddings locaux `all-MiniLM-L6-v2` |
| `google-genai` | 1.7.0 | Client Google Gemini (`from google import genai`) |
| `python-dotenv` | 1.0.1 | Chargement `.env` |
| `httpx` | 0.28.1 | HTTP async (appels PlantUML, SysON) |
| `pytest` | 8.3.4 | Tests |
| `pytest-asyncio` | 0.25.0 | Tests asynchrones |
| `antlr4-python3-runtime` | 4.13.2 | **COMMENTÉ** — réservé validation ANTLR4 SysML v2 |

### Frontend `frontend/requirements.txt`

| Librairie | Version | Rôle |
|-----------|---------|------|
| `streamlit` | 1.42.0 | Interface web |
| `requests` | 2.32.3 | Appels HTTP synchrones vers backend |

### Scripts racine (NON dans les requirements)

Les scripts `check_access.py` et `list_models.py` à la racine utilisent :
- `google.generativeai` (ancienne API — `pip install google-generativeai`)
- `python-dotenv`

⚠️ Ces scripts utilisent l'**ancienne API** (`import google.generativeai as genai`), incompatible avec le backend qui utilise la nouvelle API (`from google import genai`).

---

## 8. Structure du frontend

**Fichier :** `frontend/app.py` (1 100 lignes)

### Organisation globale

```
app.py
├── Configuration globale (lignes 1-62)
│   ├── BACKEND_URL, API_TIMEOUT
│   ├── Constantes niveaux : NIVEAUX_ORDER, LEVEL_NAMES, LEVEL_SHORT_NAMES
│   └── DIAGRAM_LABELS (10 types)
│
├── Initialisation session_state (lignes 51-61)
│   └── session_id, current_level, levels_data, system_description, level_status
│
├── Fonctions utilitaires (lignes 64-97)
│   ├── format_timestamp()
│   ├── load_level_status() → GET /api/v2/status/{id}
│   └── get_level_icon() → ✅/🔄/⬜ selon statut
│
├── SIDEBAR (lignes 100-250)
│   ├── Statut backend → GET /api/health
│   ├── Stats RAG (expander) → GET /api/rag/stats
│   ├── Gestion sessions → GET /api/sessions
│   ├── Renommer session → PUT /api/v2/session/{id}/name
│   ├── Navigation niveaux MBSE (boutons ✅/🔄/⬜)
│   └── Bouton supprimer session → DELETE /api/session/{id}
│
├── ZONE PRINCIPALE (lignes 250+)
│   ├── Si pas de session : formulaire nouveau projet
│   │   ├── Champ description texte
│   │   ├── Sélection modèle LLM, RAG on/off
│   │   └── Bouton "Générer le niveau Opérationnel" → POST /api/v2/generate
│   │
│   └── Si session active : 4 onglets
│       ├── Onglet "📝 Modèle"
│       │   ├── Résumé JSON du modèle (expander)
│       │   ├── Bouton "Modifier" (instruction patch) → POST /api/v2/patch
│       │   ├── Bouton "Valider ce niveau" → POST /api/v2/validate
│       │   ├── Cohérence inter-niveaux → GET /api/v2/coherence/{id}/{level}
│       │   └── Génération niveau suivant → POST /api/v2/generate
│       │
│       ├── Onglet "💻 Code SysML v2"
│       │   ├── Affichage code (st.code)
│       │   └── Bouton "Valider syntaxe" → POST /api/validate-sysml
│       │
│       ├── Onglet "📊 Diagrammes"
│       │   ├── Bouton génération → POST /api/v2/diagrams
│       │   ├── Affichage SVG (st.components.v1.html)
│       │   ├── Diagrammes niveaux précédents (expanders)
│       │   └── Bouton "Ouvrir dans SysON" → /api/syson/push + URL SysON
│       │
│       └── Onglet "📖 Historique"
│           └── Échanges LLM → GET /api/v2/exchanges/{id}
```

### Appels API depuis le frontend

| Endpoint appelé | Contexte UI |
|-----------------|-------------|
| `GET /api/health` | Sidebar — statut backend (à chaque rechargement) |
| `GET /api/rag/stats` | Sidebar — expander stats RAG |
| `GET /api/sessions` | Sidebar — liste sessions |
| `GET /api/v2/status/{id}` | Sidebar + onglet Modèle — statut niveaux |
| `PUT /api/v2/session/{id}/name` | Sidebar — renommage |
| `POST /api/v2/generate` | Formulaire initial + onglet Modèle (niveau suivant) |
| `POST /api/v2/patch` | Onglet Modèle — bouton Modifier |
| `POST /api/v2/validate` | Onglet Modèle — bouton Valider |
| `GET /api/v2/coherence/{id}/{level}` | Onglet Modèle — cohérence |
| `POST /api/validate-sysml` | Onglet Code SysML |
| `POST /api/v2/diagrams` | Onglet Diagrammes — génération |
| `GET /api/v2/diagrams/{id}/{level}` | Onglet Diagrammes — affichage sauvegardés |
| `GET /api/syson/status` | Onglet Diagrammes — vérification SysON |
| `POST /api/syson/push` | Onglet Diagrammes — bouton SysON |
| `GET /api/v2/exchanges/{id}` | Onglet Historique |

---

## 9. Fichiers de données et expériences

### 9.1 Données runtime (non versionnées)

| Chemin | Type | Contenu |
|--------|------|---------|
| `backend/data/chroma/` | ChromaDB | Base vectorielle RAG (197 fichiers, 337 chunks indexés) |
| `backend/data/state/{uuid}.json` | JSON | Sessions persistées (format `SessionData`) |

### 9.2 Fichiers d'expérimentation

| Fichier | Rôle |
|---------|------|
| `experiments/run_experiment.py` | Lance une expérience complète via API (4 niveaux en séquence) |
| `experiments/export_markdown.py` | Exporte les échanges LLM d'une session en Markdown |
| `experiments/descriptions/controle_acces/*.txt` | 4 styles description contrôle d'accès (formel, conversationnel, liste, narratif) |
| `experiments/descriptions/bleed_air_system/style_formel.txt` | Description BAS Silvercrest — version initiale |
| `experiments/descriptions/bleed_air_system/style_formel_v2.txt` | Description BAS Silvercrest — version corrigée |
| `experiments/results/controle_acces/` | Résultats V1 (avant corrections P1-P4) — 4 styles × 4 niveaux |
| `experiments/results/controle_acces_v2/` | Résultats V2 (après corrections P1-P4) — style conversationnel |
| `experiments/results/bleed_air_system/` | Résultats BAS Silvercrest — 2 versions |
| `experiments/results/COMPARAISON_V1_V2.md` | Comparaison pipeline V1 vs V2 |

**Format des fichiers de résultats** (ex: `style_formel/operational.md`) :
- Prompt exact envoyé au LLM
- Réponse brute (JSON)
- Code SysML v2 généré
- Warnings
- Diagrammes PlantUML

### 9.3 Livrables

| Fichier | Contenu |
|---------|---------|
| `deliverables/pipeline_analysis.md` | Analyse exhaustive pipeline (2 327 lignes) |
| `deliverables/rapport_final.md` | Rapport final Safran |
| `deliverables/rapport_interactif.html` | Rapport HTML interactif |
| `deliverables/echanges_ia.xlsx` | Export Excel échanges LLM |
| `deliverables/generate_excel.py` | Script génération Excel depuis les sessions |

### 9.4 Documentation

| Fichier | Contenu |
|---------|---------|
| `docs/LLM_PROBLEMES_ET_CORRECTIONS.md` | Documentation des 6 problèmes LLM identifiés + corrections P1-P4 appliquées |
| `CONTEXT.md` | Document contexte court (68 lignes) — architecture et points clés |
| `new.md` | Document contexte complet (525 lignes) — contexte contractuel, expérimentations, SysON, état au 21/02/2026 |
| `README.md` | Documentation principale du projet |

---

## 10. Classification de chaque fichier

### Légende
- 🗑️ **À SUPPRIMER** : fichier obsolète, dupliqué, ou ne devant pas être dans le dépôt
- ✅ **À CONSERVER TEL QUEL** : fichier sain, pas de modification nécessaire
- 🔧 **À RESTRUCTURER** : fichier fonctionnel mais avec des problèmes (bug, dette technique, taille excessive)
- 🆕 **À CRÉER** : fichier manquant nécessaire pour la restructuration

---

### Racine du projet

| Fichier | Classification | Justification |
|---------|---------------|---------------|
| `docker-compose.yml` | ✅ À conserver | Fonctionnel — 5 services bien configurés |
| `rebuild.sh` | ✅ À conserver | Script utile et simple |
| `README.md` | ✅ À conserver | Documentation principale |
| `CONTEXT.md` | 🗑️ À supprimer | Redondant avec `new.md` et la documentation structurée |
| `new.md` | 🗑️ À supprimer | Document de contexte de session — ne devrait pas être commité ; les informations utiles sont dans CONTEXT.md ou la documentation |
| `check_access.py` | 🗑️ À supprimer | Script de diagnostic one-shot avec **ancienne API** (`google.generativeai`). Inutile après installation confirmée |
| `list_models.py` | 🗑️ À supprimer | Script one-shot avec **ancienne API** (`google.generativeai`). Même objectif que `check_access.py` |
| `.env` | ✅ À conserver (non versionné) | Fichier de config local — ne pas commiter |
| `LIVRABLES_v1.zip` | 🗑️ À supprimer | Archive binaire dans un dépôt Git — à déplacer hors du repo |
| `LIVRABLES_v1/` | 🗑️ À supprimer | Dossier de livrables dans le repo — à déplacer hors du repo ou gitignorer |

---

### `backend/` — Core

| Fichier | Classification | Justification |
|---------|---------------|---------------|
| `backend/main.py` | 🔧 À restructurer | 1 127 lignes — trop grand. Tous les endpoints dans un seul fichier. À splitter en routers FastAPI : `routers/health.py`, `routers/v1.py`, `routers/v2.py`, `routers/syson.py`, `routers/validation.py` |
| `backend/config.py` | ✅ À conserver | Simple, clair, bien structuré |
| `backend/conftest.py` | ✅ À conserver | Essentiel pour les tests |
| `backend/__init__.py` | ✅ À conserver | Package marker |
| `backend/Dockerfile` | ✅ À conserver | Configuration Docker valide |
| `backend/.dockerignore` | ✅ À conserver | Optimisation image Docker |
| `backend/requirements.txt` | 🔧 À restructurer | Commenter clairement la ligne ANTLR4 ou la retirer. Ajouter `google-generativeai` pour les scripts racine si conservés |

---

### `backend/models/`

| Fichier | Classification | Justification |
|---------|---------------|---------------|
| `backend/models/__init__.py` | ✅ À conserver | — |
| `backend/models/schemas.py` | 🔧 À restructurer | 261 lignes — acceptables mais pourrait être splitté en `schemas_v1.py`, `schemas_v2.py`, `schemas_session.py`. Priorité basse |

---

### `backend/prompts/`

| Fichier | Classification | Justification |
|---------|---------------|---------------|
| `backend/prompts/__init__.py` | ✅ À conserver | — |
| `backend/prompts/json_prompt.py` | ✅ À conserver | Pipeline V1 — fonctionnel |
| `backend/prompts/sysml_prompt.py` | ✅ À conserver | Pipeline V1 — fonctionnel |
| `backend/prompts/patch_prompt.py` | ✅ À conserver | Pipeline V1 — fonctionnel |
| `backend/prompts/operational_prompt.py` | ✅ À conserver | Corrections P1-P2 appliquées |
| `backend/prompts/functional_prompt.py` | ✅ À conserver | Fonctionnel |
| `backend/prompts/logical_prompt.py` | ✅ À conserver | Corrections P3-P4 appliquées |
| `backend/prompts/technical_prompt.py` | ✅ À conserver | Fonctionnel |

---

### `backend/services/`

| Fichier | Classification | Justification |
|---------|---------------|---------------|
| `backend/services/__init__.py` | ✅ À conserver | — |
| `backend/services/llm_base.py` | ✅ À conserver | Interface abstraite propre |
| `backend/services/llm_gemini.py` | ✅ À conserver | Rotation multi-clés fonctionnelle |
| `backend/services/llm_factory.py` | ✅ À conserver | Pattern Factory propre |
| `backend/services/rag_service.py` | ✅ À conserver | Fonctionnel |
| `backend/services/state_service.py` | ✅ À conserver | CRUD sessions solide |
| `backend/services/sysml_service.py` | ✅ À conserver | Pipeline V1 — potentiellement obsolète si V2 est la priorité, mais à conserver |
| `backend/services/level_service.py` | 🔧 À restructurer | **BUG CRITIQUE** ligne ~130 : `r["file"]` doit être `r["source_file"]`. De plus, 747 lignes — peut être découpé en sous-modules |
| `backend/services/diagram_service.py` | ✅ À conserver | 890 lignes — acceptable pour la richesse des 10 types de diagrammes |
| `backend/services/fidelity_checker.py` | ✅ À conserver | Fonctionnel et bien testé |
| `backend/services/sysml_validator.py` | ✅ À conserver | Fonctionnel et bien testé (23 tests) |
| `backend/services/syson_service.py` | 🔧 À restructurer | Fonctionnel mais **NON COMMITÉ**. À commiter. Vérifier que `test_level_service.py` (supprimé) n'est pas une régression |

---

### `backend/scripts/`

| Fichier | Classification | Justification |
|---------|---------------|---------------|
| `backend/scripts/index_sysml.py` | ✅ À conserver | Script utile pour forcer la ré-indexation RAG |

---

### `backend/tests/`

| Fichier | Classification | Justification |
|---------|---------------|---------------|
| `backend/tests/__init__.py` | ✅ À conserver | — |
| `backend/tests/test_api_health.py` | ✅ À conserver | 186 lignes — tests santé |
| `backend/tests/test_config.py` | ✅ À conserver | 43 lignes — tests config |
| `backend/tests/test_schemas.py` | ✅ À conserver | 246 lignes — tests schémas Pydantic |
| `backend/tests/test_prompts.py` | ✅ À conserver | 142 lignes — tests prompts |
| `backend/tests/test_state_service.py` | ✅ À conserver | 150 lignes — tests CRUD sessions |
| `backend/tests/test_fidelity_checker.py` | ✅ À conserver | 260 lignes, 16 tests — bien couvert |
| `backend/tests/test_diagram_service.py` | ✅ À conserver | 359 lignes — tests diagrammes |
| `backend/tests/test_diagram_levels.py` | ✅ À conserver | 287 lignes — tests diagrammes par niveau |
| `backend/tests/test_llm_factory.py` | ✅ À conserver | 79 lignes — tests factory |
| `backend/tests/test_llm_rotation.py` | ✅ À conserver | 181 lignes, 10 tests — rotation bien testée |
| `backend/tests/test_sysml_validator.py` | ✅ À conserver | 436 lignes, 23 tests — le plus complet |
| `backend/tests/test_syson_integration.py` | 🔧 À restructurer | **NON COMMITÉ** — à commiter avec `syson_service.py` |
| `[test_level_service.py]` | 🆕 À recréer | **SUPPRIMÉ** dans git status — fichier de tests du pipeline V2 principal. Sa suppression est une **régression de couverture** critique |

---

### `frontend/`

| Fichier | Classification | Justification |
|---------|---------------|---------------|
| `frontend/app.py` | 🔧 À restructurer | 1 100 lignes — tout dans un seul fichier. À découper en pages/composants Streamlit. Corrections UX 2-10 identifiées dans CONTEXT.md |
| `frontend/Dockerfile` | ✅ À conserver | — |
| `frontend/requirements.txt` | ✅ À conserver | Minimal et correct |

---

### `deliverables/`

| Fichier | Classification | Justification |
|---------|---------------|---------------|
| `deliverables/pipeline_analysis.md` | ✅ À conserver | Livrable d'analyse technique (2 327 lignes) |
| `deliverables/rapport_final.md` | ✅ À conserver | Livrable Safran |
| `deliverables/rapport_interactif.html` | ✅ À conserver | Livrable HTML |
| `deliverables/echanges_ia.xlsx` | ✅ À conserver | Livrable Excel |
| `deliverables/generate_excel.py` | ✅ À conserver | Script de génération du livrable |

---

### `docs/`

| Fichier | Classification | Justification |
|---------|---------------|---------------|
| `docs/LLM_PROBLEMES_ET_CORRECTIONS.md` | ✅ À conserver | Documentation technique utile |

---

### `experiments/`

| Fichier | Classification | Justification |
|---------|---------------|---------------|
| `experiments/run_experiment.py` | ✅ À conserver | Script d'expérimentation réutilisable |
| `experiments/export_markdown.py` | ✅ À conserver | Export utile |
| `experiments/descriptions/` | ✅ À conserver | Corpus de test (8 fichiers) |
| `experiments/results/` | ✅ À conserver | Résultats d'expériences (historique) |

---

### Fichiers à créer (restructuration)

| Fichier à créer | Justification |
|-----------------|---------------|
| `backend/routers/health.py` | Extraire les endpoints santé de `main.py` |
| `backend/routers/v1.py` | Extraire les endpoints pipeline V1 de `main.py` |
| `backend/routers/v2.py` | Extraire les endpoints pipeline V2 de `main.py` |
| `backend/routers/syson.py` | Extraire les endpoints SysON de `main.py` |
| `backend/routers/validation.py` | Extraire les endpoints validation de `main.py` |
| `backend/tests/test_level_service.py` | **REÉCRIRE** — tests pipeline V2 supprimés |
| `.env.example` | Fichier exemple `.env` (si non existant déjà) |

---

## 11. Anomalies et points d'attention

### 🔴 CRITIQUE — Bug RAG dans le pipeline V2

**Fichier :** `backend/services/level_service.py`, ligne ~130
**Code actuel (bugué) :**
```python
rag_sources = [r["file"] for r in results]
```
**Code correct :**
```python
rag_sources = [r["source_file"] for r in results]
```
**Impact :** `KeyError: 'file'` à chaque appel du pipeline V2 avec `use_rag=True`. Le pipeline V2 en production avec RAG activé plante systématiquement. Le pipeline V1 (`sysml_service.py`) utilise correctement `r["source_file"]`.

---

### 🔴 CRITIQUE — `test_level_service.py` supprimé (régression couverture)

**Git status :** `D backend/tests/test_level_service.py`
**Impact :** Le fichier de tests du pipeline V2 (le pipeline principal !) a été supprimé sans remplacement. Les ~25 tests qui couvraient `generate_level()`, `patch_level()`, `validate_level()`, `check_coherence()` n'existent plus. La CI/CD ne détectera pas de régressions sur le cœur du système.
**Action requise :** Recréer `test_level_service.py` avant tout commit.

---

### 🟠 IMPORTANT — Fichiers non commités (état Git incohérent)

Les fichiers suivants ont des **modifications non commitées** :

| Fichier | Statut Git | Impact |
|---------|-----------|--------|
| `backend/main.py` | Modifié (M) | Endpoints SysON ajoutés mais non commités |
| `backend/prompts/functional_prompt.py` | Modifié (M) | Corrections prompts non commitées |
| `backend/prompts/operational_prompt.py` | Modifié (M) | Corrections P1-P2 non commitées |
| `backend/services/level_service.py` | Modifié (M) | Inclut le bug RAG + modifications SysON |
| `backend/services/state_service.py` | Modifié (M) | — |
| `docker-compose.yml` | Modifié (M) | Services syson + syson-db ajoutés |
| `frontend/app.py` | Modifié (M) | Bouton SysON ajouté |
| `backend/services/syson_service.py` | Non tracké (??) | Fichier entier non commité |
| `backend/tests/test_syson_integration.py` | Non tracké (??) | 12 tests non commités |

**Risque :** Si la branche est réinitialisée ou si le repo est cloné depuis GitHub, toute l'intégration SysON (code + tests) sera perdue.

---

### 🟠 IMPORTANT — Incohérence double modèle LLM dans `config.py`

```python
GEMINI_MODEL: str = "gemini-2.0-flash"   # Rétrocompatibilité
LLM_MODEL: str = "gemini-2.5-flash"      # Modèle actif
```

Deux variables pour le même usage, avec des noms et valeurs différents. La variable `GEMINI_MODEL` est référencée pour la rétrocompatibilité mais crée de la confusion. Un seul champ `LLM_MODEL` serait suffisant.

---

### 🟡 ATTENTION — Scripts racine avec ancienne API Google

**Fichiers :** `check_access.py`, `list_models.py`
**Problème :** Utilisent `import google.generativeai as genai` (ancienne librairie `google-generativeai`) alors que le backend utilise `from google import genai` (nouvelle librairie `google-genai`). Ces deux librairies sont différentes et incompatibles.
**Impact :** Ces scripts ne fonctionneront pas dans l'environnement Docker (seul `google-genai` est dans `requirements.txt`).

---

### 🟡 ATTENTION — `main.py` monolithique (1 127 lignes)

Tous les endpoints FastAPI dans un seul fichier. Pas d'utilisation des `APIRouter` de FastAPI. Difficile à maintenir au-delà d'une certaine taille. Recommandation : découper en 5 routers.

---

### 🟡 ATTENTION — `frontend/app.py` monolithique (1 100 lignes)

Toute l'interface Streamlit dans un seul fichier. Recommandation de refactoring identifiée dans `CONTEXT.md` (corrections 2-10 non appliquées).

---

### 🟢 INFO — ANTLR4 commenté dans requirements.txt

```python
# antlr4-python3-runtime==4.13.2
```

La validation syntaxique officielle SysML v2 via la grammaire ANTLR4 est intentionnellement reportée. La validation actuelle (regex, 5 niveaux) est fonctionnelle mais approximative.

---

### 🟢 INFO — Support multi-LLM incomplet

L'architecture (`LLMBase` + `LLMFactory`) supporte OpenAI et Ollama, mais seul Gemini est implémenté. La factory lève une `ValueError` pour les autres providers. Architecture prête, implémentation à compléter si besoin.

---

## 12. État Git — fichiers non commités

```
Branche courante : main

Fichiers modifiés (non commités) :
  M  backend/main.py
   M backend/prompts/functional_prompt.py
   M backend/prompts/operational_prompt.py
   M backend/services/level_service.py
   M backend/services/state_service.py
  D  backend/tests/test_level_service.py     ← SUPPRIMÉ
   M docker-compose.yml
   M frontend/app.py

Fichiers non trackés (untracked) :
  ?? LIVRABLES_v1.zip
  ?? LIVRABLES_v1/
  ?? backend/services/syson_service.py       ← NOUVEAU fichier non commité
  ?? backend/tests/test_syson_integration.py ← NOUVEAU fichier non commité
  ?? deliverables/
  ?? docs/
  ?? experiments/descriptions/bleed_air_system/
  ?? new.md

Commits récents :
  1f131de resultat
  0910904 Initial commit - SysML v2 Agent
```

### Actions recommandées avant restructuration

1. **Immédiat** : Corriger le bug `r["file"]` → `r["source_file"]` dans `level_service.py`
2. **Immédiat** : Recréer `test_level_service.py` (tests pipeline V2 supprimés)
3. **Court terme** : Commiter tous les fichiers non trackés (syson_service.py, test_syson_integration.py, deliverables/, docs/)
4. **Court terme** : Ajouter `LIVRABLES_v1.zip` et `LIVRABLES_v1/` au `.gitignore`
5. **Moyen terme** : Découper `main.py` en routers FastAPI
6. **Moyen terme** : Appliquer les corrections UX 2-10 identifiées dans `CONTEXT.md`

---

*Cartographie produite le 27 février 2026 — Aucun fichier modifié*
