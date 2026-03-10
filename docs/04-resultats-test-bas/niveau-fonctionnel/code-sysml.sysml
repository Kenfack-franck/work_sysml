// ===== FUNCTIONAL_BREAKDOWN =====

package 'BAS (Bleed Air System) - Functional Breakdown' {

    // Item definitions for flow types
    item def Information;
    item def Pneumatic;
    item def Electric;
    item def Data;

    // Leaf action definitions
    action def PreleveAir {
        doc /* Le port de pression intermédiaire prélève l'air chaud haute pression sur le compresseur du moteur. */
        in airChaudHautePression : Pneumatic;
        out airChaudHautePression : Pneumatic;
    }

    action def LaissePasser {
        doc /* La vanne NAI contrôle le passage de l'air chaud vers la nacelle en fonction de la consigne d'ouverture. */
        in airChaudHautePression : Pneumatic;
        in consigneOuvertureVanne : Electric;
        out airChaudNacelle : Pneumatic;
    }

    action def ReguleTemperatureNacelle {
        doc /* L'échangeur ACAC mélange l'air chaud nacelle avec l'air ambiant pour réguler la température de sortie. */
        in airChaudNacelle : Pneumatic;
        in airAmbiant : Pneumatic;
        out airChaudReguleNacelle : Pneumatic;
        out airTiede : Pneumatic;
    }

    action def ReguleVanneNAI {
        doc /* Le calculateur de régulation reçoit la commande de dégivrage et la mesure de température, et calcule la consigne d'ouverture de la vanne NAI. */
        in commandeDegiveageNacelle : Information;
        in mesureTemperatureAir : Electric;
        out consigneOuvertureVanne : Electric;
    }

    action def MesurerTemperature {
        doc /* Le capteur de température mesure la température de l'air chaud nacelle et transmet la mesure au calculateur. */
        in airChaudNacelle : Pneumatic;
        out mesureTemperatureAir : Electric;
    }

    action def FournirAirInterfaceNacelle {
        doc /* Le port nacelle fournit l'air chaud régulé à l'interface de la nacelle. */
        in airChaudReguleNacelle : Pneumatic;
        out airChaudNacelle : Pneumatic;
    }

    // Composite action with decomposition
    action def EnvoyerAirChaudNacelle {
        doc /* Satisfait le use case 'Dégivrer la nacelle'. */
        in commandeDegiveageNacelle : Information;
        in airChaudHautePression : Pneumatic;
        in airAmbiant : Pneumatic;
        out airChaudNacelle : Pneumatic;
        out airTiede : Pneumatic;

        // Sub-actions
        action preleveAir : PreleveAir {
            in airChaudHautePression;
            out airChaudHautePression;
        }

        action laissePasser : LaissePasser {
            in airChaudHautePression;
            in consigneOuvertureVanne;
            out airChaudNacelle;
        }

        action reguleTemperatureNacelle : ReguleTemperatureNacelle {
            in airChaudNacelle;
            in airAmbiant;
            out airChaudReguleNacelle;
            out airTiede;
        }

        action reguleVanneNAI : ReguleVanneNAI {
            in commandeDegiveageNacelle;
            in mesureTemperatureAir;
            out consigneOuvertureVanne;
        }

        action mesurerTemperature : MesurerTemperature {
            in airChaudNacelle;
            out mesureTemperatureAir;
        }

        action fournirAirInterfaceNacelle : FournirAirInterfaceNacelle {
            in airChaudReguleNacelle;
            out airChaudNacelle;
        }

        // Bindings to parent parameters
        bind preleveAir.airChaudHautePression = airChaudHautePression;
        bind laissePasser.airChaudHautePression = preleveAir.airChaudHautePression;
        bind laissePasser.consigneOuvertureVanne = reguleVanneNAI.consigneOuvertureVanne;
        bind reguleTemperatureNacelle.airChaudNacelle = laissePasser.airChaudNacelle;
        bind reguleTemperatureNacelle.airAmbiant = airAmbiant;
        bind mesurerTemperature.airChaudNacelle = laissePasser.airChaudNacelle;
        bind reguleVanneNAI.commandeDegiveageNacelle = commandeDegiveageNacelle;
        bind reguleVanneNAI.mesureTemperatureAir = mesurerTemperature.mesureTemperatureAir;
        bind fournirAirInterfaceNacelle.airChaudReguleNacelle = reguleTemperatureNacelle.airChaudReguleNacelle;
        bind airChaudNacelle = fournirAirInterfaceNacelle.airChaudNacelle;
        bind airTiede = reguleTemperatureNacelle.airTiede;
    }

    // Service functions without decomposition
    action def EnvoyerAirReguleAvion {
        doc /* Satisfait les use cases 'Pressuriser les réservoirs', 'Dégivrer les ailes', 'Pressuriser et tempérer la cabine'. */
        in consignePT : Information;
        in airChaudHautePression : Pneumatic;
        in airAmbiant : Pneumatic;
        out airRegulePT : Pneumatic;
        out airTiede : Pneumatic;
    }

    action def DeterminerEtatSysteme {
        doc /* Satisfait le use case 'Être informé de l'état du système'. */
    }

    action def Communiquer {
        doc /* Satisfait le use case 'Être informé de l'état du système'. */
        out stateData : Data;
    }

    // Allocation to logical constituents
    part def IPPort {
        doc /* Intermediate Pressure port */
        perform action preleveAir : PreleveAir;
    }

    part def VanneNAI {
        doc /* NAI valve */
        perform action laissePasser : LaissePasser;
    }

    part def ACAC {
        doc /* Air Conditioning Air Cooler */
        perform action reguleTemperatureNacelle : ReguleTemperatureNacelle;
    }

    part def Calculateur {
        doc /* Regulation calculator */
        perform action reguleVanneNAI : ReguleVanneNAI;
    }

    part def AirTemperatureSensor {
        doc /* Air temperature sensor */
        perform action mesurerTemperature : MesurerTemperature;
    }

    part def nacellePort {
        doc /* Nacelle port */
        perform action fournirAirInterfaceNacelle : FournirAirInterfaceNacelle;
    }

}

// ===== FUNCTIONAL_BEHAVIOUR =====

package 'BAS (Bleed Air System) - Functional Behaviour' {

    // Item definitions for exchanged flows
    item def Pneumatic;
    item def Information;
    item def Electric;
    item def Data;

    // Action definitions for individual functions
    action def PreleveAir {
        in airChaudHautePression : Pneumatic;
        out airChaudHautePression : Pneumatic;
    }

    action def LaissePasser {
        in airChaudHautePression : Pneumatic;
        in consigneOuvertureVanne : Electric;
        out airChaudNacelle : Pneumatic;
    }

    action def ReguleTemperatureNacelle {
        in airChaudNacelle : Pneumatic;
        in airAmbiant : Pneumatic;
        out airChaudReguleNacelle : Pneumatic;
        out airTiede : Pneumatic;
    }

    action def ReguleVanneNAI {
        in commandeDegivageNacelle : Information;
        in mesureTemperatureAir : Electric;
        out consigneOuvertureVanne : Electric;
    }

    action def MesurerTemperature {
        in airChaudNacelle : Pneumatic;
        out mesureTemperatureAir : Electric;
    }

    action def FournirAirInterfaceNacelle {
        in airChaudReguleNacelle : Pneumatic;
        out airChaudNacelle : Pneumatic;
    }

    action def EnvoyerAirChaudNacelle {
        in commandeDegivageNacelle : Information;
        in airChaudHautePression : Pneumatic;
        in airAmbiant : Pneumatic;
        out airChaudNacelle : Pneumatic;
        out airTiede : Pneumatic;

        action preleveAir : PreleveAir {
            in airChaudHautePression;
            out airChaudHautePression;
        }

        action laissePasser : LaissePasser {
            in airChaudHautePression;
            in consigneOuvertureVanne;
            out airChaudNacelle;
        }

        action reguleTemperatureNacelle : ReguleTemperatureNacelle {
            in airChaudNacelle;
            in airAmbiant;
            out airChaudReguleNacelle;
            out airTiede;
        }

        action fournirAirInterfaceNacelle : FournirAirInterfaceNacelle {
            in airChaudReguleNacelle;
            out airChaudNacelle;
        }

        action mesurerTemperature : MesurerTemperature {
            in airChaudNacelle;
            out mesureTemperatureAir;
        }

        action reguleVanneNAI : ReguleVanneNAI {
            in commandeDegivageNacelle;
            in mesureTemperatureAir;
            out consigneOuvertureVanne;
        }

        // Functional flows between sub-functions
        flow preleveAir.airChaudHautePression to laissePasser.airChaudHautePression;
        flow reguleVanneNAI.consigneOuvertureVanne to laissePasser.consigneOuvertureVanne;
        flow laissePasser.airChaudNacelle to reguleTemperatureNacelle.airChaudNacelle;
        flow reguleTemperatureNacelle.airChaudReguleNacelle to fournirAirInterfaceNacelle.airChaudReguleNacelle;
        flow fournirAirInterfaceNacelle.airChaudNacelle to mesurerTemperature.airChaudNacelle;
        flow mesurerTemperature.mesureTemperatureAir to reguleVanneNAI.mesureTemperatureAir;

        // Binding to system inputs/outputs
        bind preleveAir.airChaudHautePression = airChaudHautePression;
        bind reguleTemperatureNacelle.airAmbiant = airAmbiant;
        bind reguleVanneNAI.commandeDegivageNacelle = commandeDegivageNacelle;
        bind fournirAirInterfaceNacelle.airChaudNacelle = airChaudNacelle;
        bind reguleTemperatureNacelle.airTiede = airTiede;
    }

    action def EnvoyerAirReguleAvion {
        in consignePT : Information;
        in airChaudHautePression : Pneumatic;
        in airAmbiant : Pneumatic;
        out airRegulePT : Pneumatic;
        out airTiede : Pneumatic;
    }

    action def DeterminerEtatSysteme {
    }

    action def Communiquer {
        out stateData : Data;
    }

}

// ===== FUNCTIONAL_MODES =====

package 'BAS (Bleed Air System) - Functional Modes' {

    attribute def SystemPowerSignal;
    attribute def OperationalCommandSignal;
    attribute def OperationalCommandStopSignal;

    action def Communiquer;
    action def DeterminerEtatSysteme;
    action def EnvoyerAirChaudNacelle;
    action def EnvoyerAirReguleAvion;
    action def PreleveAir;
    action def LaissePasser;
    action def ReguleTemperatureNacelle;
    action def ReguleVanneNAI;
    action def MesurerTemperature;
    action def FournirAirInterfaceNacelle;

    state def FunctionalModes {
        entry; then ModeOff;

        state ModeOff {
            doc /* État initial du système. Aucune fonction active. */
        }
        transition PowerOn
            first ModeOff
            accept SystemPowerSignal
            then ModeOn;

        state ModeOn {
            entry; then Standby;

            state Standby {
                doc /* État initial dans On. */
                perform action communiquer : Communiquer;
                perform action determinerEtatSysteme : DeterminerEtatSysteme;
            }
            transition StartOperation
                first Standby
                accept OperationalCommandSignal
                then Operating;

            state Operating {
                doc /* Toutes les fonctions sont actives. */
                perform action envoyerAirChaudNacelle : EnvoyerAirChaudNacelle;
                perform action envoyerAirReguleAvion : EnvoyerAirReguleAvion;
                perform action communiquer : Communiquer;
                perform action determinerEtatSysteme : DeterminerEtatSysteme;
                perform action preleveAir : PreleveAir;
                perform action laissePasser : LaissePasser;
                perform action reguleTemperatureNacelle : ReguleTemperatureNacelle;
                perform action reguleVanneNAI : ReguleVanneNAI;
                perform action mesurerTemperature : MesurerTemperature;
                perform action fournirAirInterfaceNacelle : FournirAirInterfaceNacelle;
            }
            transition StopOperation
                first Operating
                accept OperationalCommandStopSignal
                then Standby;
        }
        transition PowerOff
            first ModeOn
            accept SystemPowerSignal
            then ModeOff;
    }
}