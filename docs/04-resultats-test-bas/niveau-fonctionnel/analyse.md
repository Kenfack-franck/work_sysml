# Analyse de conformite -- Niveau Fonctionnel

## Packages generes

3 packages generes :

1. **Functional Breakdown** -- decomposition fonctionnelle et flux
2. **Functional Behaviour** -- comportement et sequences d'execution
3. **Functional Modes** -- activation des fonctions par mode

## Metriques

- **Code SysML v2 :** 11 965 caracteres
- **Syntaxe valide :** oui
- **Nombre de warnings :** 7
- **Tentatives de generation :** 7 (history_count=7), montrant un raffinement iteratif

## Constructs SysML v2 utilises

- `action def` / `action` pour les fonctions et sous-fonctions
- `first` / `then` / `succession` pour les sequences d'execution
- `state def` / `state` pour les modes fonctionnels
- `perform action` pour l'activation des fonctions dans les etats

## Warnings

7 warnings generes, tous legitimes :

| # | Type | Section | Message |
|---|------|---------|---------|
| 1 | missing_info | functions | "Determiner l'etat du systeme" n'a pas d'entrees ni de sorties explicitement definies |
| 2 | missing_info | functions | "Communiquer" n'a pas d'entrees explicitement definies |
| 3 | missing_info | functions | Decomposition interne de "Envoyer de l'air regule en (P,T) a l'avion" non detaillee |
| 4 | missing_info | functions | Decomposition interne de "Determiner l'etat du systeme" non detaillee |
| 5 | missing_info | functions | Decomposition interne de "Communiquer" non detaillee |
| 6 | inconsistency | modes | "Determiner l'etat du systeme" est active dans Stand by et En fonctionnement mais n'a pas d'entrees/sorties definies |
| 7 | ambiguity | modes | Les modes sont decrits avec une hierarchie mais representes en liste plate avec notation ">" |

## Observations

- Le raffinement iteratif (7 tentatives) montre que le LLM a du corriger des erreurs de syntaxe ou de conformite au fil des generations
- Les 5 warnings de type missing_info concernent tous des decompositions absentes du document source -- le LLM ne les a pas inventees
- La fidelite aux entrees utilisateur est respectee : seules les fonctions documentees sont modelisees
