# Configuration

Toutes les variables d'environnement du projet sont definies dans le fichier `.env` a la racine du projet. Copiez `.env.example` comme point de depart :

```bash
cp .env.example .env
```

---

## Variables d'environnement

### Fournisseur LLM

| Variable | Description | Valeurs | Defaut |
|----------|-------------|---------|--------|
| `LLM_PROVIDER` | Fournisseur du modele de langage | `gemini`, `claude` | `gemini` |

---

### Configuration Gemini (Google)

| Variable | Description | Exemple | Defaut |
|----------|-------------|---------|--------|
| `GEMINI_API_KEYS` | Liste de cles API Gemini separees par des virgules. Permet la rotation automatique entre plusieurs cles pour eviter les limites de debit. | `AIzaSy_CLE1,AIzaSy_CLE2` | — |
| `GEMINI_API_KEY` | Cle API Gemini unique (legacy). Utilisee si `GEMINI_API_KEYS` n'est pas definie. | `AIzaSy_VOTRE_CLE` | — |
| `GEMINI_MODEL` | Nom du modele Gemini a utiliser | `gemini-2.0-flash` | `gemini-2.0-flash` |
| `LLM_MODEL` | Alias pour le modele LLM. Surcharge `GEMINI_MODEL` si les deux sont definis. | `gemini-2.5-flash` | `gemini-2.5-flash` |

> **Note :** Si `GEMINI_API_KEYS` et `GEMINI_API_KEY` sont toutes deux definies, `GEMINI_API_KEYS` est prioritaire. `GEMINI_API_KEY` existe pour la retro-compatibilite.

---

### Configuration Claude (Anthropic)

| Variable | Description | Exemple | Defaut |
|----------|-------------|---------|--------|
| `ANTHROPIC_API_KEY` | Cle API Anthropic | `sk-ant-VOTRE_CLE` | — |
| `ANTHROPIC_MODEL` | Nom du modele Anthropic a utiliser | `claude-haiku-4-5-20251001` | `claude-haiku-4-5-20251001` |

---

### Configuration des embeddings

| Variable | Description | Valeurs | Defaut |
|----------|-------------|---------|--------|
| `EMBEDDING_PROVIDER` | Fournisseur du modele d'embeddings pour le RAG | `sentence-transformers` | `sentence-transformers` |
| `EMBEDDING_MODEL` | Nom du modele d'embeddings | `all-MiniLM-L6-v2` | `all-MiniLM-L6-v2` |

Le modele d'embeddings est telecharge automatiquement au premier lancement (~500 Mo). Il est utilise pour indexer la specification OMG SysML v2 dans ChromaDB et retrouver les passages pertinents lors de la generation (RAG).

---

### Autres

| Variable | Description | Valeurs | Defaut |
|----------|-------------|---------|--------|
| `DEBUG` | Active le mode debug (logs detailles) | `true`, `false` | `false` |

---

## Fichier .env.example

Voici le contenu du fichier `.env.example` fourni avec le projet :

```dotenv
# === LLM Configuration ===
# Provider: "gemini" ou "claude"
LLM_PROVIDER=gemini

# --- Gemini ---
# Cles API Gemini (une ou plusieurs, separees par des virgules)
# Obtenez vos cles sur https://aistudio.google.com/app/apikey
GEMINI_API_KEYS=AIzaSy_VOTRE_CLE_1,AIzaSy_VOTRE_CLE_2
GEMINI_API_KEY=AIzaSy_VOTRE_CLE_1
LLM_MODEL=gemini-2.5-flash
GEMINI_MODEL=gemini-2.0-flash

# --- Claude (Anthropic) ---
# Obtenez votre cle sur https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-VOTRE_CLE
ANTHROPIC_MODEL=claude-haiku-4-5-20251001
```

---

## Exemples de configuration

### Configuration minimale avec Gemini

```dotenv
LLM_PROVIDER=gemini
GEMINI_API_KEYS=AIzaSy_VOTRE_CLE
```

### Configuration minimale avec Claude

```dotenv
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-VOTRE_CLE
```

### Configuration avec plusieurs cles Gemini (rotation)

```dotenv
LLM_PROVIDER=gemini
GEMINI_API_KEYS=AIzaSy_CLE_1,AIzaSy_CLE_2,AIzaSy_CLE_3
LLM_MODEL=gemini-2.5-flash
```

### Configuration debug

```dotenv
LLM_PROVIDER=gemini
GEMINI_API_KEYS=AIzaSy_VOTRE_CLE
DEBUG=true
```
