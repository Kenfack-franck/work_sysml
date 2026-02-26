# Niveau Technical — BAS Silvercrest - Formel

## Description fournie
> Le système BAS (Bleed Air System) est un système de prélèvement et de conditionnement d'air intégré au moteur Silvercrest. Il est intercalé entre la turbomachine et l'avion.

Le système interagit avec les entités externes suivantes :
- L'avionique de l'avion (A/C Avionics), qui fournit l'énergie électrique, envoie les consignes de pression et température, envoie les commandes de dégivrage, et reçoit les données d'état du système.
- La turbomachine (cœur du moteur), qui est la source d'air chaud à haute pression.
- Le conduit de soufflante (Fan by-pass duct), qui est la source d'air froid ambiant.
- La nacelle, qui reçoit l'air chaud pour le dégivrage et évacue l'air de refroidissement.
- Le système pneumatique de l'avion (A/C Pneumatic System), qui reçoit l'air conditionné et régulé en pression et température.
- La vanne d'isolement de l'avion (SOV - Shut-Off Valve), qui est la frontière physique en sortie du BAS.

Le système réalise quatre fonctions de service :
1. Envoyer de l'air régulé en pression et température à l'avion.
2. Envoyer de l'air chaud à la nacelle pour le dégivrage.
3. Déterminer l'état du système par mesures physiques et auto-diagnostic.
4. Communiquer les consignes et statuts avec l'avionique.

Le système possède trois modes de fonctionnement :
- OFF : Le système n'est pas alimenté, aucune vanne n'est active.
- Stand-by : Le système est alimenté et communique son état, mais les commandes de flux d'air ne sont pas activées.
- Running : Le système régule activement la pression et la température pour envoyer de l'air à la cabine et/ou ouvre le circuit de dégivrage.

Le système est composé des sous-systèmes et composants suivants :

Sous-système de Prélèvement d'air :
- IP Port (Intermediate Pressure) : prélèvement primaire d'air chaud depuis la turbomachine.
- HP Port (High Pressure) : prélèvement secondaire d'air chaud depuis la turbomachine.
- HPV (High Pressure Valve) : vanne qui contrôle l'ouverture du port HP, activée lorsque la pression IP est insuffisante.
- IPCV (Intermediate Pressure Check Valve) : clapet anti-retour entre la jonction HP et IP, empêche l'air HP de refouler vers l'étage IP.

Sous-système de Dégivrage Nacelle :
- NAIV (Nacelle Anti-Ice Valve) : vanne d'arrêt qui autorise ou bloque le passage de l'air chaud vers la nacelle.
- NAI press. sensor : capteur de pression après la NAIV pour surveiller la pression de dégivrage.
- Nacelle anti-ice port : interface de sortie vers la nacelle.

Sous-système de Conditionnement :
- PRV (Pressure Regulating Valve) : vanne qui abaisse et régule la pression de l'air chaud selon une consigne.
- Exchanger (échangeur thermique ACAC) : dispositif qui refroidit l'air chaud régulé en pression par échange avec l'air froid.
- Fan bleed port : entrée d'air froid prélevé sur le flux secondaire du moteur.
- FAV (Fan Air Valve) : vanne qui régule le débit d'air froid admis dans l'échangeur.
- Filter : filtre pour l'air avant l'interface avion.
- Nacelle exhaust port : sortie qui rejette l'air de refroidissement après l'échangeur.

Sous-système de Mesure finale :
- Bleed press. sensor : capteur de pression finale régulée en sortie.
- Bleed temp. sensor : capteur de température finale régulée en sortie.

Sous-système de Contrôle-Commande :
- Electronic BAS Control (embarqué dans l'EEC) : calculateur qui reçoit les consignes de l'avionique, acquiert les mesures des capteurs, et envoie les signaux de commande aux vannes HPV, PRV, FAV et NAIV.

Scénario 1 - Fourniture d'air nominal :
L'avionique envoie les consignes de pression et température au calculateur. L'air est prélevé sur l'IP Port. Le calculateur pilote la PRV pour atteindre la pression cible. Simultanément, le calculateur pilote la FAV pour réguler la température via l'échangeur. Les capteurs de sortie renvoient les mesures au calculateur qui ajuste en boucle fermée. L'air régulé sort vers le système pneumatique de l'avion.

Scénario 2 - Dégivrage nacelle :
L'avionique transmet la commande de dégivrage au calculateur. Le calculateur ouvre la vanne NAIV. L'air chaud haute pression traverse la NAIV, est mesuré par le capteur NAI Press, et sort vers la nacelle. L'état est remonté à l'avionique.

Le système doit fonctionner dans une plage de température de -40°C à +85°C. Le temps de réponse de la boucle de régulation ne doit pas dépasser 500 millisecondes. La pression de sortie régulée doit être maintenue entre 20 et 50 PSI. La température de sortie régulée doit être maintenue entre 150°C et 230°C.


## Échange 1 : JSON → Code SysML v2

*2026-02-21T13:22:43.952415*

### Prompt envoyé au LLM

```
Tu es un expert SysML v2. Tu traduis un modèle technique JSON en code SysML v2 valide.

=== TON RÔLE ===
Génère du code SysML v2 pour le NIVEAU TECHNIQUE qui inclut :
1. Un package pour le niveau technique
2. Les part definitions pour chaque composant technique
3. Les attributs techniques (specs matérielles)
4. Les connections physiques
5. Les allocations de composants logiques vers techniques

=== RÈGLES DE SYNTAXE SysML v2 ===
- part def NomComposantTechnique { ... }
- attribute nomAttribut : TypeAttribut = valeur;
- port nomPort : TypeProtocole [direction];
- connect partA.portOut to partB.portIn;
- allocation NomLogique to NomTechnique;

=== STRUCTURE ATTENDUE ===
```sysml
package '{SystemName} - Technical' {
    // Composants techniques
    part def {TechnicalComponent1} {
        doc /* Description et composant logique réalisé */
        
        // Attributs techniques
        attribute fabricant : String = "NomFabricant";
        attribute modele : String = "Reference";
        attribute tension : Real = 5.0 [V];
        attribute masse : Real = 0.1 [kg];
        
        // Ports physiques
        port {port1} : {ProtocolePhysique} [in];
        port {port2} : {ProtocolePhysique} [out];
    }
    
    // Architecture physique
    part {SystemName}_Physical {
        part {comp1} : {TechnicalComponent1};
        part {comp2} : {TechnicalComponent2};
        
        // Connexions physiques
        connect {comp1}.{port2} to {comp2}.{port1};
    }
    
    // Allocations logique → technique
    allocation {LogicalComponent} to {TechnicalComponent1};
}
```

=== EXEMPLE ===
```sysml
package '{SystemName} - Technical' {
    part def {NomComposantTechnique} {
        doc /* Réalise le composant logique {NomComposantLogique} */
        
        port {port_entree} : {ProtocoleDecritParUtilisateur} [in];
        port {port_sortie} : {ProtocoleDecritParUtilisateur} [out];
    }
    
    part def {AutreComposantTechnique} {
        doc /* Réalise le composant logique {AutreComposantLogique} */
        
        port {port_entree} : {ProtocoleDecritParUtilisateur} [in];
    }
    
    part {SystemName}_Physical {
        part composant1 : {NomComposantTechnique};
        part composant2 : {AutreComposantTechnique};
        
        connect composant1.{port_sortie} to composant2.{port_entree};
    }
    
    allocation {NomComposantLogique} to {NomComposantTechnique};
    allocation {AutreComposantLogique} to {AutreComposantTechnique};
}
```


=== EXEMPLES DE CODE SysML v2 ===
Exemple 1:
```sysml
package 'Turbojet Stage Analysis' {
	private import Quantities::ScalarQuantityValue;
	private import MeasurementReferences::DimensionOneValue;
	private import ISQ::*;
	
	package 'Thermodynamic Functions' {
	    calc def 'Ideal Gas Law' { in rho; in R_bar; in T;
	    	return p = rho * R_bar * T;
	    }
	    
	    calc def 'Reversible Adiabatic Compression Density' { in rho_1; in p_1; in p_2; in gamma;
	    	return rho_2 = rho_1 * (p_2 / p_1)^(1/gamma);
	    }
	    
	    calc def 'Reversible Adiabatic Compression Temperature' { in T_1; in p_1; in p_2; in gamma;
	    	return T_2 = T_1 * (p_2 / p_1)**((gamma - 1) / gamma);
	    }
	    
	    calc def 'Total Pressure' { in P_static; in rho; in V;
	    	1/2 * rho * V^2 + P_static
	    }
	    
	    // Showing explicit parameter typing
	    calc def 'Total Temperature' { in T_static : TemperatureValue; in Cp : DimensionOneValue; in V : VolumeValue;
	    	return : TemperatureValue = 1/(2 * Cp) * V^2 + T_static;
	    }
	    
	    calc def 'Total Enthalpy' { in h_total; in h_static; in V;
	    	return H_total = 1/2 * V^2 + h_static;
	    }
	}
```

Exemple 2:
```sysml
e path-independent)
	        */
	        action 'Stage 1' :>> start;
	        action 'Stage 2' :>> done;
	    }
	    
	    action def 'Reversible Adiabatic Process' specializes 'Adiabatic Process';
	}
	
	package 'Low-Pressure Compressor Analysis' {
	    
	    part 'Analysis Context' {
	        private import 'Thermodynamic Functions'::*;
	        
	        part 'Inlet Gas' : 'Thermodynamics Structure'::'Moving Ideal Gas Parcel' {
	        	// Explicit binding notation
	        	calc 'Solve for Pressure1' : 'Ideal Gas Law';
	        	bind 'Density' = 'Solve for Pressure1'.rho;
	        	bind 'Specific Gas Constant' = 'Solve for Pressure1'.R_bar;
	        	bind 'Static Temperature' = 'Solve for Pressure1'.T;
	        	bind 'Static Pressure' = 'Solve for Pressure1'.p;	        	
	        	
	        	// Shorthand parameter binding notation
	            calc 'Solve for Pressure2' : 'Ideal Gas Law' {
	                in rho = 'Density';
	                in R_bar = 'Specific Gas Constant';
	                in T = 'Static Temperature';
				}				
				            
	            // Invocation expression notation
	            attribute :>> 'Static Pressure' = 'Ideal Gas Law'('Density', 'Specific Gas Constant', 'Static Temperature');

	            // Equation as a constraint (note "==")
	            constraint { 'Static Pressure' == 'Ideal Gas Law'('Density', 'Specific Gas Constant', 'Static Temperature') }
	        }
	    }
	}	
	
}
```

Exemple 3:
```sysml
alue;
	    	return : TemperatureValue = 1/(2 * Cp) * V^2 + T_static;
	    }
	    
	    calc def 'Total Enthalpy' { in h_total; in h_static; in V;
	    	return H_total = 1/2 * V^2 + h_static;
	    }
	}
	
	package 'Thermodynamics Structure' {
	    part def 'Ideal Gas Parcel' {
	        comment
	            /*
	            The parcel is an infinitesimal volume used to analyze points in a flow
	            */
	        attribute 'Molar Mass';
	        attribute 'Density';
	        attribute 'Pressure';
	        attribute 'Temperature';
	        attribute 'Enthalpy';
	        attribute 'Specific Gas Constant';
	    }
```



=== MODÈLE TECHNIQUE JSON ===
{
  "system_name": "BAS (Bleed Air System)",
  "warnings": [
    "Composant manquant : systeme bas",
    "Composant manquant : turbomachine",
    "Composant manquant : systeme interagit",
    "Composant manquant : entites externes suivantes",
    "Composant manquant : source",
    "Composant manquant : conduit",
    "Composant manquant : nacelle",
    "Composant manquant : degivrage",
    "Composant manquant : systeme pneumatique",
    "Composant manquant : vanne",
    "Composant manquant : frontiere physique en",
    "Composant manquant : systeme realise quatre",
    "Composant manquant : nacelle pour le",
    "Composant manquant : consignes",
    "Composant manquant : systeme possede trois",
    "Composant manquant : pression",
    "Composant manquant : temperature pour envoyer",
    "Composant manquant : cabine",
    "Composant manquant : circuit",
    "Composant manquant : systeme est compose",
    "Composant manquant : pression ip est",
    "Composant manquant : jonction hp",
    "Composant manquant : passage",
    "Composant manquant : consigne",
    "Composant manquant : debit",
    "Composant manquant : calculateur pilote la",
    "Composant manquant : pression cible",
    "Composant manquant : temperature via",
    "Composant manquant : capteurs",
    "Composant manquant : calculateur ouvre la",
    "Composant manquant : naiv",
    "Composant manquant : capteur nai press",
    "Composant manquant : plage",
    "Composant manquant : temps",
    "Composant manquant : boucle",
    "Composant manquant : temperature"
  ],
  "technical_parts": [
    {
      "name": "Calculateur BAS",
      "type": "Calculateur Embarqué",
      "description": "Réalise le composant logique Electronic BAS Control",
      "ports": [
        {
          "name": "in_consignes_avionique",
          "direction": "in",
          "type": "Bus de données (ARINC 429)"
        },
        {
          "name": "in_mesure_pression_nai",
          "direction": "in",
          "type": "Câble électrique (Analogique/CAN)"
        },
        {
          "name": "in_mesure_pression_bleed",
          "direction": "in",
          "type": "Câble électrique (Analogique/CAN)"
        },
        {
          "name": "in_mesure_temperature_bleed",
          "direction": "in",
          "type": "Câble électrique (Analogique/CAN)"
        },
        {
          "name": "out_commande_hpv",
          "direction": "out",
          "type": "Câble électrique (PWM/Discret)"
        },
        {
          "name": "out_commande_prv",
          "direction": "out",
          "type": "Câble électrique (PWM/Discret)"
        },
        {
          "name": "out_commande_fav",
          "direction": "out",
          "type": "Câble électrique (PWM/Discret)"
        },
        {
          "name": "out_commande_naiv",
          "direction": "out",
          "type": "Câble électrique (PWM/Discret)"
        },
        {
          "name": "out_statut_systeme",
          "direction": "out",
          "type": "Bus de données (ARINC 429)"
        }
      ],
      "children": []
    },
    {
      "name": "Port Prélèvement IP Physique",
      "type": "Orifice de Prélèvement",
      "description": "Réalise le composant logique Port Prélèvement IP",
      "ports": [
        {
          "name": "in_air_ip_turbomachine",
          "direction": "in",
          "type": "Conduit d'air (Air Chaud IP)"
        },
        {
          "name": "out_air_ip_preleve",
          "direction": "out",
          "type": "Conduit d'air (Air Chaud IP)"
        }
      ],
      "children": []
    },
    {
      "name": "Port Prélèvement HP Physique",
      "type": "Orifice de Prélèvement",
      "description": "Réalise le composant logique Port Prélèvement HP",
      "ports": [
        {
          "name": "in_air_hp_turbomachine",
          "direction": "in",
          "type": "Conduit d'air (Air Chaud HP)"
        },
        {
          "name": "out_air_hp_vers_hpv",
          "direction": "out",
          "type": "Conduit d'air (Air Chaud HP)"
        }
      ],
      "children": []
    },
    {
      "name": "Vanne HPV Physique",
      "type": "Vanne Pneumatique",
      "description": "Réalise le composant logique Vanne HPV",
      "ports": [
        {
          "name": "in_air_hp_vers_hpv",
          "direction": "in",
          "type": "Conduit d'air (Air Chaud HP)"
        },
        {
          "name": "in_commande_hpv",
          "direction": "in",
          "type": "Câble électrique (Commande)"
        },
        {
          "name": "out_air_hp_preleve",
          "direction": "out",
          "type": "Conduit d'air (Air Chaud HP)"
        }
      ],
      "children": []
    },
    {
      "name": "Clapet Anti-Retour IPCV Physique",
      "type": "Clapet Anti-Retour",
      "description": "Réalise le composant logique Clapet Anti-Retour IPCV",
      "ports": [
        {
          "name": "in_air_ip_preleve",
          "direction": "in",
          "type": "Conduit d'air (Air Chaud IP)"
        },
        {
          "name": "in_air_hp_preleve",
          "direction": "in",
          "type": "Conduit d'air (Air Chaud HP)"
        },
        {
          "name": "out_air_chaud_brut_manifold",
          "direction": "out",
          "type": "Conduit d'air (Air Chaud Brute)"
        }
      ],
      "children": []
    },
    {
      "name": "Vanne NAIV Physique",
      "type": "Vanne Pneumatique",
      "description": "Réalise le composant logique Vanne NAIV",
      "ports": [
        {
          "name": "in_air_chaud_brut_manifold",
          "direction": "in",
          "type": "Conduit d'air (Air Chaud Brute)"
        },
        {
          "name": "in_commande_naiv",
          "direction": "in",
          "type": "Câble électrique (Commande)"
        },
        {
          "name": "out_air_chaud_degivrage_vers_capteur",
          "direction": "out",
          "type": "Conduit d'air (Air Chaud Dégivrage)"
        }
      ],
      "children": []
    },
    {
      "name": "Capteur Pression NAI Physique",
      "type": "Capteur de Pression",
      "description": "Réalise le composant logique NAI Press Sensor",
      "ports": [
        {
          "name": "in_air_chaud_degivrage_vers_capteur",
          "direction": "in",
          "type": "Conduit d'air (Air Chaud Dégivrage)"
        },
        {
          "name": "out_mesure_pression_nai",
          "direction": "out",
          "type": "Câble électrique (Mesure Pression)"
        },
        {
          "name": "out_air_chaud_degivrage_vers_nacelle",
          "direction": "out",
          "type": "Conduit d'air (Air Chaud Dégivrage)"
        }
      ],
      "children": []
    },
    {
      "name": "Vanne PRV Physique",
      "type": "Vanne de Régulation de Pression",
      "description": "Réalise le composant logique Vanne PRV",
      "ports": [
        {
          "name": "in_air_chaud_brut_manifold",
          "direction": "in",
          "type": "Conduit d'air (Air Chaud Brute)"
        },
        {
          "name": "in_commande_prv",
          "direction": "in",
          "type": "Câble électrique (Commande)"
        },
        {
          "name": "out_air_pres_regule",
          "direction": "out",
          "type": "Conduit d'air (Air Pression Régulée)"
        }
      ],
      "children": []
    },
    {
      "name": "Échangeur Thermique Physique",
      "type": "Échangeur Air-Air",
      "description": "Réalise le composant logique Exchanger",
      "ports": [
        {
          "name": "in_air_pres_regule",
          "direction": "in",
          "type": "Conduit d'air (Air Pression Régulée)"
        },
        {
          "name": "in_air_froid_echangeur",
          "direction": "in",
          "type": "Conduit d'air (Air Froid)"
        },
        {
          "name": "out_air_refroidi",
          "direction": "out",
          "type": "Conduit d'air (Air Refroidi)"
        },
        {
          "name": "out_air_refroidissement_evacue",
          "direction": "out",
          "type": "Conduit d'air (Air de Refroidissement Évacué)"
        }
      ],
      "children": []
    },
    {
      "name": "Vanne FAV Physique",
      "type": "Vanne de Régulation de Débit",
      "description": "Réalise le composant logique Vanne FAV",
      "ports": [
        {
          "name": "in_air_froid_soufflante",
          "direction": "in",
          "type": "Conduit d'air (Air Froid Soufflante)"
        },
        {
          "name": "in_commande_fav",
          "direction": "in",
          "type": "Câble électrique (Commande)"
        },
        {
          "name": "out_air_froid_echangeur",
          "direction": "out",
          "type": "Conduit d'air (Air Froid Régulé)"
        }
      ],
      "children": []
    },
    {
      "name": "Filtre Air Physique",
      "type": "Filtre Pneumatique",
      "description": "Réalise le composant logique Filter",
      "ports": [
        {
          "name": "in_air_refroidi",
          "direction": "in",
          "type": "Conduit d'air (Air Refroidi)"
        },
        {
          "name": "out_air_conditionne_filtre",
          "direction": "out",
          "type": "Conduit d'air (Air Conditionné Filtré)"
        }
      ],
      "children": []
    },
    {
      "name": "Capteur Pression Bleed Physique",
      "type": "Capteur de Pression",
      "description": "Réalise le composant logique Bleed Press Sensor",
      "ports": [
        {
          "name": "in_air_conditionne_filtre",
          "direction": "in",
          "type": "Conduit d'air (Air Conditionné Filtré)"
        },
        {
          "name": "out_mesure_pression_bleed",
          "direction": "out",
          "type": "Câble électrique (Mesure Pression)"
        }
      ],
      "children": []
    },
    {
      "name": "Capteur Température Bleed Physique",
      "type": "Capteur de Température",
      "description": "Réalise le composant logique Bleed Temp Sensor",
      "ports": [
        {
          "name": "in_air_conditionne_filtre",
          "direction": "in",
          "type": "Conduit d'air (Air Conditionné Filtré)"
        },
        {
          "name": "out_mesure_temperature_bleed",
          "direction": "out",
          "type": "Câble électrique (Mesure Température)"
        }
      ],
      "children": []
    }
  ],
  "physical_connections": [
    {
      "from_port": "Port Prélèvement IP Physique.out_air_ip_preleve",
      "to_port": "Clapet Anti-Retour IPCV Physique.in_air_ip_preleve",
      "type": "connection",
      "item": "Conduit d'air",
      "description": "Flux d'air IP vers le clapet anti-retour."
    },
    {
      "from_port": "Port Prélèvement HP Physique.out_air_hp_vers_hpv",
      "to_port": "Vanne HPV Physique.in_air_hp_vers_hpv",
      "type": "connection",
      "item": "Conduit d'air",
      "description": "Flux d'air HP vers la vanne HPV."
    },
    {
      "from_port": "Vanne HPV Physique.out_air_hp_preleve",
      "to_port": "Clapet Anti-Retour IPCV Physique.in_air_hp_preleve",
      "type": "connection",
      "item": "Conduit d'air",
      "description": "Flux d'air HP de la vanne HPV vers le clapet anti-retour."
    },
    {
      "from_port": "Clapet Anti-Retour IPCV Physique.out_air_chaud_brut_manifold",
      "to_port": "Vanne PRV Physique.in_air_chaud_brut_manifold",
      "type": "connection",
      "item": "Conduit d'air",
      "description": "Flux d'air prélevé de la turbomachine, avant régulation de pression et température, vers la vanne PRV."
    },
    {
      "from_port": "Clapet Anti-Retour IPCV Physique.out_air_chaud_brut_manifold",
      "to_port": "Vanne NAIV Physique.in_air_chaud_brut_manifold",
      "type": "connection",
      "item": "Conduit d'air",
      "description": "Flux d'air prélevé de la turbomachine, utilisé pour le dégivrage nacelle, vers la vanne NAIV."
    },
    {
      "from_port": "Vanne PRV Physique.out_air_pres_regule",
      "to_port": "Échangeur Thermique Physique.in_air_pres_regule",
      "type": "connection",
      "item": "Conduit d'air",
      "description": "Flux d'air régulé en pression vers l'échangeur thermique."
    },
    {
      "from_port": "Vanne FAV Physique.out_air_froid_echangeur",
      "to_port": "Échangeur Thermique Physique.in_air_froid_echangeur",
      "type": "connection",
      "item": "Conduit d'air",
      "description": "Flux d'air froid régulé vers l'échangeur thermique."
    },
    {
      "from_port": "Échangeur Thermique Physique.out_air_refroidi",
      "to_port": "Filtre Air Physique.in_air_refroidi",
      "type": "connection",
      "item": "Conduit d'air",
      "description": "Flux d'air refroidi de l'échangeur vers le filtre."
    },
    {
      "from_port": "Filtre Air Physique.out_air_conditionne_filtre",
      "to_port": "Capteur Pression Bleed Physique.in_air_conditionne_filtre",
      "type": "connection",
      "item": "Conduit d'air",
      "description": "Flux d'air conditionné régulé vers le capteur de pression de sortie."
    },
    {
      "from_port": "Filtre Air Physique.out_air_conditionne_filtre",
      "to_port": "Capteur Température Bleed Physique.in_air_conditionne_filtre",
      "type": "connection",
      "item": "Conduit d'air",
      "description": "Flux d'air conditionné régulé vers le capteur de température de sortie."
    },
    {
      "from_port": "Vanne NAIV Physique.out_air_chaud_degivrage_vers_capteur",
      "to_port": "Capteur Pression NAI Physique.in_air_chaud_degivrage_vers_capteur",
      "type": "connection",
      "item": "Conduit d'air",
      "description": "Flux d'air chaud dirigé vers la nacelle pour le dégivrage, avant mesure de pression NAI."
    },
    {
      "from_port": "Calculateur BAS.out_commande_hpv",
      "to_port": "Vanne HPV Physique.in_commande_hpv",
      "type": "connection",
      "item": "Câble électrique",
      "description": "Signal de commande du calculateur pour la vanne HPV."
    },
    {
      "from_port": "Calculateur BAS.out_commande_prv",
      "to_port": "Vanne PRV Physique.in_commande_prv",
      "type": "connection",
      "item": "Câble électrique",
      "description": "Signal de commande du calculateur pour la vanne PRV."
    },
    {
      "from_port": "Calculateur BAS.out_commande_fav",
      "to_port": "Vanne FAV Physique.in_commande_fav",
      "type": "connection",
      "item": "Câble électrique",
      "description": "Signal de commande du calculateur pour la vanne FAV."
    },
    {
      "from_port": "Calculateur BAS.out_commande_naiv",
      "to_port": "Vanne NAIV Physique.in_commande_naiv",
      "type": "connection",
      "item": "Câble électrique",
      "description": "Signal de commande du calculateur pour la vanne NAIV."
    },
    {
      "from_port": "Capteur Pression NAI Physique.out_mesure_pression_nai",
      "to_port": "Calculateur BAS.in_mesure_pression_nai",
      "type": "connection",
      "item": "Câble électrique",
      "description": "Mesure de la pression de l'air de dégivrage transmise au calculateur."
    },
    {
      "from_port": "Capteur Pression Bleed Physique.out_mesure_pression_bleed",
      "to_port": "Calculateur BAS.in_mesure_pression_bleed",
      "type": "connection",
      "item": "Câble électrique",
      "description": "Mesure de la pression de l'air conditionné en sortie transmise au calculateur."
    },
    {
      "from_port": "Capteur Température Bleed Physique.out_mesure_temperature_bleed",
      "to_port": "Calculateur BAS.in_mesure_temperature_bleed",
      "type": "connection",
      "item": "Câble électrique",
      "description": "Mesure de la température de l'air conditionné en sortie transmise au calculateur."
    }
  ],
  "technology_choices": [
    {
      "component": "Electronic BAS Control",
      "technology": "Calculateur BAS",
      "justification": "Décrit par l'utilisateur"
    },
    {
      "component": "Port Prélèvement IP",
      "technology": "Port Prélèvement IP Physique",
      "justification": "Décrit par l'utilisateur"
    },
    {
      "component": "Port Prélèvement HP",
      "technology": "Port Prélèvement HP Physique",
      "justification": "Décrit par l'utilisateur"
    },
    {
      "component": "Vanne HPV",
      "technology": "Vanne HPV Physique",
      "justification": "Décrit par l'utilisateur"
    },
    {
      "component": "Clapet Anti-Retour IPCV",
      "technology": "Clapet Anti-Retour IPCV Physique",
      "justification": "Décrit par l'utilisateur"
    },
    {
      "component": "Vanne NAIV",
      "technology": "Vanne NAIV Physique",
      "justification": "Décrit par l'utilisateur"
    },
    {
      "component": "NAI Press Sensor",
      "technology": "Capteur Pression NAI Physique",
      "justification": "Décrit par l'utilisateur"
    },
    {
      "component": "Vanne PRV",
      "technology": "Vanne PRV Physique",
      "justification": "Décrit par l'utilisateur"
    },
    {
      "component": "Exchanger",
      "technology": "Échangeur Thermique Physique",
      "justification": "Décrit par l'utilisateur"
    },
    {
      "component": "Vanne FAV",
      "technology": "Vanne FAV Physique",
      "justification": "Décrit par l'utilisateur"
    },
    {
      "component": "Filter",
      "technology": "Filtre Air Physique",
      "justification": "Décrit par l'utilisateur"
    },
    {
      "component": "Bleed Press Sensor",
      "technology": "Capteur Pression Bleed Physique",
      "justification": "Décrit par l'utilisateur"
    },
    {
      "component": "Bleed Temp Sensor",
      "technology": "Capteur Température Bleed Physique",
      "justification": "Décrit par l'utilisateur"
    }
  ]
}

=== TON RÉSULTAT (CODE SysML v2 UNIQUEMENT, SANS COMMENTAIRE) ===
```

### Réponse brute du LLM

```
```sysml
package 'BAS (Bleed Air System) - Technical' {
    // Composants techniques
    part def 'Calculateur BAS' {
        doc /* Réalise le composant logique Electronic BAS Control */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute tension : Real = 28.0 [V]; // Exemple de valeur
        attribute masse : Real = 1.5 [kg]; // Exemple de valeur
        
        // Ports physiques
        port in_consignes_avionique : 'Bus de données (ARINC 429)' [in];
        port in_mesure_pression_nai : 'Câble électrique (Analogique/CAN)' [in];
        port in_mesure_pression_bleed : 'Câble électrique (Analogique/CAN)' [in];
        port in_mesure_temperature_bleed : 'Câble électrique (Analogique/CAN)' [in];
        port out_commande_hpv : 'Câble électrique (PWM/Discret)' [out];
        port out_commande_prv : 'Câble électrique (PWM/Discret)' [out];
        port out_commande_fav : 'Câble électrique (PWM/Discret)' [out];
        port out_commande_naiv : 'Câble électrique (PWM/Discret)' [out];
        port out_statut_systeme : 'Bus de données (ARINC 429)' [out];
    }
    
    part def 'Port Prélèvement IP Physique' {
        doc /* Réalise le composant logique Port Prélèvement IP */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute diametre : Real = 0.05 [m]; // Exemple de valeur
        attribute materiau : String = "Inconnu";
        
        // Ports physiques
        port in_air_ip_turbomachine : 'Conduit d\'air (Air Chaud IP)' [in];
        port out_air_ip_preleve : 'Conduit d\'air (Air Chaud IP)' [out];
    }
    
    part def 'Port Prélèvement HP Physique' {
        doc /* Réalise le composant logique Port Prélèvement HP */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute diametre : Real = 0.03 [m]; // Exemple de valeur
        attribute materiau : String = "Inconnu";
        
        // Ports physiques
        port in_air_hp_turbomachine : 'Conduit d\'air (Air Chaud HP)' [in];
        port out_air_hp_vers_hpv : 'Conduit d\'air (Air Chaud HP)' [out];
    }
    
    part def 'Vanne HPV Physique' {
        doc /* Réalise le composant logique Vanne HPV */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute tension : Real = 28.0 [V];
        attribute masse : Real = 0.8 [kg];
        
        // Ports physiques
        port in_air_hp_vers_hpv : 'Conduit d\'air (Air Chaud HP)' [in];
        port in_commande_hpv : 'Câble électrique (Commande)' [in];
        port out_air_hp_preleve : 'Conduit d\'air (Air Chaud HP)' [out];
    }
    
    part def 'Clapet Anti-Retour IPCV Physique' {
        doc /* Réalise le composant logique Clapet Anti-Retour IPCV */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute masse : Real = 0.3 [kg];
        attribute diametre_nominal : Real = 0.06 [m];
        
        // Ports physiques
        port in_air_ip_preleve : 'Conduit d\'air (Air Chaud IP)' [in];
        port in_air_hp_preleve : 'Conduit d\'air (Air Chaud HP)' [in];
        port out_air_chaud_brut_manifold : 'Conduit d\'air (Air Chaud Brute)' [out];
    }
    
    part def 'Vanne NAIV Physique' {
        doc /* Réalise le composant logique Vanne NAIV */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute tension : Real = 28.0 [V];
        attribute masse : Real = 0.7 [kg];
        
        // Ports physiques
        port in_air_chaud_brut_manifold : 'Conduit d\'air (Air Chaud Brute)' [in];
        port in_commande_naiv : 'Câble électrique (Commande)' [in];
        port out_air_chaud_degivrage_vers_capteur : 'Conduit d\'air (Air Chaud Dégivrage)' [out];
    }
    
    part def 'Capteur Pression NAI Physique' {
        doc /* Réalise le composant logique NAI Press Sensor */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute tension : Real = 5.0 [V];
        attribute masse : Real = 0.1 [kg];
        
        // Ports physiques
        port in_air_chaud_degivrage_vers_capteur : 'Conduit d\'air (Air Chaud Dégivrage)' [in];
        port out_mesure_pression_nai : 'Câble électrique (Mesure Pression)' [out];
        port out_air_chaud_degivrage_vers_nacelle : 'Conduit d\'air (Air Chaud Dégivrage)' [out];
    }
    
    part def 'Vanne PRV Physique' {
        doc /* Réalise le composant logique Vanne PRV */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute tension : Real = 28.0 [V];
        attribute masse : Real = 1.2 [kg];
        
        // Ports physiques
        port in_air_chaud_brut_manifold : 'Conduit d\'air (Air Chaud Brute)' [in];
        port in_commande_prv : 'Câble électrique (Commande)' [in];
        port out_air_pres_regule : 'Conduit d\'air (Air Pression Régulée)' [out];
    }
    
    part def 'Échangeur Thermique Physique' {
        doc /* Réalise le composant logique Exchanger */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute masse : Real = 5.0 [kg];
        attribute surface_echange : Real = 0.5 [m^2];
        
        // Ports physiques
        port in_air_pres_regule : 'Conduit d\'air (Air Pression Régulée)' [in];
        port in_air_froid_echangeur : 'Conduit d\'air (Air Froid)' [in];
        port out_air_refroidi : 'Conduit d\'air (Air Refroidi)' [out];
        port out_air_refroidissement_evacue : 'Conduit d\'air (Air de Refroidissement Évacué)' [out];
    }
    
    part def 'Vanne FAV Physique' {
        doc /* Réalise le composant logique Vanne FAV */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute tension : Real = 28.0 [V];
        attribute masse : Real = 0.6 [kg];
        
        // Ports physiques
        port in_air_froid_soufflante : 'Conduit d\'air (Air Froid Soufflante)' [in];
        port in_commande_fav : 'Câble électrique (Commande)' [in];
        port out_air_froid_echangeur : 'Conduit d\'air (Air Froid Régulé)' [out];
    }
    
    part def 'Filtre Air Physique' {
        doc /* Réalise le composant logique Filter */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute masse : Real = 0.4 [kg];
        attribute finesse_filtration : Real = 5.0 [µm];
        
        // Ports physiques
        port in_air_refroidi : 'Conduit d\'air (Air Refroidi)' [in];
        port out_air_conditionne_filtre : 'Conduit d\'air (Air Conditionné Filtré)' [out];
    }
    
    part def 'Capteur Pression Bleed Physique' {
        doc /* Réalise le composant logique Bleed Press Sensor */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute tension : Real = 5.0 [V];
        attribute masse : Real = 0.1 [kg];
        
        // Ports physiques
        port in_air_conditionne_filtre : 'Conduit d\'air (Air Conditionné Filtré)' [in];
        port out_mesure_pression_bleed : 'Câble électrique (Mesure Pression)' [out];
    }
    
    part def 'Capteur Température Bleed Physique' {
        doc /* Réalise le composant logique Bleed Temp Sensor */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute tension : Real = 5.0 [V];
        attribute masse : Real = 0.05 [kg];
        
        // Ports physiques
        port in_air_conditionne_filtre : 'Conduit d\'air (Air Conditionné Filtré)' [in];
        port out_mesure_temperature_bleed : 'Câble électrique (Mesure Température)' [out];
    }
    
    // Architecture physique
    part 'BAS (Bleed Air System)_Physical' {
        part calculateurBas : 'Calculateur BAS';
        part portPrelevementIpPhysique : 'Port Prélèvement IP Physique';
        part portPrelevementHpPhysique : 'Port Prélèvement HP Physique';
        part vanneHpvPhysique : 'Vanne HPV Physique';
        part clapetAntiRetourIpcvPhysique : 'Clapet Anti-Retour IPCV Physique';
        part vanneNaivPhysique : 'Vanne NAIV Physique';
        part capteurPressionNaiPhysique : 'Capteur Pression NAI Physique';
        part vannePrvPhysique : 'Vanne PRV Physique';
        part echangeurThermiquePhysique : 'Échangeur Thermique Physique';
        part vanneFavPhysique : 'Vanne FAV Physique';
        part filtreAirPhysique : 'Filtre Air Physique';
        part capteurPressionBleedPhysique : 'Capteur Pression Bleed Physique';
        part capteurTemperatureBleedPhysique : 'Capteur Température Bleed Physique';
        
        // Connexions physiques
        connect portPrelevementIpPhysique.out_air_ip_preleve to clapetAntiRetourIpcvPhysique.in_air_ip_preleve;
        connect portPrelevementHpPhysique.out_air_hp_vers_hpv to vanneHpvPhysique.in_air_hp_vers_hpv;
        connect vanneHpvPhysique.out_air_hp_preleve to clapetAntiRetourIpcvPhysique.in_air_hp_preleve;
        connect clapetAntiRetourIpcvPhysique.out_air_chaud_brut_manifold to vannePrvPhysique.in_air_chaud_brut_manifold;
        connect clapetAntiRetourIpcvPhysique.out_air_chaud_brut_manifold to vanneNaivPhysique.in_air_chaud_brut_manifold;
        connect vannePrvPhysique.out_air_pres_regule to echangeurThermiquePhysique.in_air_pres_regule;
        connect vanneFavPhysique.out_air_froid_echangeur to echangeurThermiquePhysique.in_air_froid_echangeur;
        connect echangeurThermiquePhysique.out_air_refroidi to filtreAirPhysique.in_air_refroidi;
        connect filtreAirPhysique.out_air_conditionne_filtre to capteurPressionBleedPhysique.in_air_conditionne_filtre;
        connect filtreAirPhysique.out_air_conditionne_filtre to capteurTemperatureBleedPhysique.in_air_conditionne_filtre;
        connect vanneNaivPhysique.out_air_chaud_degivrage_vers_capteur to capteurPressionNaiPhysique.in_air_chaud_degivrage_vers_capteur;
        connect calculateurBas.out_commande_hpv to vanneHpvPhysique.in_commande_hpv;
        connect calculateurBas.out_commande_prv to vannePrvPhysique.in_commande_prv;
        connect calculateurBas.out_commande_fav to vanneFavPhysique.in_commande_fav;
        connect calculateurBas.out_commande_naiv to vanneNaivPhysique.in_commande_naiv;
        connect capteurPressionNaiPhysique.out_mesure_pression_nai to calculateurBas.in_mesure_pression_nai;
        connect capteurPressionBleedPhysique.out_mesure_pression_bleed to calculateurBas.in_mesure_pression_bleed;
        connect capteurTemperatureBleedPhysique.out_mesure_temperature_bleed to calculateurBas.in_mesure_temperature_bleed;
    }
    
    // Allocations logique → technique
    allocation 'Electronic BAS Control' to 'Calculateur BAS';
    allocation 'Port Prélèvement IP' to 'Port Prélèvement IP Physique';
    allocation 'Port Prélèvement HP' to 'Port Prélèvement HP Physique';
    allocation 'Vanne HPV' to 'Vanne HPV Physique';
    allocation 'Clapet Anti-Retour IPCV' to 'Clapet Anti-Retour IPCV Physique';
    allocation 'Vanne NAIV' to 'Vanne NAIV Physique';
    allocation 'NAI Press Sensor' to 'Capteur Pression NAI Physique';
    allocation 'Vanne PRV' to 'Vanne PRV Physique';
    allocation 'Exchanger' to 'Échangeur Thermique Physique';
    allocation 'Vanne FAV' to 'Vanne FAV Physique';
    allocation 'Filter' to 'Filtre Air Physique';
    allocation 'Bleed Press Sensor' to 'Capteur Pression Bleed Physique';
    allocation 'Bleed Temp Sensor' to 'Capteur Température Bleed Physique';
}
```
```

### Code SysML v2 généré

```sysml
package 'BAS (Bleed Air System) - Technical' {
    // Composants techniques
    part def 'Calculateur BAS' {
        doc /* Réalise le composant logique Electronic BAS Control */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute tension : Real = 28.0 [V]; // Exemple de valeur
        attribute masse : Real = 1.5 [kg]; // Exemple de valeur
        
        // Ports physiques
        port in_consignes_avionique : 'Bus de données (ARINC 429)' [in];
        port in_mesure_pression_nai : 'Câble électrique (Analogique/CAN)' [in];
        port in_mesure_pression_bleed : 'Câble électrique (Analogique/CAN)' [in];
        port in_mesure_temperature_bleed : 'Câble électrique (Analogique/CAN)' [in];
        port out_commande_hpv : 'Câble électrique (PWM/Discret)' [out];
        port out_commande_prv : 'Câble électrique (PWM/Discret)' [out];
        port out_commande_fav : 'Câble électrique (PWM/Discret)' [out];
        port out_commande_naiv : 'Câble électrique (PWM/Discret)' [out];
        port out_statut_systeme : 'Bus de données (ARINC 429)' [out];
    }
    
    part def 'Port Prélèvement IP Physique' {
        doc /* Réalise le composant logique Port Prélèvement IP */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute diametre : Real = 0.05 [m]; // Exemple de valeur
        attribute materiau : String = "Inconnu";
        
        // Ports physiques
        port in_air_ip_turbomachine : 'Conduit d\'air (Air Chaud IP)' [in];
        port out_air_ip_preleve : 'Conduit d\'air (Air Chaud IP)' [out];
    }
    
    part def 'Port Prélèvement HP Physique' {
        doc /* Réalise le composant logique Port Prélèvement HP */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute diametre : Real = 0.03 [m]; // Exemple de valeur
        attribute materiau : String = "Inconnu";
        
        // Ports physiques
        port in_air_hp_turbomachine : 'Conduit d\'air (Air Chaud HP)' [in];
        port out_air_hp_vers_hpv : 'Conduit d\'air (Air Chaud HP)' [out];
    }
    
    part def 'Vanne HPV Physique' {
        doc /* Réalise le composant logique Vanne HPV */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute tension : Real = 28.0 [V];
        attribute masse : Real = 0.8 [kg];
        
        // Ports physiques
        port in_air_hp_vers_hpv : 'Conduit d\'air (Air Chaud HP)' [in];
        port in_commande_hpv : 'Câble électrique (Commande)' [in];
        port out_air_hp_preleve : 'Conduit d\'air (Air Chaud HP)' [out];
    }
    
    part def 'Clapet Anti-Retour IPCV Physique' {
        doc /* Réalise le composant logique Clapet Anti-Retour IPCV */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute masse : Real = 0.3 [kg];
        attribute diametre_nominal : Real = 0.06 [m];
        
        // Ports physiques
        port in_air_ip_preleve : 'Conduit d\'air (Air Chaud IP)' [in];
        port in_air_hp_preleve : 'Conduit d\'air (Air Chaud HP)' [in];
        port out_air_chaud_brut_manifold : 'Conduit d\'air (Air Chaud Brute)' [out];
    }
    
    part def 'Vanne NAIV Physique' {
        doc /* Réalise le composant logique Vanne NAIV */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute tension : Real = 28.0 [V];
        attribute masse : Real = 0.7 [kg];
        
        // Ports physiques
        port in_air_chaud_brut_manifold : 'Conduit d\'air (Air Chaud Brute)' [in];
        port in_commande_naiv : 'Câble électrique (Commande)' [in];
        port out_air_chaud_degivrage_vers_capteur : 'Conduit d\'air (Air Chaud Dégivrage)' [out];
    }
    
    part def 'Capteur Pression NAI Physique' {
        doc /* Réalise le composant logique NAI Press Sensor */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute tension : Real = 5.0 [V];
        attribute masse : Real = 0.1 [kg];
        
        // Ports physiques
        port in_air_chaud_degivrage_vers_capteur : 'Conduit d\'air (Air Chaud Dégivrage)' [in];
        port out_mesure_pression_nai : 'Câble électrique (Mesure Pression)' [out];
        port out_air_chaud_degivrage_vers_nacelle : 'Conduit d\'air (Air Chaud Dégivrage)' [out];
    }
    
    part def 'Vanne PRV Physique' {
        doc /* Réalise le composant logique Vanne PRV */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute tension : Real = 28.0 [V];
        attribute masse : Real = 1.2 [kg];
        
        // Ports physiques
        port in_air_chaud_brut_manifold : 'Conduit d\'air (Air Chaud Brute)' [in];
        port in_commande_prv : 'Câble électrique (Commande)' [in];
        port out_air_pres_regule : 'Conduit d\'air (Air Pression Régulée)' [out];
    }
    
    part def 'Échangeur Thermique Physique' {
        doc /* Réalise le composant logique Exchanger */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute masse : Real = 5.0 [kg];
        attribute surface_echange : Real = 0.5 [m^2];
        
        // Ports physiques
        port in_air_pres_regule : 'Conduit d\'air (Air Pression Régulée)' [in];
        port in_air_froid_echangeur : 'Conduit d\'air (Air Froid)' [in];
        port out_air_refroidi : 'Conduit d\'air (Air Refroidi)' [out];
        port out_air_refroidissement_evacue : 'Conduit d\'air (Air de Refroidissement Évacué)' [out];
    }
    
    part def 'Vanne FAV Physique' {
        doc /* Réalise le composant logique Vanne FAV */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute tension : Real = 28.0 [V];
        attribute masse : Real = 0.6 [kg];
        
        // Ports physiques
        port in_air_froid_soufflante : 'Conduit d\'air (Air Froid Soufflante)' [in];
        port in_commande_fav : 'Câble électrique (Commande)' [in];
        port out_air_froid_echangeur : 'Conduit d\'air (Air Froid Régulé)' [out];
    }
    
    part def 'Filtre Air Physique' {
        doc /* Réalise le composant logique Filter */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute masse : Real = 0.4 [kg];
        attribute finesse_filtration : Real = 5.0 [µm];
        
        // Ports physiques
        port in_air_refroidi : 'Conduit d\'air (Air Refroidi)' [in];
        port out_air_conditionne_filtre : 'Conduit d\'air (Air Conditionné Filtré)' [out];
    }
    
    part def 'Capteur Pression Bleed Physique' {
        doc /* Réalise le composant logique Bleed Press Sensor */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute tension : Real = 5.0 [V];
        attribute masse : Real = 0.1 [kg];
        
        // Ports physiques
        port in_air_conditionne_filtre : 'Conduit d\'air (Air Conditionné Filtré)' [in];
        port out_mesure_pression_bleed : 'Câble électrique (Mesure Pression)' [out];
    }
    
    part def 'Capteur Température Bleed Physique' {
        doc /* Réalise le composant logique Bleed Temp Sensor */
        
        // Attributs techniques
        attribute fabricant : String = "Non spécifié";
        attribute modele : String = "Non spécifié";
        attribute tension : Real = 5.0 [V];
        attribute masse : Real = 0.05 [kg];
        
        // Ports physiques
        port in_air_conditionne_filtre : 'Conduit d\'air (Air Conditionné Filtré)' [in];
        port out_mesure_temperature_bleed : 'Câble électrique (Mesure Température)' [out];
    }
    
    // Architecture physique
    part 'BAS (Bleed Air System)_Physical' {
        part calculateurBas : 'Calculateur BAS';
        part portPrelevementIpPhysique : 'Port Prélèvement IP Physique';
        part portPrelevementHpPhysique : 'Port Prélèvement HP Physique';
        part vanneHpvPhysique : 'Vanne HPV Physique';
        part clapetAntiRetourIpcvPhysique : 'Clapet Anti-Retour IPCV Physique';
        part vanneNaivPhysique : 'Vanne NAIV Physique';
        part capteurPressionNaiPhysique : 'Capteur Pression NAI Physique';
        part vannePrvPhysique : 'Vanne PRV Physique';
        part echangeurThermiquePhysique : 'Échangeur Thermique Physique';
        part vanneFavPhysique : 'Vanne FAV Physique';
        part filtreAirPhysique : 'Filtre Air Physique';
        part capteurPressionBleedPhysique : 'Capteur Pression Bleed Physique';
        part capteurTemperatureBleedPhysique : 'Capteur Température Bleed Physique';
        
        // Connexions physiques
        connect portPrelevementIpPhysique.out_air_ip_preleve to clapetAntiRetourIpcvPhysique.in_air_ip_preleve;
        connect portPrelevementHpPhysique.out_air_hp_vers_hpv to vanneHpvPhysique.in_air_hp_vers_hpv;
        connect vanneHpvPhysique.out_air_hp_preleve to clapetAntiRetourIpcvPhysique.in_air_hp_preleve;
        connect clapetAntiRetourIpcvPhysique.out_air_chaud_brut_manifold to vannePrvPhysique.in_air_chaud_brut_manifold;
        connect clapetAntiRetourIpcvPhysique.out_air_chaud_brut_manifold to vanneNaivPhysique.in_air_chaud_brut_manifold;
        connect vannePrvPhysique.out_air_pres_regule to echangeurThermiquePhysique.in_air_pres_regule;
        connect vanneFavPhysique.out_air_froid_echangeur to echangeurThermiquePhysique.in_air_froid_echangeur;
        connect echangeurThermiquePhysique.out_air_refroidi to filtreAirPhysique.in_air_refroidi;
        connect filtreAirPhysique.out_air_conditionne_filtre to capteurPressionBleedPhysique.in_air_conditionne_filtre;
        connect filtreAirPhysique.out_air_conditionne_filtre to capteurTemperatureBleedPhysique.in_air_conditionne_filtre;
        connect vanneNaivPhysique.out_air_chaud_degivrage_vers_capteur to capteurPressionNaiPhysique.in_air_chaud_degivrage_vers_capteur;
        connect calculateurBas.out_commande_hpv to vanneHpvPhysique.in_commande_hpv;
        connect calculateurBas.out_commande_prv to vannePrvPhysique.in_commande_prv;
        connect calculateurBas.out_commande_fav to vanneFavPhysique.in_commande_fav;
        connect calculateurBas.out_commande_naiv to vanneNaivPhysique.in_commande_naiv;
        connect capteurPressionNaiPhysique.out_mesure_pression_nai to calculateurBas.in_mesure_pression_nai;
        connect capteurPressionBleedPhysique.out_mesure_pression_bleed to calculateurBas.in_mesure_pression_bleed;
        connect capteurTemperatureBleedPhysique.out_mesure_temperature_bleed to calculateurBas.in_mesure_temperature_bleed;
    }
    
    // Allocations logique → technique
    allocation 'Electronic BAS Control' to 'Calculateur BAS';
    allocation 'Port Prélèvement IP' to 'Port Prélèvement IP Physique';
    allocation 'Port Prélèvement HP' to 'Port Prélèvement HP Physique';
    allocation 'Vanne HPV' to 'Vanne HPV Physique';
    allocation 'Clapet Anti-Retour IPCV' to 'Clapet Anti-Retour IPCV Physique';
    allocation 'Vanne NAIV' to 'Vanne NAIV Physique';
    allocation 'NAI Press Sensor' to 'Capteur Pression NAI Physique';
    allocation 'Vanne PRV' to 'Vanne PRV Physique';
    allocation 'Exchanger' to 'Échangeur Thermique Physique';
    allocation 'Vanne FAV' to 'Vanne FAV Physique';
    allocation 'Filter' to 'Filtre Air Physique';
    allocation 'Bleed Press Sensor' to 'Capteur Pression Bleed Physique';
    allocation 'Bleed Temp Sensor' to 'Capteur Température Bleed Physique';
}
```
