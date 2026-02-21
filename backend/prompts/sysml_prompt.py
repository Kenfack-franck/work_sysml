"""
Prompt pour la génération du code SysML v2 à partir d'un modèle JSON.
"""


def build_sysml_prompt(system_model_json: str, rag_examples: list[str] = None) -> str:
    """
    Construit le prompt pour transformer un modèle JSON en code SysML v2.
    
    Args:
        system_model_json: Modèle JSON du système
        rag_examples: Exemples de code SysML v2 pertinents (optionnel)
    
    Returns:
        Le prompt complet
    """
    prompt = """Tu es un générateur de code SysML v2 conforme au standard OMG. Tu transformes un modèle JSON en code SysML v2 syntaxiquement valide.

=== RÈGLES SYNTAXIQUES STRICTES ===

1. DÉFINITIONS ET INSTANCES :
   - Utilise "part def NomDuType" pour les définitions de types
   - Utilise "part nomInstance : NomDuType" pour les instances
   - Si pas de type spécifié, juste "part nomInstance"

2. PORTS :
   - Utilise "port def NomPortType { in item TypeDonnée; }" pour les ports d'entrée
   - Utilise "port def NomPortType { out item TypeDonnée; }" pour les ports de sortie
   - Utilise "port nomPort : NomPortType;" dans les parts

3. CONNEXIONS :
   - Pour les flux : "flow nomFlux from composant1.port1 to composant2.port2;"
   - Pour les connexions structurelles : "connect composant1.port1 to composant2.port2;"
   - Pour les interfaces : "interface nomInterface connect composant1.port1 to composant2.port2;"

4. EXIGENCES :
   - Utilise "requirement def IdExigence { doc /* texte */ }"
   - Utilise "satisfy requirement IdExigence by NomComposant;"

5. CAS D'UTILISATION :
   - Utilise "use case def NomCasUsage { actor nomActeur; include use case autreCas; }"

6. ORGANISATION :
   - Tout doit être dans un "package NomDuSystème { }"
   - Les noms avec espaces doivent être entre guillemets simples : 'Nom Avec Espaces'
   - Les commentaires utilisent doc /* ... */ ou // ...

7. BONNES PRATIQUES :
   - Groupe les définitions ensemble (part def, port def, requirement def)
   - Puis les instances
   - Puis les connexions
   - Utilise l'indentation pour la lisibilité
"""

    # Ajoute les exemples RAG si fournis
    if rag_examples:
        prompt += "\n=== EXEMPLES DE CODE SYSML V2 VALIDE ===\n"
        prompt += "Voici des exemples de code SysML v2 issus du standard officiel. Respecte exactement cette syntaxe :\n\n"
        for i, example in enumerate(rag_examples[:3], 1):  # Limite à 3 exemples
            prompt += f"--- Exemple {i} ---\n{example}\n\n"
    
    # Instruction finale
    prompt += """
=== INSTRUCTION ===
Génère le code SysML v2 pour ce modèle. Retourne UNIQUEMENT le code SysML v2, sans markdown, sans explication, sans ```sysml.

=== MODÈLE JSON À TRANSFORMER ===
"""
    prompt += system_model_json
    
    return prompt
