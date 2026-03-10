# Templates bases sur la specification OMG

## Corpus d'analyse

Le corpus est compose de 33 fichiers issus de la specification officielle OMG SysML v2, repartis en deux ensembles :

- **25 fichiers d'entrainement** dans `data/sysml-training/` -- utilises pour construire les templates
- **8 fichiers de validation** dans `data/sysml-validation/` -- utilises pour verifier la syntaxe generee

Le corpus totalise **1769 lignes** de SysML v2 valide.

## Inventaire des fichiers d'entrainement

| Dossier | Fichier | Lignes |
|---------|---------|--------|
| 09. Connections | Connections Example.sysml | 41 |
| 10. Ports | Port Conjugation Example.sysml | 19 |
| 10. Ports | Port Example.sysml | 25 |
| 11. Interfaces | Interface Example.sysml | 18 |
| 11. Interfaces | Interface Decomposition Example.sysml | 22 |
| 13. Flows | Flow Definition Example.sysml | 20 |
| 13. Flows | Flow Interface Example.sysml | 21 |
| 13. Flows | Flow Usage Example.sysml | 17 |
| 14. Action Definitions | Action Definition Example.sysml | 20 |
| 14. Action Definitions | Action Shorthand Example.sysml | 25 |
| 14. Action Definitions | Action Succession Example-1.sysml | 25 |
| 14. Action Definitions | Action Succession Example-2.sysml | 23 |
| 15. Actions | Action Decomposition.sysml | 26 |
| 21. Asynchronous Messaging | Messaging Example.sysml | 32 |
| 21. Asynchronous Messaging | Messaging with Ports.sysml | 39 |
| 23. State Definitions | State Definition Example-1.sysml | 31 |
| 23. State Definitions | State Definition Example-2.sysml | 22 |
| 24. States | State Actions.sysml | 34 |
| 24. States | State Decomposition-1.sysml | 24 |
| 24. States | State Decomposition-2.sysml | 31 |
| 25. Transitions | Change and Time Triggers.sysml | 42 |
| 25. Transitions | Local Clock Example.sysml | 31 |
| 25. Transitions | Transition Actions.sysml | 43 |
| 35. Use Cases | Use Case Definition Example.sysml | 33 |
| 35. Use Cases | Use Case Usage Example.sysml | 42 |

## Principe d'utilisation dans les prompts

Chaque prompt de generation SysML v2 inclut un **template complet et valide** qui montre la syntaxe exacte attendue. Le LLM doit suivre ce modele plutot que d'inventer sa propre syntaxe.

Le template est choisi en fonction du type de diagramme a generer. Par exemple, un prompt pour les modes operationnels utilise un template base sur les fichiers des dossiers 23-25 (State Definitions, States, Transitions), tandis qu'un prompt pour les cas d'utilisation s'appuie sur les fichiers du dossier 35.

## Exemple de template : Modes operationnels

Voici le template injecte dans le prompt de generation des modes operationnels au niveau operationnel. Il est directement derive des exemples de la specification :

```sysml
package 'SystemName - Operating Modes' {
    attribute def EnterStandby;
    attribute def StartOperation;
    attribute def StopOperation;

    state def SystemOperatingModes {
        entry; then Off;
        state Off;
        transition PowerOn first Off accept EnterStandby then Standby;
        state Standby;
        transition Activate first Standby accept StartOperation then Operating;
        state Operating;
        transition Deactivate first Operating accept StopOperation then Standby;
    }
}
```

Les points cles de ce template :

- Les signaux de transition sont declares comme `attribute def` (pas comme `event` ou `signal`)
- L'etat initial utilise `entry; then NomEtat;` (pas `entry state`)
- Les transitions suivent le pattern `transition Nom first EtatSource accept Signal then EtatCible;`
- Les identifiants sont en CamelCase ASCII sans accents ni guillemets

## Couverture des templates

Les 25 fichiers d'entrainement couvrent l'ensemble des constructions syntaxiques necessaires aux 15 diagrammes generes par l'agent :

- **Connections et ports** (dossiers 09-11) : pour les architectures logiques et techniques
- **Flows** (dossier 13) : pour les flux entre composants
- **Actions** (dossiers 14-15) : pour les decompositions fonctionnelles et les comportements
- **Messaging** (dossier 21) : pour les sequences logiques
- **States et transitions** (dossiers 23-25) : pour les modes operationnels, fonctionnels, logiques et techniques
- **Use cases** (dossier 35) : pour les cas d'utilisation operationnels
