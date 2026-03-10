# SysAgent — Documentation

Generateur automatique de modeles SysML v2 a partir de descriptions en langage naturel, suivant une approche MBSE (Model-Based Systems Engineering) en 4 niveaux.

L'outil transforme des descriptions textuelles structurees en code SysML v2 syntaxiquement correct et compatible SysON, via un pipeline LLM en 2 etapes (NL → JSON → SysML v2) enrichi par RAG.

**Statistiques du projet :** 9 140 lignes Python | 15 prompts SysML specialises | 4 niveaux MBSE | 33 fichiers spec OMG analyses

## Documentation

| Dossier | Contenu |
|---------|---------|
| [01-guide-installation](./01-guide-installation/) | Installation, prerequis, configuration |
| [02-architecture](./02-architecture/) | Architecture technique, services, pipeline |
| [03-strategie-prompts](./03-strategie-prompts/) | Strategie de prompts, regles SysON, fidelite |
| [04-resultats-test-bas](./04-resultats-test-bas/) | Resultats du test BAS Silvercrest (4 niveaux) |

## Demarrage rapide

1. Cloner le projet
2. Configurer `.env` avec une cle API (Anthropic ou Google)
3. `docker compose up --build`
4. Ouvrir http://localhost:8501

Details : [Guide d'installation](./01-guide-installation/)
