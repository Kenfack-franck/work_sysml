"""
Tests pour les fonctions de génération de prompts.
"""

import pytest
from prompts.json_prompt import build_json_prompt
from prompts.sysml_prompt import build_sysml_prompt
from prompts.patch_prompt import build_patch_prompt


def test_json_prompt_contains_description():
    """Vérifie que le prompt JSON contient la description fournie."""
    description = "un drone avec GPS"
    prompt = build_json_prompt(description)
    
    assert "un drone avec GPS" in prompt
    assert description in prompt


def test_json_prompt_contains_fidelity_rules():
    """Vérifie que le prompt JSON contient les règles de fidélité."""
    prompt = build_json_prompt("un système simple")
    
    # Doit contenir des mots-clés sur la fidélité
    assert "inventer" in prompt.lower() or "invent" in prompt.lower()
    assert "warning" in prompt.lower()
    assert "fidélité" in prompt.lower() or "fidelity" in prompt.lower()


def test_json_prompt_contains_schema():
    """Vérifie que le prompt JSON contient le schéma attendu."""
    prompt = build_json_prompt("test")
    
    assert "system_name" in prompt
    assert "parts" in prompt
    assert "connections" in prompt
    assert "warnings" in prompt


def test_json_prompt_with_rag():
    """Vérifie que les exemples RAG sont inclus dans le prompt."""
    description = "un système"
    rag_examples = [
        "part def Motor { }",
        "part def Controller { }",
        "flow data from sensor to controller;"
    ]
    
    prompt = build_json_prompt(description, rag_examples)
    
    # Vérifie que les exemples sont présents
    for example in rag_examples:
        assert example in prompt
    
    # Vérifie qu'il y a une section pour les exemples
    assert "exemple" in prompt.lower() or "example" in prompt.lower()


def test_json_prompt_without_rag():
    """Vérifie que le prompt fonctionne sans exemples RAG."""
    prompt = build_json_prompt("test system")
    
    assert prompt is not None
    assert len(prompt) > 0
    assert "test system" in prompt


def test_sysml_prompt_contains_json():
    """Vérifie que le prompt SysML contient le JSON fourni."""
    json_model = '{"system_name": "TestSystem", "description": "A test"}'
    prompt = build_sysml_prompt(json_model)
    
    assert "TestSystem" in prompt
    assert json_model in prompt


def test_sysml_prompt_contains_syntax_rules():
    """Vérifie que le prompt SysML contient les règles syntaxiques."""
    prompt = build_sysml_prompt('{"system_name": "Test"}')
    
    # Doit contenir les mots-clés SysML
    assert "part def" in prompt
    assert "port def" in prompt
    assert "flow" in prompt or "connection" in prompt
    assert "package" in prompt


def test_sysml_prompt_with_rag_examples():
    """Vérifie que les exemples RAG sont inclus dans le prompt SysML."""
    json_model = '{"system_name": "Test"}'
    rag_examples = [
        "package Example { part def Motor; }",
        "flow data from A to B;"
    ]
    
    prompt = build_sysml_prompt(json_model, rag_examples)
    
    # Vérifie que les exemples sont présents
    for example in rag_examples:
        assert example in prompt


def test_patch_prompt_contains_instruction():
    """Vérifie que le prompt patch contient l'instruction."""
    current_json = '{"system_name": "Current"}'
    instruction = "ajouter une batterie"
    
    prompt = build_patch_prompt(current_json, instruction)
    
    assert "ajouter une batterie" in prompt
    assert instruction in prompt


def test_patch_prompt_contains_current_model():
    """Vérifie que le prompt patch contient le modèle actuel."""
    current_json = '{"system_name": "DroneSystem", "parts": []}'
    instruction = "add motor"
    
    prompt = build_patch_prompt(current_json, instruction)
    
    assert "DroneSystem" in prompt
    assert current_json in prompt


def test_patch_prompt_contains_rules():
    """Vérifie que le prompt patch contient les règles de modification."""
    prompt = build_patch_prompt("{}", "test")
    
    # Doit contenir les règles
    assert "uniquement" in prompt.lower() or "only" in prompt.lower()
    assert "json" in prompt.lower()
    assert "complet" in prompt.lower() or "complete" in prompt.lower()


def test_patch_prompt_mentions_connection_types():
    """Vérifie que le prompt patch mentionne les types de connexions valides."""
    prompt = build_patch_prompt("{}", "add connection")
    
    # Doit mentionner les types valides
    assert "flow" in prompt
    assert "connection" in prompt
    assert "interface" in prompt
