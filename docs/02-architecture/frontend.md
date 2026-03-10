# Frontend (Streamlit)

Le frontend est une application Streamlit (`app.py`, 878 lignes) qui fournit une interface utilisateur guidee pour la generation de modeles SysML v2.

## Organisation en onglets

L'interface principale est divisee en 4 onglets :

### 1. Sections (formulaires guides)

Formulaires dynamiques charges depuis `GET /api/sections`. Chaque niveau MBSE possede ses propres sections avec des champs texte, des descriptions et des exemples. L'utilisateur remplit les sections en langage naturel pour decrire son systeme.

### 2. Resultats

Affichage structure du resultat de generation :
- **Summary** : resume du modele genere (nombre d'elements, packages, relations)
- **Warnings** : alertes et suggestions d'amelioration
- **Validation** : score de validation syntaxique et detail des erreurs eventuelles

### 3. Code SysML

Affichage du code SysML v2 brut genere avec coloration syntaxique. Permet de visualiser et copier le code complet du niveau courant ou de l'ensemble des niveaux.

### 4. Debug

Onglet technique affichant les echanges LLM complets :
- Prompts envoyes au LLM (avec les sections, regles, schema JSON, templates)
- Reponses brutes du LLM
- Temps de generation et tokens consommes

## Sidebar

La barre laterale contient les elements de navigation et de gestion :

### Statut backend
Indicateur de connexion au backend FastAPI avec verification periodique.

### Gestion des sessions
- **Creer** une nouvelle session
- **Renommer** une session existante
- **Supprimer** une session
- **Charger** une session precedente

### Navigation par niveaux
Navigation entre les 4 niveaux MBSE avec indicateurs visuels :
- Icones par niveau (operationnel, fonctionnel, logique, technique)
- Statut de chaque niveau (non demarre, en cours, complete, erreur)

### Bouton SysON push
Bouton pour pousser le code SysML v2 genere vers Eclipse SysON pour visualisation et edition graphique.

## Workflow utilisateur

Le workflow typique suit les etapes suivantes :

1. **Choisir ou creer une session** via la sidebar
2. **Remplir les sections** du niveau operationnel dans l'onglet Sections
3. **Generer** le code SysML v2 en cliquant sur le bouton de generation
4. **Valider** le resultat dans l'onglet Resultats (score, warnings)
5. **Visualiser** le code dans l'onglet Code SysML
6. **Passer au niveau fonctionnel** et repeter les etapes 2-5
7. **Continuer** pour les niveaux logique et technique
8. **Pousser vers SysON** pour visualiser le modele complet dans l'editeur graphique

Les sections sont dynamiques et chargees depuis le backend via `GET /api/sections`. Chaque niveau possede ses propres sections adaptees au type de modelisation attendu.
