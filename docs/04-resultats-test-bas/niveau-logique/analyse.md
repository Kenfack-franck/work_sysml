# Analyse de conformite -- Niveau Logique

## Packages generes

4 packages generes :

1. **Logical Breakdown** -- decomposition en constituants logiques avec ports
2. **Logical Architecture** -- connexions entre constituants
3. **Logical Sequences** -- sequences d'execution logiques
4. **Logical Modes** -- modes de fonctionnement des constituants

## Metriques

- **Code SysML v2 :** 13 292 caracteres
- **Syntaxe valide :** oui
- **Nombre de warnings :** 6
- **Constituants modelises :** 11
- **Connexions representees :** 25

## Warnings

6 warnings generes, tous legitimes :

| # | Type | Section | Message |
|---|------|---------|---------|
| 1 | missing_info | requirements | Aucune exigence logique explicite fournie (REQ-LOG-XXX) |
| 2 | missing_info | logical_grouping | Le regroupement en sous-systemes n'est pas explicitement defini dans le document |
| 3 | ambiguity | connections | Deux capteurs de temperature distincts produisent un flux "mesure temperature air" vers le Calculateur. La distinction n'est pas clarifiee dans les ports du Calculateur |
| 4 | inconsistency | function_allocation | "Provide Feedback" est alloue au Calculateur mais n'existe pas dans le modele fonctionnel valide. Semble etre une variante de "Communiquer" |
| 5 | inconsistency | function_allocation | "Reguler la PRV" est alloue au Calculateur mais n'existe pas dans le modele fonctionnel valide. Aucune vanne PRV n'est mentionnee dans les constituants |
| 6 | missing_info | connections | Les ports "air regule T" (PCE) et "air regule (P,T)" (Filter) utilisent des noms differents pour le meme flux |

## Observations

- L'architecture logique detaille la chaine "Envoyer de l'air regule a l'avion" qui n'etait pas decomposee au niveau fonctionnel, ce qui fait apparaitre de nouveaux composants et fonctions
- Les warnings d'inconsistency (#4, #5) identifient des ecarts de nomenclature entre les niveaux fonctionnel et logique -- ces ecarts proviennent des entrees utilisateur, pas d'inventions du LLM
- Le warning d'ambiguite (#3) sur les capteurs de temperature est pertinent : le modele devrait distinguer les deux sources de mesure dans les ports du Calculateur
