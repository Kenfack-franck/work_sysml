# Backend (FastAPI)

Le backend est le coeur du SysML v2 Agent. Il est construit avec FastAPI et expose une API REST consommee par le frontend Streamlit.

## Endpoints API

Les endpoints sont organises en 8 groupes fonctionnels :

### 1. Health

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/health` | Verification de sante du backend |
| GET | `/api/llm-status` | Statut de la connexion LLM (provider, modele, cles disponibles) |
| GET | `/api/test-llm` | Test de generation LLM avec un prompt simple |

### 2. Sections

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/sections` | Liste de toutes les sections pour tous les niveaux |
| GET | `/api/sections/{level}` | Sections pour un niveau specifique (operational, functional, logical, technical) |

### 3. Pipeline V2

| Methode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/v2/generate` | Lancer la generation SysML v2 pour un niveau |
| POST | `/api/v2/patch` | Appliquer un patch sur le code genere |
| POST | `/api/v2/validate` | Valider le code SysML v2 d'un niveau |
| GET | `/api/v2/status/{session_id}` | Statut global d'une session (niveaux completes, scores) |
| GET | `/api/v2/level/{session_id}/{level}` | Resultat complet d'un niveau (JSON, SysML, warnings, score) |
| GET | `/api/v2/full-sysml/{session_id}` | Code SysML v2 concatene de tous les niveaux |
| GET | `/api/v2/coherence/{session_id}/{level}` | Verification de coherence inter-niveaux |

### 4. Sessions

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/sessions` | Liste de toutes les sessions |
| GET | `/api/session/{session_id}` | Detail d'une session |
| DELETE | `/api/session/{session_id}` | Supprimer une session |
| PUT | `/api/v2/session/{session_id}/name` | Renommer une session |

### 5. Exchanges

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v2/exchanges/{session_id}` | Historique des echanges LLM (prompts et reponses) |
| GET | `/api/v2/export/{session_id}` | Export complet d'une session (JSON) |

### 6. RAG

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/rag/stats` | Statistiques de la base RAG (nombre de documents, taille) |
| GET | `/api/rag/search` | Recherche semantique dans les exemples SysML v2 |

### 7. Validation

| Methode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/validate-sysml` | Valider un bloc de code SysML v2 |
| GET | `/api/validate-sysml/{session_id}` | Valider le code SysML v2 d'une session existante |

### 8. SysON

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/syson/status` | Statut de connexion a Eclipse SysON |
| POST | `/api/syson/push` | Pousser le code SysML v2 vers un projet SysON |
| GET | `/api/syson/project-url/{project_id}` | URL de l'editeur SysON pour un projet |
| GET | `/api/syson/projects` | Liste des projets SysON |
| POST | `/api/syson/pull` | Recuperer le code SysML v2 depuis SysON |

## Services

| Service | Fichier | Lignes | Role |
|---------|---------|--------|------|
| LevelService | `level_service.py` | 845 | Orchestrateur MBSE 4 niveaux. Gere le pipeline complet de generation : construction des prompts, appels LLM, extraction des identifiants, concatenation des packages. |
| StateService | `state_service.py` | 366 | Persistence des sessions en fichiers JSON sur disque. Gestion CRUD des sessions, niveaux et echanges LLM. |
| RAGService | `rag_service.py` | 257 | Retrieval-Augmented Generation avec ChromaDB et sentence-transformers. Indexe 33 fichiers .sysml OMG et retourne les exemples les plus pertinents. |
| SysMLv2Validator | `sysml_validator.py` | 626 | Validation syntaxique du code SysML v2. Verifie la structure des packages, les mots-cles, les blocs imbrique et les regles de nommage. |
| SysONService | `syson_service.py` | 511 | Integration avec Eclipse SysON via son API REST. Gestion des projets, push/pull du code SysML v2, recuperation des URLs editeur. |
| LLMBase | `llm_base.py` | 35 | Interface abstraite pour les providers LLM. Definit le contrat `generate(prompt) -> str`. |
| GeminiLLM | `llm_gemini.py` | 151 | Driver pour Google Gemini 2.5 Flash. Supporte la rotation de cles API pour gerer les quotas. |
| ClaudeLLM | `llm_claude.py` | 89 | Driver pour Anthropic Claude Haiku. Supporte le streaming des reponses. |
| FileLogger | `file_logger.py` | 160 | Sauvegarde des fichiers generes sur disque (prompts, reponses, code SysML). Organise par session et niveau. |
