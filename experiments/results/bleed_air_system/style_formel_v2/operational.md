# Niveau Operational — BAS Silvercrest V2

## Prompt envoyé au LLM

```
N/A
```

## Réponse LLM (JSON)

```json
{}
```

## Code SysML v2

```sysml
package 'Bleed Air System (BAS) - Operational' {
    // Use Cases
    use case def PressuriserLesReservoirsDeLAvion {
        doc /* Pressuriser les réservoirs de l'avion */
        actor AC_Avionics;
        actor EECS;
        actor SystemePneumatiqueDeLAvion;
    }
    
    use case def DegivrerLesAiles {
        doc /* Dégivrer les ailes */
        actor AC_Avionics;
        actor EECS;
        actor SystemePneumatiqueDeLAvion;
    }
    
    use case def PressuriserEtTempererLaCabine {
        doc /* Pressuriser et tempérer la cabine */
        actor AC_Avionics;
        actor EECS;
        actor SystemePneumatiqueDeLAvion;
    }
    
    use case def DegivrerLaNacelle {
        doc /* Dégivrer la nacelle */
        actor AC_Avionics;
        actor Nacelle;
    }
    
    use case def EtreInformeDeLEtatDuSysteme {
        doc /* Être informé de l'état du système */
        actor OperateurDeMaintenance;
        actor AC_Avionics;
    }
    
    use case def DiagnostiquerLEtat {
        doc /* Diagnostiquer l'état */
        actor OperateurDeMaintenance;
    }
    
    use case def ReparerSousLAile {
        doc /* Réparer sous l'aile */
        actor OperateurDeMaintenance;
    }
    
    use case def MaintenirEnConditionsOperationnelles {
        doc /* Maintenir en conditions opérationnelles */
        actor OperateurDeMaintenance;
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
    
    requirement def REQ_OP_005 {
        doc /* La maintenabilité du système doit permettre le remplacement d'un LRU en moins de 2 heures par un opérateur qualifié. */
    }
    
    // Scénarios opérationnels
    action def FournitureAirNominal {
        doc /* L'avionique envoie les consignes de pression et température au calculateur. L'air est prélevé sur l'IP Port (flux pneumatique). Le calculateur pilote la PRV (flux électrique : :commande PRV) pour atteindre la pression cible. Simultanément, le calculateur pilote la FAV (flux électrique : :commande FAV) pour réguler la température via l'échangeur. Les capteurs de sortie (bleed press. sensor, bleed temp. sensor) renvoient les mesures (flux information) au calculateur qui ajuste en boucle fermée. L'air régulé sort vers le système pneumatique de l'avion. */
        // Étapes du scénario comme actions ou states
        /* L'avionique envoie les consignes de pression et température au calculateur. */
        /* L'air est prélevé sur l'IP Port. */
        /* Le calculateur pilote la PRV pour atteindre la pression cible. */
        /* Le calculateur pilote la FAV pour réguler la température via l'échangeur. */
        /* Les capteurs de sortie (bleed press. sensor, bleed temp. sensor) renvoient les mesures au calculateur. */
        /* Le calculateur ajuste en boucle fermée. */
        /* L'air régulé sort vers le système pneumatique de l'avion. */
    }
    
    action def DegivrageNacelle {
        doc /* L'avionique transmet la commande de dégivrage au calculateur (flux information). Le calculateur ouvre la vanne NAIV (flux électrique : :commande dégivrage nacelle). L'air chaud haute pression traverse la NAIV (flux pneumatique), passe éventuellement dans l'ACAC pour réguler la température (flux pneumatique + thermique), est mesuré par le capteur NAI Press (flux information : :mesure pression NAI), et sort vers la nacelle (flux pneumatique : :air chaud nacelle). L'état est remonté à l'avionique (flux information : :statut système). */
        // Étapes du scénario comme actions ou states
        /* L'avionique transmet la commande de dégivrage au calculateur. */
        /* Le calculateur ouvre la vanne NAIV. */
        /* L'air chaud haute pression traverse la NAIV. */
        /* L'air passe éventuellement dans l'ACAC pour réguler la température. */
        /* L'air est mesuré par le capteur NAI Press. */
        /* L'air sort vers la nacelle. */
        /* L'état est remonté à l'avionique. */
    }
}
```

## Warnings

