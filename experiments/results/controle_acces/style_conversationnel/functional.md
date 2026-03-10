# Niveau Functional — Contrôle accès - style_conversationnel

## Description fournie
> En gros, on a un bâtiment et on veut contrôler qui entre et qui sort. L'idée c'est que chaque personne a un badge RFID. Quand quelqu'un veut entrer, il passe son badge devant un lecteur. Le lecteur envoie le numéro du badge à un boîtier central qui vérifie dans une base de données si la personne a le droit d'entrer. Si oui, la porte se déverrouille automatiquement. Si non, rien ne se passe mais une alerte est envoyée au poste de sécurité. Il y a aussi des caméras à chaque entrée qui filment en permanence. Le tout doit marcher tout le temps, jour et nuit, et quand tu badges ça doit être rapide, genre moins de 2 secondes pour que la porte s'ouvre.

## Échange 1 : Description → JSON

*2026-02-21T01:42:44.801896*

### Prompt envoyé au LLM

```
Tu es un ingénieur système expert en analyse fonctionnelle. Tu décomposes les cas d'utilisation en fonctions.

=== TON RÔLE ===
À partir du modèle OPÉRATIONNEL validé, tu identifies :
- Les FONCTIONS que le système doit réaliser (QUE FAIT le système)
- Les FLUX FONCTIONNELS entre ces fonctions (échanges d'informations, d'énergie, de matière)
- Les MODES OPÉRATOIRES (configurations où certaines fonctions sont actives)

=== RÈGLES DE TRAÇABILITÉ ===
- Chaque USE CASE du niveau opérationnel doit être couvert par au moins UNE FONCTION
- Les fonctions peuvent avoir des sous-fonctions (hiérarchie)
- Les flux fonctionnels représentent les échanges entre fonctions
- Les modes permettent de décrire différentes configurations opérationnelles

=== RÈGLES DE FIDÉLITÉ ===
- Tu ne dois RIEN inventer qui ne découle pas du niveau opérationnel
- Chaque fonction doit être justifiable par un ou plusieurs use cases
- Si quelque chose est ambigu, ajoute un warning
- L'exemple ci-dessous montre uniquement la STRUCTURE attendue. En production, chaque valeur doit provenir EXCLUSIVEMENT du niveau opérationnel fourni en contexte. Si un élément n'est pas mentionné, il ne doit PAS apparaître dans ton résultat.

=== MÉTHODOLOGIE ===
1. ANALYSE : Pour chaque use case, identifie les fonctions nécessaires
2. DÉCOMPOSITION : Décompose les fonctions complexes en sous-fonctions
3. FLUX : Identifie les échanges entre fonctions (données, énergie, matière)
4. MODES : Regroupe les fonctions par modes opératoires (nominal, dégradé, maintenance, etc.)
5. VÉRIFICATION : Vérifie que tous les use cases sont couverts

=== SCHÉMA JSON ATTENDU (FunctionalModel) ===
{
  "system_name": "string",
  "warnings": ["string"],
  "functions": [
    {
      "name": "string",
      "description": "string",
      "inputs": ["string"],  // Entrées de la fonction
      "outputs": ["string"],  // Sorties de la fonction
      "sub_functions": ["string"]  // Sous-fonctions (optionnel)
    }
  ],
  "functional_flows": [
    {
      "from_function": "string",
      "to_function": "string",
      "item": "string",  // Ce qui est échangé
      "description": "string"
    }
  ],
  "modes": [
    {
      "name": "string",
      "description": "string",
      "active_functions": ["string"]  // Fonctions actives dans ce mode
    }
  ]
}

=== EXEMPLE DE STRUCTURE (placeholders — ne pas reproduire ces valeurs) ===
{
  "system_name": "Nom du système (repris depuis le niveau opérationnel)",
  "warnings": ["Avertissement si un use case ne peut être couvert"],
  "functions": [
    {
      "name": "Nom de la fonction extraite du premier use case",
      "description": "Ce que fait cette fonction, tel que déduit du use case",
      "inputs": ["Entrée mentionnée dans la description ou déduite du flux opérationnel"],
      "outputs": ["Sortie vers l'extérieur ou vers une autre fonction"],
      "sub_functions": ["Sous-fonction si la décomposition est explicite dans la description"]
    },
    {
      "name": "Nom de la fonction extraite du deuxième use case",
      "description": "Ce que fait cette fonction",
      "inputs": ["Entrée correspondant à la sortie de la première fonction"],
      "outputs": ["Sortie telle que décrite"],
      "sub_functions": []
    }
  ],
  "functional_flows": [
    {
      "from_function": "Nom de la première fonction",
      "to_function": "Nom de la deuxième fonction",
      "item": "Élément échangé tel que décrit ou déduit du contexte opérationnel",
      "description": "Pourquoi cet échange existe (traçabilité avec le use case)"
    }
  ],
  "modes": [
    {
      "name": "Mode mentionné dans la description ou déduit des scénarios opérationnels",
      "description": "Description du mode telle que fournie",
      "active_functions": ["Nom de la fonction active dans ce mode"]
    }
  ]
}


=== MODÈLE OPÉRATIONNEL VALIDÉ (CONTEXTE) ===
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


=== EXEMPLES DE SYNTAXE SysML v2 POUR RÉFÉRENCE ===
Exemple 1:
```
package AHFNorway {
	doc /* This is the Norwegian use-case for Arrowhead Framework */
	// The use-case is for Productive4.0 and Arrowhead Tools
	// The system is taken from a chemical factory
	// This is focusing on the monitoring of products when delivered
	private import AHFProfileLib::*;
	private import AHFProfileMetadata::*;
	private import AHFCoreLib::**;
	private import ScalarValues::*;

	#service def APISService {
		doc /* Service design */		

		attribute :>> serviceDefinition = "APISPullService";
		attribute :>> intrfce_protocol = "{JSON}";
		attribute :>> serviceURL = "pull";
	}

	#servicedd port def APIS_DD :> APISService {
		doc /* Service design description with nested protocol-specific ports */	

		#idd port APIS_HTTP {
			// the asynch implementation of synchronous remote calls
			out cll:CallGiveItems;
			in retrn:ResultGiveItems;
		}
		
		#idd port APIS_MQTT  {
			// GetAllItems functionality
			out pub:Publish;
			out retall:Return_AllItems;
			in subscr:Subscribe;
		}
	}
```

Exemple 2:
```
 
                                        event sendFuelCmd.sourceEvent;
                                    }
                                }
                            }
                        }
                        part redefines engine{
                            port redefines fuelCmdPort{
                                event sendFuelCmd.targetEvent;
                            }
                        }
                        message sendSensedSpeed of SensedSpeed;
                        message sendFuelCmd of FuelCmd;
                    }
                }
            }
```

Exemple 3:
```
serviceDiscovery_HTTP ;// nested port for HTTP protocol
				// here we refer the functionalities like operation Register etc.
				#idd serviceDiscovery_MQTT ; // nested port for MQTT protocol
			}
		}
		
		#systemdd authorization_DD :> authorization{
			#servicedd :>> authorisation {
				#idd authorisation_HTTP ; // nested port for HTTP protocol
				#idd authorisation_MQTT ; // nested port for MQTT protocol
			}
			action Echo_behavior :> ServiceMethod;
		}
	}
}
```



=== INSTRUCTIONS SUPPLÉMENTAIRES ===
Générer le niveau fonctionnel à partir du niveau opérationnel


=== TON RÉSULTAT (JSON UNIQUEMENT, SANS COMMENTAIRE) ===
```

### Réponse brute du LLM

```
```json
{
  "system_name": "Système de Contrôle d'Accès et de Surveillance",
  "warnings": [],
  "functions": [
    {
      "name": "Lire Badge RFID",
      "description": "Lit les informations d'identification d'un badge RFID présenté par une personne à un lecteur.",
      "inputs": [
        "Badge RFID"
      ],
      "outputs": [
        "Numéro de badge"
      ],
      "sub_functions": []
    },
    {
      "name": "Transmettre Données Badge",
      "description": "Envoie le numéro de badge lu par le lecteur au boîtier central pour traitement et vérification.",
      "inputs": [
        "Numéro de badge"
      ],
      "outputs": [
        "Numéro de badge"
      ],
      "sub_functions": []
    },
    {
      "name": "Vérifier Droits Accès",
      "description": "Interroge une base de données externe avec le numéro de badge pour déterminer si la personne a les droits d'accès requis.",
      "inputs": [
        "Numéro de badge",
        "Réponse droits d'accès (de la base de données)"
      ],
      "outputs": [
        "Requête droits d'accès (vers la base de données)",
        "Statut d'accès (Autorisé/Non Autorisé)"
      ],
      "sub_functions": []
    },
    {
      "name": "Déverrouiller Porte",
      "description": "Active le mécanisme de déverrouillage de la porte si le statut d'accès est 'Autorisé'.",
      "inputs": [
        "Statut d'accès: Autorisé"
      ],
      "outputs": [
        "Commande de déverrouillage de porte"
      ],
      "sub_functions": []
    },
    {
      "name": "Notifier Accès Non Autorisé",
      "description": "Génère et envoie une alerte au poste de sécurité en cas de tentative d'accès non autorisé.",
      "inputs": [
        "Statut d'accès: Non Autorisé"
      ],
      "outputs": [
        "Alerte d'accès non autorisé"
      ],
      "sub_functions": []
    },
    {
      "name": "Filmer Entrées",
      "description": "Capture en permanence des flux vidéo des zones d'entrée du bâtiment pour la surveillance.",
      "inputs": [
        "Scène visuelle de l'entrée"
      ],
      "outputs": [
        "Flux vidéo"
      ],
      "sub_functions": []
    }
  ],
  "functional_flows": [
    {
      "from_function": "Lire Badge RFID",
      "to_function": "Transmettre Données Badge",
      "item": "Numéro de badge",
      "description": "Le numéro de badge lu est transmis pour traitement."
    },
    {
      "from_function": "Transmettre Données Badge",
      "to_function": "Vérifier Droits Accès",
      "item": "Numéro de badge",
      "description": "Le numéro de badge est envoyé au boîtier central pour la vérification des droits."
    },
    {
      "from_function": "Vérifier Droits Accès",
      "to_function": "Déverrouiller Porte",
      "item": "Statut d'accès: Autorisé",
      "description": "Si l'accès est autorisé, une commande est envoyée pour déverrouiller la porte."
    },
    {
      "from_function": "Vérifier Droits Accès",
      "to_function": "Notifier Accès Non Autorisé",
      "item": "Statut d'accès: Non Autorisé",
      "description": "Si l'accès est non autorisé, une notification est envoyée pour alerter le poste de sécurité."
    }
  ],
  "modes": [
    {
      "name": "Opérationnel Standard",
      "description": "Mode de fonctionnement nominal où toutes les fonctions de contrôle d'accès et de surveillance sont actives en continu.",
      "active_functions": [
        "Lire Badge RFID",
        "Transmettre Données Badge",
        "Vérifier Droits Accès",
        "Déverrouiller Porte",
        "Notifier Accès Non Autorisé",
        "Filmer Entrées"
      ]
    }
  ]
}
```
```

## Échange 2 : JSON → Code SysML v2

*2026-02-21T01:43:03.717305*

### Prompt envoyé au LLM

```
Tu es un expert SysML v2. Tu traduis un modèle fonctionnel JSON en code SysML v2 valide.

=== TON RÔLE ===
Génère du code SysML v2 pour le NIVEAU FONCTIONNEL qui inclut :
1. Un package pour le niveau fonctionnel
2. Les action definitions pour chaque fonction
3. Les flow connections pour les flux fonctionnels
4. Les state definitions pour les modes

=== RÈGLES DE SYNTAXE SysML v2 ===
- action def NomDeLaFonction { ... }
- flow NomDuFlux from fonction1.output to fonction2.input;
- state def NomDuMode { ... }
- Les actions peuvent contenir des sous-actions

=== STRUCTURE ATTENDUE ===
```sysml
package '{SystemName} - Functional' {
    // Fonctions principales
    action def {Function1} {
        doc /* Description de la fonction */
        in {input1} : {Type};
        out {output1} : {Type};
        
        // Sous-fonctions si nécessaire
        action {SubFunction1} { ... }
    }
    
    // Flux fonctionnels
    flow {FlowName} from {Function1}.{output} to {Function2}.{input};
    
    // Modes opératoires
    state def {Mode1} {
        doc /* Description du mode */
        // Fonctions actives dans ce mode
    }
}
```

=== EXEMPLE ===
```sysml
package 'Drone Surveillance - Functional' {
    action def PiloterDrone {
        doc /* Contrôler la trajectoire et l'altitude du drone */
        in commandes : CommandesPilotage;
        in position : PositionGPS;
        out commandesMoteur : SignauxMoteur;
        
        action Stabiliser { ... }
        action Naviguer { ... }
    }
    
    action def CapturerImages {
        doc /* Acquérir des images vidéo de la zone */
        in declenchement : Signal;
        out images : FluxVideo;
    }
    
    action def TransmettreImages {
        doc /* Envoyer les images à la station sol */
        in images : FluxVideo;
        out fluxTransmis : FluxVideo;
    }
    
    flow FluxImages from CapturerImages.images to TransmettreImages.images;
    
    state def ModeSurveillance {
        doc /* Mode nominal de surveillance */
        entry / PiloterDrone;
        do / CapturerImages;
        do / TransmettreImages;
    }
    
    state def ModeRetourBase {
        doc /* Retour automatique à la base */
        do / PiloterDrone;
    }
}
```


=== EXEMPLES DE CODE SysML v2 ===
Exemple 1:
```sysml
package AHFNorway {
	doc /* This is the Norwegian use-case for Arrowhead Framework */
	// The use-case is for Productive4.0 and Arrowhead Tools
	// The system is taken from a chemical factory
	// This is focusing on the monitoring of products when delivered
	private import AHFProfileLib::*;
	private import AHFProfileMetadata::*;
	private import AHFCoreLib::**;
	private import ScalarValues::*;

	#service def APISService {
		doc /* Service design */		

		attribute :>> serviceDefinition = "APISPullService";
		attribute :>> intrfce_protocol = "{JSON}";
		attribute :>> serviceURL = "pull";
	}

	#servicedd port def APIS_DD :> APISService {
		doc /* Service design description with nested protocol-specific ports */	

		#idd port APIS_HTTP {
			// the asynch implementation of synchronous remote calls
			out cll:CallGiveItems;
			in retrn:ResultGiveItems;
		}
		
		#idd port APIS_MQTT  {
			// GetAllItems functionality
			out pub:Publish;
			out retall:Return_AllItems;
			in subscr:Subscribe;
		}
	}
```

Exemple 2:
```sysml
 
                                        event sendFuelCmd.sourceEvent;
                                    }
                                }
                            }
                        }
                        part redefines engine{
                            port redefines fuelCmdPort{
                                event sendFuelCmd.targetEvent;
                            }
                        }
                        message sendSensedSpeed of SensedSpeed;
                        message sendFuelCmd of FuelCmd;
                    }
                }
            }
```

Exemple 3:
```sysml
serviceDiscovery_HTTP ;// nested port for HTTP protocol
				// here we refer the functionalities like operation Register etc.
				#idd serviceDiscovery_MQTT ; // nested port for MQTT protocol
			}
		}
		
		#systemdd authorization_DD :> authorization{
			#servicedd :>> authorisation {
				#idd authorisation_HTTP ; // nested port for HTTP protocol
				#idd authorisation_MQTT ; // nested port for MQTT protocol
			}
			action Echo_behavior :> ServiceMethod;
		}
	}
}
```



=== MODÈLE FONCTIONNEL JSON ===
{
  "system_name": "Système de Contrôle d'Accès et de Surveillance",
  "warnings": [],
  "functions": [
    {
      "name": "Lire Badge RFID",
      "description": "Lit les informations d'identification d'un badge RFID présenté par une personne à un lecteur.",
      "inputs": [
        "Badge RFID"
      ],
      "outputs": [
        "Numéro de badge"
      ],
      "sub_functions": []
    },
    {
      "name": "Transmettre Données Badge",
      "description": "Envoie le numéro de badge lu par le lecteur au boîtier central pour traitement et vérification.",
      "inputs": [
        "Numéro de badge"
      ],
      "outputs": [
        "Numéro de badge"
      ],
      "sub_functions": []
    },
    {
      "name": "Vérifier Droits Accès",
      "description": "Interroge une base de données externe avec le numéro de badge pour déterminer si la personne a les droits d'accès requis.",
      "inputs": [
        "Numéro de badge",
        "Réponse droits d'accès (de la base de données)"
      ],
      "outputs": [
        "Requête droits d'accès (vers la base de données)",
        "Statut d'accès (Autorisé/Non Autorisé)"
      ],
      "sub_functions": []
    },
    {
      "name": "Déverrouiller Porte",
      "description": "Active le mécanisme de déverrouillage de la porte si le statut d'accès est 'Autorisé'.",
      "inputs": [
        "Statut d'accès: Autorisé"
      ],
      "outputs": [
        "Commande de déverrouillage de porte"
      ],
      "sub_functions": []
    },
    {
      "name": "Notifier Accès Non Autorisé",
      "description": "Génère et envoie une alerte au poste de sécurité en cas de tentative d'accès non autorisé.",
      "inputs": [
        "Statut d'accès: Non Autorisé"
      ],
      "outputs": [
        "Alerte d'accès non autorisé"
      ],
      "sub_functions": []
    },
    {
      "name": "Filmer Entrées",
      "description": "Capture en permanence des flux vidéo des zones d'entrée du bâtiment pour la surveillance.",
      "inputs": [
        "Scène visuelle de l'entrée"
      ],
      "outputs": [
        "Flux vidéo"
      ],
      "sub_functions": []
    }
  ],
  "functional_flows": [
    {
      "from_function": "Lire Badge RFID",
      "to_function": "Transmettre Données Badge",
      "item": "Numéro de badge",
      "description": "Le numéro de badge lu est transmis pour traitement."
    },
    {
      "from_function": "Transmettre Données Badge",
      "to_function": "Vérifier Droits Accès",
      "item": "Numéro de badge",
      "description": "Le numéro de badge est envoyé au boîtier central pour la vérification des droits."
    },
    {
      "from_function": "Vérifier Droits Accès",
      "to_function": "Déverrouiller Porte",
      "item": "Statut d'accès: Autorisé",
      "description": "Si l'accès est autorisé, une commande est envoyée pour déverrouiller la porte."
    },
    {
      "from_function": "Vérifier Droits Accès",
      "to_function": "Notifier Accès Non Autorisé",
      "item": "Statut d'accès: Non Autorisé",
      "description": "Si l'accès est non autorisé, une notification est envoyée pour alerter le poste de sécurité."
    }
  ],
  "modes": [
    {
      "name": "Opérationnel Standard",
      "description": "Mode de fonctionnement nominal où toutes les fonctions de contrôle d'accès et de surveillance sont actives en continu.",
      "active_functions": [
        "Lire Badge RFID",
        "Transmettre Données Badge",
        "Vérifier Droits Accès",
        "Déverrouiller Porte",
        "Notifier Accès Non Autorisé",
        "Filmer Entrées"
      ]
    }
  ]
}

=== TON RÉSULTAT (CODE SysML v2 UNIQUEMENT, SANS COMMENTAIRE) ===
```

### Réponse brute du LLM

```
```sysml
package 'Système de Contrôle d\'Accès et de Surveillance - Functional' {
    // Fonctions principales
    action def LireBadgeRFID {
        doc /* Lit les informations d'identification d'un badge RFID présenté par une personne à un lecteur. */
        in badgeRFID : BadgeRFID;
        out numeroBadge : NumeroBadge;
    }
    
    action def TransmettreDonneesBadge {
        doc /* Envoie le numéro de badge lu par le lecteur au boîtier central pour traitement et vérification. */
        in numeroBadge : NumeroBadge;
        out numeroBadgeTransmis : NumeroBadge;
    }
    
    action def VerifierDroitsAcces {
        doc /* Interroge une base de données externe avec le numéro de badge pour déterminer si la personne a les droits d'accès requis. */
        in numeroBadgeVerif : NumeroBadge;
        in reponseDroitsAcces : ReponseDroitsAcces;
        out requeteDroitsAcces : RequeteDroitsAcces;
        out statutAcces : StatutAcces;
    }
    
    action def DeverrouillerPorte {
        doc /* Active le mécanisme de déverrouillage de la porte si le statut d'accès est 'Autorisé'. */
        in statutAccesPourDeverrouillage : StatutAcces;
        out commandeDeverrouillage : CommandeDeverrouillage;
    }
    
    action def NotifierAccesNonAutorise {
        doc /* Génère et envoie une alerte au poste de sécurité en cas de tentative d'accès non autorisé. */
        in statutAccesPourNotification : StatutAcces;
        out alerteAccesNonAutorise : Alerte;
    }
    
    action def FilmerEntrees {
        doc /* Capture en permanence des flux vidéo des zones d'entrée du bâtiment pour la surveillance. */
        in sceneVisuelle : SceneVisuelle;
        out fluxVideo : FluxVideo;
    }
    
    // Flux fonctionnels
    flow FluxNumeroBadge from LireBadgeRFID.numeroBadge to TransmettreDonneesBadge.numeroBadge;
    flow FluxNumeroBadgeVerif from TransmettreDonneesBadge.numeroBadgeTransmis to VerifierDroitsAcces.numeroBadgeVerif;
    flow FluxStatutAccesAutorise from VerifierDroitsAcces.statutAcces to DeverrouillerPorte.statutAccesPourDeverrouillage;
    flow FluxStatutAccesNonAutorise from VerifierDroitsAcces.statutAcces to NotifierAccesNonAutorise.statutAccesPourNotification;
    
    // Modes opératoires
    state def OperationnelStandard {
        doc /* Mode de fonctionnement nominal où toutes les fonctions de contrôle d'accès et de surveillance sont actives en continu. */
        do / LireBadgeRFID;
        do / TransmettreDonneesBadge;
        do / VerifierDroitsAcces;
        do / DeverrouillerPorte;
        do / NotifierAccesNonAutorise;
        do / FilmerEntrees;
    }
}
```
```

### Code SysML v2 généré

```sysml
package 'Système de Contrôle d\'Accès et de Surveillance - Functional' {
    // Fonctions principales
    action def LireBadgeRFID {
        doc /* Lit les informations d'identification d'un badge RFID présenté par une personne à un lecteur. */
        in badgeRFID : BadgeRFID;
        out numeroBadge : NumeroBadge;
    }
    
    action def TransmettreDonneesBadge {
        doc /* Envoie le numéro de badge lu par le lecteur au boîtier central pour traitement et vérification. */
        in numeroBadge : NumeroBadge;
        out numeroBadgeTransmis : NumeroBadge;
    }
    
    action def VerifierDroitsAcces {
        doc /* Interroge une base de données externe avec le numéro de badge pour déterminer si la personne a les droits d'accès requis. */
        in numeroBadgeVerif : NumeroBadge;
        in reponseDroitsAcces : ReponseDroitsAcces;
        out requeteDroitsAcces : RequeteDroitsAcces;
        out statutAcces : StatutAcces;
    }
    
    action def DeverrouillerPorte {
        doc /* Active le mécanisme de déverrouillage de la porte si le statut d'accès est 'Autorisé'. */
        in statutAccesPourDeverrouillage : StatutAcces;
        out commandeDeverrouillage : CommandeDeverrouillage;
    }
    
    action def NotifierAccesNonAutorise {
        doc /* Génère et envoie une alerte au poste de sécurité en cas de tentative d'accès non autorisé. */
        in statutAccesPourNotification : StatutAcces;
        out alerteAccesNonAutorise : Alerte;
    }
    
    action def FilmerEntrees {
        doc /* Capture en permanence des flux vidéo des zones d'entrée du bâtiment pour la surveillance. */
        in sceneVisuelle : SceneVisuelle;
        out fluxVideo : FluxVideo;
    }
    
    // Flux fonctionnels
    flow FluxNumeroBadge from LireBadgeRFID.numeroBadge to TransmettreDonneesBadge.numeroBadge;
    flow FluxNumeroBadgeVerif from TransmettreDonneesBadge.numeroBadgeTransmis to VerifierDroitsAcces.numeroBadgeVerif;
    flow FluxStatutAccesAutorise from VerifierDroitsAcces.statutAcces to DeverrouillerPorte.statutAccesPourDeverrouillage;
    flow FluxStatutAccesNonAutorise from VerifierDroitsAcces.statutAcces to NotifierAccesNonAutorise.statutAccesPourNotification;
    
    // Modes opératoires
    state def OperationnelStandard {
        doc /* Mode de fonctionnement nominal où toutes les fonctions de contrôle d'accès et de surveillance sont actives en continu. */
        do / LireBadgeRFID;
        do / TransmettreDonneesBadge;
        do / VerifierDroitsAcces;
        do / DeverrouillerPorte;
        do / NotifierAccesNonAutorise;
        do / FilmerEntrees;
    }
}
```
