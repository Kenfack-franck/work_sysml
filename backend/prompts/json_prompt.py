"""
Prompt pour la génération du modèle JSON à partir d'une description en langage naturel.
"""


def build_json_prompt(description: str, rag_examples: list[str] = None, correction_feedback: str = None) -> str:
    """
    Construit le prompt pour transformer une description NL en JSON structuré.
    
    Args:
        description: Description du système en langage naturel
        rag_examples: Exemples de code SysML v2 pertinents (optionnel)
        correction_feedback: Feedback de correction du vérificateur de fidélité (optionnel)
    
    Returns:
        Le prompt complet
    """
    prompt = """Tu es un traducteur fidèle. Tu traduis des descriptions de systèmes en JSON structuré. Tu ne conçois PAS, tu TRADUIS.

=== RÈGLES DE FIDÉLITÉ (CRITIQUE) ===
- Tu ne dois RIEN inventer qui n'est pas explicitement décrit
- Tu ne dois RIEN ajouter (pas de composants, ports, connexions non mentionnés)
- Tu ne dois RIEN corriger silencieusement
- Si quelque chose est ambigu ou incohérent, ajoute un warning dans le champ "warnings"
- Utilise le vocabulaire exact de l'utilisateur pour les noms (ne traduis pas, ne reformule pas)
- Si un port n'a pas de direction explicite, utilise "inout" par défaut

=== MÉTHODOLOGIE (OBLIGATOIRE) ===
1. LISTE EXHAUSTIVE : Avant de générer le JSON, fais la liste de TOUS les composants mentionnés dans la description. Chaque composant de cette liste DOIT apparaître dans le JSON.
2. COMPTAGE : Si la description mentionne N composants, ton JSON DOIT contenir exactement N parts (ni plus, ni moins).
3. VÉRIFICATION : Après avoir généré le JSON, relis la description et vérifie que CHAQUE composant, CHAQUE connexion, CHAQUE flux mentionné est bien présent dans ton JSON.

=== SCHÉMA JSON ATTENDU ===
{
  "system_name": "string",
  "description": "string",
  "warnings": ["string"],  // Liste des ambiguïtés ou incohérences détectées
  "parts": [
    {
      "name": "string",
      "type": "string (optionnel)",
      "description": "string (optionnel)",
      "ports": [
        {
          "name": "string",
          "direction": "in | out | inout",
          "type": "string"
        }
      ],
      "children": []  // Sous-composants si hiérarchie mentionnée
    }
  ],
  "connections": [
    {
      "from_port": "PartName.portName",
      "to_port": "PartName.portName",
      "type": "flow | connection | interface",
      "item": "string (optionnel, type de données transmises)",
      "description": "string (optionnel)"
    }
  ],
  "requirements": [
    {
      "id": "string",
      "text": "string",
      "satisfied_by": "string (optionnel, nom du composant)"
    }
  ],
  "use_cases": [
    {
      "name": "string",
      "actors": ["string"],
      "includes": ["string (optionnel)"]
    }
  ]
}

=== RÈGLES POUR LES CONNEXIONS ===
- "flow" : pour les flux de données/informations (ex: GPS envoie position au contrôleur)
- "connection" : pour les connexions structurelles/physiques (ex: moteur connecté au contrôleur)
- "interface" : pour les interfaces de communication (ex: protocole CAN, I2C)
- Le champ "from_port" doit être au format "NomDuComposant.nomDuPort"
- Le champ "to_port" doit être au format "NomDuComposant.nomDuPort"
"""

    # Ajoute le feedback de correction si fourni
    if correction_feedback:
        prompt += "\n=== CORRECTION REQUISE ===\n"
        prompt += f"Un vérificateur automatique a détecté les problèmes suivants dans ta précédente tentative :\n{correction_feedback}\n\n"
        prompt += "Corrige ces problèmes dans ta réponse. Vérifie bien que TOUS les composants mentionnés dans la description sont présents.\n"
    
    # Ajoute les exemples RAG si fournis
    if rag_examples:
        prompt += "\n=== EXEMPLES DE SYSTÈMES SYSML V2 ===\n"
        prompt += "Voici des exemples de systèmes SysML v2 pour comprendre les concepts structurels :\n\n"
        for i, example in enumerate(rag_examples[:3], 1):  # Limite à 3 exemples
            prompt += f"--- Exemple {i} ---\n{example}\n\n"
    
    # Instruction finale
    prompt += """
=== INSTRUCTION ===
Traduis cette description en JSON. Retourne UNIQUEMENT le JSON, sans markdown, sans explication, sans ```json.

=== DESCRIPTION À TRADUIRE ===
"""
    prompt += description
    
    return prompt
