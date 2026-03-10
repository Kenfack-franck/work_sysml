# Entrees utilisateur -- Niveau Technique

## Section : technical_components

15 composants techniques :

| # | Composant | Type | Implemente | Role |
|---|-----------|------|------------|------|
| 1 | NAIV (Nacelle Anti-Ice Valve) | Vanne pneumatique papillon | Vanne NAI | Controler le flux d'air chaud vers le degivrage nacelle |
| 2 | PCEV (Pressure Control Exchange Valve) | Vanne pneumatique de regulation | Vanne PCE | Controler le flux d'air chaud vers l'echangeur PCE |
| 3 | ACAC (Air Cooled Air Cooler) | Echangeur thermique air-air | ACAC | Refroidir l'air chaud nacelle avec l'air ambiant |
| 4 | PCE (Pressure Control Exchanger) | Echangeur thermique | PCE | Reguler la pression et temperature de l'air pour l'avion |
| 5 | EEC / Calculateur FADEC | Calculateur numerique | Calculateur | Reguler les vannes NAIV et PCEV. Integre dans le FADEC |
| 6 | IP port | Piquage pneumatique | IP port | Prelevement air chaud HP sur le compresseur |
| 7 | Nacelle anti-ice pneumatic port | Interface pneumatique | Nacelle port | Connecter le BAS au circuit degivrage nacelle |
| 8 | Fan bleed port (by-pass duct) | Piquage pneumatique | -- | Prelevement air supplementaire cote fan |
| 9 | Nacelle exhaust port | Port d'echappement | -- | Evacuer l'air tiede apres echange thermique |
| 10 | SOV (Shut-Off Valve) | Vanne d'arret de securite | -- | Isoler le BAS du systeme pneumatique avion (cote Aircraft) |
| 11 | Air Temperature Sensor (ACAC) | Thermocouple | ACAC Air Temp Sensor | Mesurer la temperature en sortie ACAC |
| 12 | Air Temperature Sensor (PCE) | Thermocouple | PCE Air Temp Sensor | Mesurer la temperature en sortie PCE |
| 13 | Air Pressure Sensor | Capteur de pression | Air Pressure Sensor | Mesurer la pression en sortie PCE |
| 14 | Filter | Filtre pneumatique en ligne | Filter | Filtrer l'air regule avant distribution |
| 15 | Data exchange (I/O) | Interface de communication | -- | Echanger les donnees avec l'avionique |

Le BAS est integre dans l'IPPS (Integrated Power Plant System) qui englobe le perimetre moteur. L'interface avec l'avion se fait via le SOV, le Fan bleed port, et le Data exchange I/O.

## Section : physical_connections

17 connexions physiques :

**Circuit pneumatique nacelle :**

| # | Source | Destination | Type |
|---|--------|-------------|------|
| 1 | IP port | NAIV | Tuyauterie pneumatique haute temperature |
| 2 | NAIV | ACAC | Tuyauterie pneumatique |
| 3 | ACAC | Nacelle anti-ice pneumatic port | Tuyauterie pneumatique |
| 4 | ACAC | Nacelle exhaust port | Tuyauterie pneumatique (air tiede) |

**Circuit pneumatique avion :**

| # | Source | Destination | Type |
|---|--------|-------------|------|
| 5 | IP port | PCEV | Tuyauterie pneumatique haute temperature |
| 6 | PCEV | PCE | Tuyauterie pneumatique |
| 7 | PCE | Filter | Tuyauterie pneumatique (air regule) |
| 8 | Filter | SOV (interface Aircraft) | Tuyauterie pneumatique (air filtre) |
| 9 | PCE | Nacelle exhaust port | Tuyauterie pneumatique (air tiede) |

**Entrees air ambiant :**

| # | Source | Destination | Type |
|---|--------|-------------|------|
| 10 | Environnement | ACAC | Prise d'air ambiant |
| 11 | Environnement | PCE | Prise d'air ambiant |

**Capteurs :**

| # | Source | Destination | Type |
|---|--------|-------------|------|
| 12 | Air Temp Sensor (ACAC) | EEC | Cablage electrique |
| 13 | Air Temp Sensor (PCE) | EEC | Cablage electrique |
| 14 | Air Pressure Sensor | EEC | Cablage electrique |

**Commande vannes :**

| # | Source | Destination | Type |
|---|--------|-------------|------|
| 15 | EEC | NAIV | Cablage electrique |
| 16 | EEC | PCEV | Cablage electrique |

**Interface avionique :**

| # | Source | Destination | Type |
|---|--------|-------------|------|
| 17 | Data exchange (I/O) | EEC | Bus de donnees (bidirectionnel) |

Note : les types de cablage et bus (ARINC 429, CAN, etc.) et les materiaux des tuyauteries ne sont pas precises dans le document.

## Section : technology_choices

4 choix technologiques :

1. **Architecture IPPS** (Integrated Power Plant System) -- le BAS est integre dans l'ensemble IPPS (moteur + nacelle + systemes moteur) car c'est un systeme moteur, pas un systeme avion

2. **Calculateur integre au FADEC** (EEC) -- le calculateur du BAS est integre dans le calculateur moteur plutot qu'un calculateur independant. Justification : reduction du nombre d'equipements, simplification des interfaces

3. **Double echangeur** (ACAC + PCE) -- deux echangeurs separes pour les deux chaines fonctionnelles. L'ACAC traite la chaine nacelle, le PCE traite la chaine avion

4. **Prelevement IP** (Intermediate Pressure) -- l'air est preleve au stade de pression intermediaire du compresseur (IP port), pas au stade haute pression

Note : le document ne fournit pas de references industrielles, de specifications de materiaux, ni de justifications formelles des choix technologiques.

## Section : technical_requirements

Aucune exigence technique fournie. Cette section est volontairement incomplete car le document BAS ne contient pas d'exigences techniques formalisees. Les exigences devraient etre definies dans un document de specification (TND, AdB).
