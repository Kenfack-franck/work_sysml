"""
Prompts pour le niveau TECHNIQUE (Technical).
Composants physiques, technologies, implémentation.
"""

import json


def build_technical_json_prompt(description: str, logical_model: dict, rag_examples: list[str] = None, correction_feedback: str = None) -> str:
    """
    Construit le prompt pour générer le modèle technique (JSON).
    
    Args:
        description: Instructions ou précisions supplémentaires
        logical_model: Le modèle logique validé (contexte)
        rag_examples: Exemples de code SysML v2 pertinents (optionnel)
        correction_feedback: Feedback de correction (optionnel)
    
    Returns:
        Le prompt complet
    """
    # Sérialiser le modèle logique
    logical_json = json.dumps(logical_model, indent=2, ensure_ascii=False)
    
    prompt = """Tu es un ingénieur système expert en modélisation SysML v2. Tu traduis les choix techniques en modèle structuré.

=== TON RÔLE ===
À partir du modèle LOGIQUE validé et des instructions de l'utilisateur, tu :
- TRADUIS les choix techniques DÉCRITS par l'utilisateur en modèle JSON structuré
- Si l'utilisateur ne mentionne pas de technologie spécifique, utilise des noms GÉNÉRIQUES (ex: ComposantPhysique1, Module2) SANS proposer de marque ou modèle
- DÉFINIS les connexions physiques (câbles, bus, réseaux) tels que décrits
- TRACES chaque composant logique vers son équivalent physique

=== RÈGLES DE TRAÇABILITÉ ===
- Chaque COMPOSANT LOGIQUE doit être RÉALISÉ par un ou plusieurs composants techniques
- Les connexions physiques implémentent les connexions logiques

=== RÈGLES DE CONCEPTION ===
- Les noms de composants reflètent ce que l'utilisateur a décrit
- Si l'utilisateur ne spécifie pas d'attributs physiques, omets-les ou mets des valeurs génériques
- Les composants techniques ont des attributs physiques uniquement si l'utilisateur les mentionne

=== RÈGLES DE FIDÉLITÉ ===
- Tu ne PROPOSES JAMAIS de marque, modèle ou technologie spécifique non mentionnée par l'utilisateur
- Tu RETRANSCRIS uniquement les justifications FOURNIES par l'utilisateur ; si elles sont absentes, utilise "Décrit par l'utilisateur" ou "À spécifier par l'architecte"
- Tu utilises UNIQUEMENT ce que l'utilisateur a décrit
- Tout doit découler du niveau logique
- Pas de composants techniques sans composant logique correspondant
- Les choix doivent être cohérents avec le contexte opérationnel et fonctionnel
- Si quelque chose est ambigu, ajoute un warning
- L'exemple ci-dessous montre uniquement la STRUCTURE attendue. En production, chaque valeur doit provenir EXCLUSIVEMENT de la description fournie par l'utilisateur ou du niveau logique. Si un élément n'est pas mentionné, il ne doit PAS apparaître dans ton résultat.

=== MÉTHODOLOGIE ===
1. RÉALISATION : Pour chaque composant logique, identifie le composant technique décrit par l'utilisateur (ou crée un nom générique)
2. TECHNOLOGIES : Reprend uniquement ce que l'utilisateur a spécifié
3. INTÉGRATION : Définis les interfaces physiques et connexions
4. ATTRIBUTS : Ajoute uniquement les caractéristiques mentionnées par l'utilisateur
5. VÉRIFICATION : Vérifie que tous les composants logiques sont réalisés

=== SCHÉMA JSON ATTENDU (TechnicalModel) ===
{
  "system_name": "string",
  "warnings": ["string"],
  "technical_parts": [
    {
      "name": "string",
      "type": "string",
      "description": "string (composant logique réalisé)",
      "ports": [
        {
          "name": "string",
          "direction": "in | out | inout",
          "type": "string (type physique : CAN, I2C, Ethernet, etc.)"
        }
      ],
      "children": []  // Sous-composants physiques
    }
  ],
  "physical_connections": [
    {
      "from_port": "CompA.portOut",
      "to_port": "CompB.portIn",
      "type": "connection",
      "item": "string (protocole, bus, câble)",
      "description": "string"
    }
  ],
  "technology_choices": [
    {
      "component": "string (nom du composant logique)",
      "technology": "string (nom du composant technique)",
      "justification": "string (pourquoi ce choix)"
    }
  ]
}

=== EXEMPLE DE STRUCTURE (placeholders — ne pas reproduire ces valeurs) ===
{
  "system_name": "Nom du système (repris depuis le niveau logique)",
  "warnings": [],
  "technical_parts": [
    {
      "name": "NomComposantTechnique",
      "type": "TypePhysique",
      "description": "Réalise le composant logique NomComposantLogique",
      "ports": [
        {
          "name": "port_entree",
          "direction": "in",
          "type": "ProtocoleOuBusDecritParUtilisateur"
        },
        {
          "name": "port_sortie",
          "direction": "out",
          "type": "ProtocoleOuBusDecritParUtilisateur"
        }
      ],
      "children": []
    },
    {
      "name": "AutreComposantTechnique",
      "type": "AutreTypePhysique",
      "description": "Réalise le composant logique AutreComposantLogique",
      "ports": [
        {
          "name": "port_entree",
          "direction": "in",
          "type": "ProtocoleOuBusDecritParUtilisateur"
        }
      ],
      "children": []
    }
  ],
  "physical_connections": [
    {
      "from_port": "NomComposantTechnique.port_sortie",
      "to_port": "AutreComposantTechnique.port_entree",
      "type": "connection",
      "item": "Bus ou protocole décrit par l'utilisateur",
      "description": "Connexion physique correspondant à la connexion logique entre NomComposantLogique et AutreComposantLogique"
    }
  ],
  "technology_choices": [
    {
      "component": "NomComposantLogique",
      "technology": "NomComposantTechnique",
      "justification": "Décrit par l'utilisateur ou à spécifier par l'architecte"
    },
    {
      "component": "AutreComposantLogique",
      "technology": "AutreComposantTechnique",
      "justification": "Décrit par l'utilisateur ou à spécifier par l'architecte"
    }
  ]
}
"""

    # Ajout du contexte logique
    prompt += f"\n\n=== MODÈLE LOGIQUE VALIDÉ (CONTEXTE) ===\n{logical_json}\n"

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


def build_technical_sysml_prompt(technical_json: str, rag_examples: list[str] = None) -> str:
    """
    Construit le prompt pour générer le code SysML v2 du niveau technique.
    
    Args:
        technical_json: Le modèle technique en JSON
        rag_examples: Exemples de code SysML v2 pertinents (optionnel)
    
    Returns:
        Le prompt complet
    """
    prompt = """Tu es un expert SysML v2. Tu traduis un modèle technique JSON en code SysML v2 valide.

=== TON RÔLE ===
Génère du code SysML v2 pour le NIVEAU TECHNIQUE qui inclut :
1. Un package pour le niveau technique
2. Les part definitions pour chaque composant technique
3. Les attributs techniques (specs matérielles)
4. Les connections physiques
5. Les allocations de composants logiques vers techniques

=== RÈGLES DE SYNTAXE SysML v2 ===
- part def NomComposantTechnique { ... }
- attribute nomAttribut : TypeAttribut = valeur;
- port nomPort : TypeProtocole [direction];
- connect partA.portOut to partB.portIn;
- allocation NomLogique to NomTechnique;

=== STRUCTURE ATTENDUE ===
```sysml
package '{SystemName} - Technical' {
    // Composants techniques
    part def {TechnicalComponent1} {
        doc /* Description et composant logique réalisé */
        
        // Attributs techniques
        attribute fabricant : String = "NomFabricant";
        attribute modele : String = "Reference";
        attribute tension : Real = 5.0 [V];
        attribute masse : Real = 0.1 [kg];
        
        // Ports physiques
        port {port1} : {ProtocolePhysique} [in];
        port {port2} : {ProtocolePhysique} [out];
    }
    
    // Architecture physique
    part {SystemName}_Physical {
        part {comp1} : {TechnicalComponent1};
        part {comp2} : {TechnicalComponent2};
        
        // Connexions physiques
        connect {comp1}.{port2} to {comp2}.{port1};
    }
    
    // Allocations logique → technique
    allocation {LogicalComponent} to {TechnicalComponent1};
}
```

=== EXEMPLE ===
```sysml
package '{SystemName} - Technical' {
    part def {NomComposantTechnique} {
        doc /* Réalise le composant logique {NomComposantLogique} */
        
        port {port_entree} : {ProtocoleDecritParUtilisateur} [in];
        port {port_sortie} : {ProtocoleDecritParUtilisateur} [out];
    }
    
    part def {AutreComposantTechnique} {
        doc /* Réalise le composant logique {AutreComposantLogique} */
        
        port {port_entree} : {ProtocoleDecritParUtilisateur} [in];
    }
    
    part {SystemName}_Physical {
        part composant1 : {NomComposantTechnique};
        part composant2 : {AutreComposantTechnique};
        
        connect composant1.{port_sortie} to composant2.{port_entree};
    }
    
    allocation {NomComposantLogique} to {NomComposantTechnique};
    allocation {AutreComposantLogique} to {AutreComposantTechnique};
}
```
"""

    # Ajout des exemples RAG
    if rag_examples and len(rag_examples) > 0:
        prompt += "\n\n=== EXEMPLES DE CODE SysML v2 ===\n"
        for i, example in enumerate(rag_examples[:3], 1):
            prompt += f"Exemple {i}:\n```sysml\n{example}\n```\n\n"

    # Le modèle JSON à traduire
    prompt += f"\n\n=== MODÈLE TECHNIQUE JSON ===\n{technical_json}\n\n"
    prompt += "=== TON RÉSULTAT (CODE SysML v2 UNIQUEMENT, SANS COMMENTAIRE) ==="

    return prompt
