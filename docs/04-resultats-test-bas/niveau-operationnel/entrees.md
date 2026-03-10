# Entrees utilisateur -- Niveau Operationnel

## Section : system_mission

Le systeme BAS (Bleed Air System) est le systeme de prelevement d'air du moteur Silvercrest. Sa mission est de prelever l'air chaud haute pression sur le compresseur du moteur (turbomachine) et de le distribuer aux systemes avion qui en ont besoin :

- Degivrage de la nacelle
- Pressurisation et climatisation de la cabine
- Degivrage des ailes
- Pressurisation des reservoirs carburant

**Perimetre du BAS :**
- Vannes de regulation (vanne NAI, vanne PCE)
- Echangeurs thermiques (ACAC)
- Capteurs (temperature, pression)
- Calculateur de regulation
- Ports d'interface (IP port cote moteur, Nacelle port, A/C pneumatic port)

**Hors perimetre (systemes externes) :** turbomachine (moteur), avionique de bord (A/C avionics), systeme pneumatique avion (A/C Pneumatic System), nacelle, environnement.

## Section : lifecycle

Le BAS passe par 8 phases de vie :

1. **Concept evaluation** -- evaluation initiale du concept systeme
2. **Developpement** -- conception et developpement du systeme. Transition vers Production apres la revue CR/QR (S8)
3. **Production** -- 4 sous-phases :
   - Fabrication
   - Montage
   - Integration et essais (couvre l'integration avec le moteur)
   - Stockage interne
4. **Livraison** -- 2 sous-phases :
   - Stockage intermediaire
   - Transport
   - Transition vers Montage final apres livraison du moteur et du BAS
5. **Montage final** -- integration sur l'avion
6. **Exploitation** -- 2 sous-phases :
   - Operation (fonctionnement normal en vol et au sol)
   - Maintenance LRU (remplacement des unites remplacables en ligne)
   - Transition vers Recyclage en fin de vie
   - Transition vers Maintenance quand l'avion n'est pas en service
7. **Maintenance** -- maintenance lourde hors exploitation. Retour vers Exploitation apres maintenance
8. **Recyclage** -- fin de vie du systeme

## Section : stakeholders

5 acteurs interagissent avec le BAS :

1. **A/C Pneumatic System** -- systeme technique avion qui recoit l'air regule en pression et temperature (P,T) du BAS. Acteur des cas d'utilisation : Pressuriser les reservoirs, Degivrer les ailes, Pressuriser et temperer la cabine.

2. **Nacelle** -- systeme technique qui recoit l'air chaud du BAS pour le degivrage. Acteur du cas d'utilisation : Degivrer la nacelle.

3. **Turbomachine** -- moteur Silvercrest qui fournit l'air chaud haute pression au BAS. Acteur des cas d'utilisation : Pressuriser les reservoirs, Degivrer les ailes, Pressuriser et temperer la cabine, Degivrer la nacelle.

4. **EECS** (Electronic Engine Control System) -- systeme de controle electronique du moteur. Envoie les consignes de regulation (P,T) et la commande de degivrage nacelle au BAS, recoit les donnees d'etat (state data) et l'energie. Acteur des cas d'utilisation : Pressuriser les reservoirs, Degivrer les ailes, Pressuriser et temperer la cabine, Degivrer la nacelle, Etre informe de l'etat du systeme.

5. **Operation maintenance operator** -- personne humaine qui realise la maintenance operationnelle. Acteur des cas d'utilisation : Etre informe de l'etat du systeme, Diagnostiquer l'etat, Reparer sous l'aile.

## Section : external_systems

5 systemes externes et leurs interfaces avec le BAS :

1. **A/C avionics** (avionique de bord)
   - state data : flux information, bidirectionnel
   - energie : flux electrique, entree vers le BAS
   - consigne (P,T) : flux information, entree vers le BAS
   - commande degivrage nacelle : flux information, entree vers le BAS

2. **Turbomachine** (moteur Silvercrest)
   - air chaud haute pression : flux pneumatique, entree vers le BAS (Pmin, Tmax)

3. **Environnement**
   - air tiede : flux pneumatique, sortie du BAS
   - air ambiant : flux pneumatique, entree vers le BAS

4. **A/C Pneumatic System** (systeme pneumatique avion)
   - air regule (P,T) : flux pneumatique, sortie du BAS

5. **Nacelle**
   - air chaud nacelle : flux pneumatique, sortie du BAS

## Section : use_cases

8 cas d'utilisation repartis en 2 phases :

**Phase exploitation (operation) :**

1. **Pressuriser les reservoirs** -- acteurs : A/C Pneumatic System, Turbomachine, EECS
2. **Degivrer les ailes** -- acteurs : A/C Pneumatic System, Turbomachine, EECS
3. **Pressuriser et temperer la cabine** -- acteurs : A/C Pneumatic System, Turbomachine, EECS
4. **Degivrer la nacelle** -- acteurs : Nacelle, Turbomachine, EECS, A/C Pneumatic System. Inclut la fonction de service "Envoyer de l'air chaud a la nacelle"
5. **Etre informe de l'etat du systeme** -- acteurs : EECS, Operation maintenance operator. Inclut la fonction de service "Communiquer"

**Phase maintenance :**

6. **Diagnostiquer l'etat** -- acteurs : Operation maintenance operator. Inclus dans "Maintenir en conditions operationnelles"
7. **Reparer sous l'aile** -- acteurs : Operation maintenance operator

Le use case "Maintenir en conditions operationnelles" (acteurs : Operation maintenance operator, Maintenance facility) inclut "Diagnostiquer l'etat" et "Reparer en atelier".

## Section : operational_scenarios

**Scenario 1 -- Nominal alimentation air regule**

Participants : A/C Pneumatic System, A/C avionics, BAS, Turbomachine, Source Froide (Environnement).

1. A/C avionics envoie "commande de demarrage pilote" au BAS
2. A/C avionics envoie "energie" au BAS. Le BAS passe de Eteint a En fonctionnement
3. La Turbomachine passe de Eteint a En fonctionnement. A/C avionics envoie "energie" a la Turbomachine
4. A/C avionics envoie "commande (P,T)" au BAS
5. La Turbomachine fournit "air chaud haute pression = Pmin, Tmax" au BAS
6. La Source Froide fournit "air ambiant source froide" au BAS
7. Le BAS execute "Envoyer de l'air regule a la cabine"
8. Le BAS envoie "air regule (P,T)" a l'A/C Pneumatic System

**Scenario 2 -- Nominal degivrage nacelle**

Participants : Pilot, A/C avionics, BAS, Nacelle, Turbomachine.

1. Le BAS est en etat Off. La Turbomachine est en etat Running
2. A/C avionics envoie "energie" au BAS (boucle quand BAS command active). Le BAS passe en Stand by
3. Le Pilot envoie "command de-icing" a l'A/C avionics
4. L'A/C avionics envoie "Nacelle de-icing demand" au BAS. La Nacelle est en etat "Potentially iced"
5. La Turbomachine fournit "hot air" au BAS
6. Le BAS envoie "air chaud nacelle" a la Nacelle (pendant 3 min). Le BAS execute "Envoyer de l'air chaud a la nacelle"
7. La Nacelle passe en etat "De-iced"
8. Le BAS envoie "state data" a l'A/C avionics

## Section : operating_modes

Structure de modes hierarchique :

**Niveau 1 -- Mode Off :**
- Etat initial du systeme
- Aucune fonction active
- Transition vers On quand le systeme recoit de l'energie

**Niveau 1 -- Mode On** (etat composite) :
- Transition vers Off quand le systeme est mis hors tension
- Contient deux sous-modes :

  **Sous-mode Stand by :**
  - Etat initial dans On
  - Fonction active : Communicate the system state
  - Transition vers En fonctionnement quand une commande operationnelle est recue

  **Sous-mode En fonctionnement :**
  - Fonctions actives : Envoyer de l'air chaud a la nacelle, Envoyer de l'air regule a la cabine
  - Transition vers Stand by quand la commande operationnelle cesse
  - Transition vers etat final (arret) possible
