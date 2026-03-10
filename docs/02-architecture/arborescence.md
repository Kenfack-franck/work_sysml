# Arborescence du projet

```
sysml-agent/
├── .env / .env.example
├── docker-compose.yml
├── backend/
│   ├── main.py (628 lines)
│   ├── config.py (58)
│   ├── models/schemas.py (731)
│   ├── prompts/
│   │   ├── _shared.py (238)
│   │   ├── operational_prompt.py (736)
│   │   ├── functional_prompt.py (505)
│   │   ├── logical_prompt.py (502)
│   │   └── technical_prompt.py (428)
│   ├── services/
│   │   ├── level_service.py (845)
│   │   ├── state_service.py (366)
│   │   ├── rag_service.py (257)
│   │   ├── sysml_validator.py (626)
│   │   ├── syson_service.py (511)
│   │   ├── llm_base.py (35)
│   │   ├── llm_gemini.py (151)
│   │   ├── llm_claude.py (89)
│   │   ├── llm_factory.py (77)
│   │   └── file_logger.py (160)
│   ├── scripts/index_sysml.py (62)
│   └── tests/ (7 fichiers, 1251 lines)
├── frontend/
│   ├── app.py (878)
│   └── Dockerfile
├── data/
│   ├── sysml-training/ (25 fichiers .sysml)
│   ├── sysml-validation/ (8 fichiers .sysml)
│   └── sysml-syntax-report.md
└── docs/
```

**Total : 9140 lignes Python**

## Description des repertoires

### `backend/`

Le coeur applicatif. Contient l'API FastAPI, les services metier, les prompts LLM et les schemas de donnees.

- **`main.py`** : Point d'entree FastAPI, definition de tous les endpoints API
- **`config.py`** : Configuration (variables d'environnement, chemins, constantes)
- **`models/schemas.py`** : Schemas Pydantic pour les requetes, reponses et modeles JSON intermediaires

### `backend/prompts/`

Prompts LLM organises par niveau MBSE. Chaque fichier contient les templates, regles et schemas pour un niveau.

- **`_shared.py`** : Elements partages entre niveaux (regles SysON, fonctions utilitaires de construction de prompts)
- **`operational_prompt.py`** : Prompts pour le niveau operationnel (5 packages)
- **`functional_prompt.py`** : Prompts pour le niveau fonctionnel (3 packages)
- **`logical_prompt.py`** : Prompts pour le niveau logique (4 packages)
- **`technical_prompt.py`** : Prompts pour le niveau technique (3 packages)

### `backend/services/`

Services metier decouplant la logique applicative des endpoints API. Voir [backend.md](backend.md) pour le detail de chaque service.

### `backend/tests/`

7 fichiers de tests couvrant les services principaux (1251 lignes).

### `frontend/`

Application Streamlit mono-fichier. Voir [frontend.md](frontend.md) pour le detail.

### `data/`

Donnees d'entrainement et de validation pour le RAG :
- **`sysml-training/`** : 25 fichiers `.sysml` issus des exemples OMG, indexes dans ChromaDB
- **`sysml-validation/`** : 8 fichiers `.sysml` utilises pour la validation et les tests
- **`sysml-syntax-report.md`** : Rapport de syntaxe SysML v2 de reference
