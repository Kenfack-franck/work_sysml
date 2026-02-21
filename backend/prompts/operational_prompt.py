"""
Prompts pour le niveau OPÉRATIONNEL (Operational).
Contexte, acteurs, cas d'utilisation, besoins opérationnels.
"""


def build_operational_json_prompt(description: str, rag_examples: list[str] = None, correction_feedback: str = None) -> str:
    """
    Construit le prompt pour générer le modèle opérationnel (JSON).
    
    Args:
        description: Description du système en langage naturel
        rag_examples: Exemples de code SysML v2 pertinents (optionnel)
        correction_feedback: Feedback de correction (optionnel)
    
    Returns:
        Le prompt complet
    """
    prompt = """Tu es un ingénieur système expert en analyse opérationnelle. Tu analyses une description pour identifier le périmètre opérationnel du système.

=== TON RÔLE ===
- Tu identifies QUI utilise le système (stakeholders, acteurs)
- Tu identifies AVEC QUOI le système interagit (systèmes externes)
- Tu définis le PÉRIMÈTRE du système (ce qui est dedans, ce qui est dehors)
- Tu extrais les CAS D'UTILISATION (use cases)
- Tu identifies les SCÉNARIOS OPÉRATIONNELS (séquences d'interactions)
- Tu formules les BESOINS OPÉRATIONNELS (requirements de haut niveau)

=== RÈGLES DE FIDÉLITÉ (CRITIQUE) ===
- Tu ne dois RIEN inventer qui n'est pas explicitement décrit
- Tu ne dois RIEN ajouter qui n'est pas mentionné
- Si quelque chose est ambigu ou incohérent, ajoute un warning dans le champ "warnings"
- Utilise le vocabulaire exact de l'utilisateur pour les noms
- Si un élément n'est pas clair, marque-le avec un warning
- L'exemple ci-dessous montre uniquement la STRUCTURE attendue. En production, chaque valeur doit provenir EXCLUSIVEMENT de la description fournie par l'utilisateur. Si un élément n'est pas mentionné, il ne doit PAS apparaître dans ton résultat.
- DISTINCTION STAKEHOLDER / SYSTÈME EXTERNE : Un stakeholder est TOUJOURS une PERSONNE ou une ORGANISATION (jamais un dispositif, un équipement ou un logiciel). Si la description mentionne un équipement comme destinataire (ex: "poste de sécurité", "station sol"), c'est un SYSTÈME EXTERNE, pas un stakeholder. Ne confonds jamais les deux.
- PÉRIMÈTRE DU SYSTÈME : Un composant interrogé via réseau ou protocole est un système externe. Un composant physique installé sur site et contrôlé directement par le système est un composant INTERNE. Si la description ne précise pas, classe-le comme interne et ajoute un warning.
- EXIGENCES = CONTRAINTES MESURABLES UNIQUEMENT : Ne génère des requirements QUE pour des contraintes explicitement chiffrées ou mesurables dans la description (temps de réponse, disponibilité, capacité, température, etc.). Un comportement fonctionnel décrit (ex: "la porte se déverrouille", "le système vérifie l'autorisation") N'EST PAS une exigence. C'est un comportement normal du système qui sera capturé dans les use cases ou les scénarios.

=== MÉTHODOLOGIE (OBLIGATOIRE) ===
1. IDENTIFICATION : Liste tous les acteurs, systèmes externes et cas d'utilisation mentionnés
2. PÉRIMÈTRE : Définis clairement ce qui est dans le système et ce qui est externe
3. SCÉNARIOS : Pour chaque use case, identifie les étapes principales
4. BESOINS : Formule les besoins opérationnels à partir des use cases
5. VÉRIFICATION : Relis la description et vérifie que tout est bien capturé

=== SCHÉMA JSON ATTENDU (OperationalModel) ===
{
  "system_name": "string",
  "description": "string",
  "warnings": ["string"],  // Ambiguïtés ou incohérences
  "stakeholders": ["string"],  // Parties prenantes (utilisateurs, clients, organismes, etc.)
  "external_systems": ["string"],  // Systèmes externes avec lesquels le système interagit
  "system_boundaries": "string",  // Description textuelle du périmètre et des limites
  "use_cases": [
    {
      "name": "string",
      "actors": ["string"],  // Acteurs qui réalisent ce use case
      "includes": ["string"]  // Use cases inclus (optionnel)
    }
  ],
  "operational_scenarios": [
    {
      "name": "string",
      "description": "string",
      "steps": ["string"]  // Étapes principales du scénario
    }
  ],
  "requirements": [
    {
      "id": "string (ex: REQ-OP-001)",
      "text": "string",
      "satisfied_by": null  // Au niveau opérationnel, pas encore alloué
    }
  ]
}

=== EXEMPLE DE STRUCTURE (placeholders — ne pas reproduire ces valeurs) ===
{
  "system_name": "Nom du système extrait de la description",
  "description": "Résumé de la description fournie",
  "warnings": ["Avertissement si un élément est ambigu ou manquant"],
  "stakeholders": [
    "Premier acteur mentionné dans la description",
    "Deuxième acteur mentionné dans la description"
  ],
  "external_systems": [
    "Système externe mentionné dans la description"
  ],
  "system_boundaries": "Périmètre tel qu'il découle de la description : ce qui est dans le système et ce qui est externe",
  "use_cases": [
    {
      "name": "Cas d'utilisation mentionné dans la description",
      "actors": ["Acteur associé, tel que mentionné"],
      "includes": ["Sous-cas d'utilisation si mentionné explicitement"]
    }
  ],
  "operational_scenarios": [
    {
      "name": "Nom du scénario tel que décrit",
      "description": "Description du scénario telle que fournie",
      "steps": [
        "Étape 1 telle que décrite ou directement déduite",
        "Étape 2 telle que décrite ou directement déduite"
      ]
    }
  ],
  "requirements": [
    {
      "id": "REQ-OP-001",
      "text": "Besoin opérationnel formulé à partir de la description",
      "satisfied_by": null
    }
  ]
}
"""

    # Ajout des exemples RAG
    if rag_examples and len(rag_examples) > 0:
        prompt += "\n\n=== EXEMPLES DE SYNTAXE SysML v2 POUR RÉFÉRENCE ===\n"
        prompt += "Ces exemples te donnent des idées de structure, mais tu dois rester fidèle à la description.\n\n"
        for i, example in enumerate(rag_examples[:3], 1):
            prompt += f"Exemple {i}:\n```\n{example}\n```\n\n"

    # Ajout du feedback de correction
    if correction_feedback:
        prompt += f"\n\n=== CORRECTION REQUISE ===\n"
        prompt += f"Un vérificateur automatique a détecté les problèmes suivants : {correction_feedback}\n"
        prompt += "Corrige ces problèmes dans ta réponse.\n"

    # La description à analyser
    prompt += f"\n\n=== DESCRIPTION À ANALYSER ===\n{description}\n\n"
    prompt += "=== TON RÉSULTAT (JSON UNIQUEMENT, SANS COMMENTAIRE) ==="

    return prompt


def build_operational_sysml_prompt(operational_json: str, rag_examples: list[str] = None) -> str:
    """
    Construit le prompt pour générer le code SysML v2 du niveau opérationnel.
    
    Args:
        operational_json: Le modèle opérationnel en JSON
        rag_examples: Exemples de code SysML v2 pertinents (optionnel)
    
    Returns:
        Le prompt complet
    """
    prompt = """Tu es un expert SysML v2. Tu traduis un modèle opérationnel JSON en code SysML v2 valide.

=== TON RÔLE ===
Génère du code SysML v2 pour le NIVEAU OPÉRATIONNEL qui inclut :
1. Un package pour le niveau opérationnel
2. Les use case definitions
3. Les requirement definitions pour les besoins opérationnels
4. Les action definitions pour les scénarios opérationnels

=== RÈGLES DE SYNTAXE SysML v2 ===
- use case def NomDuUseCase { ... }
- requirement def NomDeLExigence { ... }
- action def NomDuScenario { ... }
- Les noms doivent respecter la casse CamelCase ou snake_case
- Utilise des commentaires /* ... */ pour les descriptions

=== STRUCTURE ATTENDUE ===
```sysml
package '{SystemName} - Operational' {
    // Use Cases
    use case def {UseCase1} {
        doc /* Description du use case */
        actor {Actor1};
    }
    
    // Exigences opérationnelles
    requirement def {RequirementId} {
        doc /* Texte de l'exigence */
    }
    
    // Scénarios opérationnels
    action def {Scenario1} {
        doc /* Description du scénario */
        // Étapes du scénario comme actions ou states
    }
}
```

=== EXEMPLE ===
Pour un système de drone avec use case "SurveillerZone" et exigence "REQ-OP-001: Surveiller une zone" :

```sysml
package 'Drone Surveillance - Operational' {
    use case def SurveillerZone {
        doc /* L'opérateur surveille une zone avec le drone */
        actor Operateur;
    }
    
    requirement def REQ_OP_001 {
        doc /* Le système doit permettre de surveiller une zone définie */
    }
    
    action def MissionSurveillance {
        doc /* Scénario nominal d'une mission de surveillance */
        // Étapes : démarrage, définition zone, survol, capture, analyse
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
    prompt += f"\n\n=== MODÈLE OPÉRATIONNEL JSON ===\n{operational_json}\n\n"
    prompt += "=== TON RÉSULTAT (CODE SysML v2 UNIQUEMENT, SANS COMMENTAIRE) ==="

    return prompt
