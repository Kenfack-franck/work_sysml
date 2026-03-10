# Entrees utilisateur -- Niveau Logique

## Section : logical_components

11 constituants logiques :

| # | Composant | Type | Role | Fonctions |
|---|-----------|------|------|-----------|
| 1 | Calculateur | Calculateur numerique | Traiter les commandes et mesures pour reguler les vannes et communiquer l'etat | Provide Feedback, Reguler la PRV, Reguler la vanne NAI, Reguler la vanne PCE |
| 2 | IP port | Port d'interface d'entree | Point de prelevement de l'air chaud HP sur le compresseur | Prelever air |
| 3 | Vanne NAI | Vanne pneumatique | Controler le passage de l'air chaud vers la nacelle | Laisser passer l'air |
| 4 | Vanne PCE | Vanne pneumatique | Controler le passage de l'air chaud vers l'echangeur PCE | Actuated bleed select |
| 5 | PCE | Echangeur thermique | Transfert d'energie thermique pour reguler P/T | Transfert d'energie thermique |
| 6 | ACAC | Echangeur thermique | Reguler la temperature de l'air chaud nacelle | Reguler la temperature nacelle |
| 7 | Filter | Filtre pneumatique | Filtrer l'air regule avant distribution | Filtrer air |
| 8 | PCE Air Temp Sensor | Capteur de temperature | Mesurer la temperature en sortie PCE | Mesurer la temperature (cote PCE) |
| 9 | Air Pressure Sensor | Capteur de pression | Mesurer la pression en sortie PCE | Mesurer la pression |
| 10 | ACAC Air Temp Sensor | Capteur de temperature | Mesurer la temperature en sortie ACAC | Mesurer la temperature (cote ACAC) |
| 11 | Nacelle port | Port d'interface de sortie | Fournir l'air chaud regule a la nacelle | Fournir l'air a l'interface Nacelle |

## Section : function_allocation

Allocation des fonctions aux constituants :

- **Calculateur** : Reguler la vanne NAI, Reguler la vanne PCE, Reguler la PRV, Provide Feedback (Communiquer), Determiner l'etat du systeme
- **IP port** : Prelever l'air
- **Vanne NAI** : Laisser passer l'air (vers nacelle)
- **Vanne PCE** : Actuated bleed select (laisser passer l'air vers avion)
- **PCE** : Transfert d'energie thermique (reguler P/T pour l'avion)
- **ACAC** : Reguler la temperature nacelle
- **Filter** : Filtrer l'air regule
- **PCE Air Temperature Sensor** : Mesurer la temperature (cote PCE/avion)
- **Air Pressure Sensor** : Mesurer la pression (air regule)
- **ACAC Air Temperature Sensor** : Mesurer la temperature (cote ACAC/nacelle)
- **Nacelle port** : Fournir l'air a l'interface Nacelle

Toutes les fonctions elementaires du niveau fonctionnel sont allouees. Des fonctions supplementaires apparaissent (Reguler la vanne PCE, Filtrer air, Mesurer la pression) car l'architecture logique detaille la chaine "Envoyer de l'air regule a l'avion" non decomposee au niveau fonctionnel.

## Section : internal_connections

23 connexions internes :

**Chaine degivrage nacelle :**

| # | Source | Destination | Flux | Type |
|---|--------|-------------|------|------|
| 1 | IP port | Vanne NAI | air chaud haute pression | pneumatique |
| 2 | Calculateur | Vanne NAI | consigne ouverture vanne | electrique |
| 3 | Vanne NAI | ACAC | air chaud nacelle | pneumatique |
| 4 | ACAC | Nacelle port | air chaud nacelle | pneumatique |
| 5 | ACAC | ACAC Air Temp Sensor | air chaud nacelle | pneumatique |
| 6 | ACAC Air Temp Sensor | Calculateur | mesure temperature air | electrique |

**Chaine air regule avion :**

| # | Source | Destination | Flux | Type |
|---|--------|-------------|------|------|
| 7 | IP port | Vanne PCE | air chaud haute pression | pneumatique |
| 8 | Calculateur | Vanne PCE | consigne ouverture vanne | electrique |
| 9 | Calculateur | Vanne PCE | position vanne PCE | electrique |
| 10 | Vanne PCE | PCE | air chaud haute pression | pneumatique |
| 11 | PCE | Air Pressure Sensor | air regule T | pneumatique |
| 12 | PCE | Filter | air regule (P,T) | pneumatique |
| 13 | Air Pressure Sensor | Calculateur | mesure pression air | electrique |
| 14 | PCE Air Temp Sensor | Calculateur | mesure temperature air | electrique |
| 15 | Filter | sortie systeme A/C pneumatic port | air regule (P,T) | pneumatique |

**Interfaces externes :**

| # | Source | Destination | Type |
|---|--------|-------------|------|
| 16 | Moteur | IP port | pneumatique |
| 17 | Environnement | ACAC | pneumatique |
| 18 | Environnement | PCE | pneumatique |
| 19 | ACAC | Environnement (air tiede) | pneumatique |
| 20 | PCE | Environnement (air tiede) | pneumatique |
| 21 | Nacelle port | Nacelle | pneumatique |
| 22 | Systeme (commandes, energie) | Calculateur | information/electrique |
| 23 | Calculateur | Avionique (state data) | information |

## Section : logical_grouping

2 groupes fonctionnels + 1 composant transversal :

**Groupe 1 -- Chaine degivrage nacelle :**
- IP port (partage avec le groupe 2)
- Vanne NAI
- ACAC
- ACAC Air Temperature Sensor
- Nacelle port

**Groupe 2 -- Chaine air regule avion :**
- IP port (partage avec le groupe 1)
- Vanne PCE
- PCE
- Air Pressure Sensor
- PCE Air Temperature Sensor
- Filter

**Composant transversal :**
- Calculateur (commun aux deux chaines)

Note : ce regroupement est deduit de l'architecture logique, il n'est pas explicitement present dans le document source.

## Section : logical_requirements

Aucune exigence logique fournie. Cette section est volontairement incomplete car le document BAS ne contient pas d'exigences logiques formalisees.
