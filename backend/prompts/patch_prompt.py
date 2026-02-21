"""
Prompt pour la modification incrémentale d'un modèle JSON existant.
"""


def build_patch_prompt(current_model_json: str, instruction: str) -> str:
    """
    Construit le prompt pour modifier un modèle JSON existant.
    
    Args:
        current_model_json: Le modèle JSON actuel
        instruction: L'instruction de modification
    
    Returns:
        Le prompt complet
    """
    prompt = """Tu modifies un modèle JSON existant selon une instruction utilisateur.

=== RÈGLES STRICTES ===
1. Applique UNIQUEMENT la modification demandée dans l'instruction
2. Ne supprime RIEN qui n'est pas explicitement demandé
3. Ne modifie RIEN qui n'est pas concerné par l'instruction
4. Conserve toute la structure existante intacte
5. Retourne le JSON COMPLET mis à jour (pas juste la partie modifiée)
6. Si tu ajoutes un composant, ajoute-le aussi dans les connexions si pertinent
7. Si tu ajoutes une connexion, vérifie que les ports existent ou crée-les

=== TYPES DE CONNEXIONS VALIDES ===
Les connexions doivent OBLIGATOIREMENT avoir un des types suivants :
- "flow" : pour les flux de données/informations/énergie (ex: batterie alimente moteur, GPS envoie position)
- "connection" : pour les connexions structurelles/physiques
- "interface" : pour les interfaces de communication (ex: protocole CAN, I2C)

IMPORTANT : Utilise "flow" pour les alimentations électriques (batterie → composants).

=== EXEMPLES DE MODIFICATIONS ===
- "Ajouter une batterie" → Ajoute un part "batterie" dans parts[]
- "Ajouter une batterie qui alimente le moteur" → Ajoute le part ET la connexion avec type "flow"
- "Renommer le GPS en Capteur GPS" → Change le name dans le part existant
- "Supprimer le moteur" → Retire le part ET toutes les connexions liées
- "Changer la connexion entre A et B en interface" → Modifie le type de la connexion

=== MODÈLE JSON ACTUEL ===
"""
    prompt += current_model_json
    
    prompt += """

=== INSTRUCTION DE MODIFICATION ===
"""
    prompt += instruction
    
    prompt += """

=== RÉSULTAT ATTENDU ===
Retourne UNIQUEMENT le JSON complet modifié, sans markdown, sans explication, sans ```json.
N'oublie pas : les connexions doivent avoir type "flow", "connection" ou "interface" uniquement.
"""
    
    return prompt
