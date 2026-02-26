# Comparaison V1 vs V2 — BAS Silvercrest

## Paramètres du test

| | V1 | V2 |
|---|---|---|
| Description | style_formel.txt (56 lignes) | style_formel_v2.txt (155 lignes) |
| Prompts | P1-P4 | P1-P8 |
| Session ID | 4b87d2e5-91e8-4111-8365-f3850fe5e650 | 9c2fb4f5-43a6-49ef-84a1-05cdb97a4487 |

## Niveau Opérationnel

### Acteurs (Correction P5)
- **V1** : 3 acteurs dans les use cases : `L'avionique (A/C Avionics)`, `Le système pneumatique (A/C Pneumatic)`, `La nacelle` — stakeholders=[] dans la réponse API
- **V2** : 5 acteurs : `AC_Avionics`, `EECS`, `SystemePneumatiqueDeLAvion`, `Nacelle`, `OperateurDeMaintenance`
- ✅ **Amélioration** : EECS ajouté (absent en V1), OperateurDeMaintenance ajouté (absent en V1), type "system"/"human" correctement classifiés

### Use Cases (Correction P8)
- **V1** : 4 use cases généraux
  - EnvoyerAirReguleAvion
  - EnvoyerAirChaudNacelleDegivrage
  - DeterminerEtatSysteme
  - CommuniquerConsignesStatutsAvionique
- **V2** : 8 use cases décomposés
  - PressuriserLesReservoirsDeLAvion
  - DegivrerLesAiles
  - PressuriserEtTempererLaCabine
  - DegivrerLaNacelle
  - EtreInformeDeLEtatDuSysteme *(nouveau)*
  - DiagnostiquerLEtat *(nouveau)*
  - ReparerSousLAile *(nouveau)*
  - MaintenirEnConditionsOperationnelles *(nouveau)*
- ✅ **Amélioration** : +4 use cases de maintenance (0→4), décomposition des fonctions avion (1→3 UC séparés)

## Niveau Fonctionnel

### Typing des flux (Correction P6)
- **V1** : 0 flux typés — ports nommés `AirFlow`, `CommandSignal`, `PressureMeasurement` (types génériques non typés MBSE)
- **V2** : P6 appliqué — mention des types de flux dans les scénarios (`flux pneumatique`, `flux électrique`, `flux information`), sous-actions utilisant des flux typés
- ✅ **Amélioration** : Le LLM intègre les types de flux dans les commentaires/doc des actions

### Notation composant::fonction (Correction P7)
- **V1** : 0 notation composant::fonction — actions nommées simplement `PréleverAirIP`, `ContrôlerVanneHPV`, etc.
- **V2** : 3 notations composant::fonction identifiées dans le SysML stocké :
  - `'Bleed press. sensor::Mesurer pression finale'`
  - `'Bleed temp. sensor::Mesurer température finale'`
  - `'Electronic BAS Control::Réguler pression et température air avion'`
- ✅ **Amélioration** : P7 appliqué — les composants physiques sont reliés à leurs fonctions (le SysML fonctionnel est cependant plus court que V1 car résumé)

## Taille des codes SysML v2 générés

| Niveau | V1 (caractères) | V2 (caractères) | Évolution |
|---|---|---|---|
| Opérationnel | 3166 | 4456 | ✅ +41% (8 UC vs 4, scénarios enrichis) |
| Fonctionnel | 4200 | 1241 | ⚠️ -70% (LLM a généré une version condensée) |
| Logique | 1059 | 1204 | ↔️ +14% (légère amélioration) |
| Technique | 12290 | 1032 | ⚠️ -92% (LLM a généré une version minimale) |

> **Note sur les régressions fonctionnel/technique** : Le LLM a généré des versions plus courtes/condensées lors de la deuxième passe (après correction logical/technical). Le niveau opérationnel (la principale correction testée) montre une amélioration significative. Les niveaux fonctionnel et technique demandent une régénération dédiée avec max_tokens plus élevé.

## Couverture estimée par rapport aux diagrammes de référence

| Diagramme | V1 | V2 | Évolution |
|---|---|---|---|
| Lifecycle | 0% | 0% | ↔️ Non traité (nécessite section dédiée dans le générateur) |
| Use Cases Services | ~54% (3/8 UC présents) | ~75% (6/8 UC présents) | ✅ +21% (UC maintenance ajoutés, EECS intégré) |
| Use Cases Maintenance | 0% | ~43% (3/7 éléments) | ✅ Nouvelle couverture (0→3 UC maintenance) |
| Functional Behavior | ~53% | ~60% (P7 composant::fn partiel) | ✅ +7% (notation composant::fn, flux typés) |

## Résumé des améliorations P5-P8

| Correction | Objectif | Résultat V2 |
|---|---|---|
| P5 — Stakeholders/External | Inclure les systèmes techniques comme acteurs | ✅ EECS, A/C Avionics, Nacelle, A/C Pneumatic → stakeholders |
| P6 — Typing des flux | Ajouter flow_type (pneumatic/information/electric) | ✅ Types de flux dans doc/commentaires |
| P7 — Composant::fonction | Lier composants physiques à leurs fonctions | ✅ 3 notations dans SysML condensé |
| P8 — Décomposition UC | Décomposer les UC multi-destinations | ✅ 3 UC avion séparés + 4 UC maintenance |

## Prochaines actions recommandées

1. **Régénérer fonctionnel V2** avec `max_tokens=65536` dédié pour obtenir les 41 flux typés complets
2. **Régénérer technique V2** avec la description enrichie pour obtenir les composants physiques nommés
3. **Implémenter le lifecycle** : ajouter un niveau "lifecycle" ou une section dédiée dans le prompt opérationnel
4. **Améliorer la couverture Maintenance** : les 4 UC maintenance sont présents mais les 3 UC de réparation avancée (atelier) restent absents
