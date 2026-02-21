"""
Prompts pour le niveau FONCTIONNEL (Functional).
Fonctions, flux fonctionnels, modes opératoires.
"""

import json


def build_functional_json_prompt(description: str, operational_model: dict, rag_examples: list[str] = None, correction_feedback: str = None) -> str:
    """
    Construit le prompt pour générer le modèle fonctionnel (JSON).
    
    Args:
        description: Instructions ou précisions supplémentaires
        operational_model: Le modèle opérationnel validé (contexte)
        rag_examples: Exemples de code SysML v2 pertinents (optionnel)
        correction_feedback: Feedback de correction (optionnel)
    
    Returns:
        Le prompt complet
    """
    # Sérialiser le modèle opérationnel
    operational_json = json.dumps(operational_model, indent=2, ensure_ascii=False)
    
    prompt = """Tu es un ingénieur système expert en analyse fonctionnelle. Tu décomposes les cas d'utilisation en fonctions.

=== TON RÔLE ===
À partir du modèle OPÉRATIONNEL validé, tu identifies :
- Les FONCTIONS que le système doit réaliser (QUE FAIT le système)
- Les FLUX FONCTIONNELS entre ces fonctions (échanges d'informations, d'énergie, de matière)
- Les MODES OPÉRATOIRES (configurations où certaines fonctions sont actives)

=== RÈGLES DE TRAÇABILITÉ ===
- Chaque USE CASE du niveau opérationnel doit être couvert par au moins UNE FONCTION
- Les fonctions peuvent avoir des sous-fonctions (hiérarchie)
- Les flux fonctionnels représentent les échanges entre fonctions
- Les modes permettent de décrire différentes configurations opérationnelles

=== RÈGLES DE FIDÉLITÉ ===
- Tu ne dois RIEN inventer qui ne découle pas du niveau opérationnel
- Chaque fonction doit être justifiable par un ou plusieurs use cases
- Si quelque chose est ambigu, ajoute un warning
- L'exemple ci-dessous montre uniquement la STRUCTURE attendue. En production, chaque valeur doit provenir EXCLUSIVEMENT du niveau opérationnel fourni en contexte. Si un élément n'est pas mentionné, il ne doit PAS apparaître dans ton résultat.

=== MÉTHODOLOGIE ===
1. ANALYSE : Pour chaque use case, identifie les fonctions nécessaires
2. DÉCOMPOSITION : Décompose les fonctions complexes en sous-fonctions
3. FLUX : Identifie les échanges entre fonctions (données, énergie, matière)
4. MODES : Regroupe les fonctions par modes opératoires (nominal, dégradé, maintenance, etc.)
5. VÉRIFICATION : Vérifie que tous les use cases sont couverts

=== SCHÉMA JSON ATTENDU (FunctionalModel) ===
{
  "system_name": "string",
  "warnings": ["string"],
  "functions": [
    {
      "name": "string",
      "description": "string",
      "inputs": ["string"],  // Entrées de la fonction
      "outputs": ["string"],  // Sorties de la fonction
      "sub_functions": ["string"]  // Sous-fonctions (optionnel)
    }
  ],
  "functional_flows": [
    {
      "from_function": "string",
      "to_function": "string",
      "item": "string",  // Ce qui est échangé
      "description": "string"
    }
  ],
  "modes": [
    {
      "name": "string",
      "description": "string",
      "active_functions": ["string"]  // Fonctions actives dans ce mode
    }
  ]
}

=== EXEMPLE DE STRUCTURE (placeholders — ne pas reproduire ces valeurs) ===
{
  "system_name": "Nom du système (repris depuis le niveau opérationnel)",
  "warnings": ["Avertissement si un use case ne peut être couvert"],
  "functions": [
    {
      "name": "Nom de la fonction extraite du premier use case",
      "description": "Ce que fait cette fonction, tel que déduit du use case",
      "inputs": ["Entrée mentionnée dans la description ou déduite du flux opérationnel"],
      "outputs": ["Sortie vers l'extérieur ou vers une autre fonction"],
      "sub_functions": ["Sous-fonction si la décomposition est explicite dans la description"]
    },
    {
      "name": "Nom de la fonction extraite du deuxième use case",
      "description": "Ce que fait cette fonction",
      "inputs": ["Entrée correspondant à la sortie de la première fonction"],
      "outputs": ["Sortie telle que décrite"],
      "sub_functions": []
    }
  ],
  "functional_flows": [
    {
      "from_function": "Nom de la première fonction",
      "to_function": "Nom de la deuxième fonction",
      "item": "Élément échangé tel que décrit ou déduit du contexte opérationnel",
      "description": "Pourquoi cet échange existe (traçabilité avec le use case)"
    }
  ],
  "modes": [
    {
      "name": "Mode mentionné dans la description ou déduit des scénarios opérationnels",
      "description": "Description du mode telle que fournie",
      "active_functions": ["Nom de la fonction active dans ce mode"]
    }
  ]
}
"""

    # Ajout du contexte opérationnel
    prompt += f"\n\n=== MODÈLE OPÉRATIONNEL VALIDÉ (CONTEXTE) ===\n{operational_json}\n"

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


def build_functional_sysml_prompt(functional_json: str, rag_examples: list[str] = None) -> str:
    """
    Construit le prompt pour générer le code SysML v2 du niveau fonctionnel.
    
    Args:
        functional_json: Le modèle fonctionnel en JSON
        rag_examples: Exemples de code SysML v2 pertinents (optionnel)
    
    Returns:
        Le prompt complet
    """
    prompt = """Tu es un expert SysML v2. Tu traduis un modèle fonctionnel JSON en code SysML v2 valide.

=== TON RÔLE ===
Génère du code SysML v2 pour le NIVEAU FONCTIONNEL qui inclut :
1. Un package pour le niveau fonctionnel
2. Les action definitions pour chaque fonction
3. Les flow connections pour les flux fonctionnels
4. Les state definitions pour les modes

=== RÈGLES DE SYNTAXE SysML v2 ===
- action def NomDeLaFonction { ... }
- flow NomDuFlux from fonction1.output to fonction2.input;
- state def NomDuMode { ... }
- Les actions peuvent contenir des sous-actions

=== STRUCTURE ATTENDUE ===
```sysml
package '{SystemName} - Functional' {
    // Fonctions principales
    action def {Function1} {
        doc /* Description de la fonction */
        in {input1} : {Type};
        out {output1} : {Type};
        
        // Sous-fonctions si nécessaire
        action {SubFunction1} { ... }
    }
    
    // Flux fonctionnels
    flow {FlowName} from {Function1}.{output} to {Function2}.{input};
    
    // Modes opératoires
    state def {Mode1} {
        doc /* Description du mode */
        // Fonctions actives dans ce mode
    }
}
```

=== EXEMPLE ===
```sysml
package 'Drone Surveillance - Functional' {
    action def PiloterDrone {
        doc /* Contrôler la trajectoire et l'altitude du drone */
        in commandes : CommandesPilotage;
        in position : PositionGPS;
        out commandesMoteur : SignauxMoteur;
        
        action Stabiliser { ... }
        action Naviguer { ... }
    }
    
    action def CapturerImages {
        doc /* Acquérir des images vidéo de la zone */
        in declenchement : Signal;
        out images : FluxVideo;
    }
    
    action def TransmettreImages {
        doc /* Envoyer les images à la station sol */
        in images : FluxVideo;
        out fluxTransmis : FluxVideo;
    }
    
    flow FluxImages from CapturerImages.images to TransmettreImages.images;
    
    state def ModeSurveillance {
        doc /* Mode nominal de surveillance */
        entry / PiloterDrone;
        do / CapturerImages;
        do / TransmettreImages;
    }
    
    state def ModeRetourBase {
        doc /* Retour automatique à la base */
        do / PiloterDrone;
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
    prompt += f"\n\n=== MODÈLE FONCTIONNEL JSON ===\n{functional_json}\n\n"
    prompt += "=== TON RÉSULTAT (CODE SysML v2 UNIQUEMENT, SANS COMMENTAIRE) ==="

    return prompt
