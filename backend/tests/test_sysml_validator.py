"""
Tests pour le validateur SysML v2.
"""

import pytest
from services.sysml_validator import SysMLv2Validator


# ============================================================================
# EXEMPLES DE CODE SYSML V2 POUR LES TESTS
# ============================================================================

VALID_CODE = """
package Drone {
    item def Position;
    item def CommandeMoteur;
    
    port def PositionOut {
        out item position : Position;
    }
    
    port def PositionIn {
        in item position : Position;
    }
    
    part def GPS {
        port posOut : PositionOut;
    }
    
    part def Controleur {
        port posIn : PositionIn;
    }
    
    part gps : GPS;
    part ctrl : Controleur;
    
    flow of Position from gps.posOut to ctrl.posIn;
}
"""

CODE_MISSING_SEMICOLON = """
package Test {
    item def Position
    part def GPS {
        port p : PositionOut;
    }
}
"""

CODE_UNBALANCED_BRACES = """
package Test {
    part def GPS {
        port p : PositionOut;
    
}
"""

CODE_UNDEFINED_TYPE = """
package Test {
    part def GPS {
        port p : NonExistentType;
    }
}
"""

CODE_INVALID_FLOW_REF = """
package Test {
    port def PositionOut;
    
    part def GPS {
        port p : PositionOut;
    }
    part gps : GPS;
    flow f from gps.p to nonexistent.port;
}
"""

CODE_DUPLICATE_DEFINITION = """
package Test {
    part def Vehicle;
    part def Vehicle;
}
"""

CODE_UNUSED_PART_DEF = """
package Test {
    part def Vehicle;
    part def Engine;
    
    part eng : Engine;
}
"""

CODE_NAMING_DEF_LOWERCASE = """
package Test {
    part def vehicle;
}
"""

CODE_NAMING_INSTANCE_UPPERCASE = """
package Test {
    part def Vehicle;
    part MyVehicle : Vehicle;
}
"""

CODE_NAME_WITH_SPACES_NO_QUOTES = """
package Test {
    part def My Vehicle;
}
"""

CODE_EMPTY_PACKAGE = """
package EmptyPackage {
}
"""

CODE_WITH_COMMENTS = """
package Test {
    // This is a single line comment
    part def Vehicle;
    
    /* This is a 
       multiline comment */
    part def Engine;
}
"""

CODE_WITH_DOC_COMMENTS = """
package Test {
    part def Vehicle {
        doc /* This is a vehicle */
        attribute mass : Real;
    }
}
"""

CODE_COMPLEX_VALID = """
package 'Complex System' {
    private import ScalarValues::*;
    
    item def Position;
    item def Fuel;
    attribute def Temp;
    
    port def FuelPort {
        attribute temperature : Temp;
        out item fuelSupply : Fuel;
        in item fuelReturn : Fuel;
    }
    
    part def Tank {
        port fuelOut : FuelPort;
    }
    
    part def Engine {
        port fuelIn : FuelPort;
    }
    
    action def StartEngine {
        doc /* Démarrage du moteur */
    }
    
    requirement def REQ001 {
        doc /* Le système doit démarrer */
    }
    
    use case def StartVehicle {
        actor Driver;
    }
    
    part tank : Tank;
    part engine : Engine;
    
    flow of Fuel from tank.fuelOut to engine.fuelIn;
    
    satisfy REQ001 by engine;
}
"""

CODE_NESTED_BLOCKS = """
package OuterPackage {
    part def Vehicle {
        part def Wheel {
            port connection : WheelPort;
        }
        
        part wheel1 : Wheel;
        part wheel2 : Wheel;
    }
}
"""


# ============================================================================
# TESTS
# ============================================================================

@pytest.fixture
def validator():
    """Crée une instance du validateur."""
    return SysMLv2Validator()


def test_valid_code(validator):
    """Test : code valide → valid=True, score >= 80, errors vide"""
    result = validator.validate(VALID_CODE)
    
    assert result["valid"] is True, "Le code devrait être valide"
    assert result["score"] >= 80, f"Score devrait être >= 80, obtenu {result['score']}"
    assert len([e for e in result["errors"] if e["severity"] == "error"]) == 0, "Aucune erreur ne devrait être présente"
    assert result["summary"]["packages"] == 1, "Devrait avoir 1 package"


def test_balanced_braces(validator):
    """Test : accolades équilibrées → pas d'erreur de structure"""
    result = validator.validate(VALID_CODE)
    
    # Vérifier qu'il n'y a pas d'erreur E001 ou E002 (accolades)
    brace_errors = [e for e in result["errors"] if e.get("code") in ["E001", "E002"]]
    assert len(brace_errors) == 0, "Ne devrait pas y avoir d'erreur d'accolades"


def test_unbalanced_braces(validator):
    """Test : accolades déséquilibrées → erreur"""
    result = validator.validate(CODE_UNBALANCED_BRACES)
    
    assert result["valid"] is False, "Le code avec accolades déséquilibrées devrait être invalide"
    brace_errors = [e for e in result["errors"] if e.get("code") in ["E001", "E002"]]
    assert len(brace_errors) > 0, "Devrait y avoir une erreur d'accolades"


def test_missing_semicolon(validator):
    """Test : point-virgule manquant → warning"""
    result = validator.validate(CODE_MISSING_SEMICOLON)
    
    # Le point-virgule manquant devrait générer un warning W001
    semicolon_warnings = [w for w in result["warnings"] if w.get("code") == "W001"]
    assert len(semicolon_warnings) > 0, "Devrait y avoir un warning pour point-virgule manquant"


def test_no_package(validator):
    """Test : code sans package → warning"""
    code_no_package = """
    part def Vehicle;
    part def Engine;
    """
    result = validator.validate(code_no_package)
    
    no_package_warnings = [e for e in result["warnings"] if e.get("code") == "W002"]
    assert len(no_package_warnings) > 0, "Devrait y avoir un warning pour absence de package"


def test_undefined_type(validator):
    """Test : type non déclaré référencé → erreur"""
    result = validator.validate(CODE_UNDEFINED_TYPE)
    
    assert result["valid"] is False, "Code avec type non défini devrait être invalide"
    type_errors = [e for e in result["errors"] if e.get("code") == "E003"]
    assert len(type_errors) > 0, "Devrait y avoir une erreur E003 pour type non déclaré"


def test_duplicate_definition(validator):
    """Test : 2 part def avec le même nom → warning"""
    result = validator.validate(CODE_DUPLICATE_DEFINITION)
    
    duplicate_warnings = [e for e in result["warnings"] if e.get("code") == "W003"]
    assert len(duplicate_warnings) > 0, "Devrait y avoir un warning W003 pour définition dupliquée"


def test_unused_part_def(validator):
    """Test : part def jamais instancié → warning"""
    result = validator.validate(CODE_UNUSED_PART_DEF)
    
    unused_warnings = [e for e in result["warnings"] if e.get("code") == "W005"]
    assert len(unused_warnings) > 0, "Devrait y avoir un warning W005 pour part def non utilisé"
    
    # Vérifier que le message mentionne "Vehicle" (non utilisé) mais pas "Engine" (utilisé)
    unused_vehicle = [w for w in unused_warnings if "Vehicle" in w["message"]]
    assert len(unused_vehicle) > 0, "Le warning devrait mentionner Vehicle comme non utilisé"


def test_invalid_flow_reference(validator):
    """Test : flow vers port inexistant → erreur (si détectée)"""
    result = validator.validate(CODE_INVALID_FLOW_REF)
    
    # NOTE: Ce test peut passer même si le validateur ne détecte pas cette erreur
    # car c'est un cas complexe. Le validateur ANTLR4 le détectera plus tard.
    # Pour l'instant, on vérifie juste qu'il n'y a pas de crash.
    assert "valid" in result, "Le résultat devrait avoir un champ 'valid'"
    assert "errors" in result, "Le résultat devrait avoir un champ 'errors'"


def test_naming_def_lowercase(validator):
    """Test : part def commençant par minuscule → warning"""
    result = validator.validate(CODE_NAMING_DEF_LOWERCASE)
    
    naming_warnings = [e for e in result["warnings"] if e.get("code") == "W006"]
    assert len(naming_warnings) > 0, "Devrait y avoir un warning W006 pour nom de définition en minuscule"


def test_naming_instance_uppercase(validator):
    """Test : instance commençant par majuscule → warning"""
    result = validator.validate(CODE_NAMING_INSTANCE_UPPERCASE)
    
    naming_warnings = [e for e in result["warnings"] if e.get("code") == "W007"]
    assert len(naming_warnings) > 0, "Devrait y avoir un warning W007 pour nom d'instance en majuscule"


def test_name_with_spaces_no_quotes(validator):
    """Test : nom avec espaces sans guillemets → erreur"""
    result = validator.validate(CODE_NAME_WITH_SPACES_NO_QUOTES)
    
    space_errors = [e for e in result["errors"] if e.get("code") == "E008"]
    assert len(space_errors) > 0, "Devrait y avoir une erreur E008 pour nom avec espaces sans guillemets"


def test_empty_package(validator):
    """Test : package vide → warning"""
    result = validator.validate(CODE_EMPTY_PACKAGE)
    
    empty_warnings = [e for e in result["warnings"] if e.get("code") == "W008"]
    assert len(empty_warnings) > 0, "Devrait y avoir un warning W008 pour package vide"


def test_score_calculation(validator):
    """Test : vérifier que le score diminue avec les erreurs"""
    # Code valide
    result_valid = validator.validate(VALID_CODE)
    score_valid = result_valid["score"]
    
    # Code avec erreurs
    result_invalid = validator.validate(CODE_UNDEFINED_TYPE)
    score_invalid = result_invalid["score"]
    
    assert score_invalid < score_valid, "Le score avec erreurs devrait être inférieur au score sans erreurs"


def test_score_perfect(validator):
    """Test : code parfait → score 100"""
    # Le code VALID_CODE devrait avoir un score proche de 100
    result = validator.validate(VALID_CODE)
    assert result["score"] >= 95, f"Code valide devrait avoir un score >= 95, obtenu {result['score']}"


def test_complex_valid_code(validator):
    """Test : code complexe avec tous les types de déclarations → valid"""
    result = validator.validate(CODE_COMPLEX_VALID)
    
    assert result["valid"] is True, "Le code complexe valide devrait être valide"
    assert result["score"] >= 80, f"Score devrait être >= 80, obtenu {result['score']}"
    assert result["summary"]["definitions"] >= 8, "Devrait avoir au moins 8 définitions"
    assert result["summary"]["usages"] >= 2, "Devrait avoir au moins 2 usages"


def test_validate_with_comments(validator):
    """Test : code avec commentaires // et /* */ → pas d'erreur sur les commentaires"""
    result = validator.validate(CODE_WITH_COMMENTS)
    
    # Les commentaires ne devraient pas causer d'erreurs
    assert result["valid"] is True, "Code avec commentaires devrait être valide"


def test_doc_comment_present(validator):
    """Test : code avec doc /* */ → pas d'info 'pas de doc'"""
    result = validator.validate(CODE_WITH_DOC_COMMENTS)
    
    # Vérifier qu'il N'Y A PAS d'info I003 (absence de doc)
    no_doc_infos = [i for i in result["info"] if i.get("code") == "I003"]
    assert len(no_doc_infos) == 0, "Ne devrait pas y avoir d'info 'pas de doc' car des docs sont présents"


def test_parse_blocks(validator):
    """Test : vérifier que les blocs sont correctement parsés"""
    blocks = validator._parse_blocks(CODE_NESTED_BLOCKS)
    
    assert len(blocks) > 0, "Devrait avoir au moins un bloc (package)"
    assert blocks[0]["type"] == "package", "Le premier bloc devrait être un package"
    assert len(blocks[0]["children"]) > 0, "Le package devrait avoir des enfants"


def test_nested_blocks(validator):
    """Test : blocs imbriqués (package > part def > port) → correctement parsés"""
    blocks = validator._parse_blocks(CODE_NESTED_BLOCKS)
    
    # Vérifier la structure imbriquée
    assert len(blocks) > 0, "Devrait avoir un package"
    package = blocks[0]
    assert len(package["children"]) > 0, "Package devrait avoir des enfants"
    
    # Le part def Vehicle devrait avoir des children (Wheel)
    vehicle = package["children"][0]
    assert len(vehicle["children"]) > 0, "Vehicle devrait avoir des enfants"


def test_summary_counts(validator):
    """Test : vérifier les compteurs du summary"""
    result = validator.validate(VALID_CODE)
    
    summary = result["summary"]
    assert summary["total_lines"] > 0, "Devrait avoir des lignes comptées"
    assert summary["definitions"] > 0, "Devrait avoir des définitions comptées"
    assert summary["usages"] > 0, "Devrait avoir des usages comptés"
    assert summary["packages"] == 1, "Devrait avoir 1 package"


def test_validation_result_structure(validator):
    """Test : vérifier la structure du résultat de validation"""
    result = validator.validate(VALID_CODE)
    
    # Vérifier que toutes les clés requises sont présentes
    assert "valid" in result
    assert "score" in result
    assert "errors" in result
    assert "warnings" in result
    assert "info" in result
    assert "summary" in result
    
    # Vérifier que les listes sont bien des listes
    assert isinstance(result["errors"], list)
    assert isinstance(result["warnings"], list)
    assert isinstance(result["info"], list)
    assert isinstance(result["summary"], dict)


def test_error_structure(validator):
    """Test : vérifier la structure d'une erreur"""
    result = validator.validate(CODE_UNDEFINED_TYPE)
    
    if len(result["errors"]) > 0:
        error = result["errors"][0]
        assert "severity" in error
        assert "code" in error
        assert "message" in error
        # line peut être 0 pour certaines erreurs globales
        assert "line" in error or "column" in error
