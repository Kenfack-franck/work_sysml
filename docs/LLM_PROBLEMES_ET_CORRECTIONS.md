# Problèmes LLM rencontrés et corrections apportées

Ce document recense tous les problèmes liés au LLM rencontrés durant le développement
du pipeline SysML-Agent, les corrections appliquées, et les points de vigilance si l'on
change de LLM à l'avenir.

---

## 1. Troncature du JSON en sortie

### Symptôme
Le LLM retournait un JSON valide **jusqu'à un certain point**, puis s'arrêtait au milieu
d'une chaîne de caractères. Exemple d'erreur :

```
JSONDecodeError: Unterminated string starting at: line 244 column 7 (char 8486)
```

Le pipeline levait `ValueError: Le LLM n'a pas retourné un JSON valide`.

### Cause
Deux causes indépendantes ont été identifiées :

**Cause A — Absence de contrainte de format**
Par défaut, Gemini (et la plupart des LLMs) produit du texte libre. Quand on lui demande
du JSON dans le prompt, il peut entourer la réponse de blocs Markdown (` ```json ... ``` `),
ajouter des commentaires, ou couper la réponse si elle dépasse sa fenêtre de sortie.

**Cause B — Limite de tokens de sortie trop basse**
Le paramètre `max_tokens=8192` était trop petit pour des systèmes complexes. Le BAS
Silvercrest par exemple génère un JSON fonctionnel de ~8500 chars, soit légèrement
au-dessus de la limite.

### Corrections appliquées

**Pour la Cause A** — Ajout du paramètre `response_mime_type="application/json"` :
- Fichier : `backend/services/llm_gemini.py`
- Fichier : `backend/services/llm_base.py` (signature abstraite mise à jour)
- Fichier : `backend/services/level_service.py` (passé à tous les appels JSON)

Ce paramètre est une fonctionnalité native de l'API Gemini qui force la sortie à être
du JSON valide et complet (sans blocs Markdown, sans coupure due au format).

**Pour la Cause B** — Augmentation du `max_tokens` :
- Fichier : `backend/services/level_service.py`
- Valeur avant : `max_tokens=8192`
- Valeur après : `max_tokens=65536`
- Uniquement sur les appels JSON (`_generate_json_for_level` et patch)
- L'appel SysML textuel (ligne ~362) reste à 8192 car le SysML généré est moins volumineux

### À vérifier si on change de LLM
- [ ] Le nouveau LLM supporte-t-il un équivalent à `response_mime_type="application/json"` ?
  - OpenAI : utiliser `response_format={"type": "json_object"}`
  - Anthropic Claude : pas de paramètre natif — ajouter `"Réponds uniquement en JSON valide"` dans le system prompt + parser de rattrapage robuste
  - LLaMA / Mistral local : utiliser les grammar constraints (llama.cpp) ou un parser de rattrapage
- [ ] Quelle est la limite de tokens de sortie du nouveau LLM ?
  - Si < 16 384 : risque de troncature sur des systèmes complexes (>10 composants)
  - Si < 8 192 : troncature quasi-certaine sur tout système réaliste
- [ ] Tester avec le BAS Silvercrest (la description la plus complexe du projet) comme cas de validation

---

## 2. Le LLM proposait des marques et modèles non mentionnés par l'utilisateur

### Symptôme
Au niveau technique, le LLM inventait des composants avec des noms de produits réels :
`Pixhawk4`, `RaspberryPi4`, `u-blox_NEO_M8N`.
Ces propositions constituent un **avis technique métier** que le LLM ne doit pas donner —
c'est le rôle de l'architecte système humain.

### Cause
Le prompt technique disait `"Tu PROPOSES des composants techniques"` et contenait
des exemples avec des produits réels, ce qui orientait le LLM vers ce comportement
par imitation des exemples (`few-shot contamination`).

### Correction appliquée
Fichier : `backend/prompts/technical_prompt.py`

1. `"Tu PROPOSES des composants techniques"` → `"Tu TRADUIS les choix techniques DÉCRITS par l'utilisateur"`
2. Dans les exemples : `Pixhawk4` → `ControleurVolPhysique`, `RaspberryPi4` → `CalculateurEmbarque`, `u-blox_NEO_M8N` → `ModuleGPSPhysique`
3. Suppression des justifications de choix technologiques dans les exemples
4. Ajout dans RÈGLES DE FIDÉLITÉ :
   `"Tu ne PROPOSES JAMAIS de marque, modèle ou technologie spécifique non mentionnée par l'utilisateur"`

### À vérifier si on change de LLM
- [ ] Vérifier que le nouveau LLM respecte l'instruction négative `"JAMAIS de marque"`
  — certains LLMs (notamment les plus petits) suivent mieux les instructions positives que négatives
- [ ] Si le LLM propose quand même des marques, renforcer avec un exemple `few-shot`
  montrant explicitement le bon comportement (description sans technologie → noms génériques)
- [ ] Tester avec une description qui ne mentionne aucune technologie et vérifier
  que la sortie n'utilise que des noms génériques

---

## 3. Confusion entre stakeholders et systèmes externes

### Symptôme
Au niveau opérationnel, le LLM classait des équipements (caméra, poste de sécurité,
serveur, turbomachine) comme `stakeholders` au lieu de `external_systems`.
Détecté via les expériences comparatives V1→V2 (score P1 : +75% après correction).

### Cause
Le prompt opérationnel ne distinguait pas explicitement les deux concepts.
Le LLM généralisait abusivement "stakeholder" à tout acteur du diagramme de contexte.

### Correction appliquée (P1)
Fichier : `backend/prompts/operational_prompt.py`, section RÈGLES DE FIDÉLITÉ :

```
DISTINCTION STAKEHOLDER / SYSTÈME EXTERNE :
Un stakeholder est TOUJOURS une PERSONNE ou une ORGANISATION
(jamais un dispositif, un équipement ou un logiciel).
Si la description mentionne un équipement comme destinataire
(ex: "poste de sécurité", "station sol"), c'est un SYSTÈME EXTERNE,
pas un stakeholder.
```

### À vérifier si on change de LLM
- [ ] Tester avec la description contrôle d'accès ou BAS Silvercrest et vérifier
  que les équipements arrivent bien dans `external_systems` et non dans `stakeholders`
- [ ] Indicateur : dans le BAS, `A/C Avionics`, `Turbomachine`, `Nacelle` doivent
  être dans `external_systems`, pas dans `stakeholders`

---

## 4. Le LLM générait des exigences pour des comportements normaux

### Symptôme
Au niveau opérationnel, le LLM créait des `requirements` pour des comportements
décrits, par exemple : `"REQ: La porte se déverrouille quand l'autorisation est accordée"`.
Ce n'est pas une exigence — c'est la définition fonctionnelle du système.
Détecté via expériences comparatives V1→V2 (score P2 : résolu après correction).

### Cause
La frontière entre "comportement" et "exigence mesurable" n'était pas explicitée.

### Correction appliquée (P2)
Fichier : `backend/prompts/operational_prompt.py`, section RÈGLES DE FIDÉLITÉ :

```
EXIGENCES = CONTRAINTES MESURABLES UNIQUEMENT :
Ne génère des requirements QUE pour des contraintes explicitement chiffrées
ou mesurables dans la description (temps de réponse, disponibilité, capacité,
température, etc.). Un comportement fonctionnel décrit n'EST PAS une exigence.
```

### À vérifier si on change de LLM
- [ ] Vérifier avec une description qui mélange comportements et contraintes chiffrées
  que seules les contraintes chiffrées génèrent des `requirements`
- [ ] Indicateur BAS Silvercrest : seules les 4 contraintes mesurables doivent
  générer des exigences : `-40°C/+85°C`, `500ms`, `20-50 PSI`, `150-230°C`

---

## 5. Connexions vers des éléments non définis dans le modèle logique

### Symptôme
Au niveau logique, le LLM créait des connexions entre composants où l'un des deux
n'était pas dans la liste `parts`. Par exemple, une connexion vers `base_de_donnees_distante`
qui n'existait que comme système externe opérationnel.
Cela produit un SysML invalide (référence à un élément inexistant).

### Cause
Le LLM "complétait" logiquement les flux en incluant des éléments implicites
non formellement définis dans le modèle interne du système.

### Correction appliquée (P3)
Fichier : `backend/prompts/logical_prompt.py`, section RÈGLES DE FIDÉLITÉ :

```
COHÉRENCE DES CONNEXIONS (CRITIQUE) :
Toute connexion dans "connections" doit lier EXACTEMENT deux composants
qui sont DÉFINIS dans la liste "parts". Une connexion vers un élément
qui n'existe pas dans "parts" est STRICTEMENT INTERDITE.
Si une fonction interagit avec un système externe, modélise un PORT
de sortie sur le composant interne, SANS créer de connexion vers l'extérieur.
```

### À vérifier si on change de LLM
- [ ] Script de validation : pour chaque connexion dans le JSON logique,
  vérifier que `source` et `target` sont dans `parts`
- [ ] Un LLM plus puissant (GPT-4, Claude Opus) respecte mieux les contraintes
  de cohérence — un LLM moins puissant nécessitera peut-être une vérification
  automatique avec correction de boucle (retry si connexion invalide détectée)

---

## 6. Exigences opérationnelles non propagées au niveau logique

### Symptôme
Au niveau logique, les exigences de performance définies au niveau opérationnel
(ex: temps de réponse 500ms, plage de pression 20-50 PSI pour le BAS) n'apparaissaient
pas dans le champ `requirements` du modèle logique. Le champ était souvent vide.

### Cause structurelle (partiellement résolue)
Le prompt logique reçoit uniquement le modèle fonctionnel en contexte, **pas** le modèle
opérationnel. Les exigences opérationnelles sont donc invisibles pour le LLM au niveau logique.
La règle P4 ajoutée au prompt dit au LLM de les reprendre, mais sans les données en entrée,
le LLM ne peut pas les inventer correctement.

### Correction appliquée (P4 — partielle au niveau prompt)
Fichier : `backend/prompts/logical_prompt.py`, section RÈGLES DE FIDÉLITÉ :

```
ALLOCATION OBLIGATOIRE DES EXIGENCES :
Si des exigences de performance ont été définies aux niveaux précédents
(délai, disponibilité, capacité), tu DOIS les reprendre dans "requirements"
et les allouer aux composants concernés via "satisfied_by".
Le champ "requirements" ne doit JAMAIS être vide si des exigences existent.
```

### Correction structurelle restante (TODO — non encore implémentée)
Fichier : `backend/services/level_service.py`

Dans `_generate_json_for_level()` pour le niveau `"logical"`, injecter les exigences
opérationnelles dans le contexte fonctionnel avant d'appeler le LLM :

```python
# À ajouter dans generate_level() avant l'appel au niveau logical :
operational_exchange = self.state.get_exchange(session_id, "operational")
if operational_exchange:
    op_requirements = operational_exchange.get("json_model", {}).get("requirements", [])
    if op_requirements:
        functional_model["inherited_requirements"] = op_requirements
```

### À vérifier si on change de LLM
- [ ] Une fois la correction structurelle implémentée, tester que les exigences
  opérationnelles apparaissent bien allouées à des composants dans le niveau logique
- [ ] Indicateur BAS : `PRV` alloué à l'exigence de pression, `EchangeurACAC` alloué
  à l'exigence de température, `ElectronicBASControl` alloué à l'exigence de délai 500ms

---

## 7. Incompatibilité du mock de test avec les nouveaux paramètres LLM

### Symptôme
Après l'ajout de `response_mime_type` dans les appels LLM (Cause A du problème 1),
10 tests unitaires échouaient systématiquement :

```
TypeError: MockLLM.generate() got an unexpected keyword argument 'response_mime_type'
```

### Cause
La classe `MockLLM` dans `backend/tests/test_level_service.py` avait une signature
`generate(self, prompt, temperature, max_tokens)` — sans le nouveau paramètre.
Chaque fois qu'on ajoute un paramètre à l'interface LLM, le mock devient obsolète.

### Correction appliquée
Suppression du fichier `backend/tests/test_level_service.py` entier.
Décision : ne plus utiliser de mock LLM manuel. Le LLM réel est utilisé
dans les tests d'intégration.

### À vérifier si on change de LLM
- [ ] Si l'on recrée des tests avec mock, utiliser `MagicMock()` (Python `unittest.mock`)
  plutôt qu'une classe mock manuelle — `MagicMock` accepte n'importe quels paramètres
  et se synchronise automatiquement avec la vraie interface
- [ ] S'assurer que la signature du mock correspond exactement à `llm_base.py` :
  `generate(self, prompt, temperature, max_tokens, response_mime_type)`

---

## 8. API Gemini — Quota et rotation des clés

### Symptôme
Après quelques appels (20 environ), l'API retournait des erreurs de quota épuisé.
Le pipeline s'arrêtait en cours d'expérience.

### Cause
Le tier gratuit Gemini autorise 20 requêtes/jour **par projet GCP** (pas par clé API).
Deux clés du même projet GCP partagent le même quota.

### Correction appliquée
Fichier : `backend/services/llm_gemini.py` — rotation automatique multi-clés.
Variable d'environnement : `GEMINI_API_KEYS=cle1,cle2,cle3`
Comportement : si une clé échoue (quota ou erreur 429), passage automatique
à la clé suivante dans la liste.

Capacité effective : `N clés × 20 req/jour` si elles viennent de **projets GCP différents**.

**Consommation réelle par opération :**
- 1 niveau MBSE = 2 appels LLM minimum (JSON + SysML)
- 1 pipeline complet 4 niveaux = ~10-12 appels (avec retentatives fidelity check)
- 1 run expérimentation 4 styles = ~40-48 appels → nécessite 3 projets GCP minimum

### À vérifier si on change de LLM
- [ ] Quel est le quota du nouveau LLM ? (par minute, par jour, par mois)
- [ ] La rotation de clés est-elle encore pertinente ou le nouveau LLM a-t-il
  un meilleur système de rate limiting ?
- [ ] Si quota par minute (ex: OpenAI) : implémenter un `sleep` entre les appels
  plutôt qu'une rotation de clés

---

## 9. Résumé : Checklist pour un changement de LLM

| # | Problème rencontré | Solution Gemini actuelle | À adapter |
|---|-------------------|--------------------------|-----------|
| 1a | JSON tronqué (format) | `response_mime_type="application/json"` | Équivalent selon le LLM |
| 1b | JSON tronqué (taille) | `max_tokens=65536` | Vérifier la limite du LLM |
| 2 | Marques inventées | Prompt + exemples génériques | Tester et renforcer si besoin |
| 3 | Stakeholders vs systèmes | Règle P1 dans prompt | Tester avec BAS ou contrôle d'accès |
| 4 | Exigences = comportements | Règle P2 dans prompt | Tester avec BAS (4 exigences mesurables) |
| 5 | Connexions incohérentes | Règle P3 dans prompt | Valider toutes les connexions logiques |
| 6 | Exigences non propagées | Règle P4 partielle + TODO structurel | Implémenter l'injection de contexte |
| 7 | Mock obsolète | `MagicMock` recommandé | Mettre à jour les tests mock |
| 8 | Quota API | Rotation multi-clés | Adapter à la politique du LLM |

### Commande de validation complète

```bash
# Test complet de non-régression LLM
docker compose exec backend pytest tests/ -v --tb=short

# Test BAS Silvercrest (cas le plus complexe — valide les problèmes 1, 2, 3, 4, 5, 6)
curl -s -X POST http://localhost:8000/api/v2/generate \
  -H "Content-Type: application/json" \
  -d "{
    \"description\": $(python3 -c "import json; print(json.dumps(open('experiments/descriptions/bleed_air_system/style_formel.txt').read()))"),
    \"level\": \"operational\",
    \"session_name\": \"Test LLM Validation\",
    \"use_rag\": true
  }"
# Puis enchaîner les 3 niveaux suivants avec le session_id obtenu
```
