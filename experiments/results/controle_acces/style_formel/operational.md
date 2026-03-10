# Niveau Operational — Contrôle accès - style_formel

## Description fournie
> Le système de contrôle d'accès du bâtiment est composé des éléments suivants. Un lecteur de badges RFID est installé à chaque point d'entrée. Il lit l'identifiant du badge et transmet cette information au contrôleur central. Le contrôleur central reçoit les identifiants des badges, interroge la base de données des autorisations, et prend la décision d'autoriser ou refuser l'accès. En cas d'autorisation, le contrôleur envoie une commande d'ouverture à la serrure électrique. La serrure électrique verrouille ou déverrouille la porte selon la commande reçue. Une caméra de surveillance est positionnée à chaque entrée et enregistre en continu. En cas de tentative d'accès refusée, le contrôleur déclenche une alerte sur le poste de sécurité. Le système doit fonctionner 24 heures sur 24 et 7 jours sur 7. Le temps entre la lecture du badge et le déverrouillage de la porte ne doit pas dépasser 2 secondes.

## Échange 1 : Description → JSON

*2026-02-21T01:44:59.709875*

### Prompt envoyé au LLM

```
Tu es un ingénieur système expert en analyse opérationnelle. Tu analyses une description pour identifier le périmètre opérationnel du système.

=== TON RÔLE ===
- Tu identifies QUI utilise le système (stakeholders, acteurs)
- Tu identifies AVEC QUOI le système interagit (systèmes externes)
- Tu définis le PÉRIMÈTRE du système (ce qui est dedans, ce qui est dehors)
- Tu extrais les CAS D'UTILISATION (use cases)
- Tu identifies les SCÉNARIOS OPÉRATIONNELS (séquences d'interactions)
- Tu formules les BESOINS OPÉRATIONNELS (requirements de haut niveau)

=== RÈGLES DE FIDÉLITÉ (CRITIQUE) ===
- Tu ne dois RIEN inventer qui n'est pas explicitement décrit
- Tu ne dois RIEN ajouter qui n'est pas mentionné
- Si quelque chose est ambigu ou incohérent, ajoute un warning dans le champ "warnings"
- Utilise le vocabulaire exact de l'utilisateur pour les noms
- Si un élément n'est pas clair, marque-le avec un warning
- L'exemple ci-dessous montre uniquement la STRUCTURE attendue. En production, chaque valeur doit provenir EXCLUSIVEMENT de la description fournie par l'utilisateur. Si un élément n'est pas mentionné, il ne doit PAS apparaître dans ton résultat.

=== MÉTHODOLOGIE (OBLIGATOIRE) ===
1. IDENTIFICATION : Liste tous les acteurs, systèmes externes et cas d'utilisation mentionnés
2. PÉRIMÈTRE : Définis clairement ce qui est dans le système et ce qui est externe
3. SCÉNARIOS : Pour chaque use case, identifie les étapes principales
4. BESOINS : Formule les besoins opérationnels à partir des use cases
5. VÉRIFICATION : Relis la description et vérifie que tout est bien capturé

=== SCHÉMA JSON ATTENDU (OperationalModel) ===
{
  "system_name": "string",
  "description": "string",
  "warnings": ["string"],  // Ambiguïtés ou incohérences
  "stakeholders": ["string"],  // Parties prenantes (utilisateurs, clients, organismes, etc.)
  "external_systems": ["string"],  // Systèmes externes avec lesquels le système interagit
  "system_boundaries": "string",  // Description textuelle du périmètre et des limites
  "use_cases": [
    {
      "name": "string",
      "actors": ["string"],  // Acteurs qui réalisent ce use case
      "includes": ["string"]  // Use cases inclus (optionnel)
    }
  ],
  "operational_scenarios": [
    {
      "name": "string",
      "description": "string",
      "steps": ["string"]  // Étapes principales du scénario
    }
  ],
  "requirements": [
    {
      "id": "string (ex: REQ-OP-001)",
      "text": "string",
      "satisfied_by": null  // Au niveau opérationnel, pas encore alloué
    }
  ]
}

=== EXEMPLE DE STRUCTURE (placeholders — ne pas reproduire ces valeurs) ===
{
  "system_name": "Nom du système extrait de la description",
  "description": "Résumé de la description fournie",
  "warnings": ["Avertissement si un élément est ambigu ou manquant"],
  "stakeholders": [
    "Premier acteur mentionné dans la description",
    "Deuxième acteur mentionné dans la description"
  ],
  "external_systems": [
    "Système externe mentionné dans la description"
  ],
  "system_boundaries": "Périmètre tel qu'il découle de la description : ce qui est dans le système et ce qui est externe",
  "use_cases": [
    {
      "name": "Cas d'utilisation mentionné dans la description",
      "actors": ["Acteur associé, tel que mentionné"],
      "includes": ["Sous-cas d'utilisation si mentionné explicitement"]
    }
  ],
  "operational_scenarios": [
    {
      "name": "Nom du scénario tel que décrit",
      "description": "Description du scénario telle que fournie",
      "steps": [
        "Étape 1 telle que décrite ou directement déduite",
        "Étape 2 telle que décrite ou directement déduite"
      ]
    }
  ],
  "requirements": [
    {
      "id": "REQ-OP-001",
      "text": "Besoin opérationnel formulé à partir de la description",
      "satisfied_by": null
    }
  ]
}


=== EXEMPLES DE SYNTAXE SysML v2 POUR RÉFÉRENCE ===
Ces exemples te donnent des idées de structure, mais tu dois rester fidèle à la description.

Exemple 1:
```
ceived;
				event controllerBehavior.sendFuelCommand[1] :>> fuelCommandSent;
			}
			part :>> speedometer :>> speedometer_a {
				event speedometerBehavior.sendSensedSpeed[1] :>> sensedSpeedSent;
			}
			part :>> engine :>> engine_a {
				event engineBehavior.receiveFuelCommand[1] :>> fuelCommandReceived;
			}
		}
		
		message :>> setSpeedMessage = driver_a.driverBehavior.sendSetSpeed.sentMessage;
		message :>> sensedSpeedMessage = vehicle_a.speedometer_a.speedometerBehavior.sendSensedSpeed.sentMessage;
		message :>> fuelCommandMessage = vehicle_a.cruiseController_a.controllerBehavior.sendFuelCommand.sentMessage;
	}
}
```

Exemple 2:
```
package 'Control Structures Example' {
	private import ScalarValues::*;
	
	attribute def BatteryCharged;
	
	part battery;
	part powerSystem;
	
	action def MonitorBattery { out charge : Real; }
	action def AddCharge { in charge : Real; }
	action def EndCharging;
	
	action def ChargeBattery {
		loop action charging {
			action monitor : MonitorBattery {
				out charge;
			}
			
			then if monitor.charge < 100 {
				action addCharge : AddCharge {
					in charge = monitor.charge;
				}
			}				
		} until charging.monitor.charge >= 100;
		
		then action endCharging : EndCharging;
		then done;
	}
}
```

Exemple 3:
```
package 'Change and Time Triggers' {
	private import ISQ::TemperatureValue;
	private import ISQ::DurationValue;
	private import Time::TimeInstantValue;
	private import SI::h;
	
	attribute def OverTemp;
	
	part def Vehicle {
		attribute maintenanceTime : TimeInstantValue;
		attribute maintenanceInterval : DurationValue;
		attribute maxTemperature : TemperatureValue;
	}
	
	part def VehicleController;
	
	action senseTemperature { out temp : TemperatureValue; }
	
	state healthStates {
		in vehicle : Vehicle;
		in controller : VehicleController;
		
		entry; then normal;
		do senseTemperature;
		
		state normal;
		accept at vehicle.maintenanceTime
			then maintenance;
		accept when senseTemperature.temp > vehicle.maxTemperature
			do send new OverTemp() to controller 
			then degraded;
		
		state maintenance {
			entry assign vehicle.maintenanceTime := vehicle.maintenanceTime + vehicle.maintenanceInterval;
		}
		accept after 48 [h]
			then normal;
		
		state degraded;
		accept when senseTemperature.temp <= vehicle.maxTemperature
			then normal;
	}
}
```



=== DESCRIPTION À ANALYSER ===
Le système de contrôle d'accès du bâtiment est composé des éléments suivants. Un lecteur de badges RFID est installé à chaque point d'entrée. Il lit l'identifiant du badge et transmet cette information au contrôleur central. Le contrôleur central reçoit les identifiants des badges, interroge la base de données des autorisations, et prend la décision d'autoriser ou refuser l'accès. En cas d'autorisation, le contrôleur envoie une commande d'ouverture à la serrure électrique. La serrure électrique verrouille ou déverrouille la porte selon la commande reçue. Une caméra de surveillance est positionnée à chaque entrée et enregistre en continu. En cas de tentative d'accès refusée, le contrôleur déclenche une alerte sur le poste de sécurité. Le système doit fonctionner 24 heures sur 24 et 7 jours sur 7. Le temps entre la lecture du badge et le déverrouillage de la porte ne doit pas dépasser 2 secondes.

=== TON RÉSULTAT (JSON UNIQUEMENT, SANS COMMENTAIRE) ===
```

### Réponse brute du LLM

```
```json
{
  "system_name": "Système de contrôle d'accès du bâtiment",
  "description": "Le système de contrôle d'accès du bâtiment gère l'accès aux points d'entrée. Il est composé d'un lecteur de badges RFID, d'un contrôleur central et d'une serrure électrique. Le système lit les identifiants de badges, interroge une base de données d'autorisations pour décider d'autoriser ou refuser l'accès, et commande l'ouverture de la serrure. En cas de refus, il déclenche une alerte sur le poste de sécurité. Une caméra de surveillance enregistre en continu à chaque entrée.",
  "warnings": [
    "L'intégration exacte de la 'base de données des autorisations' et de la 'caméra de surveillance' au périmètre du 'Système de contrôle d'accès du bâtiment' est ambiguë. Elles sont considérées comme des systèmes externes avec lesquels le système interagit ou qui cohabitent, plutôt que des composants internes du système de contrôle d'accès lui-même, basé sur la formulation 'interroge la base de données' et 'Une caméra de surveillance est positionnée... et enregistre en continu' sans mention d'interaction directe du contrôleur central avec la caméra pour la décision d'accès."
  ],
  "stakeholders": [
    "Utilisateur",
    "Agent de sécurité"
  ],
  "external_systems": [
    "Base de données des autorisations",
    "Caméra de surveillance"
  ],
  "system_boundaries": "Le système de contrôle d'accès du bâtiment inclut le lecteur de badges RFID, le contrôleur central et la serrure électrique. Il interagit avec la base de données des autorisations pour la validation des accès et avec le poste de sécurité pour la gestion des alertes. La caméra de surveillance est un système externe cohabitant, enregistrant indépendamment de la logique de décision d'accès du système.",
  "use_cases": [
    {
      "name": "Gérer l'accès d'un utilisateur",
      "actors": ["Utilisateur"],
      "includes": []
    },
    {
      "name": "Notifier une tentative d'accès refusée",
      "actors": ["Agent de sécurité"],
      "includes": []
    }
  ],
  "operational_scenarios": [
    {
      "name": "Accès autorisé d'un utilisateur",
      "description": "Un utilisateur autorisé présente son badge pour accéder au bâtiment, et l'accès est accordé.",
      "steps": [
        "L'Utilisateur présente son badge au lecteur de badges RFID.",
        "Le lecteur de badges RFID lit l'identifiant du badge.",
        "Le lecteur de badges RFID transmet l'identifiant au contrôleur central.",
        "Le contrôleur central reçoit l'identifiant du badge.",
        "Le contrôleur central interroge la base de données des autorisations.",
        "La base de données des autorisations confirme l'autorisation.",
        "Le contrôleur central prend la décision d'autoriser l'accès.",
        "Le contrôleur central envoie une commande d'ouverture à la serrure électrique.",
        "La serrure électrique déverrouille la porte."
      ]
    },
    {
      "name": "Accès refusé et alerte de sécurité",
      "description": "Un utilisateur non autorisé ou avec un badge invalide tente d'accéder au bâtiment, l'accès est refusé et une alerte est déclenchée.",
      "steps": [
        "L'Utilisateur présente son badge au lecteur de badges RFID.",
        "Le lecteur de badges RFID lit l'identifiant du badge.",
        "Le lecteur de badges RFID transmet l'identifiant au contrôleur central.",
        "Le contrôleur central reçoit l'identifiant du badge.",
        "Le contrôleur central interroge la base de données des autorisations.",
        "La base de données des autorisations indique un refus ou une absence d'autorisation.",
        "Le contrôleur central prend la décision de refuser l'accès.",
        "Le contrôleur central déclenche une alerte sur le poste de sécurité."
      ]
    }
  ],
  "requirements": [
    {
      "id": "REQ-OP-001",
      "text": "Le système doit fonctionner 24 heures sur 24 et 7 jours sur 7.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-002",
      "text": "Le temps entre la lecture du badge et le déverrouillage de la porte ne doit pas dépasser 2 secondes.",
      "satisfied_by": null
    }
  ]
}
```
```

## Échange 2 : JSON → Code SysML v2

*2026-02-21T01:45:23.754281*

### Prompt envoyé au LLM

```
Tu es un expert SysML v2. Tu traduis un modèle opérationnel JSON en code SysML v2 valide.

=== TON RÔLE ===
Génère du code SysML v2 pour le NIVEAU OPÉRATIONNEL qui inclut :
1. Un package pour le niveau opérationnel
2. Les use case definitions
3. Les requirement definitions pour les besoins opérationnels
4. Les action definitions pour les scénarios opérationnels

=== RÈGLES DE SYNTAXE SysML v2 ===
- use case def NomDuUseCase { ... }
- requirement def NomDeLExigence { ... }
- action def NomDuScenario { ... }
- Les noms doivent respecter la casse CamelCase ou snake_case
- Utilise des commentaires /* ... */ pour les descriptions

=== STRUCTURE ATTENDUE ===
```sysml
package '{SystemName} - Operational' {
    // Use Cases
    use case def {UseCase1} {
        doc /* Description du use case */
        actor {Actor1};
    }
    
    // Exigences opérationnelles
    requirement def {RequirementId} {
        doc /* Texte de l'exigence */
    }
    
    // Scénarios opérationnels
    action def {Scenario1} {
        doc /* Description du scénario */
        // Étapes du scénario comme actions ou states
    }
}
```

=== EXEMPLE ===
Pour un système de drone avec use case "SurveillerZone" et exigence "REQ-OP-001: Surveiller une zone" :

```sysml
package 'Drone Surveillance - Operational' {
    use case def SurveillerZone {
        doc /* L'opérateur surveille une zone avec le drone */
        actor Operateur;
    }
    
    requirement def REQ_OP_001 {
        doc /* Le système doit permettre de surveiller une zone définie */
    }
    
    action def MissionSurveillance {
        doc /* Scénario nominal d'une mission de surveillance */
        // Étapes : démarrage, définition zone, survol, capture, analyse
    }
}
```


=== EXEMPLES DE CODE SysML v2 ===
Exemple 1:
```sysml
ceived;
				event controllerBehavior.sendFuelCommand[1] :>> fuelCommandSent;
			}
			part :>> speedometer :>> speedometer_a {
				event speedometerBehavior.sendSensedSpeed[1] :>> sensedSpeedSent;
			}
			part :>> engine :>> engine_a {
				event engineBehavior.receiveFuelCommand[1] :>> fuelCommandReceived;
			}
		}
		
		message :>> setSpeedMessage = driver_a.driverBehavior.sendSetSpeed.sentMessage;
		message :>> sensedSpeedMessage = vehicle_a.speedometer_a.speedometerBehavior.sendSensedSpeed.sentMessage;
		message :>> fuelCommandMessage = vehicle_a.cruiseController_a.controllerBehavior.sendFuelCommand.sentMessage;
	}
}
```

Exemple 2:
```sysml
package 'Control Structures Example' {
	private import ScalarValues::*;
	
	attribute def BatteryCharged;
	
	part battery;
	part powerSystem;
	
	action def MonitorBattery { out charge : Real; }
	action def AddCharge { in charge : Real; }
	action def EndCharging;
	
	action def ChargeBattery {
		loop action charging {
			action monitor : MonitorBattery {
				out charge;
			}
			
			then if monitor.charge < 100 {
				action addCharge : AddCharge {
					in charge = monitor.charge;
				}
			}				
		} until charging.monitor.charge >= 100;
		
		then action endCharging : EndCharging;
		then done;
	}
}
```

Exemple 3:
```sysml
package 'Change and Time Triggers' {
	private import ISQ::TemperatureValue;
	private import ISQ::DurationValue;
	private import Time::TimeInstantValue;
	private import SI::h;
	
	attribute def OverTemp;
	
	part def Vehicle {
		attribute maintenanceTime : TimeInstantValue;
		attribute maintenanceInterval : DurationValue;
		attribute maxTemperature : TemperatureValue;
	}
	
	part def VehicleController;
	
	action senseTemperature { out temp : TemperatureValue; }
	
	state healthStates {
		in vehicle : Vehicle;
		in controller : VehicleController;
		
		entry; then normal;
		do senseTemperature;
		
		state normal;
		accept at vehicle.maintenanceTime
			then maintenance;
		accept when senseTemperature.temp > vehicle.maxTemperature
			do send new OverTemp() to controller 
			then degraded;
		
		state maintenance {
			entry assign vehicle.maintenanceTime := vehicle.maintenanceTime + vehicle.maintenanceInterval;
		}
		accept after 48 [h]
			then normal;
		
		state degraded;
		accept when senseTemperature.temp <= vehicle.maxTemperature
			then normal;
	}
}
```



=== MODÈLE OPÉRATIONNEL JSON ===
{
  "system_name": "Système de contrôle d'accès du bâtiment",
  "description": "Le système de contrôle d'accès du bâtiment gère l'accès aux points d'entrée. Il est composé d'un lecteur de badges RFID, d'un contrôleur central et d'une serrure électrique. Le système lit les identifiants de badges, interroge une base de données d'autorisations pour décider d'autoriser ou refuser l'accès, et commande l'ouverture de la serrure. En cas de refus, il déclenche une alerte sur le poste de sécurité. Une caméra de surveillance enregistre en continu à chaque entrée.",
  "warnings": [
    "L'intégration exacte de la 'base de données des autorisations' et de la 'caméra de surveillance' au périmètre du 'Système de contrôle d'accès du bâtiment' est ambiguë. Elles sont considérées comme des systèmes externes avec lesquels le système interagit ou qui cohabitent, plutôt que des composants internes du système de contrôle d'accès lui-même, basé sur la formulation 'interroge la base de données' et 'Une caméra de surveillance est positionnée... et enregistre en continu' sans mention d'interaction directe du contrôleur central avec la caméra pour la décision d'accès."
  ],
  "stakeholders": [
    "Utilisateur",
    "Agent de sécurité"
  ],
  "external_systems": [
    "Base de données des autorisations",
    "Caméra de surveillance"
  ],
  "system_boundaries": "Le système de contrôle d'accès du bâtiment inclut le lecteur de badges RFID, le contrôleur central et la serrure électrique. Il interagit avec la base de données des autorisations pour la validation des accès et avec le poste de sécurité pour la gestion des alertes. La caméra de surveillance est un système externe cohabitant, enregistrant indépendamment de la logique de décision d'accès du système.",
  "use_cases": [
    {
      "name": "Gérer l'accès d'un utilisateur",
      "actors": [
        "Utilisateur"
      ],
      "includes": []
    },
    {
      "name": "Notifier une tentative d'accès refusée",
      "actors": [
        "Agent de sécurité"
      ],
      "includes": []
    }
  ],
  "operational_scenarios": [
    {
      "name": "Accès autorisé d'un utilisateur",
      "description": "Un utilisateur autorisé présente son badge pour accéder au bâtiment, et l'accès est accordé.",
      "steps": [
        "L'Utilisateur présente son badge au lecteur de badges RFID.",
        "Le lecteur de badges RFID lit l'identifiant du badge.",
        "Le lecteur de badges RFID transmet l'identifiant au contrôleur central.",
        "Le contrôleur central reçoit l'identifiant du badge.",
        "Le contrôleur central interroge la base de données des autorisations.",
        "La base de données des autorisations confirme l'autorisation.",
        "Le contrôleur central prend la décision d'autoriser l'accès.",
        "Le contrôleur central envoie une commande d'ouverture à la serrure électrique.",
        "La serrure électrique déverrouille la porte."
      ]
    },
    {
      "name": "Accès refusé et alerte de sécurité",
      "description": "Un utilisateur non autorisé ou avec un badge invalide tente d'accéder au bâtiment, l'accès est refusé et une alerte est déclenchée.",
      "steps": [
        "L'Utilisateur présente son badge au lecteur de badges RFID.",
        "Le lecteur de badges RFID lit l'identifiant du badge.",
        "Le lecteur de badges RFID transmet l'identifiant au contrôleur central.",
        "Le contrôleur central reçoit l'identifiant du badge.",
        "Le contrôleur central interroge la base de données des autorisations.",
        "La base de données des autorisations indique un refus ou une absence d'autorisation.",
        "Le contrôleur central prend la décision de refuser l'accès.",
        "Le contrôleur central déclenche une alerte sur le poste de sécurité."
      ]
    }
  ],
  "requirements": [
    {
      "id": "REQ-OP-001",
      "text": "Le système doit fonctionner 24 heures sur 24 et 7 jours sur 7.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-002",
      "text": "Le temps entre la lecture du badge et le déverrouillage de la porte ne doit pas dépasser 2 secondes.",
      "satisfied_by": null
    }
  ]
}

=== TON RÉSULTAT (CODE SysML v2 UNIQUEMENT, SANS COMMENTAIRE) ===
```

### Réponse brute du LLM

```
```sysml
package 'Système de contrôle d\'accès du bâtiment - Operational' {
    // Use Cases
    use case def GererAccesUtilisateur {
        doc /* L'utilisateur interagit avec le système pour obtenir ou se voir refuser l'accès. */
        actor Utilisateur;
    }
    
    use case def NotifierTentativeAccesRefusee {
        doc /* Le système informe l'agent de sécurité d'une tentative d'accès non autorisée. */
        actor AgentDeSecurite;
    }
    
    // Exigences opérationnelles
    requirement def REQ_OP_001 {
        doc /* Le système doit fonctionner 24 heures sur 24 et 7 jours sur 7. */
    }
    
    requirement def REQ_OP_002 {
        doc /* Le temps entre la lecture du badge et le déverrouillage de la porte ne doit pas dépasser 2 secondes. */
    }
    
    // Scénarios opérationnels
    action def AccesAutoriseUtilisateur {
        doc /* Un utilisateur autorisé présente son badge pour accéder au bâtiment, et l'accès est accordé. */
        /* L'Utilisateur présente son badge au lecteur de badges RFID. */
        /* Le lecteur de badges RFID lit l'identifiant du badge. */
        /* Le lecteur de badges RFID transmet l'identifiant au contrôleur central. */
        /* Le contrôleur central reçoit l'identifiant du badge. */
        /* Le contrôleur central interroge la base de données des autorisations. */
        /* La base de données des autorisations confirme l'autorisation. */
        /* Le contrôleur central prend la décision d'autoriser l'accès. */
        /* Le contrôleur central envoie une commande d'ouverture à la serrure électrique. */
        /* La serrure électrique déverrouille la porte. */
    }
    
    action def AccesRefuseAlerteSecurite {
        doc /* Un utilisateur non autorisé ou avec un badge invalide tente d'accéder au bâtiment, l'accès est refusé et une alerte est déclenchée. */
        /* L'Utilisateur présente son badge au lecteur de badges RFID. */
        /* Le lecteur de badges RFID lit l'identifiant du badge. */
        /* Le lecteur de badges RFID transmet l'identifiant au contrôleur central. */
        /* Le contrôleur central reçoit l'identifiant du badge. */
        /* Le contrôleur central interroge la base de données des autorisations. */
        /* La base de données des autorisations indique un refus ou une absence d'autorisation. */
        /* Le contrôleur central prend la décision de refuser l'accès. */
        /* Le contrôleur central déclenche une alerte sur le poste de sécurité. */
    }
}
```
```

### Code SysML v2 généré

```sysml
package 'Système de contrôle d\'accès du bâtiment - Operational' {
    // Use Cases
    use case def GererAccesUtilisateur {
        doc /* L'utilisateur interagit avec le système pour obtenir ou se voir refuser l'accès. */
        actor Utilisateur;
    }
    
    use case def NotifierTentativeAccesRefusee {
        doc /* Le système informe l'agent de sécurité d'une tentative d'accès non autorisée. */
        actor AgentDeSecurite;
    }
    
    // Exigences opérationnelles
    requirement def REQ_OP_001 {
        doc /* Le système doit fonctionner 24 heures sur 24 et 7 jours sur 7. */
    }
    
    requirement def REQ_OP_002 {
        doc /* Le temps entre la lecture du badge et le déverrouillage de la porte ne doit pas dépasser 2 secondes. */
    }
    
    // Scénarios opérationnels
    action def AccesAutoriseUtilisateur {
        doc /* Un utilisateur autorisé présente son badge pour accéder au bâtiment, et l'accès est accordé. */
        /* L'Utilisateur présente son badge au lecteur de badges RFID. */
        /* Le lecteur de badges RFID lit l'identifiant du badge. */
        /* Le lecteur de badges RFID transmet l'identifiant au contrôleur central. */
        /* Le contrôleur central reçoit l'identifiant du badge. */
        /* Le contrôleur central interroge la base de données des autorisations. */
        /* La base de données des autorisations confirme l'autorisation. */
        /* Le contrôleur central prend la décision d'autoriser l'accès. */
        /* Le contrôleur central envoie une commande d'ouverture à la serrure électrique. */
        /* La serrure électrique déverrouille la porte. */
    }
    
    action def AccesRefuseAlerteSecurite {
        doc /* Un utilisateur non autorisé ou avec un badge invalide tente d'accéder au bâtiment, l'accès est refusé et une alerte est déclenchée. */
        /* L'Utilisateur présente son badge au lecteur de badges RFID. */
        /* Le lecteur de badges RFID lit l'identifiant du badge. */
        /* Le lecteur de badges RFID transmet l'identifiant au contrôleur central. */
        /* Le contrôleur central reçoit l'identifiant du badge. */
        /* Le contrôleur central interroge la base de données des autorisations. */
        /* La base de données des autorisations indique un refus ou une absence d'autorisation. */
        /* Le contrôleur central prend la décision de refuser l'accès. */
        /* Le contrôleur central déclenche une alerte sur le poste de sécurité. */
    }
}
```
