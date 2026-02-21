# 📚 CONTEXT — SysML v2 Agent

> Fichier de référence complet pour reprendre le projet sans perdre le contexte.
> Dernière mise à jour : 20 février 2026

---

## 🎯 Objectif du projet

Créer un **agent IA** capable de générer des **modèles SysML v2** à partir de descriptions en langage naturel (français/anglais). Le système suit une approche **MBSE (Model-Based Systems Engineering)** progressive en 4 niveaux, assistée par un LLM (Google Gemini) et enrichie par RAG (base de connaissances SysML v2).

**Cas d'usage typique :** L'ingénieur décrit son système en langage naturel → l'agent génère progressivement un modèle complet (Opérationnel → Fonctionnel → Logique → Technique) avec du code SysML v2 syntaxiquement correct et des diagrammes PlantUML.

---

## 🏗️ Architecture générale

```
sysml-agent/
├── .env                          # Clés API et config (NE PAS COMMITTER)
├── docker-compose.yml            # Orchestration des 3 conteneurs
├── rebuild.sh                    # Script de rebuild Docker
├── backend/                      # API FastAPI (Python)
│   ├── main.py                   # Point d'entrée, tous les endpoints
│   ├── config.py                 # Configuration centralisée (pydantic-settings)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── models/
│   │   └── schemas.py            # Schémas Pydantic (requêtes/réponses API)
│   ├── prompts/                  # Prompts LLM par niveau MBSE
│   │   ├── json_prompt.py        # NL → JSON (v1, pipeline linéaire)
│   │   ├── sysml_prompt.py       # JSON → SysML v2 (v1, pipeline linéaire)
│   │   ├── patch_prompt.py       # Modification incrémentale (v1)
│   │   ├── operational_prompt.py # Niveau Opérationnel (v2 MBSE)
│   │   ├── functional_prompt.py  # Niveau Fonctionnel (v2 MBSE)
│   │   ├── logical_prompt.py     # Niveau Logique (v2 MBSE)
│   │   └── technical_prompt.py  # Niveau Technique (v2 MBSE)
│   ├── services/
│   │   ├── llm_base.py           # Classe abstraite LLMBase
│   │   ├── llm_gemini.py         # Implémentation Gemini + rotation de clés
│   │   ├── llm_factory.py        # Factory pattern pour instanciation LLM
│   │   ├── rag_service.py        # RAG : indexation + recherche ChromaDB
│   │   ├── state_service.py      # Persistence sessions JSON sur disque
│   │   ├── sysml_service.py      # Pipeline v1 : NL → JSON → SysML
│   │   ├── level_service.py      # Pipeline v2 MBSE multi-niveaux
│   │   ├── fidelity_checker.py   # Vérification fidélité LLM vs description
│   │   ├── diagram_service.py    # Génération diagrammes PlantUML
│   │   └── sysml_validator.py    # Validation syntaxique SysML v2
│   ├── scripts/
│   │   └── index_sysml.py        # Script de ré-indexation manuelle RAG
│   └── tests/
│       ├── test_api_health.py
│       ├── test_config.py
│       ├── test_schemas.py
│       ├── test_prompts.py
│       ├── test_state_service.py
│       ├── test_fidelity_checker.py
│       ├── test_diagram_service.py
│       ├── test_diagram_levels.py
│       ├── test_level_service.py
│       ├── test_llm_factory.py
│       ├── test_llm_rotation.py
│       └── test_sysml_validator.py
└── frontend/
    ├── app.py                    # Interface Streamlit (987 lignes)
    ├── Dockerfile
    └── requirements.txt
```

---

## 🐳 Infrastructure Docker

3 conteneurs orchestrés via `docker-compose.yml` :

| Conteneur | Image/Build | Port | Rôle |
|-----------|-------------|------|------|
| `sysml_backend` | `./backend` | `8000` | API FastAPI |
| `sysml_frontend` | `./frontend` | `8501` | Interface Streamlit |
| `sysml_plantuml` | `plantuml/plantuml-server:tomcat` | `8080` | Rendu SVG des diagrammes |

**Volume persistant :** `backend_data` → monté sur `/app/data` dans le backend (sessions + ChromaDB)
**Volume read-only :** `../SysML-v2-Release` → monté sur `/app/SysML-v2-Release` (source RAG)

**Commandes utiles :**
```bash
docker compose up --build -d          # Démarrer (rebuild)
docker compose exec backend pytest tests/ -v  # Lancer les tests
docker compose logs backend -f        # Voir les logs backend
./rebuild.sh                          # Script de rebuild complet
```

> ⚠️ Le code backend est **copié dans l'image** (pas monté en volume). Tout changement dans `/backend/` nécessite un rebuild Docker.

---

## 🔧 Technologies & Dépendances

### Backend (Python 3.x)
| Librairie | Version | Usage |
|-----------|---------|-------|
| `fastapi` | 0.115.6 | Framework API REST |
| `uvicorn` | 0.34.0 | Serveur ASGI |
| `pydantic` | 2.10.4 | Validation des données |
| `pydantic-settings` | 2.7.1 | Config via .env |
| `chromadb` | 0.6.3 | Base vectorielle RAG |
| `sentence-transformers` | 3.4.1 | Embeddings locaux (all-MiniLM-L6-v2) |
| `google-genai` | 1.7.0 | Client Gemini (API `google.genai`, PAS `google.generativeai`) |
| `httpx` | 0.28.1 | HTTP client (pour PlantUML) |
| `pytest` | 8.3.4 | Tests |
| `pytest-asyncio` | 0.25.0 | Tests asynchrones |
| `antlr4-python3-runtime` | 4.13.2 | ⚠️ COMMENTÉ — réservé pour future validation ANTLR4 |

### Frontend (Python)
- `streamlit` — Interface web
- `requests` — Appels HTTP vers le backend

---

## 🤖 LLM : Google Gemini

### Configuration (`config.py`)
```python
LLM_PROVIDER = "gemini"
GEMINI_MODEL = "gemini-2.0-flash"    # Rétrocompatibilité
LLM_MODEL = "gemini-2.5-flash"       # Modèle actif (configurable via .env)
LLM_TEMPERATURE = 0.05               # Très bas pour maximiser la fidélité
LLM_MAX_TOKENS = 8192
```

### Rotation multi-clés (`.env`)
```env
GEMINI_API_KEYS=AIzaSy...,AIzaSy...,AIzaSy...   # 5 clés séparées par virgules
GEMINI_API_KEY=AIzaSy...                          # Rétrocompatibilité clé unique
LLM_MODEL=gemini-2.5-flash
```

### Mécanique de rotation (`llm_gemini.py`)
- `failed_keys` (set) : indexes des clés ayant atteint leur quota
- Rotation déclenchée par : erreur 429, "RESOURCE_EXHAUSTED", "quota", "rate limit"
- Les erreurs non-quota (clé invalide, réseau) ne déclenchent PAS la rotation
- Endpoint `/api/llm-status` retourne l'état de chaque clé

### Hiérarchie LLM (pattern Factory)
```
LLMBase (abstraite)
└── GeminiLLM
        ↑
   LLMFactory.create() → lit config, instancie la bonne classe
```

---

## 🗃️ RAG (Retrieval-Augmented Generation)

**Source :** dépôt `SysML-v2-Release` (monté en read-only)
**Base vectorielle :** ChromaDB (persisté dans `backend_data:/app/data/chroma`)
**Modèle d'embeddings :** `all-MiniLM-L6-v2` (local, pas d'appel API)

**Statistiques :** ~197 fichiers indexés, ~337 chunks

**Paramètres RAG (`config.py`) :**
```python
RAG_CHUNK_SIZE = 1500
RAG_CHUNK_OVERLAP = 200
RAG_TOP_K = 8  # Nombre de chunks retournés par recherche
```

**Endpoints :**
- `GET /api/rag/stats` — Statistiques (nb chunks, fichiers)
- `GET /api/rag/search?q=...` — Recherche manuelle

---

## 📡 Tous les endpoints API

### Santé & Statut
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/health` | Statut global (backend, LLM, RAG) |
| GET | `/api/llm-status` | État des clés API (rotation) |
| GET | `/api/test-llm` | Test rapide du LLM |
| GET | `/api/rag/stats` | Statistiques ChromaDB |
| GET | `/api/rag/search` | Recherche dans la base RAG |

### Pipeline v1 (linéaire — NL → JSON → SysML)
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/generate` | Génère un nouveau système complet |
| POST | `/api/patch` | Modifie un système existant |
| GET | `/api/session/{id}` | Récupère une session |
| GET | `/api/sessions` | Liste toutes les sessions |
| POST | `/api/diagrams` | Génère tous les diagrammes |
| POST | `/api/diagrams/{type}` | Génère un diagramme spécifique |

### Pipeline v2 (MBSE multi-niveaux — ✅ Actif)
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/v2/generate` | Génère un niveau MBSE |
| POST | `/api/v2/patch` | Modifie un niveau existant |
| POST | `/api/v2/validate` | Valide un niveau (passage au suivant) |
| PUT | `/api/v2/session/{id}/name` | Renomme une session |
| GET | `/api/v2/coherence/{session_id}/{level}` | Vérifie cohérence inter-niveaux |
| GET | `/api/v2/status/{session_id}` | Statut de tous les niveaux |
| GET | `/api/v2/level/{session_id}/{level}` | Données d'un niveau |
| GET | `/api/v2/full-sysml/{session_id}` | SysML v2 complet (tous niveaux) |
| POST | `/api/v2/diagrams` | Génère diagrammes d'un niveau |
| GET | `/api/v2/diagrams/{session_id}/{level}` | Diagrammes sauvegardés |

### Validation SysML v2
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/validate-sysml` | Valide du code SysML v2 |
| GET | `/api/validate-sysml/{session_id}` | Valide le code SysML d'une session |

---

## 🔄 Workflow MBSE multi-niveaux

### Les 4 niveaux (ordre fixe, progression obligatoire)

```
1. OPERATIONAL  → QUI utilise le système et POURQUOI ?
                   Stakeholders, cas d'utilisation, scénarios, besoins
                   
2. FUNCTIONAL   → QUE FAIT le système ?
                   Fonctions, flux fonctionnels, modes de fonctionnement
                   
3. LOGICAL      → COMMENT est-il structuré ? (indépendant de la techno)
                   Parts, connexions, interfaces, exigences allouées
                   
4. TECHNICAL    → AVEC QUOI est-il construit ?
                   Composants physiques, technologies, choix d'implémentation
```

### Schémas de données par niveau (`schemas.py`)

**OperationalModel :** `system_name`, `stakeholders`, `external_systems`, `system_boundaries`, `use_cases`, `operational_scenarios`, `requirements`

**FunctionalModel :** `system_name`, `functions` (avec `sub_functions`, `inputs`, `outputs`), `functional_flows`, `modes`

**LogicalModel :** `system_name`, `parts` (avec `ports`, `children`), `connections`, `requirements`

**TechnicalModel :** `system_name`, `technical_parts`, `physical_connections`, `technology_choices`

### Session (`SessionData`)
```
SessionData:
  session_id: str (UUID)
  session_name: str
  current_level: ModelLevel
  levels: Dict[str, LevelData]
    → LevelData: {model, sysml_code, diagrams, validated, history}
```

Sessions persistées en JSON dans `backend_data:/app/data/state/`

---

## 📊 Diagrammes PlantUML

Le `DiagramService` génère du code PlantUML en **pur Python** (sans LLM) depuis les modèles JSON, puis envoie au serveur PlantUML pour obtenir le SVG.

### Diagrammes disponibles par niveau

| Niveau | Diagrammes |
|--------|-----------|
| Opérationnel | Contexte, Cas d'Utilisation |
| Fonctionnel | Arborescence Fonctionnelle (FBS), Comportement Fonctionnel |
| Logique | BDD (Block Definition Diagram), IBD (Internal Block Diagram) |
| Technique | Architecture Technique |

### Rendu SVG
- `diagram_service._render_svg()` fait un POST HTTP vers `http://plantuml:8080`
- Retourne une chaîne SVG inline (affichée dans Streamlit avec `st.components.v1.html`)

---

## ✅ Fidelity Checker

**Problème résolu :** Le LLM "oublie" parfois des composants mentionnés dans la description.

**Fonctionnement :**
1. Extraction des composants depuis la description (regex + filtrage)
2. Extraction des composants depuis le modèle JSON généré
3. Fuzzy matching (distance de Levenshtein ≤ 2)
4. Si composants manquants → retry automatique avec feedback (`correction_feedback`)

**Niveaux où il est actif :** `logical` et `technical` uniquement
(Les niveaux `operational` et `functional` n'ont pas de "parts" mais des stakeholders/fonctions)

**Filtrages anti-faux-positifs :**
- `EXCLUDED_PATTERNS` : 7 regex pour supprimer phrases du type "les parties prenantes sont..."
- `EXCLUDED_WORDS` : 27 mots (stakeholder, acteur, système, verbes, unités de temps...)
- `_contains_conjugated_verb()` : filtre les expressions verbales conjuguées

---

## ✅ Validateur SysML v2

**Fichier :** `backend/services/sysml_validator.py` (626 lignes)

5 niveaux de validation :
1. **Structure** : accolades équilibrées, points-virgules, mots-clés SysML
2. **Déclarations** : types définis vs référencés, détection de doublons
3. **Références** : flux, connexions, `satisfy`/`verify`
4. **Naming** : conventions PascalCase (types), camelCase (instances)
5. **Complétude** : packages vides, définitions inutilisées

Retourne : `{score: 0-100, errors: [], warnings: [], info: [], valid: bool}`

> ⚠️ **ANTLR4 — Décision reportée :** L'intégration de la grammaire officielle ANTLR4 (`SysMLv2Lexer.g4`, `SysMLv2Parser.g4`) a été évaluée mais reportée. La dépendance `antlr4-python3-runtime==4.13.2` est commentée dans `requirements.txt`.

---

## 🖥️ Frontend Streamlit

**URL :** `http://localhost:8501`

### Sidebar (panneau gauche)
- Statut backend (ping `/api/health`)
- Stats RAG (nb chunks/fichiers)
- 5 dernières sessions (cliquables)
- **Progression MBSE** : boutons par niveau (icône + statut : ✅ validé, 🔄 généré, ⬜ vide)

### Zone principale

**Si pas de session active :**
- Header "Nouveau projet MBSE"
- Champ description + options (modèle, RAG on/off)
- Bouton "Générer le niveau Opérationnel"

**Si session active** — 4 onglets :
| Onglet | Contenu |
|--------|---------|
| 📝 Modèle | Résumé JSON du modèle + boutons Modifier/Valider + cohérence inter-niveaux |
| 💻 Code SysML v2 | Code généré + bouton de validation syntaxique |
| 📊 Diagrammes | Diagrammes du niveau actuel + diagrammes des niveaux précédents |
| 📖 Historique | Historique des modifications de la session |

---

## 🧪 Tests

**Exécution :**
```bash
docker compose exec backend pytest tests/ -v
docker compose exec backend pytest tests/test_fidelity_checker.py -v  # un seul fichier
```

**État actuel : 151/151 tests passent ✅**

| Fichier | Nb tests | Ce qu'il teste |
|---------|----------|----------------|
| `test_api_health.py` | ~3 | Endpoints santé |
| `test_config.py` | ~5 | Configuration settings |
| `test_schemas.py` | ~8 | Validation schémas Pydantic |
| `test_prompts.py` | ~6 | Construction des prompts |
| `test_state_service.py` | ~10 | CRUD sessions JSON |
| `test_fidelity_checker.py` | 16 | Extraction composants + filtrage faux positifs |
| `test_diagram_service.py` | ~17 | Génération PlantUML (BDD, IBD, context, UC, requirements) |
| `test_diagram_levels.py` | ~12 | Diagrammes par niveau MBSE |
| `test_level_service.py` | ~25 | Pipeline MBSE complet (génération, patch, validate, cohérence) |
| `test_llm_factory.py` | ~10 | Factory + multi-clés |
| `test_llm_rotation.py` | 10 | Rotation automatique des clés API |
| `test_sysml_validator.py` | 23 | Validation syntaxique SysML v2 |

---

## ✅ Ce qui est IMPLÉMENTÉ et FONCTIONNEL

- [x] Pipeline v1 : NL → JSON → SysML v2 (pipeline linéaire)
- [x] Pipeline v2 : MBSE 4 niveaux (Opérationnel → Fonctionnel → Logique → Technique)
- [x] RAG avec ChromaDB (197 fichiers SysML v2 indexés)
- [x] Fidelity Checker avec retry automatique
- [x] 5 types de diagrammes PlantUML générés sans LLM
- [x] Validateur SysML v2 syntaxique (regex, 5 niveaux)
- [x] Rotation automatique de 5 clés API Gemini
- [x] Sessions persistées (JSON sur volume Docker)
- [x] Cohérence inter-niveaux (vérification sémantique)
- [x] Frontend Streamlit avec workflow MBSE complet
- [x] Navigation entre niveaux dans la sidebar
- [x] Renommage de session
- [x] Historique des modifications par session
- [x] Validation syntaxique depuis l'UI (onglet Code)
- [x] Diagrammes des niveaux précédents affichés en expanders

---

## 🔴 Ce qui reste à FAIRE (Corrections 2-10)

La session s'est arrêtée pendant les **10 corrections MBSE**. Correction 1 terminée, Corrections 2-10 à faire :

| # | Priorité | Description | Fichier(s) concerné(s) |
|---|----------|-------------|------------------------|
| 2 | 🔴 CRITIQUE | **Navigation entre niveaux** — boutons cliquables dans sidebar pour naviguer vers un niveau déjà généré (en cours au moment de l'arrêt) | `frontend/app.py` lignes 162-200 |
| 3 | 🟡 IMPORTANT | **Nommage de session** — permettre à l'utilisateur de donner un nom personnalisé à sa session dès la création | `frontend/app.py` |
| 4 | 🟡 IMPORTANT | **JSON dans expander** — afficher le modèle JSON dans un `st.expander` fermé par défaut (moins de bruit visuel) | `frontend/app.py` onglet Modèle |
| 5 | 🟡 IMPORTANT | **Warnings dans expander** — idem pour les warnings/alertes | `frontend/app.py` |
| 6 | 🟠 UX | **Diagrammes interactifs** — zoom, bouton plein écran, meilleure visualisation SVG | `frontend/app.py` onglet Diagrammes |
| 7 | 🟠 UX | **Conserver tous les diagrammes** — afficher les diagrammes de TOUS les niveaux précédents (pas seulement le niveau actuel) | `frontend/app.py` + `diagram_service.py` |
| 8 | 🟠 UX | **Lisibilité IBD** — améliorer le rendu des IBD (skinparam, layout, labels tronqués) | `backend/services/diagram_service.py` |
| 9 | 🟢 QUALITÉ | **Cohérence sémantique inter-niveaux** — matching sémantique avec 30% de recouvrement de mots | `backend/services/level_service.py` |
| 10 | 🟢 QUALITÉ | **Éliminer les warnings dupliqués** — filtrer les warnings redondants entre niveaux | `backend/services/level_service.py` ou `frontend/app.py` |

### Fonctionnalités futures plus larges
- [ ] **Support multi-LLM** : OpenAI GPT, Ollama (local) — architecture prête (`llm_base.py`), factory prête
- [ ] **Validation ANTLR4** : intégration de la grammaire officielle SysML v2 (`antlr4-python3-runtime` déjà en commentaire)
- [ ] **Export** : export des modèles en XMI, JSON, PDF
- [ ] **Collaboration** : sessions multi-utilisateurs
- [ ] **Versioning** : historique git-like des modèles

---

## ⚙️ Variables d'environnement (`.env`)

```env
# Clés API Gemini (rotation automatique)
GEMINI_API_KEYS=AIzaSy...,AIzaSy...,AIzaSy...,AIzaSy...,AIzaSy...
GEMINI_API_KEY=AIzaSy...        # Rétrocompatibilité

# Modèle LLM
LLM_MODEL=gemini-2.5-flash
GEMINI_MODEL=gemini-2.0-flash   # Rétrocompatibilité

# Chemins (injectés par docker-compose, pas besoin de changer)
# SYSML_REPO_PATH=/app/SysML-v2-Release
# PLANTUML_SERVER_URL=http://plantuml:8080
```

---

## 🔑 Points techniques importants à retenir

1. **Import Gemini** : utiliser `from google import genai` (PAS `import google.generativeai`) — cela causait un `ModuleNotFoundError`

2. **Rebuild obligatoire** : tout changement dans `backend/` nécessite `docker compose up --build` car le code est copié dans l'image, pas monté en volume

3. **Fidelity checker** : actif uniquement sur `logical` et `technical` (pas `operational`/`functional` car ces niveaux n'ont pas de "parts")

4. **Ordre des niveaux** : `operational → functional → logical → technical` — ordre fixe, chaque niveau doit être **validé** avant de passer au suivant

5. **Modèle LLM actif** : `gemini-2.5-flash` (dans `.env`) — modèle configuré pour très faible température (0.05) pour maximiser la fidélité structurelle

6. **Tests** : se lancent **dans** le conteneur Docker (`docker compose exec backend pytest tests/ -v`), pas en local

7. **Volume des données** : les sessions ChromaDB et les sessions JSON sont dans `backend_data` (volume Docker nommé) — persistent entre les rebuilds

8. **Sessions stockées** : `/app/data/state/{session_id}.json` — format `SessionData` Pydantic sérialisé en JSON

---

## 📁 Fichiers clés et leur rôle précis

| Fichier | Lignes | Rôle |
|---------|--------|------|
| `backend/main.py` | 870 | Tous les endpoints FastAPI, initialisation des services |
| `frontend/app.py` | 987 | Toute l'UI Streamlit |
| `backend/services/level_service.py` | 659 | Orchestration du pipeline MBSE (cœur du système v2) |
| `backend/services/diagram_service.py` | 746 | Génération PlantUML pour tous les types et niveaux |
| `backend/services/sysml_validator.py` | 626 | Validation syntaxique SysML v2 (5 niveaux) |
| `backend/models/schemas.py` | ~350 | Tous les schémas Pydantic |
| `backend/services/rag_service.py` | 257 | Indexation + recherche ChromaDB |
| `backend/services/state_service.py` | 371 | CRUD sessions JSON sur disque |
| `backend/services/fidelity_checker.py` | 349 | Anti-hallucination LLM |
| `backend/services/llm_gemini.py` | 150 | Client Gemini + rotation clés |
| `backend/config.py` | ~55 | Config centralisée via pydantic-settings |
