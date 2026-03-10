# Coherence de nommage inter-packages

## Le probleme

Lorsque l'agent genere plusieurs packages SysML v2 pour un meme niveau d'architecture, chaque appel au LLM est independant. Sans mecanisme de coordination, le LLM peut utiliser des noms differents pour un meme concept d'un package a l'autre.

**Exemple concret** : pour un systeme de climatisation aeronautique, trois packages successifs peuvent generer :

- Package 1 (Decomposition fonctionnelle) : `PreleveAir`
- Package 2 (Comportement fonctionnel) : `PreleverLAir`
- Package 3 (Modes fonctionnels) : `PrelevAir`

Ces trois identifiants designent la meme action, mais SysON les traite comme trois elements distincts. Les references croisees entre packages sont alors cassees, rendant le modele incoherent.

## La solution : generation sequentielle avec extraction d'identifiants

Le mecanisme repose sur un cycle extraction-injection repete pour chaque package genere :

1. **Generer le Package 1** sans contrainte de nommage (premier package du niveau)
2. **Extraire les identifiants** du code genere a l'aide de patterns regex qui detectent les definitions SysML v2 :
   - `action def`, `part def`, `port def`, `state def`
   - `item def`, `attribute def`, `use case def`, `occurrence def`
3. **Construire un bloc de contrainte de nommage** listant tous les identifiants extraits par type
4. **Injecter ce bloc** dans le prompt de generation du Package 2
5. **Repeter** en accumulant les identifiants de chaque package genere pour les injecter dans le suivant

## Implementation

Le mecanisme est implemente dans trois fonctions du module `prompts/_shared.py` :

### `extract_identifiers_from_sysml(code)`

Analyse le code SysML v2 genere et retourne un dictionnaire d'identifiants classes par type de definition.

**Entree** : une chaine de caracteres contenant du code SysML v2

**Sortie** : un dictionnaire de la forme :
```python
{
    "action def": ["RegulateTemperature", "PreleveAir", "DistributeAir"],
    "part def": ["AirConditioningSystem", "PneumaticValve"],
    "port def": ["PneumaticPort", "ElectricalPort"],
    "state def": ["SystemOperatingModes"],
    ...
}
```

### `merge_identifiers(accumulated, new)`

Fusionne les identifiants nouvellement extraits avec ceux deja accumules des packages precedents, en evitant les doublons.

**Entree** : deux dictionnaires d'identifiants

**Sortie** : un dictionnaire fusionne

### `build_naming_constraint_block(identifiers)`

Construit le bloc de texte a injecter dans le prompt du package suivant.

**Entree** : le dictionnaire d'identifiants accumules

**Sortie** : un bloc de texte formatee, par exemple :

```
=== CONTRAINTE DE NOMMAGE (OBLIGATOIRE) ===
Les packages precedents ont deja defini les identifiants suivants.
Tu DOIS reutiliser EXACTEMENT ces noms. Ne PAS inventer de variantes.

Action definitions existantes : RegulateTemperature, PreleveAir
Part definitions existantes : AirConditioningSystem, PneumaticValve
Port definitions existantes : PneumaticPort, ElectricalPort

Si tu dois referencer un element deja defini, utilise EXACTEMENT le nom ci-dessus.
```

## Orchestration

L'orchestration se fait dans la methode `_generate_sysml_multi()` du module `level_service.py`. La boucle de generation suit ce schema :

```
identifiants_accumules = {}

pour chaque diagramme du niveau :
    1. Construire le prompt avec le template et les regles specifiques
    2. Si identifiants_accumules non vide :
         Injecter le bloc de contrainte de nommage dans le prompt
    3. Appeler le LLM pour generer le code SysML v2
    4. Extraire les identifiants du code genere
    5. Fusionner avec identifiants_accumules
```

Ce mecanisme garantit que le dernier package genere a connaissance de tous les identifiants definis dans les packages precedents du meme niveau, assurant ainsi la coherence des references croisees dans le modele SysML v2 final.
