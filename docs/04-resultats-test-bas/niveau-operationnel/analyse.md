# Analyse de conformite -- Niveau Operationnel

## Packages generes

5 packages generes :

1. **Lifecycle** -- phases de vie du systeme
2. **Use Cases** -- cas d'utilisation et acteurs
3. **Context** -- systemes externes et interfaces
4. **Scenarios** -- scenarios operationnels
5. **Operating Modes** -- modes de fonctionnement hierarchiques

## Metriques

- **Code SysML v2 :** 10 696 caracteres
- **Syntaxe valide :** oui
- **Nombre de warnings :** 4

## Conformite syntaxe SysML v2

Constructs utilises, tous issus des templates valides :

- `state def` / `state` pour les modes et phases de vie
- `transition` / `accept` pour les transitions entre etats
- `part def` / `part` pour les composants et systemes externes
- `port def` pour les ports d'interface
- `use case def` pour les cas d'utilisation

## Conformite regles SysON (RS1-RS9)

- **RS1** : Identifiants en CamelCase
- **RS2** : Pas d'accents dans les identifiants
- **RS3** : Ports bases sur des attributs
- **RS6** : Pas de `connect` / `flow` (constructs non supportes par SysON)

## Warnings

4 warnings generes, tous legitimes (aucune invention) :

| # | Type | Section | Message |
|---|------|---------|---------|
| 1 | inconsistency | use_cases | L'acteur "Maintenance facility" est mentionne dans le use case "Maintenir en conditions operationnelles" mais n'est pas defini dans la section stakeholders |
| 2 | inconsistency | use_cases | Le use case "Maintenir en conditions operationnelles" inclut "Reparer en atelier", mais "Reparer en atelier" n'est pas defini comme use case autonome. "Reparer sous l'aile" est defini a la place |
| 3 | missing_info | requirements | Pas d'exigences operationnelles explicites (REQ-OP-XXX) trouvees |
| 4 | ambiguity | operating_modes | Les modes sont decrits avec une hierarchie (Mode On contient Stand by et En fonctionnement), mais le JSON les represente en liste plate |

## Fidelite aux entrees utilisateur

- **F1** (pas d'invention) : Respecte -- aucun element invente par le LLM
- **F2** (incoherences signalees) : Respecte -- les incoherences entre stakeholders et use cases sont signalees
- **F3** (informations manquantes signalees) : Respecte -- l'absence d'exigences operationnelles est signalee
