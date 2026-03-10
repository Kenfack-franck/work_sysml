# Analyse de conformite -- Niveau Technique

## Packages generes

3 packages generes :

1. **Technical Breakdown** -- decomposition en composants techniques avec ports
2. **Technical Architecture** -- connexions physiques entre composants
3. **Technical States** -- etats techniques des composants

## Metriques

- **Code SysML v2 :** 15 307 caracteres
- **Syntaxe valide :** oui (syntaxiquement)
- **Valide par l'utilisateur :** non (l'utilisateur n'a pas clique sur "valider" dans le frontend)
- **Nombre de warnings :** 6
- **Composants modelises :** 15
- **Connexions representees :** 17
- **Choix technologiques :** 4

## Warnings

6 warnings generes, tous legitimes :

| # | Type | Section | Message |
|---|------|---------|---------|
| 1 | missing_info | requirements | Aucune exigence technique explicite fournie |
| 2 | missing_info | technical_components | Fan bleed port, Nacelle exhaust port, SOV et Data exchange (I/O) n'implementent pas explicitement de constituants logiques du modele valide |
| 3 | missing_info | physical_connections | Types de cablage et bus de donnees non precises (ARINC 429, CAN, etc.) |
| 4 | missing_info | physical_connections | Materiaux des tuyauteries pneumatiques non precises |
| 5 | ambiguity | physical_connections | Deux capteurs de temperature distincts produisent un flux "mesure temperature air" vers l'EEC. La distinction n'est pas clarifiee dans les ports de l'EEC |
| 6 | missing_info | technical_components | References et part numbers des composants techniques non fournis |

## Observations

- Le niveau technique n'a pas ete valide par l'utilisateur dans le frontend. Le code SysML a ete genere mais le workflow s'est arrete avant la validation
- 4 composants techniques (Fan bleed port, Nacelle exhaust port, SOV, Data exchange I/O) apparaissent au niveau technique sans correspondance directe avec le modele logique valide. Ce sont des elements physiques qui emergent lors du passage a l'architecture technique
- Les warnings de type missing_info dominent (5 sur 6), refletant le caractere volontairement incomplet des entrees techniques (pas d'exigences, pas de specifications materiaux)
- Le warning d'ambiguite sur les capteurs de temperature est le meme qu'au niveau logique, confirmant que cette imprecision traverse les niveaux d'architecture
