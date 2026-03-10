# Analyse Comparative — Pipeline SysML v2 sur 4 Styles de Description
## Système testé : Contrôle d'accès d'un bâtiment

*Généré le 2026-02-21 — Pipeline SysML v2 (Gemini 2.5 Flash)*

---

## 1. Éléments de référence attendus

Les 4 descriptions décrivent le **même système**. Voici la "vérité terrain" : les éléments explicitement mentionnés dans **toutes** les descriptions.

### 1.1 Composants physiques / logiciels

| Composant | Formel | Conversationnel | Liste | Narratif |
|---|:---:|:---:|:---:|:---:|
| Lecteur de badges RFID | ✅ | ✅ | ✅ | ✅ |
| Contrôleur central (boîtier central) | ✅ | ✅ | ✅ | ✅ |
| Base de données des autorisations | ✅ | ✅ | ✅ | ✅ |
| Serrure électrique | ✅ | ✅ | ✅ | ✅ |
| Caméra de surveillance | ✅ | ✅ | ✅ | ✅ |
| Poste de sécurité | ✅ | ✅ | ✅ | ✅ |

> **6 composants font l'unanimité des 4 descriptions.**

### 1.2 Flux / connexions

| Flux | Formel | Conv. | Liste | Narratif |
|---|:---:|:---:|:---:|:---:|
| Badge → Lecteur RFID (lecture identifiant) | ✅ | ✅ | ✅ | ✅ |
| Lecteur → Contrôleur (identifiant badge) | ✅ | ✅ | ✅ | ✅ |
| Contrôleur → Base de données (requête autorisation) | ✅ | ✅ | ✅ | ✅ |
| Base de données → Contrôleur (réponse autorisation) | ✅ | ✅ | ✅ | ✅ |
| Contrôleur → Serrure (commande ouverture) | ✅ | ✅ | ✅ | ✅ |
| Contrôleur → Poste de sécurité (alerte accès refusé) | ✅ | ✅ | ✅ | ✅ |
| Caméra → Poste de sécurité (flux vidéo) | ❌ | ❌ | ✅ | ✅ |

> **6 flux sont communs à toutes les descriptions. Le flux Caméra→Poste est explicite dans 2 styles seulement (liste et narratif l'impliquent, formel et conversationnel le rendent implicite).**

### 1.3 Acteurs / stakeholders

| Acteur | Présence |
|---|---|
| Personne portant un badge (employé, utilisateur) | Toutes les descriptions |
| Personnel de sécurité (agent, poste de sécurité) | Toutes les descriptions |

### 1.4 Exigences explicites

| Exigence | Formulation dans les descriptions |
|---|---|
| **REQ-1** : Disponibilité | "24h/24 7j/7" (formel, liste) / "tout le temps, jour et nuit" (conversationnel) / "sans interruption, 24 heures sur 24" (narratif) |
| **REQ-2** : Performance | "< 2 secondes" (toutes) |

---

## 2. Comparaison par style — Niveau Opérationnel

### 2.1 Tableau comparatif

| Critère | Style Formel | Style Conversationnel | Style Liste | Style Narratif |
|---|---|---|---|---|
| **system_name** | "Système de contrôle d'accès du bâtiment" | "Système de Contrôle d'Accès **et de Surveillance**" ⚠️ | "Système de contrôle d'accès bâtiment" | "Système de Contrôle d'Accès au Bâtiment" |
| **Nb stakeholders** | 2 | 2 | 2 | 2 |
| **Stakeholders (noms exacts)** | Utilisateur, Agent de sécurité | personne, **poste de sécurité** ❌ | Utilisateur, Agent de sécurité | Employés, Personnel de sécurité |
| **Nb systèmes externes** | 2 | 1 | **0** ❌ | 4 |
| **Systèmes externes (noms)** | Base de données des autorisations, Caméra de surveillance | base de données | *(aucun)* | Base de données, **Serrure électrique** ⚠️, **Poste de sécurité** ⚠️, **Caméras de surveillance** ⚠️ |
| **Nb use cases** | 2 | 3 | 2 | 2 |
| **Use cases (noms)** | Gérer l'accès d'un utilisateur ; Notifier une tentative d'accès refusée | Contrôler l'accès d'une personne ; Notifier un accès non autorisé ; **Filmer les entrées** ⚠️ | Accéder au bâtiment ; Surveiller les accès | Accéder au bâtiment ; Notifier tentative d'accès non autorisé |
| **Nb exigences** | **2** ✅ | 8 ⚠️ | 7 ⚠️ | 5 ⚠️ |
| **Nb scénarios** | 2 | 3 | 2 | 2 |
| **Nb warnings LLM** | **1** | 0 | 0 | **2** |

### 2.2 Détail des exigences générées

**Style Formel (2 — exact)** ✅
- REQ-OP-001 : "Le système doit fonctionner 24h/24 et 7j/7."
- REQ-OP-002 : "Le temps entre la lecture du badge et le déverrouillage de la porte ne doit pas dépasser 2 secondes."

**Style Conversationnel (8 — sur-décomposées)** ⚠️
- 2 exigences de référence + 6 reformulations de comportements décrits (ex: "Le système doit déverrouiller automatiquement la porte si la personne a le droit d'entrer." — c'est une fonction, pas une exigence).

**Style Liste (7 — sur-décomposées)** ⚠️
- 2 exigences de référence + 5 reformulations des flux décrits (ex: "Le système doit permettre l'identification des badges RFID." — comportement normal, pas une exigence).

**Style Narratif (5 — mélangées)** ⚠️
- 2 exigences de référence + 3 reformulations fonctionnelles (ex: "Le système doit permettre aux employés autorisés d'accéder au bâtiment." — objectif, pas exigence de conception).

---

## 3. Comparaison par style — Niveau Logique

### 3.1 Tableau comparatif

| Critère | Style Formel | Style Conversationnel | Style Liste | Style Narratif |
|---|---|---|---|---|
| **Nb de composants (parts)** | **3** | 5 | 5 | 4 |
| **Composants identifiés** | Lecteur de Badges ; Contrôleur d'Accès Central ; Module de Commande Serrure | LecteurDeBadge ; ControleurAccesCentral ; ActionneurDePorte ; SystemeDeNotification ; **CameraDeSurveillance** ⚠️ | ComposantLecteurBadge ; ComposantMoteurAutorisation ; ComposantActionneurPorte ; ComposantGenerateurAlerte ; **ComposantCameraVideo** ⚠️ | LecteurBadge ; ControleurAcces ; GestionnairePorte ; GestionnaireAlertes |
| **Nb connexions internes** | 2 | 3 | 3 | **7** |
| **Connexions référencent des éléments ext.** | Non | Non | Non | **Oui** ❌ |
| **Nb ports total** | 7 | 10 | **12** | 11 |
| **Nb exigences allouées** | 0 ❌ | 0 ❌ | **5** ✅ | 0 ❌ |
| **Nb warnings** | 2 | 0 | 0 | 1 |

### 3.2 Détail des connexions

**Style Formel (2 connexions internes)** — minimal mais cohérent
- `Lecteur de Badges → Contrôleur d'Accès Central` : Identifiant Badge
- `Contrôleur d'Accès Central → Module de Commande Serrure` : Commande Ouverture Serrure

**Style Conversationnel (3 connexions)** — cohérent
- `LecteurDeBadge → ControleurAccesCentral` : Numéro de badge
- `ControleurAccesCentral → ActionneurDePorte` : Statut d'accès Autorisé
- `ControleurAccesCentral → SystemeDeNotification` : Statut d'accès Non Autorisé

**Style Liste (3 connexions)** — cohérent avec bonne traçabilité
- `ComposantLecteurBadge → ComposantMoteurAutorisation` : Identifiant badge
- `ComposantMoteurAutorisation → ComposantActionneurPorte` : Statut autorisation (accordée)
- `ComposantMoteurAutorisation → ComposantGenerateurAlerte` : Statut autorisation (refusée)

**Style Narratif (7 connexions)** ❌ — incohérent
- Référence `Base de données`, `Serrure électrique`, `Poste de sécurité` directement dans les connexions alors que ces éléments ne sont **pas définis comme des `parts`**. Le modèle logique est auto-contradictoire.

---

## 4. Analyse de fidélité

### 4.1 Tableau de fidélité — Niveau Opérationnel

| Style | ✅ Éléments correctement identifiés | ❌ Éléments manquants | ⚠️ Éléments inventés (hallucinations) |
|---|---|---|---|
| **Formel** | Lecteur RFID, Contrôleur, Base de données, Serrure, Caméra, Agent de sécurité, REQ-001 (24h/7j), REQ-002 (2s) | Poste de sécurité absent des external_systems (référencé uniquement dans les scénarios) | *(aucun)* |
| **Conversationnel** | Lecteur RFID, Contrôleur, Base de données, Serrure, Caméra, REQ-001, REQ-002 | Poste de sécurité absent des external_systems | "**poste de sécurité**" classé comme *stakeholder* (c'est un système) ; "Filmer les entrées" comme use case autonome (implicite, non formulé) ; "et de Surveillance" ajouté au system_name ; 6 exigences qui sont des comportements décrits reformulés |
| **Liste** | Tous les 6 composants identifiés (même s'ils sont tous dedans), Utilisateur, Agent de sécurité, REQ-001, REQ-002, flux caméra→poste | Aucun système externe identifié (la limite du système est incorrecte) | 5 exigences supplémentaires = reformulations de comportements normaux |
| **Narratif** | Lecteur RFID, Contrôleur, REQ-001, REQ-002, Employés, Personnel de sécurité | Caméra absente des parts logiques | "**Serrure électrique**" et "**Caméras de surveillance**" classées comme systèmes *externes* (ce sont des composants du système) ; au niveau logique, connexions vers des éléments non définis |

### 4.2 Tableau de fidélité — Niveau Logique

| Style | ✅ Éléments correctement identifiés | ❌ Éléments manquants | ⚠️ Éléments inventés / incohérents |
|---|---|---|---|
| **Formel** | Lecteur (→ Lecteur de Badges), Contrôleur (→ Contrôleur d'Accès Central), Serrure (→ Module de Commande Serrure), 2 connexions internes principales | Caméra absente du modèle logique ; Poste de sécurité absent ; 0 exigences allouées | *(aucun)* |
| **Conversationnel** | Lecteur, Contrôleur, Serrure (→ ActionneurDePorte), Alerte (→ SystemeDeNotification), Caméra (→ CameraDeSurveillance) | 0 exigences allouées | CameraDeSurveillance modélisée comme composant interne alors qu'elle était external_system en opérationnel — **incohérence inter-niveaux** |
| **Liste** | Lecteur, Contrôleur (→ ComposantMoteurAutorisation), Serrure (→ ComposantActionneurPorte), Alerte (→ ComposantGenerateurAlerte), Caméra (→ ComposantCameraVideo), 5 exigences allouées | Connexions ne montrent pas le flux vidéo caméra | Nommage préfixé "Composant..." non mentionné dans la description |
| **Narratif** | Lecteur, Contrôleur, Serrure (→ GestionnairePorte), Alerte (→ GestionnaireAlertes) | Caméra absente ; 0 exigences allouées | Connexions vers **Base de données, Serrure électrique, Poste de sécurité** non définis comme parts — **modèle auto-contradictoire** ; 7 connexions dont 5 vers des entités externes non déclarées |

---

## 5. Analyse du code SysML v2

### 5.1 Structure syntaxique

| Critère | Formel | Conversationnel | Liste | Narratif |
|---|:---:|:---:|:---:|:---:|
| Package présent | ✅ | ✅ | ✅ | ✅ |
| `use case def` utilisé (opérationnel) | ✅ | ✅ | ✅ | ✅ |
| `requirement def` utilisé | ✅ | ✅ | ✅ | ✅ |
| `part def` utilisé (logique) | ✅ | ✅ | ✅ | ✅ |
| `port def` ou ports définis | ✅ | ✅ | ✅ | ✅ |
| `connection def` ou `connect` utilisé | ✅ | ✅ | ✅ | ✅ |
| Noms CamelCase cohérents | ✅ | ✅ | ✅ | ✅ |

> Tous les styles produisent un SysML v2 syntaxiquement structuré. Les 4 packages compilent sans erreur majeure de forme.

### 5.2 Correspondance vocabulaire description ↔ SysML

| Style | Correspondance vocabulaire |
|---|---|
| **Formel** | Très bonne : "Lecteur de Badges", "Contrôleur d'Accès Central", "Module de Commande Serrure" — noms proches de la description ✅ |
| **Conversationnel** | Partiellement bonne : "LecteurDeBadge" ✅, "ControleurAccesCentral" ✅, mais "ActionneurDePorte" (invention) ⚠️, "SystemeDeNotification" (abstraction non mentionnée) ⚠️ |
| **Liste** | Artificielle : "ComposantMoteurAutorisation", "ComposantActionneurPorte" — préfixe "Composant" artificiel, "Moteur" pour désigner le contrôleur est une hallucination ⚠️ |
| **Narratif** | Abstractions correctes : "LecteurBadge" ✅, "ControleurAcces" ✅, "GestionnairePorte" ✅, "GestionnaireAlertes" ✅ — bon niveau d'abstraction |

### 5.3 Éléments ajoutés dans la traduction JSON → SysML

| Style | Ajouts dans le SysML non présents dans le JSON |
|---|---|
| **Formel** | Aucun ajout significatif ✅ |
| **Conversationnel** | `actor AgentDeSecurite` ajouté dans use case de notification (absent du JSON) ⚠️ |
| **Liste** | Interfaces de port plus détaillées (noms de types de données) — enrichissement cohérent ✅ |
| **Narratif** | Connexions vers éléments externes redéfinies en SysML malgré l'incohérence du JSON ❌ |

---

## 6. Classement des styles

### 6.1 Scores par critère (1 = mauvais, 5 = excellent)

| Critère | Style Formel | Style Conversationnel | Style Liste | Style Narratif |
|---|:---:|:---:|:---:|:---:|
| **Fidélité** (résultat = description, rien de plus, rien de moins) | **5** | 2 | 3 | 3 |
| **Complétude** (tous les éléments capturés) | 3 | 3 | **4** | 3 |
| **Absence d'hallucinations** | **5** | 2 | 4 | 3 |
| **Cohérence inter-niveaux** | 4 | 3 | **5** | 2 |
| **Qualité des exigences** | **5** | 2 | 3 | 3 |
| **TOTAL /25** | **22** | 12 | 19 | 14 |

### 6.2 Classement final

| Rang | Style | Score | Commentaire |
|---|---|:---:|---|
| 🥇 1 | **Style Formel** | 22/25 | Fidèle, sans hallucination, exigences précises. Légère lacune : Poste de sécurité non formalisé en externe, caméra absente du logique. |
| 🥈 2 | **Style Liste** | 19/25 | Complétude maximale, cohérence inter-niveaux excellente, exigences allouées. Défaut : limite du système incorrecte (tout mis à l'intérieur), noms artificiels. |
| 🥉 3 | **Style Narratif** | 14/25 | Bonne abstraction, bon vocabulaire. Défaut majeur : modèle logique auto-contradictoire (connexions vers des éléments non définis). |
| 4 | **Style Conversationnel** | 12/25 | Inventions multiples : stakeholder erroné, 8 exigences verboses, use case non fondé. Incohérence interne (caméra externe→interne). |

---

## 7. Recommandations pour améliorer les prompts

### 7.1 Pourquoi certains styles produisent des hallucinations

#### Problème A : Style conversationnel → sur-génération d'exigences
Le style "En gros, on a un bâtiment..." pousse le LLM à **inférer des besoins implicites** parce que la description est formulée comme une *liste de comportements souhaités* plutôt que comme une description de système. Le LLM transforme chaque phrase comportementale en exigence.

**Fix pour `backend/prompts/operational_prompt.py`** — Ajouter dans `RÈGLES DE FIDÉLITÉ` :
```
- Les exigences sont UNIQUEMENT les contraintes explicites (chiffres, SLAs, disponibilité).
  Un comportement fonctionnel décrit (ex: "la porte se déverrouille") N'EST PAS une exigence.
  Ne génère PAS d'exigence à partir d'un comportement normal du système.
```

#### Problème B : Style conversationnel → "poste de sécurité" comme stakeholder
La phrase "une alerte est envoyée **au** poste de sécurité" est ambiguë : le LLM interprète "au" comme un destinataire humain. Le prompt n'explique pas suffisamment la distinction système/acteur.

**Fix pour `backend/prompts/operational_prompt.py`** — Ajouter dans `MÉTHODOLOGIE` :
```
- Un stakeholder est TOUJOURS une PERSONNE ou une ORGANISATION (jamais un système matériel).
  Si la description mentionne un équipement comme destinataire (ex: "poste de sécurité"),
  c'est un SYSTÈME EXTERNE, pas un stakeholder.
```

#### Problème C : Style liste → périmètre du système incorrect
Le style liste énumère les composants sans préciser leur relation au système. Le LLM met **tout à l'intérieur** car "Composants :" suggère des éléments internes. Il manque un critère de décision pour la frontière.

**Fix pour `backend/prompts/operational_prompt.py`** — Ajouter dans `MÉTHODOLOGIE` :
```
- Pour délimiter le périmètre : un composant est EXTERNE si le système l'interroge, le commande,
  ou en reçoit des données sans le contenir physiquement. Exemple : une base de données
  interrogée via réseau est un système externe.
```

#### Problème D : Style narratif → modèle logique auto-contradictoire
Le style narratif décrit des interactions avec des entités externes (base de données, serrure) de façon fluide. Le LLM au niveau logique crée des connexions vers ces entités sans les définir comme `parts`, car le contexte narratif le pousse à modéliser toutes les interactions.

**Fix pour `backend/prompts/logical_prompt.py`** — Renforcer la règle existante :
```
- Ne crée PAS de connexion vers un composant qui n'est pas défini dans la liste "parts".
  Si une fonction interagit avec un système externe (base de données, système distant),
  modélise un PORT de sortie sur le composant interne, sans connexion vers l'extérieur.
```

### 7.2 Pourquoi certains styles produisent des résultats incomplets

#### Problème E : Caméra de surveillance absente du niveau logique (formel et narratif)
Le style formel classe la caméra comme "système externe" au niveau opérationnel. Le niveau logique hérite ce choix et ne crée pas de `part` pour la caméra. C'est un **problème de propagation inter-niveaux**.

**Fix pour `backend/prompts/logical_prompt.py`** — Ajouter :
```
- Même si un composant a été classé "système externe" au niveau opérationnel, s'il est
  PHYSIQUEMENT PRÉSENT dans la description et réalise des fonctions internes, crée un
  composant logique pour lui. Le périmètre opérationnel n'est pas toujours le même que
  le périmètre logique/physique.
```

#### Problème F : 0 exigences allouées dans 3 styles sur 4
Le prompt logique ne demande pas explicitement d'allouer les exigences opérationnelles aux composants.

**Fix pour `backend/prompts/logical_prompt.py`** — Ajouter dans la section `RÈGLES` :
```
- Pour CHAQUE exigence de performance mentionnée (délai, disponibilité), identifie quel(s)
  composant(s) la réalisent et place cette exigence dans "requirements" avec un lien vers
  le composant. Ne laisse jamais "requirements" vide si des exigences ont été définies
  au niveau opérationnel.
```

### 7.3 Règles concrètes à ajouter dans les prompts

#### `backend/prompts/operational_prompt.py` — Ajouter dans `RÈGLES DE FIDÉLITÉ` :
```
- DISTINCTION STAKEHOLDER / SYSTÈME EXTERNE : Un stakeholder est une personne ou organisation.
  Un dispositif, équipement ou logiciel est un système externe. Ne confonds jamais les deux.
- EXIGENCES UNIQUEMENT EXPLICITES : Ne génère des requirements QUE pour des contraintes
  mesurables (temps, disponibilité, capacité) mentionnées dans la description. Les comportements
  fonctionnels décrits ne sont pas des exigences.
- PÉRIMÈTRE : Un système interrogé via réseau/protocole est un système externe. Un composant
  physique installé dans le bâtiment et contrôlé par le système est un composant interne.
```

#### `backend/prompts/logical_prompt.py` — Ajouter dans `RÈGLES DE FIDÉLITÉ` :
```
- COHÉRENCE DES CONNEXIONS : Toute connexion doit lier deux composants définis dans "parts".
  Une connexion vers un élément non défini dans "parts" est INTERDITE.
- ALLOCATION DES EXIGENCES : Si le contexte fonctionnel contient des requirements avec délais
  ou disponibilité, alloue-les aux composants concernés. Ne laisse pas "requirements" vide.
- COMPOSANTS PHYSIQUES : Un composant physiquement présent dans le système (caméra, serrure)
  doit apparaître comme un part, même s'il a été classé "externe" au niveau opérationnel.
```

### 7.4 Style recommandé pour les utilisateurs

**⭐ Le style formel produit les meilleurs résultats.**

Le style formel ("Le système X est composé de... Il réalise... En cas de... Le système doit...") produit les résultats les plus fidèles parce que :

1. **Structure explicite** : "est composé de" identifie clairement les composants
2. **Flux explicites** : "transmet", "envoie une commande", "déclenche une alerte" sont des verbes d'interaction précis
3. **Exigences bien formulées** : "doit fonctionner 24h/24", "ne doit pas dépasser 2 secondes" sont des contraintes mesurables
4. **Vocabulaire stable** : les mêmes termes sont répétés, réduisant l'ambiguïté

**Recommandation utilisateur** : Encourager les rédacteurs à utiliser un style formel avec :
- Des phrases de type "Le composant X réalise Y"
- Des flux explicites "X envoie Z à Y"
- Des exigences chiffrées "Le délai doit être inférieur à N secondes"
- Éviter les formulations conversationnelles ("en gros", "genre") qui poussent le LLM à inférer

---

## 8. Prochaines actions

### 8.1 Priorité HAUTE — Corrections de prompts

| # | Fichier | Modification | Impact attendu |
|---|---|---|---|
| P1 | `backend/prompts/operational_prompt.py` | Ajouter règle distinction Stakeholder/Système externe | Élimine "poste de sécurité" comme stakeholder (conversationnel) |
| P2 | `backend/prompts/operational_prompt.py` | Ajouter règle exigences = contraintes mesurables seulement | Réduit à 2 req au lieu de 7-8 (conversationnel, liste) |
| P3 | `backend/prompts/logical_prompt.py` | Interdire connexions vers éléments non définis dans parts | Corrige le modèle auto-contradictoire (narratif) |
| P4 | `backend/prompts/logical_prompt.py` | Forcer l'allocation des exigences de performance | 3 styles sur 4 ont 0 requirements alloués |

### 8.2 Priorité MOYENNE — Ajustements du pipeline

| # | Composant | Action | Bénéfice |
|---|---|---|---|
| M1 | `level_service.py` | Vérifier la cohérence opérationnel→logique : si un external_system en opérationnel est physique, le reclasser en part logique | Évite la perte de la caméra entre niveaux |
| M2 | `backend/prompts/logical_prompt.py` | Ajouter une instruction explicite sur le périmètre logique vs opérationnel | Cohérence inter-niveaux |
| M3 | `fidelity_checker.py` | Ajouter contrôle : requirements alloués > 0 si requirements opérationnels > 0 | Détection automatique de l'oubli d'allocation |

### 8.3 Priorité BASSE — Nouveaux tests

| # | Test | Description |
|---|---|---|
| T1 | Style hybride | Tester un style qui combine la précision du formel avec l'exhaustivité du liste (flux explicites + exigences chiffrées + composants listés avec périmètre) |
| T2 | Système différent | Répéter l'expérience sur un autre système (ex: système de téléphonie, robot industriel) pour valider que les conclusions sont généralisables |
| T3 | Post-corrections | Relancer les 4 styles après application des corrections P1-P4 et comparer les scores de fidélité |
| T4 | Niveau technique | Analyser le niveau technique des 4 styles (même méthodologie) pour détecter si les hallucinations se propagent ou sont stoppées par le fidelity checker |

---

*Analyse réalisée par le pipeline SysML v2 — Les données brutes sont dans `experiments/results/controle_acces/{style}/*.md`*
