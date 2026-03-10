# Prerequis

Liste des prerequis pour installer et executer le SysML v2 Agent.

---

## Python 3.10+

Python 3.10 ou superieur est requis pour l'installation manuelle (sans Docker).

```bash
python3 --version
# Python 3.10.x ou superieur
```

Si Python n'est pas installe ou si la version est trop ancienne :

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install python3 python3-pip python3-venv

# macOS (via Homebrew)
brew install python@3.12
```

---

## Docker + Docker Compose

Docker est la methode d'installation recommandee. Il gere toutes les dependances automatiquement.

```bash
docker --version
# Docker version 24.x ou superieur

docker compose version
# Docker Compose version v2.x ou superieur
```

Si Docker n'est pas installe :

- **Linux** : https://docs.docker.com/engine/install/
- **macOS** : https://docs.docker.com/desktop/install/mac-install/
- **Windows** : https://docs.docker.com/desktop/install/windows-install/

> **Note :** Sur Linux, assurez-vous que votre utilisateur fait partie du groupe `docker` pour eviter d'utiliser `sudo` :
> ```bash
> sudo usermod -aG docker $USER
> ```
> Deconnectez-vous et reconnectez-vous pour que le changement prenne effet.

---

## Cle API (LLM)

Au moins une cle API est requise pour le modele de langage. Deux fournisseurs sont supportes :

### Option A : Google Gemini (par defaut)

1. Rendez-vous sur https://aistudio.google.com/app/apikey
2. Connectez-vous avec un compte Google
3. Creez une cle API
4. Copiez la cle (format : `AIzaSy...`)

> **Astuce :** Vous pouvez configurer plusieurs cles Gemini separees par des virgules dans `GEMINI_API_KEYS` pour repartir la charge et eviter les limites de debit.

### Option B : Anthropic Claude

1. Rendez-vous sur https://console.anthropic.com/
2. Creez un compte ou connectez-vous
3. Generez une cle API dans les parametres
4. Copiez la cle (format : `sk-ant-...`)

---

## Espace disque

| Composant | Taille approximative |
|-----------|---------------------|
| Images Docker (backend + frontend + SysON) | ~2 Go |
| Modele sentence-transformers (all-MiniLM-L6-v2) | ~500 Mo |
| Donnees ChromaDB (apres indexation) | ~100 Mo |
| **Total** | **~2.6 Go** |

Le modele d'embeddings est telecharge automatiquement au premier lancement.

---

## Git

Git est necessaire pour cloner le depot.

```bash
git --version
# git version 2.x ou superieur
```

Si Git n'est pas installe :

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install git

# macOS
xcode-select --install
```

---

## Resume

| Prerequis | Obligatoire | Verification |
|-----------|:-----------:|--------------|
| Python 3.10+ | Oui (sans Docker) | `python3 --version` |
| Docker + Compose | Oui (avec Docker) | `docker --version` |
| Cle API (Gemini ou Claude) | Oui | Obtenue en ligne |
| ~2.6 Go d'espace disque | Oui | `df -h` |
| Git | Oui | `git --version` |
