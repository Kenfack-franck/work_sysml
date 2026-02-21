"""
Prompts pour le niveau LOGIQUE (Logical).
Composants logiques, interfaces, architecture système.
"""

import json


def build_logical_json_prompt(description: str, functional_model: dict, rag_examples: list[str] = None, correction_feedback: str = None) -> str:
    """
    Construit le prompt pour générer le modèle logique (JSON).
    
    Args:
        description: Instructions ou précisions supplémentaires
        functional_model: Le modèle fonctionnel validé (contexte)
        rag_examples: Exemples de code SysML v2 pertinents (optionnel)
        correction_feedback: Feedback de correction (optionnel)
    
    Returns:
        Le prompt complet
    """
    # Sérialiser le modèle fonctionnel
    functional_json = json.dumps(functional_model, indent=2, ensure_ascii=False)
    
    prompt = """Tu es un ingénieur système expert en conception d'architecture logique. Tu conçois l'architecture en composants logiques.

=== TON RÔLE ===
À partir du modèle FONCTIONNEL validé, tu :
- REGROUPES les fonctions en COMPOSANTS LOGIQUES cohérents
- DÉFINIS les PORTS et INTERFACES de chaque composant
- ÉTABLIS les CONNEXIONS entre composants
- ALLOUES les EXIGENCES aux composants

=== RÈGLES DE TRAÇABILITÉ ===
- Chaque FONCTION du niveau fonctionnel doit être ALLOUÉE à un composant logique
- Les FLUX FONCTIONNELS deviennent des CONNEXIONS entre ports de composants
- L'architecture doit être INDÉPENDANTE de la technologie (pas de choix technique)
- Les composants sont définis par leur RÔLE, pas leur implémentation

=== RÈGLES DE COHÉSION ===
- Regroupe les fonctions fortement couplées dans un même composant
- Minimise les connexions entre composants
- Définis des interfaces claires (ports)
- Chaque composant doit avoir une responsabilité cohérente

=== RÈGLES DE FIDÉLITÉ ===
- Tout doit découler du niveau fonctionnel — Pas de composants qui ne réalisent aucune fonction
- Pas de connexions qui ne correspondent pas à un flux fonctionnel
- Si quelque chose est ambigu, ajoute un warning
- L'exemple ci-dessous montre uniquement la STRUCTURE attendue. En production, chaque valeur doit provenir EXCLUSIVEMENT du niveau fonctionnel fourni en contexte. Si un élément n'est pas mentionné, il ne doit PAS apparaître dans ton résultat.
- COHÉRENCE DES CONNEXIONS (CRITIQUE) : Toute connexion dans "connections" doit lier EXACTEMENT deux composants qui sont DÉFINIS dans la liste "parts". Une connexion vers un élément qui n'existe pas dans "parts" est STRICTEMENT INTERDITE. Si une fonction interagit avec un système externe (base de données distante, serveur, etc.), modélise un PORT de sortie sur le composant interne concerné, SANS créer de connexion vers l'extérieur.
- COMPOSANTS PHYSIQUES INTERNES : Un composant physiquement présent dans le système et mentionné dans la description (caméra, capteur, serrure, actionneur) DOIT apparaître comme un part dans le modèle logique, même s'il a été classé comme "système externe" au niveau opérationnel. Le périmètre logique inclut tous les composants physiques que le système contrôle.
- ALLOCATION OBLIGATOIRE DES EXIGENCES : Si des exigences de performance ont été définies aux niveaux précédents (délai, disponibilité, capacité), tu DOIS les reprendre dans le champ "requirements" et les allouer aux composants concernés via le champ "satisfied_by". Le champ "requirements" ne doit JAMAIS être vide si des exigences existent dans le contexte fonctionnel ou opérationnel.

=== MÉTHODOLOGIE ===
1. REGROUPEMENT : Identifie les groupes de fonctions cohérents → composants
2. ALLOCATION : Alloue chaque fonction à un composant
3. INTERFACES : Définis les ports d'entrée/sortie de chaque composant
4. CONNEXIONS : Traduis les flux fonctionnels en connexions entre ports
5. EXIGENCES : Alloue les exigences aux composants qui les satisfont
6. VÉRIFICATION : Vérifie que toutes les fonctions sont allouées

=== SCHÉMA JSON ATTENDU (LogicalModel) ===
{
  "system_name": "string",
  "warnings": ["string"],
  "parts": [
    {
      "name": "string",
      "type": "string (optionnel)",
      "description": "string (fonctions allouées)",
      "ports": [
        {
          "name": "string",
          "direction": "in | out | inout",
          "type": "string"
        }
      ],
      "children": []  // Sous-composants si architecture hiérarchique
    }
  ],
  "connections": [
    {
      "from_port": "ComponentA.portOut",
      "to_port": "ComponentB.portIn",
      "type": "flow | connection | interface",
      "item": "string",
      "description": "string (flux fonctionnel correspondant)"
    }
  ],
  "requirements": [
    {
      "id": "string",
      "text": "string",
      "satisfied_by": "string (nom du composant)"
    }
  ]
}

=== EXEMPLE DE STRUCTURE (placeholders — ne pas reproduire ces valeurs) ===
{
  "system_name": "Nom du système (repris depuis le niveau fonctionnel)",
  "warnings": [],
  "parts": [
    {
      "name": "NomComposantLogique",
      "type": "TypeDuComposant",
      "description": "Réalise les fonctions : FonctionA, FonctionB (issues du niveau fonctionnel)",
      "ports": [
        {
          "name": "entree_donnees",
          "direction": "in",
          "type": "TypeDeDonnéesEntrant"
        },
        {
          "name": "sortie_donnees",
          "direction": "out",
          "type": "TypeDeDonnéesSortant"
        }
      ],
      "children": []
    },
    {
      "name": "AutreComposantLogique",
      "type": "TypeDuComposant",
      "description": "Réalise la fonction : FonctionC (issue du niveau fonctionnel)",
      "ports": [
        {
          "name": "entree_depuis_composant1",
          "direction": "in",
          "type": "TypeDeDonnéesSortant"
        }
      ],
      "children": []
    }
  ],
  "connections": [
    {
      "from_port": "NomComposantLogique.sortie_donnees",
      "to_port": "AutreComposantLogique.entree_depuis_composant1",
      "type": "flow",
      "item": "TypeDeDonnéesSortant",
      "description": "Correspond au flux fonctionnel entre FonctionA et FonctionC"
    }
  ],
  "requirements": [
    {
      "id": "REQ-LOG-001",
      "text": "Exigence allouée à ce composant (reprise depuis le niveau opérationnel)",
      "satisfied_by": "NomComposantLogique"
    }
  ]
}
"""

    # Ajout du contexte fonctionnel
    prompt += f"\n\n=== MODÈLE FONCTIONNEL VALIDÉ (CONTEXTE) ===\n{functional_json}\n"

    # Ajout des exemples RAG
    if rag_examples and len(rag_examples) > 0:
        prompt += "\n\n=== EXEMPLES DE SYNTAXE SysML v2 POUR RÉFÉRENCE ===\n"
        for i, example in enumerate(rag_examples[:3], 1):
            prompt += f"Exemple {i}:\n```\n{example}\n```\n\n"

    # Ajout du feedback de correction
    if correction_feedback:
        prompt += f"\n\n=== CORRECTION REQUISE ===\n"
        prompt += f"Un vérificateur automatique a détecté les problèmes suivants : {correction_feedback}\n"
        prompt += "Corrige ces problèmes dans ta réponse.\n"

    # Instructions supplémentaires
    if description and description.strip():
        prompt += f"\n\n=== INSTRUCTIONS SUPPLÉMENTAIRES ===\n{description}\n"

    prompt += "\n\n=== TON RÉSULTAT (JSON UNIQUEMENT, SANS COMMENTAIRE) ==="

    return prompt


def build_logical_sysml_prompt(logical_json: str, rag_examples: list[str] = None) -> str:
    """
    Construit le prompt pour générer le code SysML v2 du niveau logique.
    
    Args:
        logical_json: Le modèle logique en JSON
        rag_examples: Exemples de code SysML v2 pertinents (optionnel)
    
    Returns:
        Le prompt complet
    """
    prompt = """Tu es un expert SysML v2. Tu traduis un modèle logique JSON en code SysML v2 valide.

=== TON RÔLE ===
Génère du code SysML v2 pour le NIVEAU LOGIQUE qui inclut :
1. Un package pour le niveau logique
2. Les part definitions pour chaque composant
3. Les port definitions pour chaque interface
4. Les connections entre ports
5. Les allocations d'exigences

=== RÈGLES DE SYNTAXE SysML v2 ===
- part def NomDuComposant { ... }
- port def NomDuPort : TypeDuPort;
- port NomDuPort : TypeDuPort [direction];
- flow NomDuFlux from partA.portOut to partB.portIn;
- connect partA.portOut to partB.portIn;
- requirement def NomExigence { ... }

=== STRUCTURE ATTENDUE ===
```sysml
package '{SystemName} - Logical' {
    // Composants logiques
    part def {Component1} {
        doc /* Description et fonctions allouées */
        
        port {port1} : {Type1} [in];
        port {port2} : {Type2} [out];
    }
    
    part def {Component2} {
        port {port3} : {Type1} [in];
    }
    
    // Architecture système
    part {SystemName} {
        part {component1} : {Component1};
        part {component2} : {Component2};
        
        // Connexions
        flow {flowName} from {component1}.{port2} to {component2}.{port3};
    }
    
    // Exigences allouées
    requirement def {Requirement1} {
        doc /* Texte de l'exigence */
        satisfy by {Component1};
    }
}
```

=== EXEMPLE ===
```sysml
package 'Drone Surveillance - Logical' {
    part def ControleurVol {
        doc /* Contrôleur de vol. Fonctions : Piloter, Stabiliser, Naviguer */
        
        port commandes_in : CommandesPilotage [in];
        port moteur_out : SignauxMoteur [out];
    }
    
    part def SystemeVideo {
        doc /* Système de capture et transmission vidéo. Fonctions : Capturer, Transmettre */
        
        port declenchement_in : Signal [in];
        port video_out : FluxVideo [out];
    }
    
    part DroneSurveillance {
        part controleur : ControleurVol;
        part camera : SystemeVideo;
        
        flow DeclenchementFlow from controleur.moteur_out to camera.declenchement_in;
    }
    
    requirement def REQ_LOG_001 {
        doc /* Le contrôleur de vol doit stabiliser le drone */
        satisfy by ControleurVol;
    }
    
    requirement def REQ_LOG_002 {
        doc /* Le système vidéo doit transmettre en temps réel */
        satisfy by SystemeVideo;
    }
}
```
"""

    # Ajout des exemples RAG
    if rag_examples and len(rag_examples) > 0:
        prompt += "\n\n=== EXEMPLES DE CODE SysML v2 ===\n"
        for i, example in enumerate(rag_examples[:3], 1):
            prompt += f"Exemple {i}:\n```sysml\n{example}\n```\n\n"

    # Le modèle JSON à traduire
    prompt += f"\n\n=== MODÈLE LOGIQUE JSON ===\n{logical_json}\n\n"
    prompt += "=== TON RÉSULTAT (CODE SysML v2 UNIQUEMENT, SANS COMMENTAIRE) ==="

    return prompt
