# Analyse Comparative V2 — Pipeline SysML v2 (Prompts corrigés P1-P4)
## Système testé : Contrôle d'accès d'un bâtiment

*Généré le 2026-02-21 — Prompts version 2 (corrections P1, P2, P3, P4 appliquées)*

> ⚠️ **Note importante** : Le quota journalier de l'API Gemini (20 req/jour/projet × 3 projets = 60 req/jour) a été épuisé pendant l'exécution. Seul `style_conversationnel` a pu être exécuté complètement. Les styles formel, liste et narratif sont marqués `⏳ En attente (quota)`. L'analyse complète sera mise à jour lors de la prochaine exécution.

---

## 1. Éléments de référence attendus

*(Identiques à V1 — la vérité terrain ne change pas)*

| Composant | Présent dans toutes les descriptions |
|---|:---:|
| Lecteur de badges RFID | ✅ |
| Contrôleur central | ✅ |
| Base de données des autorisations | ✅ |
| Serrure électrique | ✅ |
| Caméra de surveillance | ✅ |
| Poste de sécurité | ✅ |

**Acteurs** : Personne/Employé, Personnel de sécurité  
**Exigences** : Disponibilité 24h/24 7j/7 ; Temps de réponse < 2 secondes

---

## 2. Comparaison par style — Niveau Opérationnel

| Critère | Style Formel | Style Conversationnel | Style Liste | Style Narratif |
|---|---|---|---|---|
| **system_name** | ⏳ | "Système de contrôle d'accès au bâtiment" | ⏳ | ⏳ |
| **Nb stakeholders** | ⏳ | **1** (vs 2 en V1) | ⏳ | ⏳ |
| **Stakeholders (noms)** | ⏳ | "Personne" ✅ | ⏳ | ⏳ |
| **Nb systèmes externes** | ⏳ | **3** (vs 1 en V1) | ⏳ | ⏳ |
| **Systèmes externes** | ⏳ | "porte", "poste de sécurité" ✅, "caméras" ✅ | ⏳ | ⏳ |
| **Nb use cases** | ⏳ | **2** (vs 3 en V1) ✅ | ⏳ | ⏳ |
| **Use cases** | ⏳ | "Contrôler l'accès" ; "Notifier le poste de sécurité" | ⏳ | ⏳ |
| **Nb exigences** | ⏳ | **2** (vs 8 en V1) ✅ | ⏳ | ⏳ |
| **Nb warnings LLM** | ⏳ | 2 | ⏳ | ⏳ |

### Améliorations opérationnelles observées (style_conversationnel)

- ✅ **P1 efficace** : "poste de sécurité" correctement reclassé en `external_systems` (vs stakeholder en V1)
- ✅ **P2 efficace** : 2 exigences chiffrées exactement, contre 8 en V1 dont 6 comportements fonctionnels
- ✅ **P2 efficace** : "Filmer les entrées" supprimé en tant que use case distinct (absorbé dans les warnings)
- ✅ Le LLM ajoute des **warnings explicatifs** pertinents : ambiguïté base de données, ambiguïté caméras
- ⚠️ Un seul stakeholder "Personne" — le personnel de sécurité est implicite (il reçoit les alertes) mais absent

---

## 3. Comparaison par style — Niveau Logique

| Critère | Style Formel | Style Conversationnel | Style Liste | Style Narratif |
|---|---|---|---|---|
| **Nb composants (parts)** | ⏳ | **5** | ⏳ | ⏳ |
| **Composants** | ⏳ | LecteurRFID ; ControleurAcces ; BaseDeDonneesAutorisations ; ActionneurSerrure ; SerrurePhysique | ⏳ | ⏳ |
| **Nb connexions** | ⏳ | **5** | ⏳ | ⏳ |
| **Connexions vers éléments non définis** | ⏳ | **0** ✅ (vs connexions invalides possibles en V1) | ⏳ | ⏳ |
| **Nb ports** | ⏳ | **11** | ⏳ | ⏳ |
| **Nb exigences allouées** | ⏳ | **0** ❌ (P4 non efficace) | ⏳ | ⏳ |
| **Nb warnings** | ⏳ | 2 | ⏳ | ⏳ |

### Améliorations logiques observées (style_conversationnel)

- ✅ **P3 efficace** : Toutes les 5 connexions relient des parts définis dans la liste — 0 connexion invalide
- ✅ **P3 efficace** : La base de données est modélisée comme un `part` interne avec ports — pas de connexion externe fantôme
- ✅ La caméra de surveillance est absente (warnings du niveau opérationnel propagés correctement)
- ❌ **P4 non efficace** : `requirements: []` vide malgré 2 exigences opérationnelles (REQ-OP-001, REQ-OP-002)
- ⚠️ `SerrurePhysique` et `ActionneurSerrure` sont deux parts distincts (bonne séparation logique/physique)

---

## 4. Analyse de fidélité

| Style | ✅ Correctement identifié | ❌ Manquant | ⚠️ Inventé / incorrect |
|---|---|---|---|
| **Conversationnel V2** | Personne (porteur badge), Lecteur RFID, Contrôleur, Base de données, Serrure (→ ActionneurSerrure + SerrurePhysique), REQ-001 (24h/24), REQ-002 (2s), 5 connexions logiques valides | Personnel de sécurité absent des stakeholders ; Caméra absente du modèle logique ; 0 exigences allouées | *(aucune hallucination détectée)* ✅ |
| **Formel V2** | ⏳ | ⏳ | ⏳ |
| **Liste V2** | ⏳ | ⏳ | ⏳ |
| **Narratif V2** | ⏳ | ⏳ | ⏳ |

---

## 5. Analyse du code SysML v2

**Style conversationnel V2** — code SysML généré :

| Critère | Résultat |
|---|---|
| Structure syntaxique (packages, part def, ports) | ✅ Présents et cohérents |
| Noms correspondant au vocabulaire de la description | ✅ "LecteurRFID", "ControleurAcces" — vocabulaire fidèle |
| Éléments dans le SysML non présents dans le JSON | ⚠️ Vérification en cours |
| Connexions dans le SysML vers des éléments non définis | ✅ Aucune (cohérent avec P3) |

---

## 6. Classement des styles (partiel — 1 style sur 4 disponible)

| Rang | Style | Score V2 /25 | Évolution vs V1 |
|---|---|:---:|:---:|
| — | **Style Conversationnel** | **~20/25** | ↑ +8 (vs 12/25 en V1) |
| ⏳ | Style Formel | ⏳ | — |
| ⏳ | Style Liste | ⏳ | — |
| ⏳ | Style Narratif | ⏳ | — |

*Score conversationnel V2 estimé : Fidélité 4/5 + Complétude 3/5 + Absence hallucination 5/5 + Cohérence inter-niveaux 4/5 + Qualité exigences 5/5 = 21/25*

---

## 7. Recommandations complémentaires (post-V2)

### Problème résiduel : P4 non efficace

Le champ `requirements` reste vide au niveau logique malgré P4. L'investigation révèle la cause racine : **le modèle fonctionnel transmis comme contexte au niveau logique ne contient pas les exigences opérationnelles**. La règle P4 demande de reprendre les exigences "des niveaux précédents", mais le prompt logique ne reçoit que le modèle fonctionnel, pas le modèle opérationnel.

**Fix recommandé** : Dans `backend/services/level_service.py`, modifier la construction du contexte pour `generate_logical` en injectant les exigences opérationnelles dans le modèle fonctionnel transmis au prompt logique.

### Nouveau problème détecté : Personnel de sécurité absent

La règle P1 a correctement retiré "poste de sécurité" des stakeholders, mais le "personnel de sécurité" qui opère le poste est aussi absent. Le système ne modélise aucun opérateur humain côté sécurité.

**Fix suggéré** : Ajouter une règle dans le prompt opérationnel : "Si la description mentionne un équipement qui est opéré par un humain (poste de sécurité, station de surveillance), identifie l'humain qui l'opère comme stakeholder distinct de l'équipement."

---

## 8. Prochaines actions

| # | Action | Statut |
|---|---|---|
| A1 | Relancer styles formel, liste, narratif en V2 (quota reset le lendemain) | ⏳ À faire demain |
| A2 | Corriger P4 : injecter exigences opérationnelles dans le contexte fonctionnel→logique | ⏳ À implémenter |
| A3 | Compléter ANALYSE_COMPARATIVE.md V2 avec les 3 styles restants | ⏳ Après A1 |
| A4 | Créer V3 avec P4 corrigé + re-tester | ⏳ Après A2 |

---

*Données brutes dans `experiments/results/controle_acces_v2/style_conversationnel/`*
