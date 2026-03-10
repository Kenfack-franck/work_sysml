# Niveau Operational — Contrôle accès - style_conversationnel

## Description fournie
> En gros, on a un bâtiment et on veut contrôler qui entre et qui sort. L'idée c'est que chaque personne a un badge RFID. Quand quelqu'un veut entrer, il passe son badge devant un lecteur. Le lecteur envoie le numéro du badge à un boîtier central qui vérifie dans une base de données si la personne a le droit d'entrer. Si oui, la porte se déverrouille automatiquement. Si non, rien ne se passe mais une alerte est envoyée au poste de sécurité. Il y a aussi des caméras à chaque entrée qui filment en permanence. Le tout doit marcher tout le temps, jour et nuit, et quand tu badges ça doit être rapide, genre moins de 2 secondes pour que la porte s'ouvre.

## Échange 1 : Description → JSON

*2026-02-21T01:42:23.789649*

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
 mm, mm); }

        part cameraHousing :> subSpatialParts {
            item :>> shape : Cylinder {
                :>> radius = 15 [mm];
                :>> height = 24 [mm];
            }
        }

        /* The field of view is modeled as an item, since it is not a part of the quadcopter but rather a stay-out volume 
         * that can for example be used to formulate a constraint.
         */
        item fieldOfView :> subSpatialParts {
            doc /* Conical field of view with half-top angle 20 degree */
            item :>> shape : Cone {
                :>> radius = height * tan(20 * pi/180) [mm];
                :>> height = 500 [mm];
            }
            attribute :>> coordinateFrame {
                :>> transformation : TranslationRotationSequence {
                    :>> elements = (new Rotation( (0, 1, 0)[source], 180['°']));
                }
            }
        }
        
        // By default the shape of a Camera is the union of its owned composite items and parts that are SpatialItems.
    }
```

Exemple 3:
```
d : FuelCommand;
			}
		}
	}
	
	occurrence cruiseControlInteraction_b : CruiseControlInteraction {
		part :>> driver :>> driver_b {
			port :>> setSpeedPort {
				event driver::setSpeedSent; 
			}
		}
		
		part :>> vehicle :>> vehicle_b {
			part :>> cruiseController :>> cruiseController_b {
				port :>> setSpeedPort {
					event cruiseController::setSpeedReceived;
				}
			}
			part :>> speedometer :>> speedometer_b {
				port :>> sensedSpeedPort {
					event speedometer::sensedSpeedSent;
				}
			}
			part :>> engine :>> engine_b {
				port :>> fuelCommandPort {
					event engine::fuelCommandReceived;
				}
			}
		}
		
		message :>> setSpeedMessage = driverToVehicleInterface.setSpeedFlow;
		message :>> sensedSpeedMessage = vehicle_b.sensedSpeedFlow;
		message :>> fuelCommandMessage = vehicle_b.fuelCommandFlow;
	}
}
```



=== DESCRIPTION À ANALYSER ===
En gros, on a un bâtiment et on veut contrôler qui entre et qui sort. L'idée c'est que chaque personne a un badge RFID. Quand quelqu'un veut entrer, il passe son badge devant un lecteur. Le lecteur envoie le numéro du badge à un boîtier central qui vérifie dans une base de données si la personne a le droit d'entrer. Si oui, la porte se déverrouille automatiquement. Si non, rien ne se passe mais une alerte est envoyée au poste de sécurité. Il y a aussi des caméras à chaque entrée qui filment en permanence. Le tout doit marcher tout le temps, jour et nuit, et quand tu badges ça doit être rapide, genre moins de 2 secondes pour que la porte s'ouvre.

=== TON RÉSULTAT (JSON UNIQUEMENT, SANS COMMENTAIRE) ===
```

### Réponse brute du LLM

```
```json
{
  "system_name": "Système de Contrôle d'Accès et de Surveillance",
  "description": "Le système a pour objectif de contrôler l'entrée et la sortie des personnes d'un bâtiment en utilisant des badges RFID. Il vérifie les droits d'accès, déverrouille les portes si l'accès est autorisé, et envoie des alertes au poste de sécurité en cas d'accès non autorisé. Des caméras filment en permanence à chaque entrée pour la surveillance.",
  "warnings": [],
  "stakeholders": [
    "personne",
    "poste de sécurité"
  ],
  "external_systems": [
    "base de données"
  ],
  "system_boundaries": "Le système inclut les lecteurs de badges, le boîtier central, les mécanismes de déverrouillage des portes et les caméras. Il interagit avec les personnes (via leurs badges RFID), le poste de sécurité (pour les alertes) et une base de données externe (pour la vérification des droits). Le bâtiment lui-même et les badges RFID sont externes au système.",
  "use_cases": [
    {
      "name": "Contrôler l'accès d'une personne",
      "actors": [
        "personne"
      ],
      "includes": []
    },
    {
      "name": "Notifier un accès non autorisé",
      "actors": [
        "poste de sécurité"
      ],
      "includes": []
    },
    {
      "name": "Filmer les entrées",
      "actors": [],
      "includes": []
    }
  ],
  "operational_scenarios": [
    {
      "name": "Accès autorisé d'une personne",
      "description": "Une personne autorisée utilise son badge RFID pour entrer dans le bâtiment.",
      "steps": [
        "La personne passe son badge RFID devant un lecteur.",
        "Le lecteur envoie le numéro du badge à un boîtier central.",
        "Le boîtier central vérifie les droits d'accès dans une base de données.",
        "La base de données confirme que la personne a le droit d'entrer.",
        "La porte se déverrouille automatiquement."
      ]
    },
    {
      "name": "Accès non autorisé d'une personne",
      "description": "Une personne non autorisée utilise son badge RFID pour tenter d'entrer dans le bâtiment.",
      "steps": [
        "La personne passe son badge RFID devant un lecteur.",
        "Le lecteur envoie le numéro du badge à un boîtier central.",
        "Le boîtier central vérifie les droits d'accès dans une base de données.",
        "La base de données indique que la personne n'a pas le droit d'entrer.",
        "Rien ne se passe (la porte reste verrouillée).",
        "Une alerte est envoyée au poste de sécurité."
      ]
    },
    {
      "name": "Surveillance vidéo continue des entrées",
      "description": "Les caméras filment en permanence à chaque entrée du bâtiment.",
      "steps": [
        "Les caméras à chaque entrée filment en permanence."
      ]
    }
  ],
  "requirements": [
    {
      "id": "REQ-OP-001",
      "text": "Le système doit contrôler qui entre et qui sort du bâtiment.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-002",
      "text": "Le système doit permettre à une personne de passer son badge RFID devant un lecteur pour initier un contrôle d'accès.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-003",
      "text": "Le système doit vérifier les droits d'accès d'une personne dans une base de données via un boîtier central.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-004",
      "text": "Le système doit déverrouiller automatiquement la porte si la personne a le droit d'entrer.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-005",
      "text": "Le système doit envoyer une alerte au poste de sécurité si la personne n'a pas le droit d'entrer.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-006",
      "text": "Le système doit inclure des caméras à chaque entrée qui filment en permanence.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-007",
      "text": "Le système doit fonctionner tout le temps, jour et nuit.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-008",
      "text": "Le temps entre le passage du badge et l'ouverture de la porte doit être inférieur à 2 secondes.",
      "satisfied_by": null
    }
  ]
}
```
```

## Échange 2 : JSON → Code SysML v2

*2026-02-21T01:42:37.943839*

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
 mm, mm); }

        part cameraHousing :> subSpatialParts {
            item :>> shape : Cylinder {
                :>> radius = 15 [mm];
                :>> height = 24 [mm];
            }
        }

        /* The field of view is modeled as an item, since it is not a part of the quadcopter but rather a stay-out volume 
         * that can for example be used to formulate a constraint.
         */
        item fieldOfView :> subSpatialParts {
            doc /* Conical field of view with half-top angle 20 degree */
            item :>> shape : Cone {
                :>> radius = height * tan(20 * pi/180) [mm];
                :>> height = 500 [mm];
            }
            attribute :>> coordinateFrame {
                :>> transformation : TranslationRotationSequence {
                    :>> elements = (new Rotation( (0, 1, 0)[source], 180['°']));
                }
            }
        }
        
        // By default the shape of a Camera is the union of its owned composite items and parts that are SpatialItems.
    }
```

Exemple 3:
```sysml
d : FuelCommand;
			}
		}
	}
	
	occurrence cruiseControlInteraction_b : CruiseControlInteraction {
		part :>> driver :>> driver_b {
			port :>> setSpeedPort {
				event driver::setSpeedSent; 
			}
		}
		
		part :>> vehicle :>> vehicle_b {
			part :>> cruiseController :>> cruiseController_b {
				port :>> setSpeedPort {
					event cruiseController::setSpeedReceived;
				}
			}
			part :>> speedometer :>> speedometer_b {
				port :>> sensedSpeedPort {
					event speedometer::sensedSpeedSent;
				}
			}
			part :>> engine :>> engine_b {
				port :>> fuelCommandPort {
					event engine::fuelCommandReceived;
				}
			}
		}
		
		message :>> setSpeedMessage = driverToVehicleInterface.setSpeedFlow;
		message :>> sensedSpeedMessage = vehicle_b.sensedSpeedFlow;
		message :>> fuelCommandMessage = vehicle_b.fuelCommandFlow;
	}
}
```



=== MODÈLE OPÉRATIONNEL JSON ===
{
  "system_name": "Système de Contrôle d'Accès et de Surveillance",
  "description": "Le système a pour objectif de contrôler l'entrée et la sortie des personnes d'un bâtiment en utilisant des badges RFID. Il vérifie les droits d'accès, déverrouille les portes si l'accès est autorisé, et envoie des alertes au poste de sécurité en cas d'accès non autorisé. Des caméras filment en permanence à chaque entrée pour la surveillance.",
  "warnings": [],
  "stakeholders": [
    "personne",
    "poste de sécurité"
  ],
  "external_systems": [
    "base de données"
  ],
  "system_boundaries": "Le système inclut les lecteurs de badges, le boîtier central, les mécanismes de déverrouillage des portes et les caméras. Il interagit avec les personnes (via leurs badges RFID), le poste de sécurité (pour les alertes) et une base de données externe (pour la vérification des droits). Le bâtiment lui-même et les badges RFID sont externes au système.",
  "use_cases": [
    {
      "name": "Contrôler l'accès d'une personne",
      "actors": [
        "personne"
      ],
      "includes": []
    },
    {
      "name": "Notifier un accès non autorisé",
      "actors": [
        "poste de sécurité"
      ],
      "includes": []
    },
    {
      "name": "Filmer les entrées",
      "actors": [],
      "includes": []
    }
  ],
  "operational_scenarios": [
    {
      "name": "Accès autorisé d'une personne",
      "description": "Une personne autorisée utilise son badge RFID pour entrer dans le bâtiment.",
      "steps": [
        "La personne passe son badge RFID devant un lecteur.",
        "Le lecteur envoie le numéro du badge à un boîtier central.",
        "Le boîtier central vérifie les droits d'accès dans une base de données.",
        "La base de données confirme que la personne a le droit d'entrer.",
        "La porte se déverrouille automatiquement."
      ]
    },
    {
      "name": "Accès non autorisé d'une personne",
      "description": "Une personne non autorisée utilise son badge RFID pour tenter d'entrer dans le bâtiment.",
      "steps": [
        "La personne passe son badge RFID devant un lecteur.",
        "Le lecteur envoie le numéro du badge à un boîtier central.",
        "Le boîtier central vérifie les droits d'accès dans une base de données.",
        "La base de données indique que la personne n'a pas le droit d'entrer.",
        "Rien ne se passe (la porte reste verrouillée).",
        "Une alerte est envoyée au poste de sécurité."
      ]
    },
    {
      "name": "Surveillance vidéo continue des entrées",
      "description": "Les caméras filment en permanence à chaque entrée du bâtiment.",
      "steps": [
        "Les caméras à chaque entrée filment en permanence."
      ]
    }
  ],
  "requirements": [
    {
      "id": "REQ-OP-001",
      "text": "Le système doit contrôler qui entre et qui sort du bâtiment.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-002",
      "text": "Le système doit permettre à une personne de passer son badge RFID devant un lecteur pour initier un contrôle d'accès.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-003",
      "text": "Le système doit vérifier les droits d'accès d'une personne dans une base de données via un boîtier central.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-004",
      "text": "Le système doit déverrouiller automatiquement la porte si la personne a le droit d'entrer.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-005",
      "text": "Le système doit envoyer une alerte au poste de sécurité si la personne n'a pas le droit d'entrer.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-006",
      "text": "Le système doit inclure des caméras à chaque entrée qui filment en permanence.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-007",
      "text": "Le système doit fonctionner tout le temps, jour et nuit.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-008",
      "text": "Le temps entre le passage du badge et l'ouverture de la porte doit être inférieur à 2 secondes.",
      "satisfied_by": null
    }
  ]
}

=== TON RÉSULTAT (CODE SysML v2 UNIQUEMENT, SANS COMMENTAIRE) ===
```

### Réponse brute du LLM

```
```sysml
package 'Système de Contrôle d\'Accès et de Surveillance - Operational' {
    // Use Cases
    use case def ControlerAccesPersonne {
        doc /* Le système contrôle l'accès d'une personne au bâtiment. */
        actor Personne;
    }
    
    use case def NotifierAccesNonAutorise {
        doc /* Le système notifie le poste de sécurité en cas d'accès non autorisé. */
        actor PosteDeSecurite;
    }
    
    use case def FilmerLesEntrees {
        doc /* Le système filme en permanence les entrées du bâtiment. */
    }
    
    // Exigences opérationnelles
    requirement def REQ_OP_001 {
        doc /* Le système doit contrôler qui entre et qui sort du bâtiment. */
    }
    
    requirement def REQ_OP_002 {
        doc /* Le système doit permettre à une personne de passer son badge RFID devant un lecteur pour initier un contrôle d'accès. */
    }
    
    requirement def REQ_OP_003 {
        doc /* Le système doit vérifier les droits d'accès d'une personne dans une base de données via un boîtier central. */
    }
    
    requirement def REQ_OP_004 {
        doc /* Le système doit déverrouiller automatiquement la porte si la personne a le droit d'entrer. */
    }
    
    requirement def REQ_OP_005 {
        doc /* Le système doit envoyer une alerte au poste de sécurité si la personne n'a pas le droit d'entrer. */
    }
    
    requirement def REQ_OP_006 {
        doc /* Le système doit inclure des caméras à chaque entrée qui filment en permanence. */
    }
    
    requirement def REQ_OP_007 {
        doc /* Le système doit fonctionner tout le temps, jour et nuit. */
    }
    
    requirement def REQ_OP_008 {
        doc /* Le temps entre le passage du badge et l'ouverture de la porte doit être inférieur à 2 secondes. */
    }
    
    // Scénarios opérationnels
    action def AccesAutorisePersonne {
        doc /* Une personne autorisée utilise son badge RFID pour entrer dans le bâtiment. */
        /*
        1. La personne passe son badge RFID devant un lecteur.
        2. Le lecteur envoie le numéro du badge à un boîtier central.
        3. Le boîtier central vérifie les droits d'accès dans une base de données.
        4. La base de données confirme que la personne a le droit d'entrer.
        5. La porte se déverrouille automatiquement.
        */
    }
    
    action def AccesNonAutorisePersonne {
        doc /* Une personne non autorisée utilise son badge RFID pour tenter d'entrer dans le bâtiment. */
        /*
        1. La personne passe son badge RFID devant un lecteur.
        2. Le lecteur envoie le numéro du badge à un boîtier central.
        3. Le boîtier central vérifie les droits d'accès dans une base de données.
        4. La base de données indique que la personne n'a pas le droit d'entrer.
        5. Rien ne se passe (la porte reste verrouillée).
        6. Une alerte est envoyée au poste de sécurité.
        */
    }
    
    action def SurveillanceVideoContinueDesEntrees {
        doc /* Les caméras filment en permanence à chaque entrée du bâtiment. */
        /*
        1. Les caméras à chaque entrée filment en permanence.
        */
    }
}
```
```

### Code SysML v2 généré

```sysml
package 'Système de Contrôle d\'Accès et de Surveillance - Operational' {
    // Use Cases
    use case def ControlerAccesPersonne {
        doc /* Le système contrôle l'accès d'une personne au bâtiment. */
        actor Personne;
    }
    
    use case def NotifierAccesNonAutorise {
        doc /* Le système notifie le poste de sécurité en cas d'accès non autorisé. */
        actor PosteDeSecurite;
    }
    
    use case def FilmerLesEntrees {
        doc /* Le système filme en permanence les entrées du bâtiment. */
    }
    
    // Exigences opérationnelles
    requirement def REQ_OP_001 {
        doc /* Le système doit contrôler qui entre et qui sort du bâtiment. */
    }
    
    requirement def REQ_OP_002 {
        doc /* Le système doit permettre à une personne de passer son badge RFID devant un lecteur pour initier un contrôle d'accès. */
    }
    
    requirement def REQ_OP_003 {
        doc /* Le système doit vérifier les droits d'accès d'une personne dans une base de données via un boîtier central. */
    }
    
    requirement def REQ_OP_004 {
        doc /* Le système doit déverrouiller automatiquement la porte si la personne a le droit d'entrer. */
    }
    
    requirement def REQ_OP_005 {
        doc /* Le système doit envoyer une alerte au poste de sécurité si la personne n'a pas le droit d'entrer. */
    }
    
    requirement def REQ_OP_006 {
        doc /* Le système doit inclure des caméras à chaque entrée qui filment en permanence. */
    }
    
    requirement def REQ_OP_007 {
        doc /* Le système doit fonctionner tout le temps, jour et nuit. */
    }
    
    requirement def REQ_OP_008 {
        doc /* Le temps entre le passage du badge et l'ouverture de la porte doit être inférieur à 2 secondes. */
    }
    
    // Scénarios opérationnels
    action def AccesAutorisePersonne {
        doc /* Une personne autorisée utilise son badge RFID pour entrer dans le bâtiment. */
        /*
        1. La personne passe son badge RFID devant un lecteur.
        2. Le lecteur envoie le numéro du badge à un boîtier central.
        3. Le boîtier central vérifie les droits d'accès dans une base de données.
        4. La base de données confirme que la personne a le droit d'entrer.
        5. La porte se déverrouille automatiquement.
        */
    }
    
    action def AccesNonAutorisePersonne {
        doc /* Une personne non autorisée utilise son badge RFID pour tenter d'entrer dans le bâtiment. */
        /*
        1. La personne passe son badge RFID devant un lecteur.
        2. Le lecteur envoie le numéro du badge à un boîtier central.
        3. Le boîtier central vérifie les droits d'accès dans une base de données.
        4. La base de données indique que la personne n'a pas le droit d'entrer.
        5. Rien ne se passe (la porte reste verrouillée).
        6. Une alerte est envoyée au poste de sécurité.
        */
    }
    
    action def SurveillanceVideoContinueDesEntrees {
        doc /* Les caméras filment en permanence à chaque entrée du bâtiment. */
        /*
        1. Les caméras à chaque entrée filment en permanence.
        */
    }
}
```
