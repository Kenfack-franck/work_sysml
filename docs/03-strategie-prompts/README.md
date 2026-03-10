# 03 - Strategie de prompts SysML v2

## Le probleme

Un prompting naif des LLMs produit du code SysML v2 syntaxiquement invalide. Les modeles de langage inventent des constructions qui n'existent pas dans la specification OMG, melangent des syntaxes de SysML v1 et v2, et produisent des identifiants incompatibles avec l'editeur SysON.

Les premiers tests ont montre que plus de 60% du code genere contenait au moins une erreur de syntaxe majeure, rendant le code inutilisable dans un environnement de modelisation reel.

## La solution

Une strategie de prompts structures reposant sur quatre piliers :

1. **Templates valides** : chaque prompt inclut un template complet extrait et valide a partir des 33 fichiers de la specification OMG, garantissant que le LLM dispose d'un modele syntaxiquement correct a suivre.

2. **Regles de compatibilite SysON (RS1-RS9)** : un ensemble de 9 regles injectees dans chaque prompt pour assurer que le code genere est directement importable dans l'editeur SysON sans modification manuelle.

3. **Exigences de fidelite (F1-F5)** : 5 contraintes qui empechent le LLM d'inventer des elements absents des reponses utilisateur, tout en signalant les incoherences et les manques.

4. **Coherence de nommage inter-packages** : un mecanisme d'extraction et de re-injection des identifiants entre packages successifs pour garantir la coherence des references croisees.

## Pages de cette section

- [Problematique initiale](problematique-initiale.md) -- Les erreurs de syntaxe observees lors des premiers tests et la motivation de l'approche
- [Templates bases sur la specification OMG](templates-officiels.md) -- Les 33 fichiers analyses et la structure des templates valides
- [Regles de compatibilite SysON (RS1-RS9)](regles-syson.md) -- Les 9 regles de compatibilite avec l'editeur SysON
- [Coherence de nommage inter-packages](coherence-inter-packages.md) -- Le mecanisme de propagation des identifiants entre packages
- [Exigences de fidelite (F1-F5)](fidelite-f1-f5.md) -- Les 5 contraintes de fidelite aux reponses utilisateur
- [Matrice des 15 prompts SysML v2](matrice-prompts.md) -- Vue d'ensemble des 15 prompts, leurs fonctions Python et leurs regles
