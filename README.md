# 🧪 SysML v2 Agent

Outil de génération de modèles SysML v2 à partir de descriptions en langage naturel. Utilise un pipeline LLM en 2 étapes (Description → JSON → SysML v2) avec RAG basé sur le dépôt officiel SysML-v2-Release.

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE DE GÉNÉRATION                        │
└─────────────────────────────────────────────────────────────────┘

Description NL
      ↓
┌──────────┐    ┌─────────────────┐
│   RAG    │ →  │   Exemples      │
│ Search   │    │   SysML v2      │
└──────────┘    └─────────────────┘
      ↓                ↓
┌──────────────────────────────────┐
│   LLM Étape 1 : NL → JSON        │
│   (Prompt avec exemples RAG)      │
└──────────────────────────────────┘
      ↓
   JSON Validé
      ↓
┌──────────────────────────────────┐
│   LLM Étape 2 : JSON → SysML v2  │
│   (Prompt avec règles syntaxe)    │
└──────────────────────────────────┘
      ↓
  Code SysML v2
```

### Stack technique

**Backend** (FastAPI)
- **LLM** : Gemini 2.5 Flash (configurable : OpenAI, Ollama)
- **RAG** : ChromaDB + sentence-transformers (all-MiniLM-L6-v2)
- **Validation** : Pydantic
- **Sessions** : JSON sur disque

**Frontend** (Streamlit)
- Interface en 3 onglets : Générer, Modifier, Historique
- Sidebar : Statut backend, Stats RAG, Sessions précédentes
- Communication : REST API

**Infrastructure**
- Docker Compose (backend + frontend)
- Volume persistant pour ChromaDB et sessions
- Mount read-only du dépôt SysML-v2-Release

## 🚀 Installation et Lancement

### Prérequis

- Docker et Docker Compose installés
- Clé(s) API Google Gemini (obtenir sur https://aistudio.google.com/app/apikey)
- Le dépôt officiel SysML-v2-Release cloné **à côté** de ce projet

### Étape 1 — Cloner les dépôts

```bash
# Cloner ce projet
git clone https://github.com/Kenfack-franck/work_sysml.git
cd work_sysml

# Cloner le dépôt SysML v2 officiel À CÔTÉ (pas dedans)
cd ..
git clone https://github.com/Systems-Modeling/SysML-v2-Release.git
cd work_sysml
```

La structure attendue sur votre machine :

```
votre-dossier/
├── work_sysml/           ← ce projet (sysml-agent)
└── SysML-v2-Release/     ← le dépôt officiel OMG (monté en volume Docker)
```

### Étape 2 — Configurer les variables d'environnement

```bash
cp .env.example .env
```

Éditez le fichier `.env` et remplacez les placeholders par vos vraies clés API Gemini :

```bash
nano .env
```

### Étape 3 — Lancer l'application

```bash
docker compose up --build -d
```

Le premier démarrage prend environ 2-3 minutes :

- Téléchargement du modèle d'embeddings (~80 Mo)
- Indexation RAG des fichiers SysML v2 (337 chunks)
- Démarrage du serveur PlantUML

### Étape 4 — Vérifier que tout fonctionne

```bash
# Vérifier que les 3 conteneurs sont en cours d'exécution
docker compose ps

# Vérifier la santé du backend
curl http://localhost:8000/api/health

# Lancer les tests (147 tests)
docker compose exec backend pytest tests/ -v --tb=short
```

### Accéder à l'application

| Service | URL | Description |
|---|---|---|
| Interface utilisateur | http://localhost:8501 | Application Streamlit |
| API Backend | http://localhost:8000 | API FastAPI |
| Documentation API | http://localhost:8000/docs | Swagger UI |
| Serveur PlantUML | http://localhost:8080 | Rendu des diagrammes |

## 🧪 Expérimentation

Le projet inclut un système d'expérimentation automatisé pour tester le pipeline avec différents styles de description.

### Lancer une expérience

```bash
# Voir ce qui serait fait sans appeler le LLM
python experiments/run_experiment.py --dry-run

# Lancer l'expérience réelle (environ 10 minutes, 32 appels LLM)
python experiments/run_experiment.py

# Avec un dossier de descriptions personnalisé
python experiments/run_experiment.py \
  --descriptions-dir experiments/descriptions/mon_systeme/ \
  --output-dir experiments/results/mon_systeme/
```

### Structure des expériences

```
experiments/
├── descriptions/              ← Fichiers .txt de description (1 par style)
│   └── controle_acces/
│       ├── style_formel.txt
│       ├── style_conversationnel.txt
│       ├── style_liste.txt
│       └── style_narratif.txt
├── results/                   ← Résultats générés (non versionné)
├── run_experiment.py          ← Script d'expérimentation automatisé
└── export_markdown.py         ← Export des échanges LLM en Markdown
```

### Résultats

Pour chaque style de description, le script génère :

- Les prompts envoyés au LLM à chaque niveau MBSE
- Les réponses brutes du LLM
- Le code SysML v2 généré
- Une analyse comparative entre les styles

## 🛠️ Commandes utiles

```bash
# Rebuild après modification du code
docker compose up --build -d

# Voir les logs en temps réel
docker compose logs backend -f

# Accéder au shell du conteneur backend
docker compose exec backend bash

# Arrêter l'application
docker compose down

# Arrêter et supprimer les données (sessions, RAG)
docker compose down -v
```

## ⚙️ Configuration

### Variables d'environnement (.env)

| Variable | Description | Défaut | Valeurs possibles |
|----------|-------------|--------|-------------------|
| `LLM_PROVIDER` | Fournisseur LLM | `gemini` | `gemini`, `openai`, `ollama` |
| `GEMINI_API_KEY` | Clé API Gemini | *(requis)* | Votre clé depuis AI Studio |
| `GEMINI_MODEL` | Modèle Gemini | `gemini-2.5-flash` | `gemini-2.5-flash`, `gemini-3-pro-preview` |
| `EMBEDDING_PROVIDER` | Fournisseur embeddings | `local` | `local`, `openai`, `gemini` |
| `EMBEDDING_MODEL` | Modèle d'embeddings | `all-MiniLM-L6-v2` | Modèles sentence-transformers |
| `RAG_CHUNK_SIZE` | Taille des chunks RAG | `1500` | Entier > 0 |
| `RAG_CHUNK_OVERLAP` | Chevauchement chunks | `200` | Entier ≥ 0 |
| `RAG_TOP_K` | Nombre de résultats RAG | `8` | Entier > 0 |
| `DEBUG` | Mode debug | `true` | `true`, `false` |

### Répertoire SysML-v2-Release

Le fichier `docker-compose.yml` monte le dépôt depuis :
```yaml
volumes:
  - ../SysML-v2-Release:/app/SysML-v2-Release:ro
```

Adaptez le chemin si nécessaire.

## 🔌 Endpoints API

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/health` | Vérification santé backend |
| `GET` | `/api/test-llm` | Test connexion LLM |
| `GET` | `/api/rag/stats` | Statistiques RAG (chunks, fichiers) |
| `GET` | `/api/rag/search?query=...` | Recherche sémantique dans la base RAG |
| `POST` | `/api/generate` | Génération d'un nouveau système |
| `POST` | `/api/patch` | Modification d'un système existant |
| `GET` | `/api/session/{id}` | Récupération d'une session |
| `GET` | `/api/sessions` | Liste de toutes les sessions |

### Exemple : Génération

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Un système de drone avec un GPS et un moteur. Le GPS envoie la position au contrôleur de vol qui commande le moteur.",
    "use_rag": true
  }'
```

### Exemple : Modification

```bash
curl -X POST http://localhost:8000/api/patch \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "9932a740-fc68-434b-b15f-6dac285a8559",
    "instruction": "Ajouter une batterie qui alimente le contrôleur et le moteur"
  }'
```

## 📁 Structure du projet

```
sysml-agent/
├── backend/
│   ├── main.py                    # API FastAPI — tous les endpoints
│   ├── config.py                  # Configuration centralisée
│   ├── Dockerfile
│   ├── models/
│   │   └── schemas.py             # Schémas Pydantic (API + modèles MBSE)
│   ├── services/
│   │   ├── llm_base.py            # Interface abstraite LLM
│   │   ├── llm_gemini.py          # Implémentation Gemini + rotation multi-clés
│   │   ├── llm_factory.py         # Factory pattern pour multi-LLM
│   │   ├── rag_service.py         # RAG ChromaDB + sentence-transformers
│   │   ├── state_service.py       # Gestion des sessions (JSON sur disque)
│   │   ├── sysml_service.py       # Pipeline v1 (génération linéaire)
│   │   ├── level_service.py       # Pipeline v2 (MBSE 4 niveaux)
│   │   ├── diagram_service.py     # Génération de 7 types de diagrammes PlantUML
│   │   ├── fidelity_checker.py    # Vérificateur anti-hallucination
│   │   └── sysml_validator.py     # Validateur syntaxique SysML v2 (5 niveaux)
│   ├── prompts/                   # Prompts LLM (1 fichier par niveau MBSE)
│   │   ├── operational_prompt.py
│   │   ├── functional_prompt.py
│   │   ├── logical_prompt.py
│   │   ├── technical_prompt.py
│   │   ├── json_prompt.py         # Pipeline v1
│   │   ├── sysml_prompt.py        # Pipeline v1
│   │   └── patch_prompt.py        # Modification incrémentale
│   └── tests/                     # 147 tests pytest
├── frontend/
│   ├── app.py                     # Interface Streamlit
│   └── Dockerfile
├── experiments/
│   ├── descriptions/              # Descriptions de systèmes test
│   ├── run_experiment.py          # Script d'expérimentation automatisé
│   └── export_markdown.py         # Export Markdown des échanges LLM
├── docker-compose.yml             # 3 services : backend, frontend, plantuml
├── .env.example                   # Template de configuration
├── .gitignore
└── README.md
```

## 🔧 Changer de LLM

L'architecture est extensible pour supporter d'autres LLM (OpenAI, Ollama, etc.).

### Étapes pour ajouter un nouveau fournisseur

#### 1. Créer l'implémentation

Créer `backend/services/llm_nouveau.py` :

```python
from services.llm_base import LLMBase

class NouveauLLM(LLMBase):
    def __init__(self, api_key: str, model: str = "model-name"):
        if not api_key:
            raise ValueError("Clé API manquante")
        self.api_key = api_key
        self.model = model
        # Initialiser le client...
    
    def generate(self, prompt: str, temperature: float = 0.05, max_tokens: int = 8192) -> str:
        # Appeler l'API...
        return response_text
    
    def get_model_name(self) -> str:
        return self.model
    
    def get_provider_name(self) -> str:
        return "nouveau"
```

#### 2. Ajouter dans la factory

Modifier `backend/services/llm_factory.py` :

```python
def create_llm(provider: str, **kwargs) -> LLMBase:
    if provider == "gemini":
        from services.llm_gemini import GeminiLLM
        return GeminiLLM(...)
    
    elif provider == "nouveau":
        from services.llm_nouveau import NouveauLLM
        return NouveauLLM(
            api_key=kwargs.get("api_key"),
            model=kwargs.get("model", "default-model")
        )
    
    else:
        supported = ["gemini", "nouveau"]
        raise ValueError(f"Fournisseur '{provider}' non supporté. Options : {supported}")
```

#### 3. Configurer dans .env

```env
LLM_PROVIDER=nouveau
NOUVEAU_API_KEY=...
NOUVEAU_MODEL=model-name
```

#### 4. Adapter la configuration

Modifier `backend/config.py` pour ajouter les variables.

## 🧪 Tests

### Lancer tous les tests

```bash
docker compose exec backend pytest tests/ -v
```

### Lancer un fichier de tests spécifique

```bash
docker compose exec backend pytest tests/test_config.py -v
```

### Coverage

```bash
docker compose exec backend pytest tests/ --cov=. --cov-report=html
```

### Tests disponibles

- **test_config.py** : Configuration et settings
- **test_llm_factory.py** : Création de LLM et validation
- **test_state_service.py** : Gestion des sessions
- **test_prompts.py** : Génération de prompts
- **test_schemas.py** : Validation Pydantic
- **test_api_health.py** : Endpoints API (intégration)

## 🛠️ Développement

### Rebuild après modifications

```bash
./rebuild.sh
# ou manuellement :
docker compose down
docker compose up --build -d
```

### Logs en temps réel

```bash
# Backend
docker compose logs backend -f

# Frontend
docker compose logs frontend -f

# Tous
docker compose logs -f
```

### Accès au shell du container

```bash
docker compose exec backend bash
docker compose exec frontend bash
```

### Ré-indexation manuelle du RAG

```bash
docker compose exec backend python -m backend.scripts.index_sysml
```

## 📈 Roadmap

### Version 1.0 (Actuelle)
- ✅ Pipeline de génération NL → JSON → SysML v2
- ✅ RAG avec 337 chunks indexés
- ✅ Modification incrémentale (patch)
- ✅ Gestion de sessions persistantes
- ✅ Interface Streamlit complète
- ✅ Tests automatisés

### Version 2.0 (Prochaine)
- ⏳ Validation syntaxique du code SysML v2 généré
- ⏳ Génération de diagrammes (structure, séquence)
- ⏳ Export au format JSON OMG standard
- ⏳ Support des métadonnées et stéréotypes

### Version 3.0 (Future)
- 🔮 Multi-LLM en parallèle (consensus)
- 🔮 Interface graphique drag-and-drop
- 🔮 Collaboration temps réel
- 🔮 Intégration IDE (VS Code extension)

## 🐛 Résolution de problèmes

### Backend ne démarre pas

```bash
docker compose logs backend
# Vérifier les erreurs de clé API ou de dépendances
```

### RAG ne trouve pas les fichiers

Vérifier que le chemin vers SysML-v2-Release est correct dans `docker-compose.yml`.

### Frontend ne se connecte pas au backend

Vérifier les variables d'environnement et la configuration réseau Docker.

### Espace disque saturé

Le modèle d'embeddings fait ~90 Mo + ChromaDB peut grossir.
```bash
docker system prune -a  # Nettoyer les images inutilisées
```

## 📄 Licence

MIT License - voir fichier LICENSE

## 👥 Contributeurs

- Développement initial : [Votre nom]
- Framework SysML v2 : OMG Systems Modeling Project

## 📚 Références

- [SysML v2 Specification](https://www.omgsysml.org/)
- [SysML-v2-Release Repository](https://github.com/Systems-Modeling/SysML-v2-Release)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Google Gemini API](https://ai.google.dev/)

---

**Note** : Ce projet est un outil d'assistance à la modélisation. Le code SysML v2 généré doit être vérifié par un ingénieur système avant utilisation en production.
