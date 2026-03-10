# Regles de compatibilite SysON (RS1-RS9)

Ces 9 regles sont injectees dans chaque prompt de generation SysML v2 via le bloc `SYSON_RULES_BLOCK`. Elles garantissent que le code genere est directement importable dans l'editeur SysON sans modification manuelle.

---

## RS1 : Aucun accent dans les identifiants

Les caracteres accentues ne sont pas correctement geres par SysON et provoquent des erreurs d'import.

**Mauvais** :
```sysml
part def Developpement;   // Développement
attribute def energie;     // énergie
state Regule;              // régulé
```

**Correct** :
```sysml
part def Developpement;
attribute def Energie;
state Regule;
```

---

## RS2 : Aucun caractere special (parentheses, slash, virgule, apostrophe)

Les caracteres speciaux dans les identifiants causent des erreurs de parsing dans SysON.

**Mauvais** :
```sysml
port def 'air regule (P,T)';
part def 'A/C Pneumatic System';
```

**Correct** :
```sysml
port def AirRegulePT;
part def ACPneumaticSystem;
```

---

## RS3 : CamelCase ASCII pour tous les identifiants

Tous les identifiants doivent suivre la convention CamelCase en utilisant uniquement des caracteres ASCII.

**Mauvais** :
```sysml
part def 'Operation maintenance operator';
```

**Correct** :
```sysml
part def MaintenanceOperator;
```

---

## RS4 : Aucun guillemet simple sauf si absolument necessaire

Les identifiants CamelCase n'ont pas besoin de guillemets simples. Leur utilisation doit etre evitee car elle complique le parsing dans SysON.

**Mauvais** :
```sysml
part def 'AirConditioningSystem';
state def 'SystemOperatingModes';
```

**Correct** :
```sysml
part def AirConditioningSystem;
state def SystemOperatingModes;
```

---

## RS5 : Dans port def, utiliser "attribute" au lieu de "in item"

SysON ne gere pas correctement la syntaxe `in item nom : Type;` dans les definitions de ports. La syntaxe avec `attribute` est preferee.

**Mauvais** :
```sysml
port def X {
    in item fuel : Fuel;
}
```

**Correct** :
```sysml
port def X {
    attribute fuel;
}
```

---

## RS6 : Pas de "connect" ni "flow of" dans le code

Les connexions et les flux sont crees graphiquement dans l'editeur visuel de SysON. Ils ne doivent pas apparaitre dans le code textuel.

**Mauvais** :
```sysml
connect source.outPort to destination.inPort;
flow of Air from source.outPort to destination.inPort;
```

**Correct** : ces instructions sont supprimees du code. Les connexions sont creees via l'interface graphique de SysON.

---

## RS7 : Pas de port conjugue (~)

La syntaxe de conjugaison de port avec le prefixe `~` n'est pas supportee par SysON.

**Mauvais** :
```sysml
port basPort : ~ACAvionicsPort;
```

**Correct** :
```sysml
port basPort : ACAvionicsPort;
```

---

## RS8 : Actions d'etat avec syntaxe "entry action : NomAction;"

Les actions associees aux etats doivent utiliser la syntaxe avec `action :` et un identifiant CamelCase, pas du texte libre entre guillemets.

**Mauvais** :
```sysml
do 'Communicate the system state';
entry 'Initialize parameters';
```

**Correct** :
```sysml
do action : CommunicateSystemState;
entry action : InitializeParameters;
```

---

## RS9 : Pour les sequences, utiliser occurrence def avec doc

Les diagrammes de sequence doivent utiliser `occurrence def` avec des blocs `doc` pour la description, plutot que `message` ou `event occurrence` qui ne sont pas correctement supportes par SysON.

**Mauvais** :
```sysml
message request from pilote to systeme;
event occurrence startEngine;
```

**Correct** :
```sysml
occurrence def PiloteRequestsStartEngine {
    doc /* Le pilote envoie une demande de demarrage au systeme. */
}
```

---

## Injection dans les prompts

Ces 9 regles sont rassemblees dans la constante `SYSON_RULES_BLOCK` definie dans `prompts/_shared.py`. Ce bloc est injecte dans chaque prompt de generation SysML v2, juste apres les contraintes de fidelite, assurant que le LLM les prend en compte systematiquement.
