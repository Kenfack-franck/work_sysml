# Niveau Functional — BAS Silvercrest - Formel

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

*2026-02-21T13:17:39.799685*

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



=== MODÈLE FONCTIONNEL JSON ===
{
  "system_name": "BAS (Bleed Air System)",
  "warnings": [],
  "functions": [
    {
      "name": "Gérer le Prélèvement d'Air Chaud",
      "description": "Cette fonction est responsable du prélèvement de l'air chaud depuis la turbomachine (ports IP ou HP), de l'activation de la vanne HPV si la pression IP est insuffisante, et d'assurer le non-refoulement de l'air HP vers l'étage IP. Elle contribue à la fourniture d'air pour l'avion et le dégivrage nacelle.",
      "inputs": [
        "Air Haute Pression (Turbomachine)",
        "Air Intermédiaire Pression (Turbomachine)",
        "Commande HPV"
      ],
      "outputs": [
        "Air Chaud Brute"
      ],
      "sub_functions": [
        "Prélever Air IP",
        "Prélever Air HP",
        "Contrôler Vanne HPV",
        "Empêcher Refoulement IP"
      ]
    },
    {
      "name": "Conditionner l'Air pour l'Avion",
      "description": "Cette fonction régule la pression et la température de l'air prélevé pour qu'il corresponde aux consignes de l'avionique. Elle utilise la vanne PRV pour la pression, l'échangeur thermique et la vanne FAV pour la température, et filtre l'air avant de l'envoyer au système pneumatique de l'avion. Elle couvre le cas d'utilisation 'Envoyer de l'air régulé en pression et température à l'avion'.",
      "inputs": [
        "Air Chaud Brute",
        "Air Froid (Soufflante)",
        "Consigne Pression",
        "Consigne Température",
        "Mesure Pression Sortie",
        "Mesure Température Sortie",
        "Commande PRV",
        "Commande FAV"
      ],
      "outputs": [
        "Air Conditionné Régulé",
        "Air de Refroidissement Évacué"
      ],
      "sub_functions": [
        "Réguler Pression Air",
        "Refroidir Air",
        "Réguler Débit Air Froid",
        "Filtrer Air Conditionné"
      ]
    },
    {
      "name": "Gérer le Dégivrage Nacelle",
      "description": "Cette fonction dirige l'air chaud prélevé vers la nacelle pour le dégivrage, en ouvrant la vanne NAIV sur commande de l'avionique. Elle couvre le cas d'utilisation 'Envoyer de l'air chaud à la nacelle pour le dégivrage'.",
      "inputs": [
        "Air Chaud Brute",
        "Commande NAIV"
      ],
      "outputs": [
        "Air Chaud Dégivrage"
      ],
      "sub_functions": [
        "Contrôler Vanne NAIV"
      ]
    },
    {
      "name": "Mesurer les Paramètres du Système",
      "description": "Cette fonction acquiert les mesures physiques (pression, température) aux points clés du système (dégivrage nacelle, sortie air conditionné) pour le contrôle et le diagnostic. Elle contribue au cas d'utilisation 'Déterminer l'état du système par mesures physiques et auto-diagnostic'.",
      "inputs": [
        "Air Chaud Dégivrage (pour mesure NAI)",
        "Air Conditionné Régulé (pour mesures Bleed)"
      ],
      "outputs": [
        "Mesure Pression NAI",
        "Mesure Pression Bleed",
        "Mesure Température Bleed"
      ],
      "sub_functions": [
        "Mesurer Pression Dégivrage",
        "Mesurer Pression Sortie",
        "Mesurer Température Sortie"
      ]
    },
    {
      "name": "Contrôler et Communiquer",
      "description": "Cette fonction reçoit les consignes de l'avionique, pilote les vannes (HPV, PRV, FAV, NAIV), acquiert les mesures des capteurs, réalise l'auto-diagnostic et transmet les statuts à l'avionique. Elle couvre les cas d'utilisation 'Déterminer l'état du système par mesures physiques et auto-diagnostic' et 'Communiquer les consignes et statuts avec l'avionique'.",
      "inputs": [
        "Consignes Pression/Température (Avionique)",
        "Commande Dégivrage (Avionique)",
        "Mesure Pression NAI",
        "Mesure Pression Bleed",
        "Mesure Température Bleed"
      ],
      "outputs": [
        "Commande HPV",
        "Commande PRV",
        "Commande FAV",
        "Commande NAIV",
        "Statut Système"
      ],
      "sub_functions": [
        "Recevoir Consignes",
        "Piloter Vannes",
        "Acquérir Mesures",
        "Réaliser Auto-diagnostic",
        "Transmettre Statuts"
      ]
    }
  ],
  "functional_flows": [
    {
      "from_function": "Gérer le Prélèvement d'Air Chaud",
      "to_function": "Conditionner l'Air pour l'Avion",
      "item": "Air Chaud Brute",
      "description": "Flux d'air prélevé de la turbomachine, avant régulation de pression et température, vers le sous-système de conditionnement."
    },
    {
      "from_function": "Gérer le Prélèvement d'Air Chaud",
      "to_function": "Gérer le Dégivrage Nacelle",
      "item": "Air Chaud Brute",
      "description": "Flux d'air prélevé de la turbomachine, utilisé pour le dégivrage nacelle."
    },
    {
      "from_function": "Conditionner l'Air pour l'Avion",
      "to_function": "Mesurer les Paramètres du Système",
      "item": "Air Conditionné Régulé",
      "description": "Flux d'air dont la pression et la température sont régulées, avant mesure finale par les capteurs de sortie."
    },
    {
      "from_function": "Conditionner l'Air pour l'Avion",
      "to_function": "A/C Pneumatic System",
      "item": "Air Conditionné Régulé",
      "description": "Flux d'air final régulé en pression et température fourni au système pneumatique de l'avion."
    },
    {
      "from_function": "Gérer le Dégivrage Nacelle",
      "to_function": "Mesurer les Paramètres du Système",
      "item": "Air Chaud Dégivrage",
      "description": "Flux d'air chaud dirigé vers la nacelle pour le dégivrage, avant mesure de pression NAI."
    },
    {
      "from_function": "Gérer le Dégivrage Nacelle",
      "to_function": "La nacelle",
      "item": "Air Chaud Dégivrage",
      "description": "Flux d'air chaud fourni à la nacelle pour le dégivrage."
    },
    {
      "from_function": "Conditionner l'Air pour l'Avion",
      "to_function": "La nacelle",
      "item": "Air de Refroidissement Évacué",
      "description": "Flux d'air froid ayant servi au refroidissement dans l'échangeur, évacué via la nacelle."
    },
    {
      "from_function": "La turbomachine (cœur du moteur)",
      "to_function": "Gérer le Prélèvement d'Air Chaud",
      "item": "Air Haute Pression",
      "description": "Source d'air chaud à haute pression pour le prélèvement."
    },
    {
      "from_function": "La turbomachine (cœur du moteur)",
      "to_function": "Gérer le Prélèvement d'Air Chaud",
      "item": "Air Intermédiaire Pression",
      "description": "Source d'air chaud à pression intermédiaire pour le prélèvement."
    },
    {
      "from_function": "Le conduit de soufflante (Fan by-pass duct)",
      "to_function": "Conditionner l'Air pour l'Avion",
      "item": "Air Froid",
      "description": "Source d'air froid ambiant pour le refroidissement dans l'échangeur."
    },
    {
      "from_function": "L'avionique de l'avion (A/C Avionics)",
      "to_function": "Contrôler et Communiquer",
      "item": "Consignes Pression/Température",
      "description": "Consignes de régulation de pression et température envoyées par l'avionique au calculateur BAS."
    },
    {
      "from_function": "L'avionique de l'avion (A/C Avionics)",
      "to_function": "Contrôler et Communiquer",
      "item": "Commande Dégivrage",
      "description": "Commande d'activation ou de désactivation du dégivrage nacelle envoyée par l'avionique."
    },
    {
      "from_function": "Contrôler et Communiquer",
      "to_function": "L'avionique de l'avion (A/C Avionics)",
      "item": "Statut Système",
      "description": "Informations sur l'état de fonctionnement, les mesures et les diagnostics du BAS transmises à l'avionique."
    },
    {
      "from_function": "Contrôler et Communiquer",
      "to_function": "Gérer le Prélèvement d'Air Chaud",
      "item": "Commande HPV",
      "description": "Signal de commande du calculateur pour la vanne HPV."
    },
    {
      "from_function": "Contrôler et Communiquer",
      "to_function": "Conditionner l'Air pour l'Avion",
      "item": "Commande PRV",
      "description": "Signal de commande du calculateur pour la vanne PRV."
    },
    {
      "from_function": "Contrôler et Communiquer",
      "to_function": "Conditionner l'Air pour l'Avion",
      "item": "Commande FAV",
      "description": "Signal de commande du calculateur pour la vanne FAV."
    },
    {
      "from_function": "Contrôler et Communiquer",
      "to_function": "Gérer le Dégivrage Nacelle",
      "item": "Commande NAIV",
      "description": "Signal de commande du calculateur pour la vanne NAIV."
    },
    {
      "from_function": "Mesurer les Paramètres du Système",
      "to_function": "Contrôler et Communiquer",
      "item": "Mesure Pression NAI",
      "description": "Mesure de la pression de l'air de dégivrage transmise au calculateur."
    },
    {
      "from_function": "Mesurer les Paramètres du Système",
      "to_function": "Contrôler et Communiquer",
      "item": "Mesure Pression Bleed",
      "description": "Mesure de la pression de l'air conditionné en sortie transmise au calculateur."
    },
    {
      "from_function": "Mesurer les Paramètres du Système",
      "to_function": "Contrôler et Communiquer",
      "item": "Mesure Température Bleed",
      "description": "Mesure de la température de l'air conditionné en sortie transmise au calculateur."
    }
  ],
  "modes": [
    {
      "name": "OFF",
      "description": "Le système n'est pas alimenté, aucune vanne n'est active. Le système est inactif.",
      "active_functions": []
    },
    {
      "name": "Stand-by",
      "description": "Le système est alimenté et communique son état à l'avionique, mais les commandes de flux d'air ne sont pas activées. Il est prêt à fonctionner.",
      "active_functions": [
        "Contrôler et Communiquer",
        "Mesurer les Paramètres du Système"
      ]
    },
    {
      "name": "Running",
      "description": "Le système régule activement la pression et la température pour envoyer de l'air à l'avion et/ou ouvre le circuit de dégivrage nacelle selon les besoins opérationnels.",
      "active_functions": [
        "Gérer le Prélèvement d'Air Chaud",
        "Conditionner l'Air pour l'Avion",
        "Gérer le Dégivrage Nacelle",
        "Mesurer les Paramètres du Système",
        "Contrôler et Communiquer"
      ]
    }
  ]
}

=== TON RÉSULTAT (CODE SysML v2 UNIQUEMENT, SANS COMMENTAIRE) ===
```

### Réponse brute du LLM

```
```sysml
package 'BAS (Bleed Air System) - Functional' {
    // Fonctions principales
    action def GérerLePrélèvementD_AirChaud {
        doc /* Cette fonction est responsable du prélèvement de l'air chaud depuis la turbomachine (ports IP ou HP), de l'activation de la vanne HPV si la pression IP est insuffisante, et d'assurer le non-refoulement de l'air HP vers l'étage IP. Elle contribue à la fourniture d'air pour l'avion et le dégivrage nacelle. */
        in airHautePression : AirFlow;
        in airIntermédiairePression : AirFlow;
        in commandeHPV : CommandSignal;
        out airChaudBrute : AirFlow;
        
        action PréleverAirIP { }
        action PréleverAirHP { }
        action ContrôlerVanneHPV { }
        action EmpêcherRefoulementIP { }
    }
    
    action def ConditionnerL_AirPourL_Avion {
        doc /* Cette fonction régule la pression et la température de l'air prélevé pour qu'il corresponde aux consignes de l'avionique. Elle utilise la vanne PRV pour la pression, l'échangeur thermique et la vanne FAV pour la température, et filtre l'air avant de l'envoyer au système pneumatique de l'avion. Elle couvre le cas d'utilisation 'Envoyer de l'air régulé en pression et température à l'avion'. */
        in airChaudBrute : AirFlow;
        in airFroid : AirFlow;
        in consignePression : PressureSetpoint;
        in consigneTempérature : TemperatureSetpoint;
        in mesurePressionSortie : PressureMeasurement;
        in mesureTempératureSortie : TemperatureMeasurement;
        in commandePRV : CommandSignal;
        in commandeFAV : CommandSignal;
        out airConditionnéRégulé : AirFlow;
        out airDeRefroidissementÉvacué : AirFlow;
        
        action RégulerPressionAir { }
        action RefroidirAir { }
        action RégulerDébitAirFroid { }
        action FiltrerAirConditionné { }
    }
    
    action def GérerLeDégivrageNacelle {
        doc /* Cette fonction dirige l'air chaud prélevé vers la nacelle pour le dégivrage, en ouvrant la vanne NAIV sur commande de l'avionique. Elle couvre le cas d'utilisation 'Envoyer de l'air chaud à la nacelle pour le dégivrage'. */
        in airChaudBrute : AirFlow;
        in commandeNAIV : CommandSignal;
        out airChaudDégivrage : AirFlow;
        
        action ContrôlerVanneNAIV { }
    }
    
    action def MesurerLesParamètresDuSystème {
        doc /* Cette fonction acquiert les mesures physiques (pression, température) aux points clés du système (dégivrage nacelle, sortie air conditionné) pour le contrôle et le diagnostic. Elle contribue au cas d'utilisation 'Déterminer l'état du système par mesures physiques et auto-diagnostic'. */
        in airChaudDégivragePourMesureNAI : AirFlow;
        in airConditionnéRéguléPourMesuresBleed : AirFlow;
        out mesurePressionNAI : PressureMeasurement;
        out mesurePressionBleed : PressureMeasurement;
        out mesureTempératureBleed : TemperatureMeasurement;
        
        action MesurerPressionDégivrage { }
        action MesurerPressionSortie { }
        action MesurerTempératureSortie { }
    }
    
    action def ContrôlerEtCommuniquer {
        doc /* Cette fonction reçoit les consignes de l'avionique, pilote les vannes (HPV, PRV, FAV, NAIV), acquiert les mesures des capteurs, réalise l'auto-diagnostic et transmet les statuts à l'avionique. Elle couvre les cas d'utilisation 'Déterminer l'état du système par mesures physiques et auto-diagnostic' et 'Communiquer les consignes et statuts avec l'avionique'. */
        in consignesPressionTempératureAvionique : SetpointValue;
        in commandeDégivrageAvionique : CommandSignal;
        in mesurePressionNAI : PressureMeasurement;
        in mesurePressionBleed : PressureMeasurement;
        in mesureTempératureBleed : TemperatureMeasurement;
        out commandeHPV : CommandSignal;
        out commandePRV : CommandSignal;
        out commandeFAV : CommandSignal;
        out commandeNAIV : CommandSignal;
        out statutSystème : SystemStatus;
        
        action RecevoirConsignes { }
        action PiloterVannes { }
        action AcquérirMesures { }
        action RéaliserAutoDiagnostic { }
        action TransmettreStatuts { }

```

### Code SysML v2 généré

```sysml
package 'BAS (Bleed Air System) - Functional' {
    // Fonctions principales
    action def GérerLePrélèvementD_AirChaud {
        doc /* Cette fonction est responsable du prélèvement de l'air chaud depuis la turbomachine (ports IP ou HP), de l'activation de la vanne HPV si la pression IP est insuffisante, et d'assurer le non-refoulement de l'air HP vers l'étage IP. Elle contribue à la fourniture d'air pour l'avion et le dégivrage nacelle. */
        in airHautePression : AirFlow;
        in airIntermédiairePression : AirFlow;
        in commandeHPV : CommandSignal;
        out airChaudBrute : AirFlow;
        
        action PréleverAirIP { }
        action PréleverAirHP { }
        action ContrôlerVanneHPV { }
        action EmpêcherRefoulementIP { }
    }
    
    action def ConditionnerL_AirPourL_Avion {
        doc /* Cette fonction régule la pression et la température de l'air prélevé pour qu'il corresponde aux consignes de l'avionique. Elle utilise la vanne PRV pour la pression, l'échangeur thermique et la vanne FAV pour la température, et filtre l'air avant de l'envoyer au système pneumatique de l'avion. Elle couvre le cas d'utilisation 'Envoyer de l'air régulé en pression et température à l'avion'. */
        in airChaudBrute : AirFlow;
        in airFroid : AirFlow;
        in consignePression : PressureSetpoint;
        in consigneTempérature : TemperatureSetpoint;
        in mesurePressionSortie : PressureMeasurement;
        in mesureTempératureSortie : TemperatureMeasurement;
        in commandePRV : CommandSignal;
        in commandeFAV : CommandSignal;
        out airConditionnéRégulé : AirFlow;
        out airDeRefroidissementÉvacué : AirFlow;
        
        action RégulerPressionAir { }
        action RefroidirAir { }
        action RégulerDébitAirFroid { }
        action FiltrerAirConditionné { }
    }
    
    action def GérerLeDégivrageNacelle {
        doc /* Cette fonction dirige l'air chaud prélevé vers la nacelle pour le dégivrage, en ouvrant la vanne NAIV sur commande de l'avionique. Elle couvre le cas d'utilisation 'Envoyer de l'air chaud à la nacelle pour le dégivrage'. */
        in airChaudBrute : AirFlow;
        in commandeNAIV : CommandSignal;
        out airChaudDégivrage : AirFlow;
        
        action ContrôlerVanneNAIV { }
    }
    
    action def MesurerLesParamètresDuSystème {
        doc /* Cette fonction acquiert les mesures physiques (pression, température) aux points clés du système (dégivrage nacelle, sortie air conditionné) pour le contrôle et le diagnostic. Elle contribue au cas d'utilisation 'Déterminer l'état du système par mesures physiques et auto-diagnostic'. */
        in airChaudDégivragePourMesureNAI : AirFlow;
        in airConditionnéRéguléPourMesuresBleed : AirFlow;
        out mesurePressionNAI : PressureMeasurement;
        out mesurePressionBleed : PressureMeasurement;
        out mesureTempératureBleed : TemperatureMeasurement;
        
        action MesurerPressionDégivrage { }
        action MesurerPressionSortie { }
        action MesurerTempératureSortie { }
    }
    
    action def ContrôlerEtCommuniquer {
        doc /* Cette fonction reçoit les consignes de l'avionique, pilote les vannes (HPV, PRV, FAV, NAIV), acquiert les mesures des capteurs, réalise l'auto-diagnostic et transmet les statuts à l'avionique. Elle couvre les cas d'utilisation 'Déterminer l'état du système par mesures physiques et auto-diagnostic' et 'Communiquer les consignes et statuts avec l'avionique'. */
        in consignesPressionTempératureAvionique : SetpointValue;
        in commandeDégivrageAvionique : CommandSignal;
        in mesurePressionNAI : PressureMeasurement;
        in mesurePressionBleed : PressureMeasurement;
        in mesureTempératureBleed : TemperatureMeasurement;
        out commandeHPV : CommandSignal;
        out commandePRV : CommandSignal;
        out commandeFAV : CommandSignal;
        out commandeNAIV : CommandSignal;
        out statutSystème : SystemStatus;
        
        action RecevoirConsignes { }
        action PiloterVannes { }
        action AcquérirMesures { }
        action RéaliserAutoDiagnostic { }
        action TransmettreStatuts { }
```
