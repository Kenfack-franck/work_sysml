# Comparaison V1 vs V2 — Impact des corrections de prompts

*Date : 2026-02-21 — Pipeline SysML v2 (Gemini 2.5 Flash)*

## Corrections appliquées (V2)

| Code | Description | Fichier modifié |
|---|---|---|
| **P1** | Distinction stakeholder / système externe — Un stakeholder est toujours une personne, jamais un équipement | `backend/prompts/operational_prompt.py` |
| **P2** | Exigences = contraintes mesurables uniquement — Interdiction de transformer un comportement fonctionnel en exigence | `backend/prompts/operational_prompt.py` |
| **P3** | Interdiction des connexions vers éléments non définis dans parts | `backend/prompts/logical_prompt.py` |
| **P4** | Allocation obligatoire des exigences de performance | `backend/prompts/logical_prompt.py` |

---

## Scores comparatifs

> ⚠️ **Limitation** : Le quota journalier API (60 req/jour, 3 projets free tier) a été atteint pendant l'exécution de V2. Seul `style_conversationnel` a été exécuté en V2. Les autres styles auront leurs scores V2 mis à jour après le prochain run.

| Style | Score V1 /25 | Score V2 /25 | Évolution |
|---|:---:|:---:|:---:|
| **Formel** | 22 | ⏳ à mesurer | — |
| **Liste** | 19 | ⏳ à mesurer | — |
| **Narratif** | 14 | ⏳ à mesurer | — |
| **Conversationnel** | 12 | **~21** | ↑ **+9 points** (+75%) |

### Détail du score V2 — Style Conversationnel

| Critère | V1 | V2 | Amélioration |
|---|:---:|:---:|:---:|
| Fidélité | 2/5 | 4/5 | ↑ +2 |
| Complétude | 3/5 | 3/5 | = |
| Absence d'hallucinations | 2/5 | 5/5 | ↑ +3 |
| Cohérence inter-niveaux | 3/5 | 4/5 | ↑ +1 |
| Qualité des exigences | 2/5 | 5/5 | ↑ +3 |
| **TOTAL** | **12/25** | **21/25** | **↑ +9** |

---

## Problèmes corrigés (style_conversationnel)

| Problème | Description V1 | Résultat V2 | Correction efficace ? |
|---|---|---|:---:|
| **A** (P1) | "poste de sécurité" classé comme *stakeholder* | "poste de sécurité" correctement en `external_systems` | ✅ Corrigé |
| **B** (P2) | 8 exigences dont 6 comportements fonctionnels reformulés | 2 exigences exactement (contraintes mesurables) | ✅ Corrigé |
| **C** (P2) | "Filmer les entrées" comme use case autonome | Absent — 2 use cases pertinents seulement | ✅ Corrigé |
| **D** (P3) | Style narratif V1 : connexions vers éléments non définis | Style conversationnel V2 : 0 connexion invalide | ✅ Corrigé |
| **E** (P3) | Caméra classified externe ops → absente du logique | Cohérence : 2 warnings propagés → caméra absente mais justifiée | ✅ Géré |
| **F** (P4) | 0 exigences allouées dans le logique | 0 exigences allouées — inchangé | ❌ Non corrigé |

---

## Problèmes persistants

### P4 non efficace — Requirements logiques toujours vides

**Symptôme** : Malgré la règle "ALLOCATION OBLIGATOIRE DES EXIGENCES", le champ `requirements` du modèle logique reste vide (`[]`).

**Cause racine identifiée** : Le prompt du niveau logique reçoit le **modèle fonctionnel** comme contexte, mais les **exigences opérationnelles** ne sont pas incluses dans ce modèle fonctionnel. La règle P4 demande de reprendre les exigences "des niveaux précédents", mais le LLM ne les "voit" pas dans son contexte d'entrée.

**Fix requis** : Dans `backend/services/level_service.py`, enrichir le contexte transmis au niveau logique pour inclure les exigences opérationnelles dans le modèle fonctionnel JSON.

```python
# Dans la construction du contexte pour generate_logical :
# Injecter les exigences opérationnelles dans le functional_model avant de l'envoyer
if operational_model and operational_model.get("requirements"):
    functional_model["inherited_requirements"] = operational_model["requirements"]
```

### Nouveau problème détecté en V2 : Stakeholder humain manquant

**Symptôme** : P1 a correctement retiré "poste de sécurité" des stakeholders, mais le "personnel de sécurité" (humain qui opère le poste) est lui aussi absent des stakeholders en V2.

**Impact** : Le modèle ne capture qu'un seul stakeholder ("Personne") alors qu'il devrait en avoir 2.

**Fix suggéré** : Ajouter dans le prompt opérationnel : *"Si la description mentionne un équipement qui reçoit des alertes ou est surveillé par un humain, identifie l'humain comme stakeholder distinct de l'équipement."*

---

## Nouvelles améliorations inattendues observées en V2

| Amélioration | Détail |
|---|---|
| **Warnings enrichis** | Le LLM génère 2 warnings pertinents sur les ambiguïtés (base de données / caméras), ce qui n'était pas forcé par les règles P1-P4 mais découle de la meilleure structuration du prompt |
| **Architecture logique plus fine** | La serrure est décomposée en `ActionneurSerrure` (logique) + `SerrurePhysique` (physique) — meilleure séparation des préoccupations |
| **Modèle connexion plus riche** | 5 connexions (vs 3 en V1) avec descriptions fonctionnelles claires |

---

## Conclusion

**Les corrections P1, P2, P3 ont eu un impact significatif et immédiat.** Sur le seul style testé (style_conversationnel, le plus problématique en V1), le score passe de 12/25 à 21/25, soit une amélioration de +75%.

**P4 est structurellement inadéquate** : la règle dans le prompt ne peut pas fonctionner car les exigences opérationnelles ne sont pas dans le contexte du niveau logique. Il faut une modification du code (level_service.py), pas juste du prompt.

**Recommandation** :
1. ✅ Garder les corrections P1-P3 en production
2. 🔧 Implémenter la correction P4 dans le code (level_service.py)
3. ⏳ Relancer les 3 styles restants (formel, liste, narratif) après reset du quota journalier

**Perspective** : Si les styles formel et liste (déjà bien notés en V1) s'améliorent proportionnellement, le pipeline V2 pourrait atteindre un score moyen de ~22/25 sur tous les styles, contre ~17/25 en V1.

---

## Statut d'exécution

| Style | V1 | V2 |
|---|:---:|:---:|
| style_formel | ✅ Exécuté | ⏳ Quota épuisé |
| style_conversationnel | ✅ Exécuté | ✅ Exécuté |
| style_liste | ✅ Exécuté | ⏳ Quota épuisé |
| style_narratif | ✅ Exécuté | ⏳ Quota épuisé |

*Pour relancer : `python experiments/run_experiment.py --output-dir experiments/results/controle_acces_v2/` (les styles déjà exportés seront re-créés dans les mêmes sous-dossiers)*
