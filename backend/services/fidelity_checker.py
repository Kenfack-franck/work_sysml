"""
Vérificateur de fidélité pour s'assurer que le modèle JSON généré
correspond fidèlement à la description en langage naturel.
"""

import re
import logging
import unicodedata
from typing import Dict, List

logger = logging.getLogger(__name__)


class FidelityChecker:
    """Vérifie que le JSON généré est fidèle à la description."""
    
    # Patterns de phrases à exclure complètement
    EXCLUDED_PATTERNS = [
        r"les?\s+parties?\s+prenantes?\s+sont",
        r"le\s+système\s+externe\s+est",
        r"le\s+système\s+doit",
        r"doit\s+(?:détecter|fonctionner|assurer|garantir|permettre|supporter)",
        r"en\s+moins\s+de\s+\d+",
        r"\d+\s+heures?\s+sur\s+\d+",
        r"(?:envoie|transmet|commande|alimente|reçoit)\s+(?:un|une|le|la|les|des|l')",
    ]
    
    # Mots à exclure après extraction
    EXCLUDED_WORDS = {
        "agent", "administrateur", "opérateur", "utilisateur", "technicien", "ingénieur",
        "partie", "parties", "prenante", "prenantes", "stakeholder", "acteur",
        "réseau", "police", "serveur", "système externe",
        "signal", "flux", "commande", "alerte", "donnée", "information", "position",
        "secondes", "heures", "minutes", "intrusion",
        "détecte", "envoie", "commande", "fonctionne", "doit", "peut",
        "moins", "plus", "sur", "par", "entre", "vers", "depuis",
    }

    def check(self, description: str, system_model: dict) -> dict:
        """
        Vérifie la fidélité entre la description et le modèle JSON.
        
        Args:
            description: Description en langage naturel
            system_model: Modèle JSON généré
        
        Returns:
            {
                "is_faithful": bool,
                "missing_components": list,
                "extra_components": list,
                "warnings": list
            }
        """
        # Extraction des composants
        described_components = self._extract_components_from_description(description)
        model_components = self._extract_components_from_model(system_model)
        
        logger.info(f"Composants décrits : {described_components}")
        logger.info(f"Composants dans le modèle : {model_components}")
        
        # Vérification des composants manquants
        missing_components = []
        for desc_comp in described_components:
            matched = False
            for model_comp in model_components:
                if self._fuzzy_match(desc_comp, model_comp):
                    matched = True
                    break
            if not matched:
                missing_components.append(desc_comp)
        
        # Vérification des composants en trop
        extra_components = []
        for model_comp in model_components:
            matched = False
            for desc_comp in described_components:
                if self._fuzzy_match(model_comp, desc_comp):
                    matched = True
                    break
            if not matched:
                extra_components.append(model_comp)
        
        # Vérification des connexions
        warnings = []
        connection_warnings = self._check_connections(description, system_model)
        warnings.extend(connection_warnings)
        
        is_faithful = len(missing_components) == 0 and len(extra_components) == 0
        
        return {
            "is_faithful": is_faithful,
            "missing_components": missing_components,
            "extra_components": extra_components,
            "warnings": warnings,
        }

    def _extract_components_from_description(self, description: str) -> List[str]:
        """
        Extrait les noms de composants de la description.
        
        Stratégie : Trouver tous les mots précédés d'un article défini ou indéfini,
        en excluant les phrases parlant d'acteurs/exigences/stakeholders.
        """
        components = []
        
        # ÉTAPE 1 : Retirer les phrases qui matchent EXCLUDED_PATTERNS
        cleaned_description = description
        for pattern in self.EXCLUDED_PATTERNS:
            cleaned_description = re.sub(pattern, '', cleaned_description, flags=re.IGNORECASE)
        
        # Mots de liaison à exclure du match
        liaison_words = r'(?!(?:avec|et|and|qui|que|which|that|de|of)\b)'
        
        # Pattern : article + 1-3 mots (mais pas des mots de liaison)
        pattern = r'\b(?:un|une|des|le|la|les|a|an|the)\s+' + liaison_words + r'([A-ZÀ-ÿa-z]+(?:\s+' + liaison_words + r'[A-ZÀ-ÿa-z]+){0,2})(?=[,.\s]|$)'
        
        matches = re.findall(pattern, cleaned_description, re.IGNORECASE)
        
        for match in matches:
            # Normalise
            component = self._normalize_component_name(match)
            
            # Filtrer les composants trop courts (sauf acronymes comme GPS, IMU)
            if not component or len(component) < 3:
                # Vérifier si c'est un acronyme (tout en majuscules)
                if not (len(component) >= 2 and component.isupper()):
                    continue
            
            # ÉTAPE 2 : Filtrer avec EXCLUDED_WORDS
            component_words = component.split()
            if any(word in self.EXCLUDED_WORDS for word in component_words):
                continue
            
            # Filtre les mots courants qui ne sont pas des composants
            stop_words = [
                'système', 'systeme', 'system', 'drone', 'qui', 'que', 'dont', 'où', 'ou',
                'which', 'that', 'where', 'aussi', 'also', 'avec', 'with',
                'contient', 'contains', 'compose', 'composed'
            ]
            
            # Vérifier si le composant est un stop word
            if component in stop_words:
                continue
            
            # Si c'est un nom composé, vérifier qu'il ne contient pas que des stop words
            words = component.split()
            if len(words) > 1 and all(w in stop_words for w in words):
                continue
            
            # ÉTAPE 3 : Retirer les composants qui contiennent des verbes conjugués
            if self._contains_conjugated_verb(component):
                continue
            
            components.append(component)
        
        # Déduplication tout en préservant l'ordre
        seen = set()
        unique_components = []
        for comp in components:
            if comp not in seen:
                seen.add(comp)
                unique_components.append(comp)
        
        return unique_components
    
    def _contains_conjugated_verb(self, text: str) -> bool:
        """Vérifie si le texte contient un verbe conjugué."""
        # Liste de verbes courants à exclure (qui apparaissent dans descriptions)
        common_verbs = [
            'détecte', 'envoie', 'commande', 'fonctionne', 'transmet',
            'alimente', 'reçoit', 'active', 'désactive', 'contrôle',
            'surveille', 'mesure', 'calcule', 'génère', 'produit'
        ]
        
        text_lower = text.lower()
        for verb in common_verbs:
            if verb in text_lower:
                return True
        
        return False

    def _extract_components_from_model(self, system_model: dict) -> List[str]:
        """
        Extrait les noms de composants du modèle JSON.
        """
        components = []
        
        def extract_parts(parts_list):
            for part in parts_list:
                name = self._normalize_component_name(part.get("name", ""))
                if name:
                    components.append(name)
                # Récursion pour les children
                if "children" in part and part["children"]:
                    extract_parts(part["children"])
        
        if "parts" in system_model:
            extract_parts(system_model["parts"])
        
        return components

    def _normalize_component_name(self, name: str) -> str:
        """
        Normalise un nom de composant pour la comparaison.
        """
        if not name:
            return ""
        
        # Enlève les articles
        articles = ['un ', 'une ', 'des ', 'le ', 'la ', 'les ', 'a ', 'an ', 'the ']
        name_lower = name.lower().strip()
        for article in articles:
            if name_lower.startswith(article):
                name_lower = name_lower[len(article):]
                break
        
        # Enlève les accents
        name_lower = self._remove_accents(name_lower)
        
        return name_lower.strip()

    def _remove_accents(self, text: str) -> str:
        """
        Enlève les accents d'une chaîne.
        """
        return ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )

    def _fuzzy_match(self, name1: str, name2: str) -> bool:
        """
        Vérifie si deux noms réfèrent au même composant.
        
        Règles :
        - Identiques après normalisation → True
        - L'un contient l'autre → True
        - Distance de Levenshtein normalisée < 0.3 → True
        """
        n1 = self._normalize_component_name(name1)
        n2 = self._normalize_component_name(name2)
        
        if not n1 or not n2:
            return False
        
        # Identiques
        if n1 == n2:
            return True
        
        # L'un contient l'autre
        if n1 in n2 or n2 in n1:
            return True
        
        # Distance de Levenshtein
        distance = self._levenshtein_distance(n1, n2)
        max_len = max(len(n1), len(n2))
        if max_len == 0:
            return False
        
        normalized_distance = distance / max_len
        
        return normalized_distance < 0.3

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calcule la distance de Levenshtein entre deux chaînes.
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

    def _check_connections(self, description: str, system_model: dict) -> List[str]:
        """
        Vérifie que les connexions décrites sont présentes dans le modèle.
        
        Cherche les patterns de flux :
        - "X envoie Y à Z"
        - "X alimente Z"
        - "X commande Z"
        - "X sends Y to Z"
        """
        warnings = []
        desc_lower = description.lower()
        
        # Patterns de connexion
        connection_patterns = [
            (r'(\w+)\s+envoie\s+\w+\s+(?:à|au)\s+(\w+)', 'flow'),
            (r'(\w+)\s+alimente\s+(?:le|la|les)?\s*(\w+)', 'flow'),
            (r'(\w+)\s+commande\s+(?:le|la|les)?\s*(\w+)', 'flow'),
            (r'(\w+)\s+sends\s+\w+\s+to\s+(\w+)', 'flow'),
        ]
        
        described_connections = []
        for pattern, conn_type in connection_patterns:
            matches = re.findall(pattern, desc_lower)
            for match in matches:
                from_comp = self._normalize_component_name(match[0])
                to_comp = self._normalize_component_name(match[1])
                described_connections.append((from_comp, to_comp, conn_type))
        
        # Extraction des connexions du modèle
        model_connections = []
        if "connections" in system_model:
            for conn in system_model["connections"]:
                # Parse "PartName.portName"
                from_port = conn.get("from_port", "")
                to_port = conn.get("to_port", "")
                
                from_part = from_port.split(".")[0] if "." in from_port else from_port
                to_part = to_port.split(".")[0] if "." in to_port else to_port
                
                from_part = self._normalize_component_name(from_part)
                to_part = self._normalize_component_name(to_part)
                conn_type = conn.get("type", "")
                
                model_connections.append((from_part, to_part, conn_type))
        
        # Vérification des connexions manquantes
        for desc_conn in described_connections:
            found = False
            for model_conn in model_connections:
                # Fuzzy match sur les noms de composants
                if (self._fuzzy_match(desc_conn[0], model_conn[0]) and 
                    self._fuzzy_match(desc_conn[1], model_conn[1]) and
                    desc_conn[2] == model_conn[2]):
                    found = True
                    break
            
            if not found:
                warnings.append(
                    f"Connexion manquante : {desc_conn[0]} → {desc_conn[1]} ({desc_conn[2]})"
                )
        
        return warnings
