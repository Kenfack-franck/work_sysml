# Resultats du test BAS (Bleed Air System) Silvercrest

| Parametre | Valeur |
|-----------|--------|
| Session | `0699efd3-67db-4d4b-afa0-3263be3d3366` (bas_ameliorer) |
| Date | 10 mars 2026 |
| LLM | Claude Haiku (`claude-haiku-4-5-20251001`) |
| Systeme | BAS (Bleed Air System) du moteur Silvercrest |

## Synthese des resultats

| Niveau | Packages | Code SysML | Warnings | Valide |
|--------|----------|------------|----------|--------|
| Operationnel | 5 | 10 696 chars | 4 | oui |
| Fonctionnel | 3 | 11 965 chars | 7 | oui |
| Logique | 4 | 13 292 chars | 6 | oui |
| Technique | 3 | 15 307 chars | 6 | non |
| **Total** | **15** | **51 260 chars** | **23** | |

## Structure des resultats

Chaque niveau contient les fichiers suivants :

| Fichier | Description |
|---------|-------------|
| `entrees.md` | Entrees utilisateur formatees |
| `analyse.md` | Analyse de conformite |
| `code-sysml.sysml` | Code SysML v2 genere |
| `modele-json.json` | Modele JSON structure |
| `warnings.json` | Warnings generes par le LLM |
| `user-inputs.json` | Entrees utilisateur brutes |

## Niveaux d'architecture

- [Niveau Operationnel](niveau-operationnel/) -- contexte, cycle de vie, cas d'utilisation, scenarios, modes
- [Niveau Fonctionnel](niveau-fonctionnel/) -- decomposition fonctionnelle, flux, comportement, chaines, modes
- [Niveau Logique](niveau-logique/) -- constituants logiques, allocation, connexions, regroupement
- [Niveau Technique](niveau-technique/) -- composants techniques, connexions physiques, choix technologiques
