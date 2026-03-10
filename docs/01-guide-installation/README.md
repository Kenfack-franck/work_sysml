# Guide d'installation

Ce guide couvre l'installation et le lancement du SysML v2 Agent, aussi bien via Docker (recommande) qu'en mode manuel.

## Prerequis

- **Python 3.10+** — verifie avec `python3 --version`
- **Docker + Docker Compose** — verifie avec `docker --version` et `docker compose version`
- **Cle API** — au moins une cle parmi :
  - Anthropic (Claude) : https://console.anthropic.com/
  - Google (Gemini) : https://aistudio.google.com/app/apikey
- **Espace disque** : ~2 Go pour les images Docker, ~500 Mo pour le modele d'embeddings sentence-transformers

Details complets : [prerequis.md](./prerequis.md)

---

## Installation avec Docker (recommande)

C'est la methode la plus simple. Docker gere toutes les dependances automatiquement.

### 1. Cloner le projet

```bash
git clone <url-du-depot> sysml-agent
cd sysml-agent
```

### 2. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Editez `.env` et renseignez au minimum une cle API :

```dotenv
# Pour Gemini (par defaut)
LLM_PROVIDER=gemini
GEMINI_API_KEYS=AIzaSy_VOTRE_CLE

# OU pour Claude
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-VOTRE_CLE
```

Voir [configuration.md](./configuration.md) pour la liste complete des variables.

### 3. Lancer les services

```bash
docker compose up --build
```

### 4. Acceder a l'application

Ouvrez http://localhost:8501 dans votre navigateur.

- **Frontend (Streamlit)** : http://localhost:8501
- **Backend (API)** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

---

## Installation sans Docker (manuelle)

Si vous preferez une installation locale sans Docker.

### 1. Cloner le projet

```bash
git clone <url-du-depot> sysml-agent
cd sysml-agent
```

### 2. Creer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dependances

```bash
# Backend
pip install -r backend/requirements.txt

# Frontend
pip install -r frontend/requirements.txt
```

### 4. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Editez `.env` avec vos cles API. Voir [configuration.md](./configuration.md) pour les details.

### 5. Lancer le backend

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Le backend demarre sur http://localhost:8000.

### 6. Lancer le frontend

Dans un second terminal :

```bash
cd frontend
streamlit run app.py --server.port 8501
```

Le frontend demarre sur http://localhost:8501.

---

## Test rapide

Une fois l'application lancee, vous pouvez tester avec le cas d'usage BAS (Building Automation System) Silvercrest :

1. Ouvrez http://localhost:8501
2. Entrez une description en langage naturel d'un systeme (par exemple un systeme domotique)
3. Selectionnez le niveau MBSE souhaite (L0 a L3)
4. Lancez la generation

Des resultats de reference pour le test BAS sont disponibles dans [docs/04-resultats-test-bas/](../04-resultats-test-bas/).

---

## Liens utiles

- [Prerequis detailles](./prerequis.md)
- [Configuration des variables d'environnement](./configuration.md)
- [Architecture technique](../02-architecture/)
