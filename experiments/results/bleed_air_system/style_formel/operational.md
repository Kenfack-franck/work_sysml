# Niveau Operational — BAS Silvercrest - Formel

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

*2026-02-21T13:16:40.351978*

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



=== MODÈLE OPÉRATIONNEL JSON ===
{
  "system_name": "BAS (Bleed Air System)",
  "description": "Le système BAS (Bleed Air System) est un système de prélèvement et de conditionnement d'air intégré au moteur Silvercrest. Il est intercalé entre la turbomachine et l'avion.",
  "warnings": [],
  "stakeholders": [],
  "external_systems": [
    "L'avionique de l'avion (A/C Avionics)",
    "La turbomachine (cœur du moteur)",
    "Le conduit de soufflante (Fan by-pass duct)",
    "La nacelle",
    "Le système pneumatique de l'avion (A/C Pneumatic System)",
    "La vanne d'isolement de l'avion (SOV - Shut-Off Valve)"
  ],
  "system_boundaries": "Le système BAS est intégré au moteur Silvercrest, positionné entre la turbomachine et l'avion. Il comprend les sous-systèmes de Prélèvement d'air, de Dégivrage Nacelle, de Conditionnement, de Mesure finale et de Contrôle-Commande. La vanne d'isolement de l'avion (SOV) marque la frontière physique en sortie du BAS. Le système interagit avec l'avionique de l'avion, la turbomachine, le conduit de soufflante, la nacelle, et le système pneumatique de l'avion.",
  "use_cases": [
    {
      "name": "Envoyer de l'air régulé en pression et température à l'avion",
      "actors": [
        "L'avionique de l'avion (A/C Avionics)",
        "Le système pneumatique de l'avion (A/C Pneumatic System)"
      ],
      "includes": []
    },
    {
      "name": "Envoyer de l'air chaud à la nacelle pour le dégivrage",
      "actors": [
        "L'avionique de l'avion (A/C Avionics)",
        "La nacelle"
      ],
      "includes": []
    },
    {
      "name": "Déterminer l'état du système par mesures physiques et auto-diagnostic",
      "actors": [
        "L'avionique de l'avion (A/C Avionics)"
      ],
      "includes": []
    },
    {
      "name": "Communiquer les consignes et statuts avec l'avionique",
      "actors": [
        "L'avionique de l'avion (A/C Avionics)"
      ],
      "includes": []
    }
  ],
  "operational_scenarios": [
    {
      "name": "Fourniture d'air nominal",
      "description": "L'avionique envoie les consignes de pression et température au calculateur. L'air est prélevé sur l'IP Port. Le calculateur pilote la PRV pour atteindre la pression cible. Simultanément, le calculateur pilote la FAV pour réguler la température via l'échangeur. Les capteurs de sortie renvoient les mesures au calculateur qui ajuste en boucle fermée. L'air régulé sort vers le système pneumatique de l'avion.",
      "steps": [
        "L'avionique envoie les consignes de pression et température au calculateur.",
        "L'air est prélevé sur l'IP Port.",
        "Le calculateur pilote la PRV pour atteindre la pression cible.",
        "Simultanément, le calculateur pilote la FAV pour réguler la température via l'échangeur.",
        "Les capteurs de sortie renvoient les mesures au calculateur qui ajuste en boucle fermée.",
        "L'air régulé sort vers le système pneumatique de l'avion."
      ]
    },
    {
      "name": "Dégivrage nacelle",
      "description": "L'avionique transmet la commande de dégivrage au calculateur. Le calculateur ouvre la vanne NAIV. L'air chaud haute pression traverse la NAIV, est mesuré par le capteur NAI Press, et sort vers la nacelle. L'état est remonté à l'avionique.",
      "steps": [
        "L'avionique transmet la commande de dégivrage au calculateur.",
        "Le calculateur ouvre la vanne NAIV.",
        "L'air chaud haute pression traverse la NAIV.",
        "L'air est mesuré par le capteur NAI Press.",
        "L'air sort vers la nacelle.",
        "L'état est remonté à l'avionique."
      ]
    }
  ],
  "requirements": [
    {
      "id": "REQ-OP-001",
      "text": "Le système doit fonctionner dans une plage de température de -40°C à +85°C.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-002",
      "text": "Le temps de réponse de la boucle de régulation ne doit pas dépasser 500 millisecondes.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-003",
      "text": "La pression de sortie régulée doit être maintenue entre 20 et 50 PSI.",
      "satisfied_by": null
    },
    {
      "id": "REQ-OP-004",
      "text": "La température de sortie régulée doit être maintenue entre 150°C et 230°C.",
      "satisfied_by": null
    }
  ]
}

=== TON RÉSULTAT (CODE SysML v2 UNIQUEMENT, SANS COMMENTAIRE) ===
```

### Réponse brute du LLM

```
```sysml
package 'BAS (Bleed Air System) - Operational' {
    // Use Cases
    use case def EnvoyerAirReguleAvion {
        doc /* Envoyer de l'air régulé en pression et température à l'avion */
        actor 'L\'avionique de l\'avion (A/C Avionics)';
        actor 'Le système pneumatique de l\'avion (A/C Pneumatic System)';
    }
    
    use case def EnvoyerAirChaudNacelleDegivrage {
        doc /* Envoyer de l'air chaud à la nacelle pour le dégivrage */
        actor 'L\'avionique de l\'avion (A/C Avionics)';
        actor 'La nacelle';
    }
    
    use case def DeterminerEtatSysteme {
        doc /* Déterminer l'état du système par mesures physiques et auto-diagnostic */
        actor 'L\'avionique de l\'avion (A/C Avionics)';
    }
    
    use case def CommuniquerConsignesStatutsAvionique {
        doc /* Communiquer les consignes et statuts avec l'avionique */
        actor 'L\'avionique de l\'avion (A/C Avionics)';
    }
    
    // Exigences opérationnelles
    requirement def REQ_OP_001 {
        doc /* Le système doit fonctionner dans une plage de température de -40°C à +85°C. */
    }
    
    requirement def REQ_OP_002 {
        doc /* Le temps de réponse de la boucle de régulation ne doit pas dépasser 500 millisecondes. */
    }
    
    requirement def REQ_OP_003 {
        doc /* La pression de sortie régulée doit être maintenue entre 20 et 50 PSI. */
    }
    
    requirement def REQ_OP_004 {
        doc /* La température de sortie régulée doit être maintenue entre 150°C et 230°C. */
    }
    
    // Scénarios opérationnels
    action def FournitureAirNominal {
        doc /* L'avionique envoie les consignes de pression et température au calculateur. L'air est prélevé sur l'IP Port. Le calculateur pilote la PRV pour atteindre la pression cible. Simultanément, le calculateur pilote la FAV pour réguler la température via l'échangeur. Les capteurs de sortie renvoient les mesures au calculateur qui ajuste en boucle fermée. L'air régulé sort vers le système pneumatique de l'avion. */
        /*
        1. L'avionique envoie les consignes de pression et température au calculateur.
        2. L'air est prélevé sur l'IP Port.
        3. Le calculateur pilote la PRV pour atteindre la pression cible.
        4. Simultanément, le calculateur pilote la FAV pour réguler la température via l'échangeur.
        5. Les capteurs de sortie renvoient les mesures au calculateur qui ajuste en boucle fermée.
        6. L'air régulé sort vers le système pneumatique de l'avion.
        */
    }
    
    action def DegivrageNacelle {
        doc /* L'avionique transmet la commande de dégivrage au calculateur. Le calculateur ouvre la vanne NAIV. L'air chaud haute pression traverse la NAIV, est mesuré par le capteur NAI Press, et sort vers la nacelle. L'état est remonté à l'avionique. */
        /*
        1. L'avionique transmet la commande de dégivrage au calculateur.
        2. Le calculateur ouvre la vanne NAIV.
        3. L'air chaud haute pression traverse la NAIV.
        4. L'air est mesuré par le capteur NAI Press.
        5. L'air sort vers la nacelle.
        6. L'état est remonté à l'avionique.
        */
    }
}
```
```

### Code SysML v2 généré

```sysml
package 'BAS (Bleed Air System) - Operational' {
    // Use Cases
    use case def EnvoyerAirReguleAvion {
        doc /* Envoyer de l'air régulé en pression et température à l'avion */
        actor 'L\'avionique de l\'avion (A/C Avionics)';
        actor 'Le système pneumatique de l\'avion (A/C Pneumatic System)';
    }
    
    use case def EnvoyerAirChaudNacelleDegivrage {
        doc /* Envoyer de l'air chaud à la nacelle pour le dégivrage */
        actor 'L\'avionique de l\'avion (A/C Avionics)';
        actor 'La nacelle';
    }
    
    use case def DeterminerEtatSysteme {
        doc /* Déterminer l'état du système par mesures physiques et auto-diagnostic */
        actor 'L\'avionique de l\'avion (A/C Avionics)';
    }
    
    use case def CommuniquerConsignesStatutsAvionique {
        doc /* Communiquer les consignes et statuts avec l'avionique */
        actor 'L\'avionique de l\'avion (A/C Avionics)';
    }
    
    // Exigences opérationnelles
    requirement def REQ_OP_001 {
        doc /* Le système doit fonctionner dans une plage de température de -40°C à +85°C. */
    }
    
    requirement def REQ_OP_002 {
        doc /* Le temps de réponse de la boucle de régulation ne doit pas dépasser 500 millisecondes. */
    }
    
    requirement def REQ_OP_003 {
        doc /* La pression de sortie régulée doit être maintenue entre 20 et 50 PSI. */
    }
    
    requirement def REQ_OP_004 {
        doc /* La température de sortie régulée doit être maintenue entre 150°C et 230°C. */
    }
    
    // Scénarios opérationnels
    action def FournitureAirNominal {
        doc /* L'avionique envoie les consignes de pression et température au calculateur. L'air est prélevé sur l'IP Port. Le calculateur pilote la PRV pour atteindre la pression cible. Simultanément, le calculateur pilote la FAV pour réguler la température via l'échangeur. Les capteurs de sortie renvoient les mesures au calculateur qui ajuste en boucle fermée. L'air régulé sort vers le système pneumatique de l'avion. */
        /*
        1. L'avionique envoie les consignes de pression et température au calculateur.
        2. L'air est prélevé sur l'IP Port.
        3. Le calculateur pilote la PRV pour atteindre la pression cible.
        4. Simultanément, le calculateur pilote la FAV pour réguler la température via l'échangeur.
        5. Les capteurs de sortie renvoient les mesures au calculateur qui ajuste en boucle fermée.
        6. L'air régulé sort vers le système pneumatique de l'avion.
        */
    }
    
    action def DegivrageNacelle {
        doc /* L'avionique transmet la commande de dégivrage au calculateur. Le calculateur ouvre la vanne NAIV. L'air chaud haute pression traverse la NAIV, est mesuré par le capteur NAI Press, et sort vers la nacelle. L'état est remonté à l'avionique. */
        /*
        1. L'avionique transmet la commande de dégivrage au calculateur.
        2. Le calculateur ouvre la vanne NAIV.
        3. L'air chaud haute pression traverse la NAIV.
        4. L'air est mesuré par le capteur NAI Press.
        5. L'air sort vers la nacelle.
        6. L'état est remonté à l'avionique.
        */
    }
}
```
