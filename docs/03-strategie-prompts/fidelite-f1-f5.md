# Exigences de fidelite (F1-F5)

Ces 5 exigences sont injectees dans chaque prompt de generation JSON via le bloc `SYSML_FIDELITY_BLOCK`. Elles encadrent le comportement du LLM pour garantir que les donnees generees refletent fidelement les reponses de l'utilisateur, sans invention ni correction silencieuse.

---

## F1 -- Zero invention

**Regle** : Generer UNIQUEMENT ce qui est explicitement decrit dans les reponses de l'utilisateur. Si une section est vide ou absente, le champ JSON correspondant doit etre un tableau vide `[]`. Ne JAMAIS inventer de contenu.

**Exemple concret (test BAS)** : au niveau operationnel, les reponses de l'utilisateur ne contenaient aucune exigence operationnelle explicite (pas de REQ-OP-XXX). Au lieu d'inventer des exigences, le champ `requirements` a ete laisse vide et un avertissement `missing_info` a ete ajoute.

---

## F2 -- Signalement des incoherences

**Regle** : Si un element est mentionne dans un contexte (par exemple un acteur dans un cas d'utilisation) mais absent d'un autre contexte ou il devrait etre defini (par exemple la liste des parties prenantes), ne pas corriger silencieusement. Ajouter un avertissement de type `inconsistency`.

**Exemple concret (test BAS)** : l'acteur "Maintenance facility" etait mentionne dans un cas d'utilisation mais n'apparaissait pas dans la liste des parties prenantes. Un avertissement a ete genere au lieu d'ajouter silencieusement l'acteur manquant.

---

## F3 -- Signalement des manques

**Regle** : Si une information attendue est absente des reponses de l'utilisateur, ajouter un avertissement de type `missing_info` sans inventer de donnees pour combler le manque.

**Exemple concret (test BAS)** : aucune exigence operationnelle explicite n'a ete trouvee dans les reponses. Le message "No explicit operational requirements (e.g., REQ-OP-XXX) were found" a ete ajoute comme avertissement.

---

## F4 -- Vocabulaire exact

**Regle** : Utiliser EXACTEMENT les noms, termes et formulations de l'utilisateur. Ne jamais renommer, traduire ni reformuler. Si l'utilisateur parle de "Bleed Air System", le JSON doit contenir "Bleed Air System" et non "Systeme de prelevement d'air" ou "Air Extraction System".

---

## F5 -- Tracabilite

**Regle** : Chaque element du JSON genere doit pouvoir etre rattache a une section identifiable des reponses de l'utilisateur. Le LLM ne doit pas synthetiser d'elements qui ne correspondent a aucun passage precis des reponses.

---

## Exemple concret d'avertissements

Lors du test sur le cas BAS (Bleed Air System), les exigences de fidelite ont produit les avertissements suivants dans le JSON genere :

```json
[
  {
    "type": "inconsistency",
    "message": "The actor 'Maintenance facility' is mentioned in the use case..."
  },
  {
    "type": "missing_info",
    "message": "No explicit operational requirements..."
  },
  {
    "type": "ambiguity",
    "message": "The operating modes are described with a hierarchical structure..."
  }
]
```

Ces avertissements permettent a l'ingenieur systeme de :

- Identifier rapidement les lacunes dans sa specification
- Corriger les incoherences entre les differentes sections de ses reponses
- Lever les ambiguites avant de valider le modele SysML v2 genere

## Injection dans les prompts

Le bloc de fidelite est defini dans la constante `SYSML_FIDELITY_BLOCK` du module `prompts/_shared.py`. Il est injecte dans chaque prompt de generation JSON, en position 2 (juste apres le role), garantissant que le LLM prend ces contraintes en compte avant de commencer la generation.
