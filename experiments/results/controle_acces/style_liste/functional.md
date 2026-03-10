# Niveau Functional — Contrôle accès - style_liste

## Description fournie
> Système de contrôle d'accès bâtiment.

Composants :
- Lecteur de badges RFID (un par entrée)
- Contrôleur central
- Base de données des autorisations
- Serrure électrique (une par porte)
- Caméra de surveillance (une par entrée)
- Poste de sécurité

Flux :
- Lecteur RFID → Contrôleur central : identifiant badge
- Contrôleur central → Base de données : requête autorisation
- Base de données → Contrôleur central : réponse autorisation
- Contrôleur central → Serrure électrique : commande ouverture/fermeture
- Contrôleur central → Poste de sécurité : alerte accès refusé
- Caméra → Poste de sécurité : flux vidéo

Exigences :
- Disponibilité 24h/24 7j/7
- Temps de réponse badge → ouverture porte < 2 secondes

## Échange 1 : Description → JSON

*2026-02-21T02:00:29.222354*

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
  "system_name": "Système de contrôle d'accès bâtiment",
  "description": "Le système de contrôle d'accès bâtiment gère l'accès aux entrées via des lecteurs de badges RFID, un contrôleur central, une base de données d'autorisations, des serrures électriques et des caméras de surveillance. Il interagit avec un poste de sécurité pour les alertes et la surveillance vidéo.",
  "warnings": [],
  "stakeholders": [
    "Utilisateur",
    "Agent de sécurité"
  ],
  "external_systems": [],
  "system_boundaries": "Le système de contrôle d'accès bâtiment inclut les Lecteurs de badges RFID, le Contrôleur central, la Base de données des autorisations, les Serrures électriques, les Caméras de surveillance et le Poste de sécurité. Les Utilisateurs présentant des badges et les Agents de sécurité surveillant le système sont des acteurs externes interagissant avec le système.",
  "use_cases": [
    {
      "name": "Accéder au bâtiment",
      "actors": [
        "Utilisateur"
      ],
      "includes": []
    },
    {
      "name": "Surveiller les accès",
      "actors": [
        "Agent de sécurité"
      ],
      "includes": []
    }
  ],
  "operational_scenarios": [
    {
      "name": "Scénario d'accès au bâtiment",
      "description": "Un utilisateur tente d'accéder au bâtiment en présentant son badge, le système vérifie l'autorisation et ouvre la porte ou alerte le poste de sécurité.",
      "steps": [
        "L'Utilisateur présente son badge au Lecteur de badges RFID.",
        "Le Lecteur de badges RFID envoie l'identifiant badge au Contrôleur central.",
        "Le Contrôleur central envoie une requête autorisation à la Base de données des autorisations.",
        "La Base de données des autorisations envoie une réponse autorisation au Contrôleur central.",
        "Si l'autorisation est accordée, le Contrôleur central envoie une commande ouverture/fermeture à la Serrure électrique (ouverture).",
        "Si l'autorisation est refusée, le Contrôleur central envoie une alerte accès refusé au Poste de sécurité.",
        "La Caméra de surveillance envoie un flux vidéo au Poste de sécurité."
      ]
    },
    {
      "name": "Scénario de surveillance des accès",
      "description": "Un agent de sécurité surveille les accès au bâtiment via le poste de sécurité, recevant les alertes et les flux vidéo.",
      "steps": [
        "L'Agent de sécurité consulte le flux vidéo de la Caméra de surveillance via le Poste de sécurité.",
        "L'Agent de sécurité reçoit les alertes accès refusé du Contrôleur central via le Poste de sécurité."
      ]
    }
  ],
  "requirements": [
    {
      "id": "REQ-OP-001",
      "text": "Le système doit être disponible 24h/24 7j/7.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-002",
      "text": "Le temps de réponse entre la présentation du badge et l'ouverture de la porte doit être inférieur à 2 secondes.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-003",
      "text": "Le système doit permettre l'identification des badges RFID.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-004",
      "text": "Le système doit gérer les autorisations d'accès via une base de données.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-005",
      "text": "Le système doit contrôler l'ouverture et la fermeture des serrures électriques.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-006",
      "text": "Le système doit alerter le poste de sécurité en cas d'accès refusé.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-007",
      "text": "Le système doit fournir un flux vidéo au poste de sécurité.",
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
{
  "system_name": "Système de contrôle d'accès bâtiment",
  "warnings": [],
  "functions": [
    {
      "name": "Gérer l'identification des badges",
      "description": "Lit l'identifiant d'un badge RFID présenté par un utilisateur pour initier une demande d'accès. (Couvre REQ-OP-003)",
      "inputs": [
        "Badge RFID présenté"
      ],
      "outputs": [
        "Identifiant badge"
      ],
      "sub_functions": []
    },
    {
      "name": "Gérer les autorisations d'accès",
      "description": "Vérifie si un identifiant badge est autorisé à accéder au bâtiment en consultant la base de données des autorisations. (Couvre REQ-OP-004)",
      "inputs": [
        "Identifiant badge",
        "Requête autorisation"
      ],
      "outputs": [
        "Statut autorisation (accordée/refusée)"
      ],
      "sub_functions": []
    },
    {
      "name": "Contrôler l'accès physique",
      "description": "Ouvre ou ferme la serrure électrique d'une porte en fonction du statut d'autorisation reçu. (Couvre REQ-OP-005)",
      "inputs": [
        "Statut autorisation (accordée)"
      ],
      "outputs": [
        "Serrure (ouverte/fermée)"
      ],
      "sub_functions": []
    },
    {
      "name": "Gérer les alertes d'accès",
      "description": "Génère et transmet une alerte au poste de sécurité en cas d'accès refusé. (Couvre REQ-OP-006)",
      "inputs": [
        "Statut autorisation (refusée)"
      ],
      "outputs": [
        "Alerte accès refusé"
      ],
      "sub_functions": []
    },
    {
      "name": "Fournir la surveillance vidéo",
      "description": "Capture un flux vidéo de la zone d'accès et le diffuse en continu au poste de sécurité. (Couvre REQ-OP-007)",
      "inputs": [
        "Zone d'accès"
      ],
      "outputs": [
        "Flux vidéo"
      ],
      "sub_functions": []
    }
  ],
  "functional_flows": [
    {
      "from_function": "Gérer l'identification des badges",
      "to_function": "Gérer les autorisations d'accès",
      "item": "Identifiant badge",
      "description": "Transmission de l'identifiant du badge pour vérification d'autorisation."
    },
    {
      "from_function": "Gérer les autorisations d'accès",
      "to_function": "Contrôler l'accès physique",
      "item": "Statut autorisation (accordée)",
      "description": "Commande d'ouverture de la serrure suite à une autorisation accordée."
    },
    {
      "from_function": "Gérer les autorisations d'accès",
      "to_function": "Gérer les alertes d'accès",
      "item": "Statut autorisation (refusée)",
      "description": "Déclenchement d'une alerte au poste de sécurité suite à une autorisation refusée."
    }
  ],
  "modes": [
    {
      "name": "Mode Opérationnel Standard",
      "description": "Le système est en fonctionnement nominal, gérant les demandes d'accès des utilisateurs et assurant la surveillance continue du bâtiment. Ce mode est actif 24h/24 7j/7.",
      "active_functions": [
        "Gérer l'identification des badges",
        "Gérer les autorisations d'accès",
        "Contrôler l'accès physique",
        "Gérer les alertes d'accès",
        "Fournir la surveillance vidéo"
      ]
    }
  ]
}
```

## Échange 2 : JSON → Code SysML v2

*2026-02-21T02:00:46.604061*

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
  "system_name": "Système de contrôle d'accès bâtiment",
  "warnings": [],
  "functions": [
    {
      "name": "Gérer l'identification des badges",
      "description": "Lit l'identifiant d'un badge RFID présenté par un utilisateur pour initier une demande d'accès. (Couvre REQ-OP-003)",
      "inputs": [
        "Badge RFID présenté"
      ],
      "outputs": [
        "Identifiant badge"
      ],
      "sub_functions": []
    },
    {
      "name": "Gérer les autorisations d'accès",
      "description": "Vérifie si un identifiant badge est autorisé à accéder au bâtiment en consultant la base de données des autorisations. (Couvre REQ-OP-004)",
      "inputs": [
        "Identifiant badge",
        "Requête autorisation"
      ],
      "outputs": [
        "Statut autorisation (accordée/refusée)"
      ],
      "sub_functions": []
    },
    {
      "name": "Contrôler l'accès physique",
      "description": "Ouvre ou ferme la serrure électrique d'une porte en fonction du statut d'autorisation reçu. (Couvre REQ-OP-005)",
      "inputs": [
        "Statut autorisation (accordée)"
      ],
      "outputs": [
        "Serrure (ouverte/fermée)"
      ],
      "sub_functions": []
    },
    {
      "name": "Gérer les alertes d'accès",
      "description": "Génère et transmet une alerte au poste de sécurité en cas d'accès refusé. (Couvre REQ-OP-006)",
      "inputs": [
        "Statut autorisation (refusée)"
      ],
      "outputs": [
        "Alerte accès refusé"
      ],
      "sub_functions": []
    },
    {
      "name": "Fournir la surveillance vidéo",
      "description": "Capture un flux vidéo de la zone d'accès et le diffuse en continu au poste de sécurité. (Couvre REQ-OP-007)",
      "inputs": [
        "Zone d'accès"
      ],
      "outputs": [
        "Flux vidéo"
      ],
      "sub_functions": []
    }
  ],
  "functional_flows": [
    {
      "from_function": "Gérer l'identification des badges",
      "to_function": "Gérer les autorisations d'accès",
      "item": "Identifiant badge",
      "description": "Transmission de l'identifiant du badge pour vérification d'autorisation."
    },
    {
      "from_function": "Gérer les autorisations d'accès",
      "to_function": "Contrôler l'accès physique",
      "item": "Statut autorisation (accordée)",
      "description": "Commande d'ouverture de la serrure suite à une autorisation accordée."
    },
    {
      "from_function": "Gérer les autorisations d'accès",
      "to_function": "Gérer les alertes d'accès",
      "item": "Statut autorisation (refusée)",
      "description": "Déclenchement d'une alerte au poste de sécurité suite à une autorisation refusée."
    }
  ],
  "modes": [
    {
      "name": "Mode Opérationnel Standard",
      "description": "Le système est en fonctionnement nominal, gérant les demandes d'accès des utilisateurs et assurant la surveillance continue du bâtiment. Ce mode est actif 24h/24 7j/7.",
      "active_functions": [
        "Gérer l'identification des badges",
        "Gérer les autorisations d'accès",
        "Contrôler l'accès physique",
        "Gérer les alertes d'accès",
        "Fournir la surveillance vidéo"
      ]
    }
  ]
}

=== TON RÉSULTAT (CODE SysML v2 UNIQUEMENT, SANS COMMENTAIRE) ===
```

### Réponse brute du LLM

```
```sysml
package 'Système de contrôle d\'accès bâtiment - Functional' {
    // Fonctions principales
    action def GérerLIdentificationDesBadges {
        doc /* Lit l'identifiant d'un badge RFID présenté par un utilisateur pour initier une demande d'accès. (Couvre REQ-OP-003) */
        in badgeRFIDPrésenté : BadgeRFID;
        out identifiantBadge : IdentifiantBadge;
    }
    
    action def GérerLesAutorisationsDAccès {
        doc /* Vérifie si un identifiant badge est autorisé à accéder au bâtiment en consultant la base de données des autorisations. (Couvre REQ-OP-004) */
        in identifiantBadge : IdentifiantBadge;
        in requêteAutorisation : RequêteAutorisation;
        out statutAutorisationAccordée : StatutAutorisationAccordée;
        out statutAutorisationRefusée : StatutAutorisationRefusée;
    }
    
    action def ContrôlerLAccèsPhysique {
        doc /* Ouvre ou ferme la serrure électrique d'une porte en fonction du statut d'autorisation reçu. (Couvre REQ-OP-005) */
        in statutAutorisationAccordée : StatutAutorisationAccordée;
        out étatSerrure : ÉtatSerrure;
    }
    
    action def GérerLesAlertesDAccès {
        doc /* Génère et transmet une alerte au poste de sécurité en cas d'accès refusé. (Couvre REQ-OP-006) */
        in statutAutorisationRefusée : StatutAutorisationRefusée;
        out alerteAccèsRefusé : AlerteAccèsRefusé;
    }
    
    action def FournirLaSurveillanceVidéo {
        doc /* Capture un flux vidéo de la zone d'accès et le diffuse en continu au poste de sécurité. (Couvre REQ-OP-007) */
        in zoneAccès : ZoneAccès;
        out fluxVideo : FluxVideo;
    }
    
    // Flux fonctionnels
    flow FluxIdentifiantBadge from GérerLIdentificationDesBadges.identifiantBadge to GérerLesAutorisationsDAccès.identifiantBadge;
    flow FluxAutorisationAccordée from GérerLesAutorisationsDAccès.statutAutorisationAccordée to ContrôlerLAccèsPhysique.statutAutorisationAccordée;
    flow FluxAutorisationRefusée from GérerLesAutorisationsDAccès.statutAutorisationRefusée to GérerLesAlertesDAccès.statutAutorisationRefusée;
    
    // Modes opératoires
    state def ModeOpérationnelStandard {
        doc /* Le système est en fonctionnement nominal, gérant les demandes d'accès des utilisateurs et assurant la surveillance continue du bâtiment. Ce mode est actif 24h/24 7j/7. */
        do / GérerLIdentificationDesBadges;
        do / GérerLesAutorisationsDAccès;
        do / ContrôlerLAccèsPhysique;
        do / GérerLesAlertesDAccès;
        do / FournirLaSurveillanceVidéo;
    }
}
```
```

### Code SysML v2 généré

```sysml
package 'Système de contrôle d\'accès bâtiment - Functional' {
    // Fonctions principales
    action def GérerLIdentificationDesBadges {
        doc /* Lit l'identifiant d'un badge RFID présenté par un utilisateur pour initier une demande d'accès. (Couvre REQ-OP-003) */
        in badgeRFIDPrésenté : BadgeRFID;
        out identifiantBadge : IdentifiantBadge;
    }
    
    action def GérerLesAutorisationsDAccès {
        doc /* Vérifie si un identifiant badge est autorisé à accéder au bâtiment en consultant la base de données des autorisations. (Couvre REQ-OP-004) */
        in identifiantBadge : IdentifiantBadge;
        in requêteAutorisation : RequêteAutorisation;
        out statutAutorisationAccordée : StatutAutorisationAccordée;
        out statutAutorisationRefusée : StatutAutorisationRefusée;
    }
    
    action def ContrôlerLAccèsPhysique {
        doc /* Ouvre ou ferme la serrure électrique d'une porte en fonction du statut d'autorisation reçu. (Couvre REQ-OP-005) */
        in statutAutorisationAccordée : StatutAutorisationAccordée;
        out étatSerrure : ÉtatSerrure;
    }
    
    action def GérerLesAlertesDAccès {
        doc /* Génère et transmet une alerte au poste de sécurité en cas d'accès refusé. (Couvre REQ-OP-006) */
        in statutAutorisationRefusée : StatutAutorisationRefusée;
        out alerteAccèsRefusé : AlerteAccèsRefusé;
    }
    
    action def FournirLaSurveillanceVidéo {
        doc /* Capture un flux vidéo de la zone d'accès et le diffuse en continu au poste de sécurité. (Couvre REQ-OP-007) */
        in zoneAccès : ZoneAccès;
        out fluxVideo : FluxVideo;
    }
    
    // Flux fonctionnels
    flow FluxIdentifiantBadge from GérerLIdentificationDesBadges.identifiantBadge to GérerLesAutorisationsDAccès.identifiantBadge;
    flow FluxAutorisationAccordée from GérerLesAutorisationsDAccès.statutAutorisationAccordée to ContrôlerLAccèsPhysique.statutAutorisationAccordée;
    flow FluxAutorisationRefusée from GérerLesAutorisationsDAccès.statutAutorisationRefusée to GérerLesAlertesDAccès.statutAutorisationRefusée;
    
    // Modes opératoires
    state def ModeOpérationnelStandard {
        doc /* Le système est en fonctionnement nominal, gérant les demandes d'accès des utilisateurs et assurant la surveillance continue du bâtiment. Ce mode est actif 24h/24 7j/7. */
        do / GérerLIdentificationDesBadges;
        do / GérerLesAutorisationsDAccès;
        do / ContrôlerLAccèsPhysique;
        do / GérerLesAlertesDAccès;
        do / FournirLaSurveillanceVidéo;
    }
}
```
