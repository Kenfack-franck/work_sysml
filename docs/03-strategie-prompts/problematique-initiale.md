# Problematique initiale

## Premiers tests avec des prompts basiques

Les premiers essais de generation de code SysML v2 avec des prompts simples (du type "genere un diagramme d'etats SysML v2 pour un systeme de climatisation") ont produit du code contenant de la syntaxe inventee. Le LLM melangeait des constructions de SysML v1, du pseudo-code, et des elements qui n'existent dans aucune version de la specification.

Ce constat a conduit a une analyse systematique des erreurs recurrentes pour identifier les patterns problematiques.

## Les 6 erreurs recurrentes

L'analyse du code genere a permis d'identifier 6 categories d'erreurs systematiques :

### Erreur 1 : Syntaxe incorrecte des etats entry/then

Le LLM genere une syntaxe inventee pour les etats initiaux dans les machines a etats.

**Mauvais** :
```sysml
entry state 'nom' { }
```

**Correct** :
```sysml
entry; then nomEtat;
```

### Erreur 2 : Syntaxe incorrecte des transitions

Les transitions sont generees avec une syntaxe melee de texte en francais et de mots-cles inventes.

**Mauvais** :
```sysml
transition Off then On if 'texte francais';
```

**Correct** :
```sysml
transition nom first Off accept Signal then On;
```

### Erreur 3 : Syntaxe incorrecte des port def

Les definitions de ports utilisent `in flow` au lieu de la syntaxe correcte avec `in item`.

**Mauvais** :
```sysml
port def X { in flow Y; }
```

**Correct** :
```sysml
port def X { in item y : Y; }
```

### Erreur 4 : Acteurs sans type

Le LLM genere des declarations d'acteurs sans passer par une definition de type, ce qui ne correspond pas a la bonne pratique SysML v2.

**Mauvais** :
```sysml
actor Pilote;
```

**Correct** :
```sysml
part def Pilote;
actor pilote : Pilote;
```

### Erreur 5 : Accents francais dans les identifiants

Les identifiants contiennent des caracteres accentues qui ne sont pas supportes par SysON.

**Mauvais** :
```sysml
part def Developpement;    // avec accent : Développement
attribute def energie;      // avec accent : énergie
state Regule;               // avec accent : régulé
```

**Correct** :
```sysml
part def Developpement;
attribute def Energie;
state Regule;
```

### Erreur 6 : Utilisation de `connect` et `flow of` dans le code

Le LLM genere des instructions `connect` et `flow of` directement dans le code textuel, alors que dans SysON ces elements sont crees graphiquement via l'editeur visuel.

**Mauvais** :
```sysml
connect source.outPort to destination.inPort;
flow of Air from source.outPort to destination.inPort;
```

**Correct** : ces connexions ne doivent pas apparaitre dans le code textuel. Elles sont creees graphiquement dans SysON.

## Solution adoptee

Pour resoudre ces problemes, l'approche retenue a ete d'analyser les **33 fichiers officiels de la specification OMG** (25 fichiers d'entrainement + 8 fichiers de validation, totalisant 1769 lignes) afin d'extraire des templates valides pour chaque type de diagramme.

Ces templates sont ensuite injectes directement dans les prompts, fournissant au LLM un modele syntaxiquement correct a suivre plutot que de le laisser inventer sa propre syntaxe.

Cette approche est detaillee dans [Templates bases sur la specification OMG](templates-officiels.md).
