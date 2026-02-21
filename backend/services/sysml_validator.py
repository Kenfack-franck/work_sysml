"""
Validateur syntaxique SysML v2.
Vérifie la conformité du code SysML v2 généré sans appel au LLM.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SysMLv2Validator:
    """Validateur de syntaxe SysML v2 en Python pur."""
    
    def __init__(self):
        """Initialise le validateur avec les mots-clés et patterns SysML v2."""
        
        # Mots-clés de définition
        self.KEYWORDS_DEFINITION = [
            "package", "part def", "port def", "item def", "attribute def",
            "connection def", "interface def", "allocation def",
            "action def", "state def", "requirement def", "use case def",
            "concern def", "constraint def", "flow def", "enum def",
            "calc def", "case def", "analysis case def", "verification case def",
            "rendering def", "view def", "viewpoint def", "metadata def",
            "occurrence def"
        ]
        
        # Mots-clés d'usage
        self.KEYWORDS_USAGE = [
            "part", "port", "item", "attribute", "connection", "interface",
            "allocation", "action", "state", "requirement", "flow",
            "ref", "in", "out", "inout", "stream",
            "bind", "connect", "succession", "transition",
            "exhibit", "expose", "import", "alias",
            "first", "then", "decide", "join", "fork", "merge",
            "accept", "send", "assign", "perform",
            "assert", "assume", "satisfy", "require", "verify",
            "subject", "actor", "objective", "stakeholder",
            "include", "event", "occurrence"
        ]
        
        # Modificateurs
        self.KEYWORDS_MODIFIERS = [
            "abstract", "readonly", "derived", "end", "ordered", "nonunique",
            "redefines", "subsets", "specializes", ":>", ":>>",
            "about", "return", "individual", "variation", "variant",
            "public", "private", "protected", "of", "from", "to", "by"
        ]
        
        # Types primitifs SysML v2
        self.PRIMITIVE_TYPES = [
            "String", "Integer", "Real", "Boolean", "Natural", "Positive",
            "Number", "Complex"
        ]
        
    def validate(self, sysml_code: str) -> Dict:
        """
        Valide un code SysML v2 complet.
        
        Args:
            sysml_code: Le code SysML v2 à valider
            
        Returns:
            dict avec valid, score, errors, warnings, info, summary
        """
        logger.info("Démarrage de la validation SysML v2")
        
        all_issues = []
        
        # Vérifications dans l'ordre
        all_issues.extend(self._check_structure(sysml_code))
        decl_issues, definitions, usages = self._check_declarations(sysml_code)
        all_issues.extend(decl_issues)
        all_issues.extend(self._check_references(sysml_code, definitions, usages))
        all_issues.extend(self._check_naming(sysml_code))
        all_issues.extend(self._check_completeness(sysml_code, definitions, usages))
        
        # Séparer par sévérité
        errors = [i for i in all_issues if i.get("severity") == "error"]
        warnings = [i for i in all_issues if i.get("severity") == "warning"]
        infos = [i for i in all_issues if i.get("severity") == "info"]
        
        # Calcul du résumé
        lines = [l for l in sysml_code.split('\n') if l.strip()]
        total_lines = len(lines)
        
        # Compter les définitions
        total_definitions = sum(len(defs) for defs in definitions.values())
        total_usages = len(usages)
        
        # Compter les packages
        packages = len(re.findall(r'package\s+', sysml_code, re.IGNORECASE))
        
        summary = {
            "total_lines": total_lines,
            "definitions": total_definitions,
            "usages": total_usages,
            "packages": packages,
            "errors_count": len(errors),
            "warnings_count": len(warnings)
        }
        
        # Calcul du score
        score = self._calculate_score(errors, warnings, infos, total_lines)
        
        # Le code est valide s'il n'y a aucune erreur critique
        valid = len(errors) == 0
        
        result = {
            "valid": valid,
            "score": score,
            "errors": errors,
            "warnings": warnings,
            "info": infos,
            "summary": summary
        }
        
        logger.info(f"Validation terminée : valid={valid}, score={score}/100, errors={len(errors)}, warnings={len(warnings)}")
        return result
    
    def _check_structure(self, code: str) -> List[Dict]:
        """Niveau 1 : Vérification structurelle (accolades, points-virgules, packages)."""
        errors = []
        lines = code.split('\n')
        
        # a. Vérifier les accolades équilibrées
        brace_stack = []
        in_string = False
        in_comment = False
        in_multiline_comment = False
        
        for line_num, line in enumerate(lines, 1):
            i = 0
            while i < len(line):
                char = line[i]
                
                # Gestion des commentaires multilignes
                if i < len(line) - 1 and line[i:i+2] == '/*':
                    in_multiline_comment = True
                    i += 2
                    continue
                if in_multiline_comment and i < len(line) - 1 and line[i:i+2] == '*/':
                    in_multiline_comment = False
                    i += 2
                    continue
                if in_multiline_comment:
                    i += 1
                    continue
                
                # Gestion des commentaires simples
                if i < len(line) - 1 and line[i:i+2] == '//':
                    break  # Ignorer le reste de la ligne
                
                # Gestion des guillemets
                if char in ['"', "'"]:
                    if not in_string:
                        in_string = char
                    elif in_string == char:
                        in_string = False
                    i += 1
                    continue
                
                if not in_string:
                    if char == '{':
                        brace_stack.append(line_num)
                    elif char == '}':
                        if not brace_stack:
                            errors.append({
                                "line": line_num,
                                "column": i + 1,
                                "severity": "error",
                                "code": "E001",
                                "message": f"Accolade fermante '}}' sans ouverture correspondante"
                            })
                        else:
                            brace_stack.pop()
                
                i += 1
        
        if brace_stack:
            errors.append({
                "line": brace_stack[-1],
                "column": 0,
                "severity": "error",
                "code": "E002",
                "message": f"Accolades non équilibrées : {len(brace_stack)} ouvrante(s) sans fermeture"
            })
        
        # b. Vérifier les points-virgules (déclarations simples)
        # Pattern : détecte les déclarations qui devraient avoir un ;
        simple_decl_pattern = re.compile(
            r'^\s*(part|port|item|attribute|flow|connect|bind|import|alias|ref)\s+[^{;]*$',
            re.MULTILINE
        )
        
        for match in simple_decl_pattern.finditer(code):
            line_content = match.group(0).strip()
            # Ignorer les lignes qui sont dans un commentaire ou qui contiennent déjà {
            if '//' in line_content or '/*' in line_content:
                continue
            if '{' in line_content:
                continue
                
            line_num = code[:match.start()].count('\n') + 1
            # Vérifier si la ligne suivante contient une définition ou un bloc
            next_line_start = match.end()
            remaining_code = code[next_line_start:next_line_start+100]
            if not remaining_code.strip().startswith('{'):
                errors.append({
                    "line": line_num,
                    "column": 0,
                    "severity": "warning",
                    "code": "W001",
                    "message": f"Déclaration '{line_content[:50]}...' semble manquer un point-virgule"
                })
        
        # c. Vérifier la présence d'au moins un package
        if not re.search(r'package\s+', code, re.IGNORECASE):
            errors.append({
                "line": 1,
                "column": 0,
                "severity": "warning",
                "code": "W002",
                "message": "Aucun package trouvé dans le code. Le code SysML v2 devrait être organisé en packages."
            })
        
        # d. Lignes vides excessives
        empty_lines_count = 0
        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                empty_lines_count += 1
                if empty_lines_count > 3:
                    errors.append({
                        "line": line_num,
                        "column": 0,
                        "severity": "info",
                        "code": "I001",
                        "message": "Plus de 3 lignes vides consécutives (cosmétique)"
                    })
                    empty_lines_count = 0  # Reset pour éviter trop de messages
            else:
                empty_lines_count = 0
        
        return errors
    
    def _check_declarations(self, code: str) -> Tuple[List[Dict], Dict, Dict]:
        """
        Niveau 2 : Vérification des déclarations.
        
        Returns:
            (errors, definitions, usages)
            definitions: {type: [noms]}
            usages: {nom: type_référencé}
        """
        errors = []
        definitions = {}
        usages = {}
        
        # a. Collecter toutes les définitions
        # Pattern : (keyword) def Name
        def_pattern = re.compile(
            r'(part|port|item|attribute|action|state|requirement|use\s+case|connection|interface|flow|enum|calc|constraint|concern|allocation|occurrence|analysis\s+case|verification\s+case)\s+def\s+([\'"]?[\w\s]+[\'"]?)',
            re.IGNORECASE
        )
        
        for match in def_pattern.finditer(code):
            def_type = match.group(1).strip().lower()
            def_name = match.group(2).strip().strip('\'"')
            
            if def_type not in definitions:
                definitions[def_type] = []
            definitions[def_type].append(def_name)
        
        # b. Collecter tous les usages
        # Pattern : part name : Type ou port name : Type
        usage_pattern = re.compile(
            r'^\s*(part|port|item|attribute)\s+(\w+)\s*:\s*([\'"]?[\w\s]+[\'"]?)',
            re.MULTILINE
        )
        
        for match in usage_pattern.finditer(code):
            usage_type_kw = match.group(1).strip()
            usage_name = match.group(2).strip()
            referenced_type = match.group(3).strip().strip('\'"')
            
            usages[usage_name] = {
                "type": referenced_type,
                "kind": usage_type_kw,
                "line": code[:match.start()].count('\n') + 1
            }
        
        # c. Vérifier que les types référencés sont déclarés
        all_defined_types = set()
        for def_list in definitions.values():
            all_defined_types.update(def_list)
        
        for usage_name, usage_info in usages.items():
            referenced_type = usage_info["type"]
            
            # Ignorer les types primitifs et ceux avec namespace
            if referenced_type in self.PRIMITIVE_TYPES:
                continue
            if '::' in referenced_type or '*' in referenced_type:
                continue
            
            # Vérifier si le type existe
            if referenced_type not in all_defined_types:
                errors.append({
                    "line": usage_info["line"],
                    "column": 0,
                    "severity": "error",
                    "code": "E003",
                    "message": f"Type '{referenced_type}' référencé par '{usage_name}' n'est pas déclaré"
                })
        
        # d. Vérifier les doublons
        for def_type, def_names in definitions.items():
            seen = {}
            for name in def_names:
                if name in seen:
                    errors.append({
                        "line": 0,
                        "column": 0,
                        "severity": "warning",
                        "code": "W003",
                        "message": f"Définition dupliquée : '{def_type} def {name}' apparaît plusieurs fois"
                    })
                seen[name] = True
        
        return errors, definitions, usages
    
    def _check_references(self, code: str, definitions: Dict, usages: Dict) -> List[Dict]:
        """Niveau 3 : Vérification des références croisées (flows, connections, etc.)."""
        errors = []
        
        # a. Flows
        # Pattern : flow ... from X.port to Y.port
        flow_pattern = re.compile(
            r'flow\s+(?:of\s+[\w\s]+\s+)?from\s+([\w.]+)\s+to\s+([\w.]+)',
            re.IGNORECASE
        )
        
        for match in flow_pattern.finditer(code):
            source_ref = match.group(1).strip()
            target_ref = match.group(2).strip()
            line_num = code[:match.start()].count('\n') + 1
            
            # Vérifier que les parts existent
            if '.' in source_ref:
                part_name = source_ref.split('.')[0]
                if part_name not in usages:
                    errors.append({
                        "line": line_num,
                        "column": 0,
                        "severity": "error",
                        "code": "E004",
                        "message": f"Flow référence '{part_name}' qui n'est pas déclaré"
                    })
            
            if '.' in target_ref:
                part_name = target_ref.split('.')[0]
                if part_name not in usages:
                    errors.append({
                        "line": line_num,
                        "column": 0,
                        "severity": "error",
                        "code": "E005",
                        "message": f"Flow référence '{part_name}' qui n'est pas déclaré"
                    })
        
        # b. Connections
        # Pattern : connect X to Y
        connect_pattern = re.compile(
            r'connect\s+([\w.]+)\s+to\s+([\w.]+)',
            re.IGNORECASE
        )
        
        for match in connect_pattern.finditer(code):
            source = match.group(1).strip().split('.')[0]
            target = match.group(2).strip().split('.')[0]
            line_num = code[:match.start()].count('\n') + 1
            
            if source not in usages:
                errors.append({
                    "line": line_num,
                    "column": 0,
                    "severity": "error",
                    "code": "E006",
                    "message": f"Connect référence '{source}' qui n'est pas déclaré"
                })
            
            if target not in usages:
                errors.append({
                    "line": line_num,
                    "column": 0,
                    "severity": "error",
                    "code": "E007",
                    "message": f"Connect référence '{target}' qui n'est pas déclaré"
                })
        
        # c. Satisfy / Verify
        satisfy_pattern = re.compile(
            r'(satisfy|verify)\s+(\w+)\s+by\s+(\w+)',
            re.IGNORECASE
        )
        
        for match in satisfy_pattern.finditer(code):
            requirement = match.group(2).strip()
            component = match.group(3).strip()
            line_num = code[:match.start()].count('\n') + 1
            
            # Vérifier que le requirement existe
            req_defs = definitions.get('requirement', []) + definitions.get('requirement def', [])
            if requirement not in req_defs and requirement not in usages:
                errors.append({
                    "line": line_num,
                    "column": 0,
                    "severity": "warning",
                    "code": "W004",
                    "message": f"Requirement '{requirement}' référencé mais non trouvé"
                })
        
        # d. Parts déclarés mais jamais utilisés
        all_defined_parts = definitions.get('part', [])
        instantiated_types = set()
        for usage_info in usages.values():
            if usage_info["kind"] == "part":
                instantiated_types.add(usage_info["type"])
        
        for part_def in all_defined_parts:
            if part_def not in instantiated_types:
                errors.append({
                    "line": 0,
                    "column": 0,
                    "severity": "warning",
                    "code": "W005",
                    "message": f"part def '{part_def}' déclaré mais jamais instancié"
                })
        
        return errors
    
    def _check_naming(self, code: str) -> List[Dict]:
        """Niveau 4 : Conventions de nommage."""
        warnings = []
        
        # a. Noms de définitions (devraient commencer par majuscule ou être entre guillemets)
        def_pattern = re.compile(
            r'(part|port|item|attribute)\s+def\s+([a-z][\w]*)',
            re.IGNORECASE
        )
        
        for match in def_pattern.finditer(code):
            name = match.group(2)
            line_num = code[:match.start()].count('\n') + 1
            
            if name[0].islower() and not name.startswith("'") and not name.startswith('"'):
                warnings.append({
                    "line": line_num,
                    "column": 0,
                    "severity": "warning",
                    "code": "W006",
                    "message": f"Nom de définition '{name}' devrait commencer par une majuscule (PascalCase)"
                })
        
        # b. Noms d'instances (devraient commencer par minuscule)
        instance_pattern = re.compile(
            r'^\s*(part|port|item|attribute)\s+([A-Z][\w]*)\s*:',
            re.MULTILINE
        )
        
        for match in instance_pattern.finditer(code):
            name = match.group(2)
            line_num = code[:match.start()].count('\n') + 1
            
            warnings.append({
                "line": line_num,
                "column": 0,
                "severity": "warning",
                "code": "W007",
                "message": f"Nom d'instance '{name}' devrait commencer par une minuscule (camelCase)"
            })
        
        # c. Noms avec espaces sans guillemets
        name_with_spaces_pattern = re.compile(
            r'def\s+([\w]+\s+[\w]+)',
            re.IGNORECASE
        )
        
        for match in name_with_spaces_pattern.finditer(code):
            name = match.group(1)
            line_num = code[:match.start()].count('\n') + 1
            
            if not (name.startswith("'") or name.startswith('"')):
                warnings.append({
                    "line": line_num,
                    "column": 0,
                    "severity": "error",
                    "code": "E008",
                    "message": f"Nom avec espaces '{name}' doit être entre guillemets simples"
                })
        
        return warnings
    
    def _check_completeness(self, code: str, definitions: Dict, usages: Dict) -> List[Dict]:
        """Niveau 5 : Vérification de complétude."""
        infos = []
        
        # a. Package sans contenu
        empty_package_pattern = re.compile(
            r'package\s+[\'"]?[\w\s]+[\'"]?\s*\{\s*\}',
            re.IGNORECASE
        )
        
        for match in empty_package_pattern.finditer(code):
            line_num = code[:match.start()].count('\n') + 1
            infos.append({
                "line": line_num,
                "severity": "warning",
                "code": "W008",
                "message": "Package vide détecté"
            })
        
        # b. Part def sans ports (INFO seulement)
        part_defs = definitions.get('part', [])
        port_pattern = re.compile(r'port\s+', re.IGNORECASE)
        
        if part_defs and not port_pattern.search(code):
            infos.append({
                "line": 0,
                "severity": "info",
                "code": "I002",
                "message": f"{len(part_defs)} part def(s) sans aucun port défini"
            })
        
        # c. Ports définis mais aucun flow/connect
        has_ports = bool(re.search(r'port\s+def\s+', code, re.IGNORECASE))
        has_flow = bool(re.search(r'flow\s+', code, re.IGNORECASE))
        has_connect = bool(re.search(r'connect\s+', code, re.IGNORECASE))
        
        if has_ports and not has_flow and not has_connect:
            infos.append({
                "line": 0,
                "severity": "warning",
                "code": "W009",
                "message": "Des ports sont définis mais aucune connexion (flow/connect) n'est présente"
            })
        
        # d. Doc comments
        has_doc = bool(re.search(r'/\*[^*]*\*/', code))
        if not has_doc:
            infos.append({
                "line": 0,
                "severity": "info",
                "code": "I003",
                "message": "Aucun commentaire de documentation (/* */) trouvé. Bonne pratique recommandée."
            })
        
        return infos
    
    def _calculate_score(self, errors: List[Dict], warnings: List[Dict], 
                        infos: List[Dict], total_lines: int) -> int:
        """Calcule un score de qualité de 0 à 100."""
        score = 100
        
        # Compter par sévérité
        error_count = len([e for e in errors if e.get("severity") == "error"])
        warning_count = len([w for w in warnings if w.get("severity") == "warning"])
        info_count = len([i for i in infos if i.get("severity") == "info"])
        
        # Pénalités
        score -= error_count * 15  # -15 par erreur
        score -= warning_count * 5  # -5 par warning
        score -= info_count * 1     # -1 par info
        
        return max(0, min(100, score))
    
    def _parse_blocks(self, code: str) -> List[Dict]:
        """
        Parse le code en blocs imbriqués.
        
        Returns:
            Liste de blocs : [{type, name, start_line, end_line, children, content}]
        """
        blocks = []
        stack = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Ignorer les commentaires et lignes vides
            if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
                continue
            
            # Détecter l'ouverture d'un bloc
            if '{' in line:
                # Extraire le type et le nom
                match = re.match(r'^\s*([\w\s]+)\s+([\'"]?[\w\s]+[\'"]?)\s*\{', line)
                if match:
                    block_type = match.group(1).strip()
                    block_name = match.group(2).strip().strip('\'"')
                    
                    block = {
                        "type": block_type,
                        "name": block_name,
                        "start_line": line_num,
                        "end_line": None,
                        "children": [],
                        "content": ""
                    }
                    
                    if stack:
                        stack[-1]["children"].append(block)
                    else:
                        blocks.append(block)
                    
                    stack.append(block)
            
            # Détecter la fermeture d'un bloc
            if '}' in line and stack:
                block = stack.pop()
                block["end_line"] = line_num
        
        return blocks
