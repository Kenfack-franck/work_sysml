# Diagnostic de Qualité — BAS Silvercrest
## Comparaison entre les diagrammes générés par l'IA et les diagrammes de référence

**Date** : 2026-02-21  
**Session analysée** : `4b87d2e5-91e8-4111-8365-f3850fe5e650` — BAS Silvercrest - Formel  
**Description fournie** : `experiments/descriptions/bleed_air_system/style_formel.txt` (56 lignes)  
**Résultats IA** : `experiments/results/bleed_air_system/style_formel/`

---

## Méthodologie

Pour chaque diagramme de référence, on identifie chaque élément (acteur, use case, composant, flux, relation) et on vérifie sa présence dans ce que l'IA a généré.

**Trois causes d'écart possibles :**
- **DESCRIPTION** : L'élément n'était pas dans la description fournie par l'utilisateur — l'IA ne pouvait pas le deviner
- **PROMPT** : L'élément était dans la description mais le prompt n'a pas guidé l'IA pour le capturer correctement
- **IA** : L'élément était dans la description et le prompt est correct, mais l'IA l'a omis ou mal interprété

**Convention d'affichage :**
- ✅ Présent — élément clairement identifiable dans la génération
- ⚠️ Partiel — élément reconnaissable mais incomplet, mal nommé, ou mal attribué
- ❌ Absent — aucun équivalent trouvé dans la génération

---

## Diagramme 1 : Lifecycle Diagram BAS

### Contexte
Le diagramme de cycle de vie montre 8 phases principales et plusieurs transitions.  
**La description fournie (style_formel.txt) ne mentionne AUCUNE phase de cycle de vie.** Ce diagramme n'a pas été demandé et aucune donnée n'a été fournie pour le générer.

| Phase / Transition de référence | Présent dans notre génération ? | Cause |
|---|---|---|
| Concept évaluation | ❌ Absent | DESCRIPTION |
| Développement | ❌ Absent | DESCRIPTION |
| Production (avec sous-cycle) | ❌ Absent | DESCRIPTION |
| Livraison (= Stockage intermédiaire + Transport) | ❌ Absent | DESCRIPTION |
| Montage final (intégration sur l'avion) | ❌ Absent | DESCRIPTION |
| Exploitation (phases maintenance LRU + Operation) | ❌ Absent | DESCRIPTION |
| Maintenance (hors A/C not in maintenance facility) | ❌ Absent | DESCRIPTION |
| Recyclage (fin de vie) | ❌ Absent | DESCRIPTION |
| Transition : Développement → Production via CR/QR | ❌ Absent | DESCRIPTION |
| Transition : Production → Livraison | ❌ Absent | DESCRIPTION |
| Transition : Exploitation ↔ Maintenance (bidirectionnel) | ❌ Absent | DESCRIPTION |
| Transition : Exploitation → Recyclage | ❌ Absent | DESCRIPTION |

**Couverture Diag 1 : 0 / 12 — 0%**  
**Cause unique : DESCRIPTION** — le cycle de vie n'est jamais mentionné dans une description de système fonctionnel. C'est un type de diagramme qui nécessite une description dédiée ou une invitation explicite dans le prompt.

---

## Diagramme 2 : Use Case Diagram (Fonctions de service)

### Contexte
Le vrai diagramme montre **7 use cases** et **5 acteurs** autour du "System BAS".  
Notre description mentionne 4 fonctions de service + 6 entités externes (sans distinguer acteurs humains et systèmes techniques).

| Élément de référence | Type | Présent dans notre génération ? | Cause de l'écart |
|---|---|---|---|
| A/C Pneumatic System | Acteur (receveur) | ⚠️ Partiel | PROMPT — présent comme `external_system`, mais notre prompt ne distingue pas "acteur SysML" (humain ou système interagissant) de "système externe passif". `stakeholders = []` dans notre JSON. |
| Nacelle | Acteur (receveur) | ⚠️ Partiel | PROMPT — même raison, dans `external_systems` mais jamais en tant qu'acteur de use case |
| Turbomachine | Acteur (fournisseur) | ⚠️ Partiel | PROMPT — même raison |
| EECS (Electronic Engine Control System) | Acteur | ❌ Absent | DESCRIPTION — notre description mentionne uniquement "A/C Avionics" globalement. L'EECS n'est jamais nommé séparément. |
| Operation maintenance operator | Acteur | ❌ Absent | DESCRIPTION — aucune mention de maintenance opérateur dans la description |
| Pressuriser les réservoirs | Use Case | ❌ Absent | DESCRIPTION — notre description dit "Envoyer de l'air régulé en pression et température à l'avion". La pressurisation des réservoirs n'est pas mentionnée explicitement. |
| Dégivrer les ailes | Use Case | ❌ Absent | DESCRIPTION — le dégivrage des ailes n'est pas mentionné. Notre description parle uniquement du dégivrage nacelle. |
| Pressuriser et tempérer la cabine | Use Case | ⚠️ Partiel | PROMPT — notre description dit "Envoyer de l'air régulé en pression et température à l'avion" ce qui couvre ce use case, mais notre prompt a généré un use case générique au lieu de décomposer par destination (cabine, réservoirs, ailes). |
| Dégivrer la nacelle | Use Case | ✅ Présent | — Généré comme "Envoyer de l'air chaud à la nacelle pour le dégivrage" |
| Être informé de l'état du système | Use Case | ⚠️ Partiel | PROMPT — notre description mentionne "Déterminer l'état du système" mais le prompt l'a lié à l'avionique (A/C Avionics), alors que le vrai diagramme lie ce UC à l'**opérateur de maintenance**. La perspective d'observateur est absente. |
| Diagnostiquer l'état | Use Case | ⚠️ Partiel | PROMPT — absorbé dans "Déterminer l'état du système", jamais extrait comme use case séparé de maintenance |
| Réparer sous l'aile | Use Case | ❌ Absent | DESCRIPTION — aucune mention de réparation dans la description |

**Couverture Diag 2 : 4 présents + 5 partiels + 3 absents sur 12**  
**En équivalents pleins : ~6.5 / 12 — ~54%**  
**Cause principale : DESCRIPTION (5 éléments), secondaire PROMPT (4 éléments)**

---

## Diagramme 3 : Use Case Diagram (Maintenance)

### Contexte
Ce diagramme est un **zoom du diagramme principal** centré sur la maintenance. Il montre des acteurs et use cases entièrement absents de notre description.

| Élément de référence | Type | Présent dans notre génération ? | Cause de l'écart |
|---|---|---|---|
| Maintenance operator | Acteur | ❌ Absent | DESCRIPTION — jamais mentionné |
| Maintenance facility | Acteur | ❌ Absent | DESCRIPTION — jamais mentionné |
| Diagnostiquer l'état | Use Case | ❌ Absent | DESCRIPTION — notre description couvre la détermination d'état pour l'avionique, pas pour un opérateur |
| Maintenir en conditions opérationnelles | Use Case | ❌ Absent | DESCRIPTION — concept de maintenabilité absent |
| Réparer en atelier | Use Case | ❌ Absent | DESCRIPTION — absent |
| Maintenir «include» Diagnostiquer l'état | Relation include | ❌ Absent | DESCRIPTION — dépend des éléments ci-dessus |
| Maintenir «include» Réparer en atelier | Relation include | ❌ Absent | DESCRIPTION — dépend des éléments ci-dessus |

**Couverture Diag 3 : 0 / 7 — 0%**  
**Cause unique : DESCRIPTION** — La maintenance est un domaine entier non couvert par la description initiale. C'est une lacune délibérée ou involontaire de la description.

---

## Diagramme 4 : Functional Behavior Diagram (Air chaud nacelle)

### Contexte
Ce diagramme montre le comportement fonctionnel détaillé de la fonction "Envoyer de l'air chaud à la nacelle". Il utilise la notation `composant::fonction` et type les flux en trois catégories (pneumatique, information, électrique).

**Important** : notre génération utilise des **fonctions de haut niveau** (5 fonctions) avec sous-fonctions, mais **ne type pas les flux** et n'utilise **pas la notation `composant::fonction`**.

### Fonctions

| Élément de référence | Type | Présent dans notre génération ? | Cause de l'écart |
|---|---|---|---|
| IP port :: Prélever air | Fonction de composant | ⚠️ Partiel | PROMPT — "Prélever Air IP" existe comme sous-fonction mais n'est pas attribuée à un composant IP port. Notation `composant::fonction` absente du prompt. |
| Vanne NAI :: Laisser passer l'air | Fonction de composant | ⚠️ Partiel | PROMPT — "Contrôler Vanne NAIV" existe mais avec un nom différent (contrôle ≠ laisser passer) et sans attribution au composant Vanne NAI |
| ACAC :: Réguler la température nacelle | Fonction de composant | ❌ Absent | DESCRIPTION — dans notre description, l'ACAC (Exchanger) est décrit uniquement pour conditionner l'air vers l'avion. Son rôle dans le circuit de dégivrage nacelle (via ACAC) n'est pas mentionné. |
| Calculateur :: Réguler la vanne NAI | Fonction de composant | ⚠️ Partiel | PROMPT — "Piloter Vannes" (sous-fonction de Contrôler et Communiquer) couvre cela, mais sans attribution composant spécifique |
| Air Temperature Sensor :: Mesurer la température | Fonction de composant | ⚠️ Partiel | PROMPT — "Mesurer Température Sortie" existe mais pas attribuée au composant "Air Temperature Sensor" avec sa désignation propre |
| Nacelle port :: Fournir l'air à l'interface Nacelle | Fonction de composant | ⚠️ Partiel | PROMPT — le flux "Air Chaud Dégivrage → La nacelle" existe mais sans composant "Nacelle port" comme acteur intermédiaire |

### Flux

| Élément de référence | Type flux | Présent dans notre génération ? | Cause de l'écart |
|---|---|---|---|
| :air chaud haute pression → IP port | Pneumatique | ⚠️ Partiel | PROMPT — "Air Haute Pression (Turbomachine) → Gérer le Prélèvement" existe mais non typé pneumatique, non nommé avec le préfixe `:` |
| IP port → Vanne NAI | Pneumatique | ❌ Absent | DESCRIPTION — dans notre modèle, le flux passe par "Gérer le Prélèvement → Gérer le Dégivrage" sans montrer IP port→NAIV directement |
| Vanne NAI → ACAC (air chaud nacelle) | Pneumatique | ❌ Absent | DESCRIPTION — notre description ne place pas l'ACAC dans le circuit de dégivrage nacelle. Ce flux suppose que l'ACAC régule aussi la température pour la nacelle, ce qui n'est pas dans notre description. |
| ACAC → Nacelle port | Pneumatique | ❌ Absent | DESCRIPTION — même raison |
| :air ambiant → ACAC | Pneumatique | ✅ Présent | — "Air Froid (Soufflante) → Conditionner l'Air pour l'Avion" clairement présent, même non typé |
| ACAC → :air tiède (exhaust) | Pneumatique | ✅ Présent | — "Air de Refroidissement Évacué" clairement présent |
| :commande dégivrage nacelle → Calculateur | Électrique | ✅ Présent | — "Commande Dégivrage (Avionique) → Contrôler et Communiquer" clairement présent, non typé électrique |
| Calculateur → Vanne NAI : consigne d'ouverture | Information | ✅ Présent | — "Commande NAIV" clairement présent, non typé information |
| Air Temperature Sensor → Calculateur : mesure température | Information | ✅ Présent | — "Mesure Température Bleed → Contrôler et Communiquer" clairement présent, non typé information |

**Note sur les flux** : 5 flux sont reconnaissables (⚠️ ou ✅) mais **aucun n'est typé** (pneumatique / information / électrique). Cette typing est entièrement absente. Cause : **PROMPT** — le prompt fonctionnel demande des flux mais ne guide pas l'IA pour les typer en catégories physiques.

**Couverture Diag 4 : 5 présents + 6 partiels + 4 absents sur 15**  
**En équivalents pleins : ~8 / 15 — ~53%**  
**Cause principale : PROMPT (typing des flux absent, notation composant::fonction absente), secondaire DESCRIPTION (ACAC dans circuit nacelle)**

---

## Synthèse globale

| Catégorie | Éléments attendus | Présents (✅) | Partiels (⚠️) | Absents (❌) | Couverture (présents + partiels/2) |
|---|---|---|---|---|---|
| Diag 1 — Lifecycle | 12 | 0 | 0 | 12 | **0%** |
| Diag 2 — Use Cases Services | 12 | 4 | 5 | 3 | **54%** |
| Diag 3 — Use Cases Maintenance | 7 | 0 | 0 | 7 | **0%** |
| Diag 4 — Functional Behavior (fonctions) | 6 | 0 | 5 | 1 | **42%** |
| Diag 4 — Functional Behavior (flux) | 9 | 5 | 1 | 3 | **61%** |
| **TOTAL** | **46** | **9** | **11** | **26** | **~42%** |

---

## Analyse des causes des écarts

| Cause | Éléments manquants | % des écarts | Exemples représentatifs |
|---|---|---|---|
| **DESCRIPTION** (pas mentionné par l'utilisateur) | 26 | **70%** | Lifecycle entier (12), maintenance entière (7), EECS, Pressuriser réservoirs, Dégivrer ailes, Réparer sous l'aile, ACAC rôle nacelle (3 flux) |
| **PROMPT** (mentionné mais mal capturé par le prompt) | 10 | **27%** | Distinction acteur/système externe absente (stakeholders=[]), typing des flux absente (0% des flux typés), notation composant::fonction absente, décomposition use cases trop grossière |
| **IA** (prompt correct mais IA a omis) | 1 | **3%** | Le champ `stakeholders` est vide alors que les entités sont clairement citées dans la description comme parties prenantes — l'IA les a toutes mises dans `external_systems` au lieu de distinguer |

### Détail des écarts PROMPT

1. **Champ `stakeholders` vs `external_systems`** : Le prompt opérationnel ne demande pas de distinguer les acteurs humains/système qui UTILISENT le système (stakeholders) des systèmes externes qui FOURNISSENT ou REÇOIVENT des ressources. Dans SysML, un acteur de use case peut être un système technique. Notre JSON met tout dans `external_systems` et laisse `stakeholders=[]`.

2. **Typing des flux fonctionnels** : Le prompt fonctionnel demande des `functional_flows` mais ne précise pas de typer chaque flux comme `pneumatique`, `information`, ou `électrique`. Sans cette instruction, l'IA génère des noms génériques ("Air Chaud Brute", "Commande HPV") sans type physique.

3. **Notation composant::fonction** : Le prompt fonctionnel génère des fonctions de haut niveau + sous-fonctions, mais n'impose pas la granularité `composant::fonction` du diagramme de comportement fonctionnel SysML. Le niveau de granularité attendu est "chaque composant physique a une fonction nommée".

4. **Décomposition des use cases** : La description dit "Envoyer de l'air régulé en pression et température à l'avion". Le prompt opérationnel aurait dû guider l'IA à décomposer cette fonction de service en use cases distincts par destination (cabine, réservoirs, ailes). Le prompt ne demande pas cette décomposition géographique/fonctionnelle.

---

## Recommandations

### 1. Si DESCRIPTION est la cause principale (70% des écarts)

**Éléments que l'utilisateur aurait dû mentionner pour couvrir les 26 éléments manquants :**
- **Cycle de vie** : phases de développement, production, livraison, montage, exploitation, maintenance, recyclage — avec les jalons CR/QR
- **Acteurs de maintenance** : opérateur de maintenance, atelier de maintenance (Maintenance facility)
- **Use cases de maintenance** : diagnostic par un opérateur, réparation sous l'aile, réparation en atelier, maintien en conditions opérationnelles
- **EECS** : l'Electronic Engine Control System est un acteur externe distinct de l'avionique générale
- **Décomposition des fonctions de service** : dégivrage des ailes, pressurisation des réservoirs comme use cases séparés
- **Rôle de l'ACAC dans le circuit nacelle** : l'échangeur régule aussi la température de l'air de dégivrage (pas seulement l'air pour l'avion)

**Question sur la réalisme :** Non, il n'est pas réaliste de demander à un utilisateur de fournir ces détails dès la première description. Le cycle de vie et la maintenance sont des domaines que l'IA devrait pouvoir **éliciter** via des questions. Une session devrait idéalement inclure un dialogue : *"Avez-vous des contraintes de maintenance ? Des phases de cycle de vie à modéliser ?"*

**Description V2 proposée** : voir `experiments/descriptions/bleed_air_system/style_formel_v2.txt`

### 2. Si PROMPT est la cause (27% des écarts)

**Corrections de prompt à implémenter :**

**a) Prompt opérationnel — Distinguer acteurs et systèmes externes :**
```
Dans le JSON opérationnel, "stakeholders" doit contenir les entités qui UTILISENT ou INTERAGISSENT 
avec le système (humains ET systèmes techniques qui sont des acteurs de use case).
"external_systems" est réservé aux systèmes passifs.
Exemple : la turbomachine est à la fois external_system (fournit l'air) ET un acteur dans les use cases.
```

**b) Prompt fonctionnel — Typer les flux :**
```
Pour chaque flux fonctionnel, ajoute un champ "type" avec une des valeurs :
- "pneumatique" : flux d'air, de gaz, de fluide
- "information" : flux de données, commandes, mesures, consignes
- "électrique" : flux d'énergie électrique, signaux électriques, alimentation
- "mécanique" : flux de force, couple, déplacement
- "thermique" : flux de chaleur
```

**c) Prompt fonctionnel — Notation composant::fonction :**
```
Pour chaque sous-fonction, si elle est réalisée par un composant physique spécifique mentionné dans 
la description, utilise la notation "NomComposant::NomFonction".
Exemple : "IP port::Prélever air" plutôt que juste "Prélever Air IP".
```

**d) Prompt opérationnel — Décomposition des use cases :**
```
Si un use case est de type "Fournir X à Y", décompose-le par destination finale si la description 
mentionne plusieurs destinations. Ex: "Fournir air à l'avion" → "Pressuriser réservoirs", 
"Tempérer cabine", "Dégivrer ailes" si ces destinations sont mentionnées.
```

### 3. Si IA est la cause (3% des écarts)

**Écart identifié** : `stakeholders = []` alors que la description cite clairement plusieurs entités qui interagissent avec le système.

**Correction** : Renforcer le prompt opérationnel avec un exemple explicite :
```json
"stakeholders": [
  {"name": "Turbomachine", "role": "Fournit l'air chaud haute pression", "type": "system"},
  {"name": "A/C Pneumatic System", "role": "Reçoit l'air conditionné régulé", "type": "system"}
],
"external_systems": [
  "SOV - Shut-Off Valve"
]
```
Cette distinction acteur (participe aux use cases) vs système externe (frontière passive) est subtile et doit être illustrée par l'exemple dans le prompt.

---

## Ce que notre IA fait BIEN (points positifs)

1. **Couverture fonctionnelle de base** : les 5 fonctions générées couvrent les 4 fonctions de service de la description de manière cohérente
2. **Composants physiques** : le niveau logique/technique identifie correctement les 15 composants mentionnés dans la description (IP Port, HP Port, HPV, IPCV, NAIV, PRV, Exchanger, FAV, Filter, bleed press sensor, bleed temp sensor, etc.)
3. **Scénarios opérationnels** : les 2 scénarios (fourniture nominale + dégivrage) sont fidèlement reproduits avec les bonnes étapes
4. **Exigences** : les 4 exigences mesurables (-40°C/+85°C, 500ms, 20-50 PSI, 150-230°C) sont toutes présentes
5. **Flux fonctionnels** : 18 flux fonctionnels générés, dont les flux de commande (HPV, PRV, FAV, NAIV) et les flux de mesure (pression, température) sont tous présents

---

## Description améliorée proposée

Voir : `experiments/descriptions/bleed_air_system/style_formel_v2.txt`

**Éléments ajoutés dans la V2 :**
1. Cycle de vie (8 phases)
2. Acteurs de maintenance (opérateur, atelier)
3. Use cases de maintenance (3 nouveaux use cases)
4. EECS comme acteur distinct
5. Décomposition des use cases de fourniture d'air (réservoirs, ailes, cabine)
6. Rôle de l'ACAC dans le circuit nacelle
7. Types de flux (pneumatique, information, électrique) explicitement mentionnés
8. Notation composant::fonction pour les fonctions clés
