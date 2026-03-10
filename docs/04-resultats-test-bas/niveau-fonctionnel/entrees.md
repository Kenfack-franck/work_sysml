# Entrees utilisateur -- Niveau Fonctionnel

## Section : functional_decomposition

4 fonctions de service identifiees au niveau operationnel :

1. **Envoyer de l'air regule en (P,T) a l'avion** -- satisfait les use cases Pressuriser les reservoirs, Degivrer les ailes, Pressuriser et temperer la cabine
2. **Envoyer de l'air chaud a la nacelle** -- satisfait le use case Degivrer la nacelle
3. **Determiner l'etat du systeme** -- satisfait le use case Etre informe de l'etat du systeme
4. **Communiquer** -- satisfait le use case Etre informe de l'etat du systeme

**Decomposition de "Envoyer de l'air chaud a la nacelle" en 6 sous-fonctions :**

1. **Prelever l'air** -- entree : air chaud haute pression (depuis le moteur via IP port) ; sortie : air chaud haute pression
2. **Laisser passer l'air** -- entrees : air chaud haute pression + consigne d'ouverture vanne ; sortie : air chaud nacelle
3. **Reguler la temperature nacelle** -- entrees : air chaud nacelle + air ambiant (depuis l'environnement) ; sorties : air chaud regule nacelle + air tiede
4. **Reguler la vanne NAI** -- entrees : commande degivrage nacelle (depuis l'avionique) + mesure temperature air ; sortie : consigne d'ouverture vanne
5. **Mesurer la temperature** -- entree : air chaud nacelle ; sortie : mesure temperature air
6. **Fournir l'air a l'interface Nacelle** -- entree : air chaud regule nacelle ; sortie : air chaud nacelle (vers la nacelle via Nacelle port)

Note : les decompositions de "Envoyer de l'air regule en (P,T) a l'avion", "Determiner l'etat du systeme" et "Communiquer" ne sont pas detaillees dans le document.

## Section : functional_flows

11 flux entre les sous-fonctions de "Envoyer de l'air chaud a la nacelle" :

| # | Source | Destination | Flux | Type |
|---|--------|-------------|------|------|
| 1 | Prelever l'air | Laisser passer l'air | air chaud haute pression | pneumatique |
| 2 | Reguler la vanne NAI | Laisser passer l'air | consigne d'ouverture vanne | electrique |
| 3 | Laisser passer l'air | Reguler la temperature nacelle | air chaud nacelle | pneumatique |
| 4 | Environnement | Reguler la temperature nacelle | air ambiant | pneumatique |
| 5 | Reguler la temperature nacelle | Fournir l'air a l'interface Nacelle | air chaud regule nacelle | pneumatique |
| 6 | Reguler la temperature nacelle | Environnement | air tiede | pneumatique |
| 7 | Mesurer la temperature | Reguler la vanne NAI | mesure temperature air | electrique |
| 8 | Fournir l'air a l'interface Nacelle | Mesurer la temperature | air chaud nacelle | pneumatique |
| 9 | Avionique | Reguler la vanne NAI | commande degivrage nacelle | information |
| 10 | Moteur | Prelever l'air | air chaud haute pression | pneumatique |
| 11 | Fournir l'air a l'interface Nacelle | Nacelle | air chaud nacelle | pneumatique |

## Section : functional_behavior

Allocation des sous-fonctions aux constituants logiques :

| Constituant | Fonction | Remarque |
|-------------|----------|----------|
| IP port | Prelever l'air | Alternative possible : ecope |
| Vanne NAI | Laisser passer l'air | Controle du passage selon la consigne |
| ACAC | Reguler la temperature nacelle | Melange air chaud / air ambiant |
| Calculateur | Reguler la vanne NAI | Calcul de la consigne d'ouverture |
| Air Temperature Sensor | Mesurer la temperature | Mesure transmise au calculateur |
| Nacelle port | Fournir l'air a l'interface Nacelle | Interface avec la nacelle |

**Ordre d'execution :**
- Sequence principale : Prelever l'air -> Laisser passer l'air -> Reguler la temperature nacelle -> Fournir l'air a l'interface Nacelle
- Boucle de retroaction en parallele : Mesurer la temperature -> Reguler la vanne NAI -> Laisser passer l'air

## Section : functional_chains

3 chaines fonctionnelles :

**Chaine 1 : Envoyer de l'air chaud a la nacelle**
- Entrees : commande degivrage nacelle (information), air chaud haute pression (pneumatique), air ambiant (pneumatique)
- Sorties : air chaud nacelle (pneumatique), air tiede (pneumatique)
- Enchainement : Prelever l'air -> Laisser passer l'air -> Reguler la temperature nacelle -> Fournir l'air a l'interface Nacelle. En parallele : boucle Mesurer la temperature -> Reguler la vanne NAI

**Chaine 2 : Envoyer de l'air regule a l'avion**
- Entrees : consigne (P,T) (information), air chaud haute pression (pneumatique), air ambiant (pneumatique)
- Sorties : air regule (P,T) (pneumatique), air tiede (pneumatique)
- Note : decomposition interne non detaillee

**Chaine 3 : Communiquer**
- Sorties : state data (information, vers A/C avionics via Data exchange I/O)
- Note : liee a "Determiner l'etat du systeme", decomposition non detaillee

Alimentation : Power Supply -- alimentation electrique commune aux fonctions du BAS.

## Section : functional_modes

Activation des fonctions par mode :

| Mode | Fonctions actives |
|------|-------------------|
| Off | Aucune |
| On > Stand by | Communiquer, Determiner l'etat du systeme |
| On > En fonctionnement | Toutes : Envoyer de l'air chaud a la nacelle (+ 6 sous-fonctions), Envoyer de l'air regule en (P,T) a l'avion, Communiquer, Determiner l'etat du systeme |
