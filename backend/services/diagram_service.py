"""
Service de génération de diagrammes PlantUML à partir du modèle JSON.
Le code PlantUML est généré en Python pur (pas par le LLM).
"""

import logging
import requests
import unicodedata
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class DiagramService:
    """Service de génération de diagrammes PlantUML."""

    def __init__(self, plantuml_server_url: str = "http://plantuml:8080"):
        """
        Initialise le service de diagrammes.
        
        Args:
            plantuml_server_url: URL du serveur PlantUML
        """
        self.plantuml_server_url = plantuml_server_url
        logger.info(f"DiagramService initialisé avec serveur: {plantuml_server_url}")

    def generate_all(self, system_model: dict) -> dict:
        """
        Génère tous les diagrammes disponibles pour ce modèle.
        
        Args:
            system_model: Modèle système (dict JSON)
        
        Returns:
            {"diagrams": [{"type": "bdd", "title": "...", "plantuml_code": "...", "svg": "..."}, ...]}
        """
        diagrams = []
        
        # BDD - toujours disponible si des parts existent
        if system_model.get("parts"):
            bdd = self.generate_bdd(system_model)
            if bdd:
                diagrams.append(bdd)
        
        # IBD - disponible si des parts existent
        if system_model.get("parts"):
            ibd = self.generate_ibd(system_model)
            if ibd:
                diagrams.append(ibd)
        
        # Context - si des connexions existent
        if system_model.get("connections"):
            context = self.generate_context(system_model)
            if context:
                diagrams.append(context)
        
        # Requirements - si des exigences existent
        if system_model.get("requirements"):
            req = self.generate_requirements(system_model)
            if req:
                diagrams.append(req)
        
        # Use Cases - si des cas d'utilisation existent
        if system_model.get("use_cases"):
            uc = self.generate_use_cases(system_model)
            if uc:
                diagrams.append(uc)
        
        logger.info(f"Généré {len(diagrams)} diagrammes")
        
        return {"diagrams": diagrams}

    def generate_bdd(self, system_model: dict) -> Optional[Dict]:
        """
        Génère un Block Definition Diagram.
        Montre les part def et leurs relations.
        
        Args:
            system_model: Modèle système
        
        Returns:
            Dict avec type, title, plantuml_code, svg
        """
        system_name = system_model.get("system_name", "System")
        parts = system_model.get("parts", [])
        connections = system_model.get("connections", [])
        
        if not parts:
            return None
        
        code_lines = [
            "@startuml",
            "skinparam style strictuml",
            f'title "BDD - {system_name}"',
            ""
        ]
        
        # Définir les blocs
        for part in parts:
            part_name = part.get("name", "Unknown")
            ports = part.get("ports", [])
            
            code_lines.append(f'class "{part_name}" <<block>> {{')
            
            # Ajouter les ports
            for port in ports:
                port_name = port.get("name", "")
                port_dir = port.get("direction", "inout")
                port_type = port.get("type", "")
                code_lines.append(f'  {port_dir} {port_name} : {port_type}')
            
            code_lines.append("}")
            code_lines.append("")
        
        # Relations de composition (parents-children)
        def add_children_relations(parent_part, parent_name):
            children = parent_part.get("children", [])
            for child in children:
                child_name = child.get("name", "Unknown")
                code_lines.append(f'"{parent_name}" *-- "{child_name}" : contient')
                # Récursif pour les sous-enfants
                add_children_relations(child, child_name)
        
        for part in parts:
            add_children_relations(part, part.get("name", "Unknown"))
        
        # Relations de connexion
        for conn in connections:
            conn_type = conn.get("type", "")
            if conn_type in ["connection", "interface"]:
                from_port = conn.get("from_port", "")
                to_port = conn.get("to_port", "")
                description = conn.get("description", "")
                
                # Extraire les noms des parts
                from_part = from_port.split(".")[0] if "." in from_port else from_port
                to_part = to_port.split(".")[0] if "." in to_port else to_port
                
                label = description if description else ""
                code_lines.append(f'"{from_part}" -- "{to_part}" : {label}')
        
        code_lines.append("")
        code_lines.append("@enduml")
        
        plantuml_code = "\n".join(code_lines)
        svg = self._render_svg(plantuml_code)
        
        return {
            "type": "bdd",
            "title": "Block Definition Diagram",
            "plantuml_code": plantuml_code,
            "svg": svg
        }

    def generate_ibd(self, system_model: dict) -> Optional[Dict]:
        """
        Génère un Internal Block Diagram.
        Montre les instances, ports et flows.
        
        Args:
            system_model: Modèle système
        
        Returns:
            Dict avec type, title, plantuml_code, svg
        """
        system_name = system_model.get("system_name", "System")
        parts = system_model.get("parts", [])
        connections = system_model.get("connections", [])
        
        if not parts:
            return None
        
        code_lines = [
            "@startuml",
            "skinparam componentStyle rectangle",
            "skinparam padding 5",
            "skinparam nodesep 60",
            "skinparam ranksep 40",
            "left to right direction",
            f'title "IBD - {system_name}"',
            "",
            f'package "{system_name}" {{',
        ]
        
        # Définir les composants avec leurs ports
        for part in parts:
            part_name = part.get("name", "Unknown")
            part_id = self._sanitize_id(part_name)
            ports = part.get("ports", [])
            
            # Si plus de 4 ports, ne pas les lister (trop chargé)
            if len(ports) > 4:
                code_lines.append(f'  component "{part_name}" as {part_id}')
                code_lines.append("")
            else:
                code_lines.append(f'  component "{part_name}" as {part_id} {{')
                
                for port in ports:
                    port_name = port.get("name", "")
                    port_id = self._sanitize_id(f"{part_name}_{port_name}")
                    code_lines.append(f'    port "{port_name}" as {port_id}')
                
                code_lines.append("  }")
                code_lines.append("")
        
        # Connexions entre ports
        for conn in connections:
            from_port = conn.get("from_port", "")
            to_port = conn.get("to_port", "")
            item = conn.get("item", "")
            description = conn.get("description", "")
            
            if not from_port or not to_port:
                continue
            
            # Sanitize les IDs
            from_id = self._sanitize_id(from_port.replace(".", "_"))
            to_id = self._sanitize_id(to_port.replace(".", "_"))
            
            # Label tronqué à 25 caractères max
            flow_label = item if item else (description if description else "")
            if len(flow_label) > 25:
                flow_label = flow_label[:25] + "..."
            
            code_lines.append(f'  {from_id} --> {to_id} : {flow_label}')
        
        code_lines.append("}")
        code_lines.append("")
        code_lines.append("@enduml")
        
        plantuml_code = "\n".join(code_lines)
        svg = self._render_svg(plantuml_code)
        
        return {
            "type": "ibd",
            "title": "Internal Block Diagram",
            "plantuml_code": plantuml_code,
            "svg": svg
        }

    def generate_context(self, system_model: dict) -> Optional[Dict]:
        """
        Génère un diagramme de contexte.
        Le système au centre avec ses interfaces externes.
        
        Supporte deux formats :
        - Niveau opérationnel : stakeholders + external_systems
        - Niveau logical : connections
        
        Args:
            system_model: Modèle système
        
        Returns:
            Dict avec type, title, plantuml_code, svg
        """
        system_name = system_model.get("system_name", "System")
        
        # Format opérationnel : stakeholders + external_systems
        stakeholders = system_model.get("stakeholders", [])
        external_systems = system_model.get("external_systems", [])
        
        # Format logical : connections
        connections = system_model.get("connections", [])
        
        # Si aucune donnée disponible, retourner None
        if not stakeholders and not external_systems and not connections:
            return None
        
        code_lines = [
            "@startuml",
            f'title "Diagramme de contexte - {system_name}"',
            "skinparam style strictuml",
            ""
        ]
        
        # Dessiner le système au centre
        code_lines.append(f'rectangle "{system_name}" as system')
        code_lines.append("")
        
        # Format opérationnel : ajouter stakeholders et external systems
        if stakeholders or external_systems:
            for stakeholder in stakeholders:
                stakeholder_id = self._sanitize_id(stakeholder)
                code_lines.append(f'actor "{stakeholder}" as {stakeholder_id}')
                code_lines.append(f'{stakeholder_id} --> system')
            
            code_lines.append("")
            
            for ext_system in external_systems:
                ext_id = self._sanitize_id(ext_system)
                code_lines.append(f'component "{ext_system}" as {ext_id}')
                code_lines.append(f'system <--> {ext_id}')
            
            code_lines.append("")
        
        # Format logical : identifier les acteurs externes depuis connections
        elif connections:
            external_actors = set()
            for conn in connections:
                from_port = conn.get("from_port", "")
                to_port = conn.get("to_port", "")
                item = conn.get("item", "")
                
                # Si c'est un flux entrant
                if from_port and to_port:
                    from_part = from_port.split(".")[0] if "." in from_port else from_port
                    to_part = to_port.split(".")[0] if "." in to_port else to_port
                    
                    # Simplification : considérer les composants comme externes si mentionnés dans les flux
                    external_actors.add((from_part, item))
            
            # Ajouter les acteurs et connexions
            for actor, item in external_actors:
                actor_id = self._sanitize_id(actor)
                code_lines.append(f'actor "{actor}" as {actor_id}')
                label = item if item else ""
                code_lines.append(f'{actor_id} --> system : {label}')
                code_lines.append("")
        
        code_lines.append("@enduml")
        
        plantuml_code = "\n".join(code_lines)
        svg = self._render_svg(plantuml_code)
        
        return {
            "type": "context",
            "title": "Diagramme de contexte",
            "plantuml_code": plantuml_code,
            "svg": svg
        }

    def generate_requirements(self, system_model: dict) -> Optional[Dict]:
        """
        Génère un diagramme d'exigences.
        
        Args:
            system_model: Modèle système
        
        Returns:
            Dict avec type, title, plantuml_code, svg ou None si pas d'exigences
        """
        requirements = system_model.get("requirements", [])
        
        if not requirements:
            return None
        
        system_name = system_model.get("system_name", "System")
        
        code_lines = [
            "@startuml",
            f'title "Diagramme d\'exigences - {system_name}"',
            ""
        ]
        
        for req in requirements:
            req_id = req.get("id", "REQ-?")
            req_text = req.get("text", "")
            satisfied_by = req.get("satisfied_by", "")
            
            # Exigence
            code_lines.append(f'class "{req_id}" <<requirement>> {{')
            # Échapper les guillemets dans le texte
            req_text_escaped = req_text.replace('"', '\\"')
            code_lines.append(f'  text = "{req_text_escaped}"')
            code_lines.append("}")
            code_lines.append("")
            
            # Satisfaction
            if satisfied_by:
                code_lines.append(f'class "{satisfied_by}" <<block>>')
                code_lines.append(f'"{satisfied_by}" ..> "{req_id}" : <<satisfy>>')
                code_lines.append("")
        
        code_lines.append("@enduml")
        
        plantuml_code = "\n".join(code_lines)
        svg = self._render_svg(plantuml_code)
        
        return {
            "type": "requirements",
            "title": "Diagramme d'exigences",
            "plantuml_code": plantuml_code,
            "svg": svg
        }

    def generate_use_cases(self, system_model: dict) -> Optional[Dict]:
        """
        Génère un diagramme de use cases.
        
        Args:
            system_model: Modèle système
        
        Returns:
            Dict avec type, title, plantuml_code, svg ou None si pas de use cases
        """
        use_cases = system_model.get("use_cases", [])
        
        if not use_cases:
            return None
        
        system_name = system_model.get("system_name", "System")
        
        code_lines = [
            "@startuml",
            f'title "Use Cases - {system_name}"',
            "",
            f'rectangle "{system_name}" {{',
        ]
        
        # Collecter tous les acteurs
        all_actors = set()
        
        # Définir les use cases
        for uc in use_cases:
            uc_name = uc.get("name", "Unknown")
            uc_id = self._sanitize_id(uc_name)
            includes = uc.get("includes", [])
            actors = uc.get("actors", [])
            
            code_lines.append(f'  usecase "{uc_name}" as {uc_id}')
            
            # Inclusions
            for include_name in includes:
                include_id = self._sanitize_id(include_name)
                code_lines.append(f'  {uc_id} ..> {include_id} : <<include>>')
            
            # Collecter les acteurs
            for actor in actors:
                all_actors.add((actor, uc_id))
        
        code_lines.append("}")
        code_lines.append("")
        
        # Définir les acteurs et leurs relations
        added_actors = set()
        for actor, uc_id in all_actors:
            actor_id = self._sanitize_id(actor)
            if actor_id not in added_actors:
                code_lines.append(f'actor "{actor}" as {actor_id}')
                added_actors.add(actor_id)
            code_lines.append(f'{actor_id} --> {uc_id}')
        
        code_lines.append("")
        code_lines.append("@enduml")
        
        plantuml_code = "\n".join(code_lines)
        svg = self._render_svg(plantuml_code)
        
        return {
            "type": "use_cases",
            "title": "Diagramme de cas d'utilisation",
            "plantuml_code": plantuml_code,
            "svg": svg
        }

    def _render_svg(self, plantuml_code: str) -> str:
        """
        Rend le code PlantUML en SVG via le serveur PlantUML.
        
        Args:
            plantuml_code: Code PlantUML
        
        Returns:
            SVG en string, ou "" si erreur
        """
        try:
            # Appel au serveur PlantUML
            response = requests.post(
                f"{self.plantuml_server_url}/svg/",
                data=plantuml_code.encode("utf-8"),
                headers={"Content-Type": "text/plain"},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"Erreur serveur PlantUML: {response.status_code}")
                return ""
        
        except requests.exceptions.RequestException as e:
            logger.warning(f"Impossible de contacter le serveur PlantUML: {e}")
            return ""

    def _sanitize_id(self, name: str) -> str:
        """
        Convertit un nom en identifiant PlantUML valide.
        
        Args:
            name: Nom à sanitizer
        
        Returns:
            Identifiant valide
        """
        if not name:
            return "unknown"
        
        # Enlever les accents
        name = unicodedata.normalize('NFD', name)
        name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
        
        # Remplacer espaces par underscores
        name = name.replace(" ", "_")
        
        # Garder uniquement alphanumériques et underscores
        name = re.sub(r'[^a-zA-Z0-9_]', '', name)
        
        # S'assurer que ça commence par une lettre
        if not name or not name[0].isalpha():
            name = "id_" + name
        
        return name

    # ========================================================================
    # MÉTHODES POUR DIAGRAMMES PAR NIVEAU MBSE
    # ========================================================================

    def generate_for_level(self, system_model: dict, level: str) -> dict:
        """
        Génère les diagrammes appropriés pour un niveau MBSE donné.
        
        Args:
            system_model: Modèle du niveau
            level: Niveau MBSE (operational, functional, logical, technical)
        
        Returns:
            {"diagrams": [...]}
        """
        DIAGRAMMES_PAR_NIVEAU = {
            "operational": ["context", "use_cases", "actors_diagram", "operational_sequence"],
            "functional": ["functional_breakdown", "functional_behavior", "modes_diagram"],
            "logical": ["bdd", "ibd"],
            "technical": ["technical_architecture"]
        }
        
        diagrams = []
        diagram_types = DIAGRAMMES_PAR_NIVEAU.get(level, [])
        
        for diagram_type in diagram_types:
            result = None
            
            if diagram_type == "context":
                result = self.generate_context(system_model)
            elif diagram_type == "use_cases":
                result = self.generate_use_cases(system_model)
            elif diagram_type == "actors_diagram":
                result = self.generate_actors_diagram(system_model)
            elif diagram_type == "operational_sequence":
                result = self.generate_operational_sequence(system_model)
            elif diagram_type == "functional_breakdown":
                result = self.generate_functional_breakdown(system_model)
            elif diagram_type == "functional_behavior":
                result = self.generate_functional_behavior(system_model)
            elif diagram_type == "modes_diagram":
                result = self.generate_modes_diagram(system_model)
            elif diagram_type == "bdd":
                result = self.generate_bdd(system_model)
            elif diagram_type == "ibd":
                result = self.generate_ibd(system_model)
            elif diagram_type == "technical_architecture":
                result = self.generate_technical_architecture(system_model)
            
            if result:
                diagrams.append(result)
        
        return {"diagrams": diagrams}

    def generate_functional_breakdown(self, system_model: dict) -> Optional[dict]:
        """
        Génère un diagramme d'arborescence fonctionnelle (FBS).
        
        Args:
            system_model: Modèle fonctionnel
        
        Returns:
            Diagramme ou None
        """
        functions = system_model.get("functions", [])
        if not functions:
            return None
        
        system_name = system_model.get("system_name", "System")
        
        # Construction du code PlantUML
        plantuml_code = "@startuml\n"
        plantuml_code += "skinparam style strictuml\n"
        plantuml_code += f"title \"Arborescence Fonctionnelle - {system_name}\"\n\n"
        
        plantuml_code += f"package \"{system_name}\" {{\n"
        
        # Créer les rectangles pour chaque fonction
        for func in functions:
            func_name = func.get("name", "Function")
            func_id = self._sanitize_id(func_name)
            sub_functions = func.get("sub_functions", [])
            
            if sub_functions:
                plantuml_code += f"  rectangle \"{func_name}\" as {func_id} {{\n"
                for sub in sub_functions:
                    sub_name = sub.get("name", "SubFunction") if isinstance(sub, dict) else str(sub)
                    sub_id = self._sanitize_id(sub_name)
                    plantuml_code += f"    rectangle \"{sub_name}\" as {sub_id}\n"
                plantuml_code += "  }\n"
            else:
                plantuml_code += f"  rectangle \"{func_name}\" as {func_id}\n"
        
        plantuml_code += "}\n\n"
        
        # Liens hiérarchiques
        for func in functions:
            if func.get("sub_functions"):
                func_id = self._sanitize_id(func.get("name", ""))
                for sub in func.get("sub_functions", []):
                    sub_name = sub.get("name", "SubFunction") if isinstance(sub, dict) else str(sub)
                    sub_id = self._sanitize_id(sub_name)
                    plantuml_code += f"{func_id} --> {sub_id}\n"
        
        plantuml_code += "@enduml"
        
        # Rendu SVG
        svg = self._render_svg(plantuml_code)
        
        return {
            "type": "functional_breakdown",
            "title": "Functional Breakdown Structure",
            "plantuml_code": plantuml_code,
            "svg": svg
        }

    def generate_functional_behavior(self, system_model: dict) -> Optional[dict]:
        """
        Génère un diagramme de comportement fonctionnel (flux entre fonctions).
        
        Args:
            system_model: Modèle fonctionnel
        
        Returns:
            Diagramme ou None
        """
        functions = system_model.get("functions", [])
        flows = system_model.get("functional_flows", [])
        
        if not functions or not flows:
            return None
        
        system_name = system_model.get("system_name", "System")
        
        # Construction du code PlantUML
        plantuml_code = "@startuml\n"
        plantuml_code += "skinparam style strictuml\n"
        plantuml_code += f"title \"Comportement Fonctionnel - {system_name}\"\n\n"
        
        # Créer les rectangles pour chaque fonction
        for func in functions:
            func_name = func.get("name", "Function")
            func_id = self._sanitize_id(func_name)
            plantuml_code += f"rectangle \"{func_name}\" as {func_id}\n"
        
        plantuml_code += "\n"
        
        # Flux entre fonctions
        for flow in flows:
            from_func = flow.get("from_function", "")
            to_func = flow.get("to_function", "")
            item = flow.get("item", "")
            
            if from_func and to_func:
                from_id = self._sanitize_id(from_func)
                to_id = self._sanitize_id(to_func)
                label = f" : {item}" if item else ""
                plantuml_code += f"{from_id} --> {to_id}{label}\n"
        
        plantuml_code += "@enduml"
        
        # Rendu SVG
        svg = self._render_svg(plantuml_code)
        
        return {
            "type": "functional_behavior",
            "title": "Functional Behavior Diagram",
            "plantuml_code": plantuml_code,
            "svg": svg
        }

    def generate_technical_architecture(self, system_model: dict) -> Optional[dict]:
        """
        Génère un diagramme d'architecture technique.
        
        Args:
            system_model: Modèle technique
        
        Returns:
            Diagramme ou None
        """
        # Chercher technical_parts ou parts
        parts = system_model.get("technical_parts", [])
        if not parts:
            parts = system_model.get("parts", [])
        
        if not parts:
            return None
        
        system_name = system_model.get("system_name", "System")
        connections = system_model.get("physical_connections", [])
        if not connections:
            connections = system_model.get("connections", [])
        
        # Construction du code PlantUML
        plantuml_code = "@startuml\n"
        plantuml_code += "skinparam style strictuml\n"
        plantuml_code += f"title \"Architecture Technique - {system_name}\"\n\n"
        
        # Créer les nodes pour chaque composant technique
        for part in parts:
            part_name = part.get("name", "Component")
            part_type = part.get("type", "")
            part_id = self._sanitize_id(part_name)
            
            stereotype = f" <<{part_type}>>" if part_type else ""
            plantuml_code += f"node \"{part_name}\" as {part_id}{stereotype}\n"
        
        plantuml_code += "\n"
        
        # Connexions physiques
        for conn in connections:
            from_port = conn.get("from_port", "")
            to_port = conn.get("to_port", "")
            description = conn.get("description", "") or conn.get("item", "")
            
            if from_port and to_port:
                # Extraire les noms des composants
                from_part = from_port.split(".")[0] if "." in from_port else from_port
                to_part = to_port.split(".")[0] if "." in to_port else to_port
                
                from_id = self._sanitize_id(from_part)
                to_id = self._sanitize_id(to_part)
                
                label = f" : {description}" if description else ""
                plantuml_code += f"{from_id} --> {to_id}{label}\n"
        
        plantuml_code += "@enduml"
        
        # Rendu SVG
        svg = self._render_svg(plantuml_code)
        
        return {
            "type": "technical_architecture",
            "title": "Technical Architecture Diagram",
            "plantuml_code": plantuml_code,
            "svg": svg
        }

    def generate_actors_diagram(self, system_model: dict) -> Optional[dict]:
        """
        Génère un diagramme d'acteurs pour le niveau opérationnel.
        Montre les stakeholders et external_systems autour du système.
        """
        system_name = system_model.get("system_name", "System")
        stakeholders = system_model.get("stakeholders", [])
        external_systems = system_model.get("external_systems", [])

        if not stakeholders and not external_systems:
            return None

        sys_id = self._sanitize_id(system_name)
        plantuml_code = "@startuml\n"
        plantuml_code += "skinparam actorStyle awesome\n"
        plantuml_code += "skinparam rectangleBorderColor #336699\n"
        plantuml_code += f'rectangle "{system_name}" as {sys_id} #E8F4FD\n\n'

        for stakeholder in stakeholders:
            s_id = self._sanitize_id(stakeholder)
            plantuml_code += f'actor "{stakeholder}" as {s_id}\n'
            plantuml_code += f"{s_id} --> {sys_id}\n"

        for ext_sys in external_systems:
            e_id = self._sanitize_id(ext_sys)
            plantuml_code += f'rectangle "{ext_sys}" as {e_id} #FFF8E1\n'
            plantuml_code += f"{e_id} <--> {sys_id}\n"

        plantuml_code += "@enduml"

        svg = self._render_svg(plantuml_code)
        return {
            "type": "actors_diagram",
            "title": "Actors & Context Diagram",
            "plantuml_code": plantuml_code,
            "svg": svg
        }

    def generate_operational_sequence(self, system_model: dict) -> Optional[dict]:
        """
        Génère un diagramme de séquence pour le niveau opérationnel.
        Basé sur les operational_scenarios du modèle.
        """
        system_name = system_model.get("system_name", "System")
        scenarios = system_model.get("operational_scenarios", [])

        if not scenarios:
            return None

        # Prendre le premier scénario (le plus représentatif)
        scenario = scenarios[0]
        scenario_name = scenario.get("name", "Scénario principal")
        steps = scenario.get("steps", [])

        if not steps:
            return None

        plantuml_code = "@startuml\n"
        plantuml_code += f'title {scenario_name}\n'
        plantuml_code += "skinparam sequenceArrowThickness 2\n"

        # Participants : acteurs du scénario + système
        stakeholders = system_model.get("stakeholders", [])
        sys_id = self._sanitize_id(system_name)
        plantuml_code += f'participant "{system_name}" as {sys_id}\n'
        for stakeholder in stakeholders[:4]:  # Limiter à 4 acteurs
            s_id = self._sanitize_id(stakeholder)
            plantuml_code += f'actor "{stakeholder}" as {s_id}\n'

        plantuml_code += "\n"

        # Étapes comme messages
        first_actor_id = self._sanitize_id(stakeholders[0]) if stakeholders else sys_id
        for i, step in enumerate(steps[:8]):  # Limiter à 8 étapes
            step_text = step if isinstance(step, str) else step.get("description", f"Étape {i+1}")
            # Alterner entre acteur → système et système → acteur
            if i % 2 == 0:
                plantuml_code += f"{first_actor_id} -> {sys_id} : {step_text}\n"
            else:
                plantuml_code += f"{sys_id} -> {first_actor_id} : {step_text}\n"

        plantuml_code += "@enduml"

        svg = self._render_svg(plantuml_code)
        return {
            "type": "operational_sequence",
            "title": f"Sequence Diagram — {scenario_name}",
            "plantuml_code": plantuml_code,
            "svg": svg
        }

    def generate_modes_diagram(self, system_model: dict) -> Optional[dict]:
        """
        Génère un diagramme d'états des modes opératoires pour le niveau fonctionnel.
        Chaque mode est un état contenant ses fonctions actives.
        """
        system_name = system_model.get("system_name", "System")
        modes = system_model.get("modes", [])

        if not modes:
            return None

        plantuml_code = "@startuml\n"
        plantuml_code += f"title Modes opératoires — {system_name}\n"
        plantuml_code += "skinparam stateBorderColor #336699\n"
        plantuml_code += "skinparam stateBackgroundColor #E8F4FD\n\n"
        plantuml_code += "[*] --> " + self._sanitize_id(modes[0].get("name", "Mode1")) + "\n"

        for mode in modes:
            mode_name = mode.get("name", "Mode")
            mode_id = self._sanitize_id(mode_name)
            active_functions = mode.get("active_functions", [])
            description = mode.get("description", "")

            plantuml_code += f"state \"{mode_name}\" as {mode_id} {{\n"
            if description:
                plantuml_code += f"  {mode_id} : {description}\n"
            for func in active_functions[:5]:  # Limiter à 5 fonctions par mode
                func_name = func if isinstance(func, str) else func.get("name", func)
                plantuml_code += f"  {mode_id} : ✓ {func_name}\n"
            plantuml_code += "}\n"

        # Transitions entre modes consécutifs
        for i in range(len(modes) - 1):
            from_id = self._sanitize_id(modes[i].get("name", f"Mode{i}"))
            to_id = self._sanitize_id(modes[i + 1].get("name", f"Mode{i+1}"))
            plantuml_code += f"{from_id} --> {to_id}\n"

        plantuml_code += "@enduml"

        svg = self._render_svg(plantuml_code)
        return {
            "type": "modes_diagram",
            "title": "Operational Modes Diagram",
            "plantuml_code": plantuml_code,
            "svg": svg
        }
