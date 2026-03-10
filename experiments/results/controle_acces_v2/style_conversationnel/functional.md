# Niveau Functional — Contrôle accès - style_conversationnel

## Description fournie
> En gros, on a un bâtiment et on veut contrôler qui entre et qui sort. L'idée c'est que chaque personne a un badge RFID. Quand quelqu'un veut entrer, il passe son badge devant un lecteur. Le lecteur envoie le numéro du badge à un boîtier central qui vérifie dans une base de données si la personne a le droit d'entrer. Si oui, la porte se déverrouille automatiquement. Si non, rien ne se passe mais une alerte est envoyée au poste de sécurité. Il y a aussi des caméras à chaque entrée qui filment en permanence. Le tout doit marcher tout le temps, jour et nuit, et quand tu badges ça doit être rapide, genre moins de 2 secondes pour que la porte s'ouvre.

## Échange 1 : Description → JSON

*2026-02-21T03:02:49.505447*

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
  "system_name": "Système de contrôle d'accès au bâtiment",
  "description": "Système permettant de contrôler l'entrée et la sortie des personnes dans un bâtiment via des badges RFID. Il vérifie les autorisations et déverrouille les portes, ou envoie une alerte au poste de sécurité en cas d'accès non autorisé. Des caméras surveillent les entrées.",
  "warnings": [
    "La description ne précise pas si le 'boîtier central' et la 'base de données' sont des composants physiques distincts ou intégrés, ni leur emplacement exact. Ils sont considérés comme des composants internes au système.",
    "La description mentionne la présence de 'caméras' qui 'filment en permanence', mais ne spécifie aucune interaction directe entre le système de contrôle d'accès et ces caméras (par exemple, déclenchement d'enregistrement ou récupération de flux vidéo)."
  ],
  "stakeholders": [
    "Personne"
  ],
  "external_systems": [
    "porte",
    "poste de sécurité",
    "caméras"
  ],
  "system_boundaries": "Le système de contrôle d'accès inclut les lecteurs de badges RFID, le boîtier central de traitement et la base de données d'autorisation. Il interagit avec les portes pour les déverrouiller et avec le poste de sécurité pour envoyer des alertes. Les personnes utilisant les badges, les badges RFID eux-mêmes, et les caméras de surveillance sont externes au système.",
  "use_cases": [
    {
      "name": "Contrôler l'accès",
      "actors": [
        "Personne"
      ],
      "includes": []
    },
    {
      "name": "Notifier le poste de sécurité",
      "actors": [
        "Système de contrôle d'accès au bâtiment"
      ],
      "includes": []
    }
  ],
  "operational_scenarios": [
    {
      "name": "Accès autorisé",
      "description": "Une personne présente son badge RFID pour obtenir l'accès, et son autorisation est validée, entraînant le déverrouillage de la porte.",
      "steps": [
        "La Personne passe son badge RFID devant un lecteur.",
        "Le lecteur envoie le numéro du badge à un boîtier central.",
        "Le boîtier central vérifie l'autorisation dans une base de données.",
        "L'autorisation est validée.",
        "La porte se déverrouille automatiquement."
      ]
    },
    {
      "name": "Accès refusé et alerte",
      "description": "Une personne présente son badge RFID pour obtenir l'accès, mais son autorisation est refusée, entraînant l'envoi d'une alerte au poste de sécurité.",
      "steps": [
        "La Personne passe son badge RFID devant un lecteur.",
        "Le lecteur envoie le numéro du badge à un boîtier central.",
        "Le boîtier central vérifie l'autorisation dans une base de données.",
        "L'autorisation est refusée.",
        "Rien ne se passe au niveau de la porte.",
        "Une alerte est envoyée au poste de sécurité."
      ]
    }
  ],
  "requirements": [
    {
      "id": "REQ-OP-001",
      "text": "Le système doit fonctionner en continu, jour et nuit.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-002",
      "text": "Le temps entre la présentation du badge et le déverrouillage de la porte doit être inférieur à 2 secondes.",
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
  "system_name": "Système de contrôle d'accès au bâtiment",
  "warnings": [
    "La description ne précise pas si le 'boîtier central' et la 'base de données' sont des composants physiques distincts ou intégrés, ni leur emplacement exact. Ils sont considérés comme des composants internes au système.",
    "La description mentionne la présence de 'caméras' qui 'filment en permanence', mais ne spécifie aucune interaction directe entre le système de contrôle d'accès et ces caméras (par exemple, déclenchement d'enregistrement ou récupération de flux vidéo)."
  ],
  "functions": [
    {
      "name": "Lire Badge RFID",
      "description": "Lit les informations (numéro d'identification) d'un badge RFID présenté par une personne devant un lecteur.",
      "inputs": [
        "Présence de badge RFID (externe)"
      ],
      "outputs": [
        "Numéro de badge"
      ],
      "sub_functions": []
    },
    {
      "name": "Transmettre Données Badge",
      "description": "Envoie le numéro du badge lu par le lecteur au boîtier central du système pour traitement.",
      "inputs": [
        "Numéro de badge"
      ],
      "outputs": [
        "Numéro de badge transmis"
      ],
      "sub_functions": []
    },
    {
      "name": "Vérifier Autorisation",
      "description": "Compare le numéro de badge reçu avec les autorisations stockées dans la base de données pour déterminer si l'accès est permis ou refusé.",
      "inputs": [
        "Numéro de badge transmis",
        "Base de données d'autorisations (interne)"
      ],
      "outputs": [
        "Statut d'autorisation (Validé/Refusé)",
        "Motif de refus (si applicable)"
      ],
      "sub_functions": []
    },
    {
      "name": "Déverrouiller Porte",
      "description": "Commande le déverrouillage physique de la porte suite à une autorisation d'accès validée.",
      "inputs": [
        "Statut d'autorisation (Validé)"
      ],
      "outputs": [
        "Commande de déverrouillage de porte"
      ],
      "sub_functions": []
    },
    {
      "name": "Notifier Poste de Sécurité",
      "description": "Envoie une alerte au poste de sécurité en cas d'accès refusé ou d'événement nécessitant une intervention.",
      "inputs": [
        "Statut d'autorisation (Refusé)",
        "Motif de refus"
      ],
      "outputs": [
        "Alerte de sécurité"
      ],
      "sub_functions": []
    }
  ],
  "functional_flows": [
    {
      "from_function": "Lire Badge RFID",
      "to_function": "Transmettre Données Badge",
      "item": "Numéro de badge",
      "description": "Le numéro du badge est transmis du lecteur au boîtier central."
    },
    {
      "from_function": "Transmettre Données Badge",
      "to_function": "Vérifier Autorisation",
      "item": "Numéro de badge transmis",
      "description": "Le numéro de badge est envoyé au boîtier central pour vérification d'autorisation."
    },
    {
      "from_function": "Vérifier Autorisation",
      "to_function": "Déverrouiller Porte",
      "item": "Statut d'autorisation (Validé)",
      "description": "Le statut 'Validé' déclenche la fonction de déverrouillage de la porte."
    },
    {
      "from_function": "Vérifier Autorisation",
      "to_function": "Notifier Poste de Sécurité",
      "item": "Statut d'autorisation (Refusé), Motif de refus",
      "description": "Le statut 'Refusé' et le motif déclenchent l'envoi d'une alerte au poste de sécurité."
    }
  ],
  "modes": [
    {
      "name": "Mode Opérationnel Nominal",
      "description": "Le système fonctionne en continu, traitant les demandes d'accès et gérant les autorisations ou les refus, y compris l'envoi d'alertes si nécessaire.",
      "active_functions": [
        "Lire Badge RFID",
        "Transmettre Données Badge",
        "Vérifier Autorisation",
        "Déverrouiller Porte",
        "Notifier Poste de Sécurité"
      ]
    }
  ]
}
```

## Échange 2 : JSON → Code SysML v2

*2026-02-21T03:03:01.697784*

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
  "system_name": "Système de contrôle d'accès au bâtiment",
  "warnings": [
    "La description ne précise pas si le 'boîtier central' et la 'base de données' sont des composants physiques distincts ou intégrés, ni leur emplacement exact. Ils sont considérés comme des composants internes au système.",
    "La description mentionne la présence de 'caméras' qui 'filment en permanence', mais ne spécifie aucune interaction directe entre le système de contrôle d'accès et ces caméras (par exemple, déclenchement d'enregistrement ou récupération de flux vidéo)."
  ],
  "functions": [
    {
      "name": "Lire Badge RFID",
      "description": "Lit les informations (numéro d'identification) d'un badge RFID présenté par une personne devant un lecteur.",
      "inputs": [
        "Présence de badge RFID (externe)"
      ],
      "outputs": [
        "Numéro de badge"
      ],
      "sub_functions": []
    },
    {
      "name": "Transmettre Données Badge",
      "description": "Envoie le numéro du badge lu par le lecteur au boîtier central du système pour traitement.",
      "inputs": [
        "Numéro de badge"
      ],
      "outputs": [
        "Numéro de badge transmis"
      ],
      "sub_functions": []
    },
    {
      "name": "Vérifier Autorisation",
      "description": "Compare le numéro de badge reçu avec les autorisations stockées dans la base de données pour déterminer si l'accès est permis ou refusé.",
      "inputs": [
        "Numéro de badge transmis",
        "Base de données d'autorisations (interne)"
      ],
      "outputs": [
        "Statut d'autorisation (Validé/Refusé)",
        "Motif de refus (si applicable)"
      ],
      "sub_functions": []
    },
    {
      "name": "Déverrouiller Porte",
      "description": "Commande le déverrouillage physique de la porte suite à une autorisation d'accès validée.",
      "inputs": [
        "Statut d'autorisation (Validé)"
      ],
      "outputs": [
        "Commande de déverrouillage de porte"
      ],
      "sub_functions": []
    },
    {
      "name": "Notifier Poste de Sécurité",
      "description": "Envoie une alerte au poste de sécurité en cas d'accès refusé ou d'événement nécessitant une intervention.",
      "inputs": [
        "Statut d'autorisation (Refusé)",
        "Motif de refus"
      ],
      "outputs": [
        "Alerte de sécurité"
      ],
      "sub_functions": []
    }
  ],
  "functional_flows": [
    {
      "from_function": "Lire Badge RFID",
      "to_function": "Transmettre Données Badge",
      "item": "Numéro de badge",
      "description": "Le numéro du badge est transmis du lecteur au boîtier central."
    },
    {
      "from_function": "Transmettre Données Badge",
      "to_function": "Vérifier Autorisation",
      "item": "Numéro de badge transmis",
      "description": "Le numéro de badge est envoyé au boîtier central pour vérification d'autorisation."
    },
    {
      "from_function": "Vérifier Autorisation",
      "to_function": "Déverrouiller Porte",
      "item": "Statut d'autorisation (Validé)",
      "description": "Le statut 'Validé' déclenche la fonction de déverrouillage de la porte."
    },
    {
      "from_function": "Vérifier Autorisation",
      "to_function": "Notifier Poste de Sécurité",
      "item": "Statut d'autorisation (Refusé), Motif de refus",
      "description": "Le statut 'Refusé' et le motif déclenchent l'envoi d'une alerte au poste de sécurité."
    }
  ],
  "modes": [
    {
      "name": "Mode Opérationnel Nominal",
      "description": "Le système fonctionne en continu, traitant les demandes d'accès et gérant les autorisations ou les refus, y compris l'envoi d'alertes si nécessaire.",
      "active_functions": [
        "Lire Badge RFID",
        "Transmettre Données Badge",
        "Vérifier Autorisation",
        "Déverrouiller Porte",
        "Notifier Poste de Sécurité"
      ]
    }
  ]
}

=== TON RÉSULTAT (CODE SysML v2 UNIQUEMENT, SANS COMMENTAIRE) ===
```

### Réponse brute du LLM

```
```sysml
package 'Système de contrôle d\'accès au bâtiment - Functional' {
    // Fonctions principales
    action def LireBadgeRFID {
        doc /* Lit les informations (numéro d'identification) d'un badge RFID présenté par une personne devant un lecteur. */
        in presenceBadge : Signal;
        out numeroBadge : NumeroBadge;
    }
    
    action def TransmettreDonneesBadge {
        doc /* Envoie le numéro du badge lu par le lecteur au boîtier central du système pour traitement. */
        in numeroBadge : NumeroBadge;
        out numeroBadgeTransmis : NumeroBadge;
    }
    
    action def VerifierAutorisation {
        doc /* Compare le numéro de badge reçu avec les autorisations stockées dans la base de données pour déterminer si l'accès est permis ou refusé. */
        in numeroBadgeTransmis : NumeroBadge;
        in dbAutorisations : BaseDeDonneesAutorisations;
        out statutAutorisation : StatutAutorisation;
        out motifRefus : MotifRefus;
    }
    
    action def DeverrouillerPorte {
        doc /* Commande le déverrouillage physique de la porte suite à une autorisation d'accès validée. */
        in statutAutorisation : StatutAutorisation;
        out commandeDeverrouillage : CommandePorte;
    }
    
    action def NotifierPosteDeSecurite {
        doc /* Envoie une alerte au poste de sécurité en cas d'accès refusé ou d'événement nécessitant une intervention. */
        in statutAutorisation : StatutAutorisation;
        in motifRefus : MotifRefus;
        out alerteSecurite : AlerteSecurite;
    }
    
    // Flux fonctionnels
    flow FluxNumeroBadge from LireBadgeRFID.numeroBadge to TransmettreDonneesBadge.numeroBadge;
    flow FluxNumeroBadgeTransmis from TransmettreDonneesBadge.numeroBadgeTransmis to VerifierAutorisation.numeroBadgeTransmis;
    flow FluxStatutAutorisationVersDeverrouillage from VerifierAutorisation.statutAutorisation to DeverrouillerPorte.statutAutorisation;
    flow FluxStatutAutorisationVersNotification from VerifierAutorisation.statutAutorisation to NotifierPosteDeSecurite.statutAutorisation;
    flow FluxMotifRefusVersNotification from VerifierAutorisation.motifRefus to NotifierPosteDeSecurite.motifRefus;
    
    // Modes opératoires
    state def ModeOperationnelNominal {
        doc /* Le système fonctionne en continu, traitant les demandes d'accès et gérant les autorisations ou les refus, y compris l'envoi d'alertes si nécessaire. */
        do / LireBadgeRFID;
        do / TransmettreDonneesBadge;
        do / VerifierAutorisation;
        do / DeverrouillerPorte;
        do / NotifierPosteDeSecurite;
    }
}
```
```

### Code SysML v2 généré

```sysml
package 'Système de contrôle d\'accès au bâtiment - Functional' {
    // Fonctions principales
    action def LireBadgeRFID {
        doc /* Lit les informations (numéro d'identification) d'un badge RFID présenté par une personne devant un lecteur. */
        in presenceBadge : Signal;
        out numeroBadge : NumeroBadge;
    }
    
    action def TransmettreDonneesBadge {
        doc /* Envoie le numéro du badge lu par le lecteur au boîtier central du système pour traitement. */
        in numeroBadge : NumeroBadge;
        out numeroBadgeTransmis : NumeroBadge;
    }
    
    action def VerifierAutorisation {
        doc /* Compare le numéro de badge reçu avec les autorisations stockées dans la base de données pour déterminer si l'accès est permis ou refusé. */
        in numeroBadgeTransmis : NumeroBadge;
        in dbAutorisations : BaseDeDonneesAutorisations;
        out statutAutorisation : StatutAutorisation;
        out motifRefus : MotifRefus;
    }
    
    action def DeverrouillerPorte {
        doc /* Commande le déverrouillage physique de la porte suite à une autorisation d'accès validée. */
        in statutAutorisation : StatutAutorisation;
        out commandeDeverrouillage : CommandePorte;
    }
    
    action def NotifierPosteDeSecurite {
        doc /* Envoie une alerte au poste de sécurité en cas d'accès refusé ou d'événement nécessitant une intervention. */
        in statutAutorisation : StatutAutorisation;
        in motifRefus : MotifRefus;
        out alerteSecurite : AlerteSecurite;
    }
    
    // Flux fonctionnels
    flow FluxNumeroBadge from LireBadgeRFID.numeroBadge to TransmettreDonneesBadge.numeroBadge;
    flow FluxNumeroBadgeTransmis from TransmettreDonneesBadge.numeroBadgeTransmis to VerifierAutorisation.numeroBadgeTransmis;
    flow FluxStatutAutorisationVersDeverrouillage from VerifierAutorisation.statutAutorisation to DeverrouillerPorte.statutAutorisation;
    flow FluxStatutAutorisationVersNotification from VerifierAutorisation.statutAutorisation to NotifierPosteDeSecurite.statutAutorisation;
    flow FluxMotifRefusVersNotification from VerifierAutorisation.motifRefus to NotifierPosteDeSecurite.motifRefus;
    
    // Modes opératoires
    state def ModeOperationnelNominal {
        doc /* Le système fonctionne en continu, traitant les demandes d'accès et gérant les autorisations ou les refus, y compris l'envoi d'alertes si nécessaire. */
        do / LireBadgeRFID;
        do / TransmettreDonneesBadge;
        do / VerifierAutorisation;
        do / DeverrouillerPorte;
        do / NotifierPosteDeSecurite;
    }
}
```
