# Rapport de syntaxe SysML v2 — Templates pour la génération LLM

## 1. Inventaire des fichiers analysés

### data/sysml-training/ (25 fichiers, 706 lignes)

| Dossier | Fichier | Lignes |
|---------|---------|--------|
| 09. Connections | Connections Example.sysml | 41 |
| 10. Ports | Port Conjugation Example.sysml | 19 |
| 10. Ports | Port Example.sysml | 25 |
| 11. Interfaces | Interface Decomposition Example.sysml | 22 |
| 11. Interfaces | Interface Example.sysml | 18 |
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

### data/sysml-validation/ (8 fichiers, 1063 lignes)

| Dossier | Fichier | Lignes |
|---------|---------|--------|
| 02-Parts Interconnection | 2a-Parts Interconnection.sysml | 205 |
| 02-Parts Interconnection | 2c-Parts Interconnection-Multiple Decompositions.sysml | 89 |
| 05-State-based Behavior | 5-State-based Behavior-1.sysml | 235 |
| 05-State-based Behavior | 5-State-based Behavior-1a.sysml | 237 |
| 05-State-based Behavior | 5-State-based Behavior-2.sysml | 127 |
| 17-Sequence Modeling | 17a-Sequence-Modeling.sysml | 41 |
| 17-Sequence Modeling | 17b-Sequence-Modeling.sysml | 41 |
| 18-Use Case | 18-Use Case.sysml | 88 |

**Total : 33 fichiers, 1 769 lignes**

---

## 2. Lifecycle — Phases de vie avec transitions

### Constructs SysML v2 à utiliser

- `state def` — définition de machine à états
- `entry; then` — état initial
- `state` — déclaration d'état
- `transition first ... then` — transition explicite nommée
- `accept` — déclencheur de transition
- `do action` — action continue dans un état

### Syntaxe exacte extraite des fichiers officiels

**État initial (entry point) :**
```sysml
state def VehicleStates {
    entry; then off;
    state off;
    // ...
}
```
Source : `State Definition Example-1.sysml` ligne 8, `State Definition Example-2.sysml` ligne 8

**Transition explicite nommée :**
```sysml
transition off_to_starting
    first off
    accept VehicleStartSignal
    then starting;
```
Source : `State Definition Example-1.sysml` lignes 12-15

**Transition abrégée (implicite depuis l'état précédent) :**
```sysml
state off;
accept VehicleStartSignal
    then starting;
```
Source : `State Definition Example-2.sysml` lignes 11-13

**Actions d'état :**
```sysml
state on {
    entry performSelfTest { in vehicle = operatingVehicle; }
    do action providePower { /* ... */ }
    exit action applyParkingBrake { /* ... */ }
}
```
Source : `State Actions.sysml` lignes 26-30

**Actions d'état simplifiées (référence par nom) :**
```sysml
state on {
    entry 'perform self test';
    do 'provide power';
    exit 'apply parking brake';
}
```
Source : `5-State-based Behavior-1.sysml` lignes 108-115

**Transition temporelle (after) :**
```sysml
accept after 48 [h]
    then normal;
```
Source : `Change and Time Triggers.sysml` lignes 36-37

**Transition conditionnelle (when) :**
```sysml
accept when senseTemperature.temp > vehicle.maxTemperature
    do send new OverTemp() to controller
    then degraded;
```
Source : `Change and Time Triggers.sysml` lignes 29-31

**Transition avec garde :**
```sysml
accept VehicleOnSignal
    if operatingVehicle.brakePedalDepressed
    do send new ControllerStartSignal() to controller
    then on;
```
Source : `Transition Actions.sysml` lignes 29-32

**Action d'assignation dans un état :**
```sysml
state maintenance {
    entry assign vehicle.maintenanceTime :=
        vehicle.maintenanceTime + vehicle.maintenanceInterval;
}
```
Source : `Change and Time Triggers.sysml` lignes 34-35

### Pièges à éviter

| Erreur courante | Syntaxe correcte |
|-----------------|------------------|
| `entry state 'nom' { }` | `entry; then nomEtat;` suivi de `state nomEtat;` |
| `transition Off then On if 'texte';` | `transition nom first Off accept Signal then On;` |
| `if 'une phrase en français'` | `if expression.booléenne` (jamais de string comme garde) |
| `state def X { initial state y; }` | `state def X { entry; then y; state y; }` |

### Template complet

```sysml
// === TEMPLATE: Lifecycle (Phases de vie) ===
// Constructs utilisés : state def, entry, state, transition, accept
// Source : State Definition Example-1.sysml, Change and Time Triggers.sysml
// Pièges à éviter : pas de "entry state", pas de garde textuelle

package 'SystemName - Lifecycle' {

    // REMPLACER: Définir les signaux de transition entre phases
    attribute def PhaseTransitionSignal;
    attribute def StartDevelopment;
    attribute def StartProduction;
    attribute def DeliverToCustomer;
    attribute def InitiateRetirement;

    state def 'SystemName Lifecycle' {

        // Point d'entrée : première phase
        entry; then 'concept evaluation';

        // REMPLACER: Adapter les phases au système réel
        state 'concept evaluation';
        transition 'start development'
            first 'concept evaluation'
            accept StartDevelopment
            then development;

        state development;
        transition 'start production'
            first development
            accept StartProduction
            then production;

        state production;
        transition 'deliver to customer'
            first production
            accept DeliverToCustomer
            then 'in service';

        state 'in service' {
            // REMPLACER: Actions pendant la phase de service
            do action 'monitor system' { /* surveillance continue */ }
        }
        transition 'initiate retirement'
            first 'in service'
            accept InitiateRetirement
            then retirement;

        state retirement;
    }
}
```

---

## 3. Use Cases — Cas d'utilisation avec acteurs

### Constructs SysML v2 à utiliser

- `part def` — prérequis : type pour chaque acteur et le sujet
- `use case def` — définition réutilisable d'un cas d'utilisation
- `use case` — usage/instanciation d'un cas d'utilisation
- `subject` — le système cible
- `actor` — participant externe
- `objective { doc /* ... */ }` — objectif documenté
- `include use case` — inclusion d'un sous-cas
- `first start` / `then done` — séquencement

### Syntaxe exacte extraite des fichiers officiels

**Déclaration des types (obligatoire avant les use cases) :**
```sysml
part def Vehicle;
part def Person;
part def Environment;
part def 'Fuel Station';
```
Source : `Use Case Definition Example.sysml` lignes 3-6

**Définition d'un use case (template réutilisable) :**
```sysml
use case def 'Provide Transportation' {
    subject vehicle : Vehicle;

    actor driver : Person;
    actor passengers : Person[0..4];
    actor environment : Environment;

    objective {
        doc
        /* Transport driver and passengers from starting location
         * to ending location.
         */
    }
}
```
Source : `Use Case Definition Example.sysml` lignes 8-21

**Définition simple sans objective :**
```sysml
use case def 'Enter Vehicle' {
    subject vehicle : Vehicle;
    actor driver : Person;
    actor passengers : Person[0..4];
}
```
Source : `Use Case Definition Example.sysml` lignes 23-27

**Usage avec séquencement et inclusion :**
```sysml
use case 'provide transportation' : 'Provide Transportation' {
    subject vehicle;

    first start;

    then include use case 'enter vehicle' : 'Enter Vehicle' {
        subject vehicle;
        actor driver = 'provide transportation'::driver;
        actor passengers = 'provide transportation'::passengers;
    }

    then use case 'drive vehicle' {
        subject vehicle;
        actor driver = 'provide transportation'::driver;
        actor environment = 'provide transportation'::environment;

        include 'add fuel'[0..*] {
            subject vehicle;
            actor fueler = driver;
        }
    }

    then include use case 'exit vehicle' : 'Exit Vehicle' {
        subject vehicle;
        actor driver = 'provide transportation'::driver;
        actor passengers = 'provide transportation'::passengers;
    }

    then done;
}
```
Source : `Use Case Usage Example.sysml` lignes 7-38

**Use case autonome (sans référence à une définition) :**
```sysml
use case 'add fuel' {
    subject vehicle : Vehicle;
    actor fueler : Person;
    actor 'fuel station' : 'Fuel Station';
}
```
Source : `Use Case Usage Example.sysml` lignes 40-44

**Pré/post-conditions (validation) :**
```sysml
ref :>> start {
    doc /* Mock-up of a pre-condition. */
    assert constraint {
        doc /* Vehicle at starting location */
    }
}
```
Source : `18-Use Case.sysml` lignes 27-30

**Actor binding avec redéfinition :**
```sysml
then include 'enter vehicle' {
    subject;
    actor :>> driver = 'provide transportation'::driver;
    actor :>> passengers = 'provide transportation'::passengers;
}
```
Source : `18-Use Case.sysml` lignes 33-37

### Pièges à éviter

| Erreur courante | Syntaxe correcte |
|-----------------|------------------|
| `actor Pilote;` (sans type) | `part def Pilote;` puis `actor pilote : Pilote;` |
| `include use case 'Diagnostiquer l\'état'` | `include use case 'Diagnostiquer l état'` (pas de backslash) |
| `use case { actor "nom" }` | `actor nom : TypeDef;` (guillemets simples pour espaces) |
| `use case def X { include Y; }` | Les `include` vont dans `use case` (usage), pas dans `use case def` |

### Template complet

```sysml
// === TEMPLATE: Use Cases ===
// Constructs utilisés : part def, use case def, use case, subject, actor, objective, include
// Source : Use Case Definition Example.sysml, Use Case Usage Example.sysml, 18-Use Case.sysml
// Pièges à éviter : pas de backslash dans les noms, actors typés obligatoirement

package 'SystemName - Use Cases' {

    // REMPLACER: Définir les types pour le sujet et les acteurs
    part def 'SystemName';
    part def Operator;
    part def Maintainer;
    part def 'External System';

    // REMPLACER: Définitions des use cases principaux
    use case def 'Operate System' {
        subject system : 'SystemName';

        actor operator : Operator;
        actor maintainer : Maintainer;
        actor 'external system' : 'External System';

        objective {
            doc
            /* REMPLACER: Décrire l'objectif principal du cas d'utilisation. */
        }
    }

    use case def 'Start System' {
        subject system : 'SystemName';
        actor operator : Operator;
    }

    use case def 'Shutdown System' {
        subject system : 'SystemName';
        actor operator : Operator;
    }

    use case def 'Perform Maintenance' {
        subject system : 'SystemName';
        actor maintainer : Maintainer;
    }

    // REMPLACER: Usage avec séquencement
    use case 'operate system' : 'Operate System' {
        subject system;

        first start;

        then include use case 'start system' : 'Start System' {
            subject system;
            actor operator = 'operate system'::operator;
        }

        then use case 'nominal operation' {
            subject system;
            actor operator = 'operate system'::operator;
            actor 'external system' = 'operate system'::'external system';

            include 'perform maintenance'[0..*] {
                subject system;
                actor maintainer = 'operate system'::maintainer;
            }
        }

        then include use case 'shutdown system' : 'Shutdown System' {
            subject system;
            actor operator = 'operate system'::operator;
        }

        then done;
    }

    use case 'perform maintenance' : 'Perform Maintenance' {
        subject system : 'SystemName';
        actor maintainer : Maintainer;
    }
}
```

---

## 4. Context — Systèmes externes avec ports et flux

### Constructs SysML v2 à utiliser

- `part def` — définition des composants (système, systèmes externes)
- `port def` — définition des ports avec `in item` / `out item`
- `attribute def` / `item def` — types pour les items échangés
- `interface def` — définition d'interface entre deux ports
- `part` — instanciation dans un contexte englobant
- `connect` — connexion simple entre ports
- `interface : Type connect ... to ...` — connexion typée
- `flow of Type from ... to ...` — flux typé

### Syntaxe exacte extraite des fichiers officiels

**Définition de port avec items directionnels :**
```sysml
port def FuelOutPort {
    attribute temperature : Temp;
    out item fuelSupply : Fuel;
    in item fuelReturn : Fuel;
}

port def FuelInPort {
    attribute temperature : Temp;
    in item fuelSupply : Fuel;
    out item fuelReturn : Fuel;
}
```
Source : `Port Example.sysml` lignes 7-18

**Port conjugué (inverse automatique des directions) :**
```sysml
port def FuelPort {
    out item fuelSupply : Fuel;
    in item fuelReturn : Fuel;
}

part def FuelTank {
    port fuelTankPort : FuelPort;
}

part def Engine {
    port engineFuelPort : ~FuelPort;
}
```
Source : `Port Conjugation Example.sysml` lignes 6-18

**Part def avec ports :**
```sysml
part def Engine {
    port fuelCmdPort : FuelCmdPort;
    port drivePwrPort : DrivePwrPort;
}
```
Source : `2a-Parts Interconnection.sysml` lignes 62-65

**Définition d'interface :**
```sysml
interface def FuelInterface {
    end supplierPort : FuelOutPort;
    end consumerPort : FuelInPort;
}
```
Source : `Interface Example.sysml` lignes 6-9

**Interface avec flux internes :**
```sysml
interface def FuelInterface {
    end supplierPort : FuelOutPort;
    end consumerPort : FuelInPort;

    flow supplierPort.fuelSupply to consumerPort.fuelSupply;
    flow consumerPort.fuelReturn to supplierPort.fuelReturn;
}
```
Source : `Flow Interface Example.sysml` lignes 6-13

**Instanciation et connexion via interface :**
```sysml
part vehicle : Vehicle {
    part tankAssy : FuelTankAssembly;
    part eng : Engine;

    interface : FuelInterface connect
        supplierPort ::> tankAssy.fuelTankPort to
        consumerPort ::> eng.engineFuelPort;
}
```
Source : `Interface Example.sysml` lignes 11-17

**Connexion simple (sans interface def) :**
```sysml
connect b11.pe to b12.pf;
```
Source : `2c-Parts Interconnection-Multiple Decompositions.sysml` ligne 58

**Flux typé anonyme :**
```sysml
flow of Fuel
  from tankAssy.fuelTankPort.fuelSupply
  to eng.engineFuelPort.fuelSupply;
```
Source : `Flow Usage Example.sysml` lignes 10-12

**Flux typé avec définition :**
```sysml
flow def FuelFlow {
    ref :>> payload : Fuel;
    end port supplierPort : FuelOutPort;
    end port consumerPort : FuelInPort;
}

flow : FuelFlow of Fuel
  from tankAssy.fuelTankPort.fuelSupply
  to eng.engineFuelPort.fuelSupply;
```
Source : `Flow Definition Example.sysml` lignes 6-18

**Connection def (définition de connexion réutilisable) :**
```sysml
connection def PressureSeat {
    end [1] part bead : TireBead;
    end [1] part mountingRim : TireMountingRim;
}

connection : PressureSeat
    connect bead references t.bead
    to mountingRim references w.rim;
```
Source : `Connections Example.sysml` lignes 13-32

**Port binding :**
```sysml
bind fuelCmdPort = engine.fuelCmdPort;
```
Source : `2a-Parts Interconnection.sysml` ligne 98

**Port redefinition/binding avec `:>>` :**
```sysml
port :>> pe = c1.pb;
```
Source : `2c-Parts Interconnection-Multiple Decompositions.sysml` ligne 52

### Pièges à éviter

| Erreur courante | Syntaxe correcte |
|-----------------|------------------|
| `port def X { in flow Y; }` | `port def X { in item y : Y; }` (utiliser `item`, pas `flow`) |
| `connection def X { flow a.out to b.in; }` | Les `flow` vont dans une `interface def` ou dans un `part`, pas dans une `connection def` |
| `port def X` imbriqué dans un `part` | `port def` au niveau package, puis `port nom : X;` dans le `part def` |
| `connect a to b` sans chemins | `connect partA.portX to partB.portY;` (toujours via des ports) |

### Template complet

```sysml
// === TEMPLATE: Context (Diagramme de contexte) ===
// Constructs utilisés : part def, port def, item def, interface def, part, connect, flow
// Source : Port Example.sysml, Interface Example.sysml, Flow Usage Example.sysml
// Pièges à éviter : pas de port def dans un part, items (pas flows) dans port def

package 'SystemName - Context' {

    // REMPLACER: Types des items échangés
    item def Command;
    item def Status;
    item def Energy;
    item def Data;

    // REMPLACER: Définitions des ports
    port def CommandPort {
        in item command : Command;
        out item status : Status;
    }

    port def EnergyInPort {
        in item energy : Energy;
    }

    port def EnergyOutPort {
        out item energy : Energy;
    }

    port def DataPort {
        out item data : Data;
        in item command : Command;
    }

    // REMPLACER: Définition du système principal
    part def 'SystemName' {
        port commandPort : CommandPort;
        port energyPort : EnergyInPort;
        port dataPort : DataPort;
    }

    // REMPLACER: Définitions des systèmes externes
    part def Operator {
        port commandPort : ~CommandPort;
    }

    part def 'Power Source' {
        port energyPort : EnergyOutPort;
    }

    part def 'External System' {
        port dataPort : ~DataPort;
    }

    // REMPLACER: Contexte englobant (instanciation + connexions)
    part context {
        part system : 'SystemName';
        part operator : Operator;
        part 'power source' : 'Power Source';
        part 'external system' : 'External System';

        connect operator.commandPort to system.commandPort;
        connect 'power source'.energyPort to system.energyPort;
        connect system.dataPort to 'external system'.dataPort;

        // Flux typés
        flow of Command
          from operator.commandPort.command
          to system.commandPort.command;

        flow of Status
          from system.commandPort.status
          to operator.commandPort.status;

        flow of Energy
          from 'power source'.energyPort.energy
          to system.energyPort.energy;
    }
}
```

---

## 5. Operational Sequences — Séquences d'actions entre participants

### Constructs SysML v2 à utiliser

- `item def` — définition des messages
- `occurrence def` — définition d'une séquence (contient participants + messages)
- `part` — participants (lifelines) dans l'`occurrence def`
- `event occurrence` — point dans la timeline d'un participant
- `then event occurrence` — chainage séquentiel des événements
- `message ... of Type from ... to ...` — message entre participants
- Alternative : `action def` avec `send ... to` et `accept`

### Syntaxe exacte extraite des fichiers officiels

**Approche 1 — occurrence def avec messages (recommandé pour les séquences) :**
```sysml
occurrence def PubSubSequence {
    part producer[1] {
        event occurrence publish_source_event;
    }

    message publish_message of Publish[1]
        from producer.publish_source_event
        to server.publish_target_event;

    part server[1] {
        event occurrence subscribe_target_event;
        then event occurrence publish_target_event;
        then event occurrence deliver_source_event;
    }

    message subscribe_message of Subscribe[1]
        from consumer.subscribe_source_event
        to server.subscribe_target_event;
    message deliver_message of Deliver[1]
        from server.deliver_source_event
        to consumer.deliver_target_event;

    part consumer[1] {
        event occurrence subscribe_source_event;
        then event occurrence deliver_target_event;
    }
}
```
Source : `17a-Sequence-Modeling.sysml` lignes 21-41

**Approche 2 — messages avec événements implicites via `.sourceEvent` / `.targetEvent` :**
```sysml
occurrence def PubSubSequence {
    part producer[1] {
        event publish_message.sourceEvent;
    }

    message publish_message of Publish[1];

    part server[1] {
        event subscribe_message.targetEvent;
        then event publish_message.targetEvent;
        then event deliver_message.sourceEvent;
    }

    message subscribe_message of Subscribe[1];
    message deliver_message of Deliver[1];

    part consumer[1] {
        event subscribe_message.sourceEvent;
        then event deliver_message.targetEvent;
    }
}
```
Source : `17b-Sequence-Modeling.sysml` lignes 21-41

**Approche 3 — action avec send/accept (pour séquences simples) :**
```sysml
action takePicture : TakePicture {
    action trigger accept scene : Scene;

    then action focus : Focus {
        in item scene = trigger.scene;
        out item image;
    }

    flow from focus.image to shoot.image;

    then action shoot : Shoot {
        in item image;
        out item picture;
    }

    then send new Show(shoot.picture) to screen;
}
```
Source : `Messaging Example.sysml` lignes 16-32

**Send via port :**
```sysml
then send new Show(shoot.picture) via displayPort;
```
Source : `Messaging with Ports.sysml` ligne 37

**Accept via port :**
```sysml
action trigger accept scene : Scene via viewPort;
```
Source : `Messaging with Ports.sysml` ligne 23

**Définition des payloads :**
```sysml
item def Subscribe {
    attribute topic : String;
    ref part subscriber;
}

item def Publish {
    attribute topic : String;
    ref publication;
}

item def Deliver {
    ref publication;
}
```
Source : `17a-Sequence-Modeling.sysml` lignes 5-18

**Succession d'actions :**
```sysml
first focus then shoot;
```
Source : `Action Succession Example-1.sysml` ligne 19

### Pièges à éviter

| Erreur courante | Syntaxe correcte |
|-----------------|------------------|
| `action step1 send 'commande' via X to Y;` | `then send new CommandType(data) to target;` (send séparé) |
| `send 'texte libre' to actor;` | `send new TypeDef(param) to partName;` (toujours un `new Type()`) |
| `lifeline Pilot { }` | `part pilot[1] { event occurrence ...; }` (pas de keyword lifeline) |
| `sequence def X { }` | `occurrence def X { }` (pas de keyword sequence) |

### Template complet

```sysml
// === TEMPLATE: Operational Sequences ===
// Constructs utilisés : item def, occurrence def, part, event occurrence, message
// Source : 17a-Sequence-Modeling.sysml, Messaging Example.sysml
// Pièges à éviter : pas de "lifeline", pas de "sequence def", messages typés obligatoires

package 'SystemName - Operational Sequences' {

    // REMPLACER: Définition des types de messages
    item def RequestCommand {
        attribute commandType : ScalarValues::String;
    }

    item def StatusReport {
        attribute systemStatus : ScalarValues::String;
    }

    item def Alert {
        attribute severity : ScalarValues::String;
    }

    // REMPLACER: Scénario nominal
    occurrence def 'Nominal Operation Sequence' {

        // Participant 1 : Opérateur
        part operator[1] {
            event occurrence sendCommand;
            then event occurrence receiveStatus;
        }

        // Message 1 : Opérateur envoie une commande au système
        message 'command message' of RequestCommand[1]
            from operator.sendCommand
            to system.receiveCommand;

        // Participant 2 : Système
        part system[1] {
            event occurrence receiveCommand;
            then event occurrence processCommand;
            then event occurrence sendStatus;
            then event occurrence sendAlert;
        }

        // Message 2 : Système renvoie le statut
        message 'status message' of StatusReport[1]
            from system.sendStatus
            to operator.receiveStatus;

        // Message 3 : Système alerte le superviseur
        message 'alert message' of Alert[1]
            from system.sendAlert
            to supervisor.receiveAlert;

        // Participant 3 : Superviseur
        part supervisor[1] {
            event occurrence receiveAlert;
        }
    }
}
```

---

## 6. Operating Modes — Machine à états hiérarchique

### Constructs SysML v2 à utiliser

- `state def` — machine à états (réutilisable)
- `state` — état simple ou composite (nommé)
- `entry; then` — état initial
- `accept` — trigger de transition
- `transition first ... then` — transition explicite
- `state ... parallel { }` — états parallèles (orthogonaux)
- `if` — garde sur transition
- `accept after` / `accept when` — triggers temporels/conditionnels
- `entry` / `do` / `exit` — actions d'état

### Syntaxe exacte extraite des fichiers officiels

**Machine à états avec hiérarchie :**
```sysml
state vehicleStates : VehicleStates parallel {
    state operationalStates {
        entry; then off;

        state off;
        accept VehicleStartSignal
            then starting;

        state starting;
        accept VehicleOnSignal
            then on;

        state on;
        accept VehicleOffSignal
            then off;
    }

    state healthStates {
        entry; then normal;
        state normal;
        state degraded;
        state maintenance;
    }
}
```
Source : `State Decomposition-2.sysml` lignes 9-30

**États composites avec transitions conditionnelles :**
```sysml
state 'operational states' {
    entry; then off;

    state off;
    accept 'Vehicle Start Signal'
        if vehicle1_c1.'brake pedal depressed'
        do send new 'Start Signal'() to vehicle1_c1.vehicleController
        then starting;

    state starting;
    accept 'Vehicle On Signal'
        then on;

    state on {
        entry 'perform self test';
        do 'provide power';
        exit 'apply parking brake';
    }
    accept 'Vehicle Off Signal'
        then off;
}
```
Source : `5-State-based Behavior-2.sysml` lignes 42-66

**Transitions temporelles dans une machine à états :**
```sysml
state def VehicleHealthStates {
    entry; then normal;
    do senseTemperature;

    state normal;
    accept at vehicle.maintenanceTime
        then maintenance;
    accept when senseTemperature.temp > vehicle.maxTemperature
        do send new OverTemp() to controller
        then degraded;

    state degraded;
    accept after 48 [h]
        then normal;

    state maintenance {
        entry assign vehicle.maintenanceTime :=
            vehicle.maintenanceTime + vehicle.maintenanceInterval;
    }
    accept when senseTemperature.temp <= vehicle.maxTemperature
        then normal;
}
```
Source : `Change and Time Triggers.sysml` lignes 21-42

### Pièges à éviter

| Erreur courante | Syntaxe correcte |
|-----------------|------------------|
| `entry state 'Mode Normal' { }` | `entry; then 'Mode Normal';` puis `state 'Mode Normal';` |
| `state def X { state On { state Sub; } }` | Le `state` imbriqué est valide tel quel |
| `parallel { region1; region2; }` | `state nomEtat parallel { state region1 { ... } state region2 { ... } }` |

### Template complet

```sysml
// === TEMPLATE: Operating Modes (Machine à états hiérarchique) ===
// Constructs utilisés : state def, state, entry, transition, accept, parallel
// Source : State Decomposition-2.sysml, Change and Time Triggers.sysml
// Pièges à éviter : pas de "entry state", pas de "region", parallel est un attribut de state

package 'SystemName - Operating Modes' {

    // REMPLACER: Signaux de transition
    attribute def PowerOnSignal;
    attribute def PowerOffSignal;
    attribute def FaultDetected;
    attribute def FaultCleared;
    attribute def MaintenanceRequest;
    attribute def MaintenanceComplete;

    // REMPLACER: Machine à états des modes opérationnels
    state def 'SystemName Modes' {

        // États parallèles : modes opérationnels + modes de santé
        entry; then 'system modes';

        state 'system modes' parallel {

            // Région 1 : Modes opérationnels
            state 'operational modes' {
                entry; then off;

                state off;
                transition 'power on'
                    first off
                    accept PowerOnSignal
                    then starting;

                state starting {
                    entry 'perform initialization';
                }
                transition 'startup complete'
                    first starting
                    accept after 5 [SI::s]
                    then nominal;

                state nominal {
                    do 'nominal operation';
                }
                transition 'power off'
                    first nominal
                    accept PowerOffSignal
                    then 'shutting down';

                state 'shutting down' {
                    entry 'perform shutdown sequence';
                    exit 'save state';
                }
                transition 'shutdown complete'
                    first 'shutting down'
                    accept after 3 [SI::s]
                    then off;
            }

            // Région 2 : Modes de santé
            state 'health modes' {
                entry; then normal;

                state normal;
                accept FaultDetected
                    then degraded;

                state degraded;
                accept FaultCleared
                    then normal;
                accept MaintenanceRequest
                    then maintenance;

                state maintenance {
                    entry 'run diagnostics';
                }
                accept MaintenanceComplete
                    then normal;
            }
        }
    }
}
```

---

## 7. Table de correspondance erreurs LLM → corrections

| # | Code LLM erroné | Problème | Syntaxe correcte (officielle) | Source |
|---|-----------------|----------|-------------------------------|--------|
| 1 | `part 'BAS' { port def 'PortToTurbomachine' { ... } }` | `port def` ne peut pas être déclaré à l'intérieur d'un `part`. Les `port def` sont au niveau package. | `port def 'PortToTurbomachine' { in item air : Air; }` au niveau package, puis `port portToTurbo : 'PortToTurbomachine';` dans le `part def`. | Port Example.sysml, 2a-Parts Interconnection.sysml |
| 2 | `connection def 'BAS-Turbomachine' { flow turbomachine.out to bas.'PortToTurbomachine'.in; }` | Les `flow` ne vont pas dans une `connection def`. Une `connection def` a des `end`, pas des `flow`. | `connection def 'BAS-Turbomachine' { end [1] part source : Turbomachine; end [1] part target : BAS; }` ou utiliser `flow of AirType from source.portOut to target.portIn;` dans le part englobant. | Connections Example.sysml, Flow Usage Example.sysml |
| 3 | `action step1 send 'commande' via acAvionics to bas;` | Syntaxe `send` incorrecte : pas de texte libre, doit être un `new Type()`, et `send` est une instruction séparée avec `then`. | `then send new CommandType() to bas;` ou `then send new CommandType() via acAvionics;` (to OU via, pas les deux). | Messaging Example.sysml:31, Messaging with Ports.sysml:37 |
| 4 | `transition Off then On if 'quand le système reçoit de l\'énergie';` | (a) La garde `if` ne prend pas de string, mais une expression booléenne. (b) La syntaxe `transition` requiert `first` et `accept`. | `transition off_to_on first Off accept PowerOnSignal then On;` | State Definition Example-1.sysml:12-15, Transition Actions.sysml:29-32 |
| 5 | `include use case 'Diagnostiquer l\'état'` | Les backslashes ne sont pas supportés dans les identifiants SysML v2 entre guillemets simples. | `include use case 'Diagnostiquer l état'` (sans backslash, espace normal) ou reformuler : `include use case 'Diagnostiquer Etat'` | Use Case Definition Example.sysml, 18-Use Case.sysml |
| 6 | `state def LifecycleStates { entry state 'Concept evaluation' { ... } }` | `entry state` n'existe pas en SysML v2. L'entrée se fait avec `entry; then nomEtat;` suivi de la déclaration `state nomEtat;`. | `state def LifecycleStates { entry; then 'Concept evaluation'; state 'Concept evaluation'; }` | State Definition Example-1.sysml:8-9, 5-State-based Behavior-1.sysml:43 |

### Règles générales issues de l'analyse

1. **Les définitions (`def`) sont au niveau package** : `port def`, `part def`, `connection def`, `interface def`, `action def`, `state def`, `use case def` — jamais imbriquées dans un `part`.

2. **Les usages sont dans les `part`** : `port portX : PortDef;`, `connect a.p to b.q;`, `flow of X from a to b;`

3. **`send` utilise toujours `new Type()`** : jamais de texte libre. Le type doit être un `attribute def` ou `item def` défini.

4. **Les gardes (`if`) sont des expressions** : jamais des chaînes de texte. Elles référencent des attributs/propriétés (`if vehicle.brakePedalDepressed`).

5. **Les guillemets simples** servent à échapper les identifiants avec espaces/caractères spéciaux. Pas de backslash à l'intérieur.

6. **Les transitions** suivent le pattern : `[transition nom] first source accept trigger [if garde] [do effet] then cible;`

7. **Les acteurs dans les use cases** doivent obligatoirement être typés avec un `part def` déclaré au préalable.

8. **Les séquences** utilisent `occurrence def` avec `event occurrence` et `message`, pas `sequence def` ni `lifeline`.

---

*Rapport généré à partir de l'analyse de 33 fichiers .sysml officiels (SysML-v2-Release, OMG).*
*Total : 1 769 lignes de syntaxe officielle analysées.*
