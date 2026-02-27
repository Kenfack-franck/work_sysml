"""
Service de communication avec Eclipse SysON.
Permet d'envoyer du code SysML v2 textuel à SysON via son API GraphQL.
"""

import json
import logging
import os
import requests
from uuid import uuid4

logger = logging.getLogger(__name__)


class SysONService:
    """Service de communication avec l'API GraphQL d'Eclipse SysON."""

    def __init__(self, syson_url: str = None):
        """
        Initialise le service SysON.

        Args:
            syson_url: URL de base de SysON. Par défaut, lit la variable d'environnement SYSON_URL.
        """
        self.syson_url = syson_url or os.getenv("SYSON_URL", "http://syson:8080")
        self.graphql_url = f"{self.syson_url}/api/graphql"
        self.headers = {"Content-Type": "application/json"}

    def is_available(self) -> bool:
        """
        Vérifie si SysON est démarré et accessible.

        Returns:
            True si SysON répond avec un statut 200, False sinon.
        """
        try:
            response = requests.get(self.syson_url, timeout=5)
            return response.status_code == 200
        except (requests.ConnectionError, requests.Timeout, Exception) as e:
            logger.debug(f"SysON non accessible : {e}")
            return False

    def _execute_graphql(self, query: str, variables: dict = None) -> dict:
        """
        Exécute une requête GraphQL contre l'API SysON.

        Args:
            query: La requête ou mutation GraphQL.
            variables: Les variables associées à la requête.

        Returns:
            Le contenu JSON de la réponse, ou un dict avec une clé "errors".
        """
        payload = {"query": query, "variables": variables}
        try:
            response = requests.post(
                self.graphql_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError as e:
            logger.error(f"Connexion à SysON impossible : {e}")
            return {"errors": [{"message": f"Connexion impossible : {e}"}]}
        except requests.Timeout:
            logger.error("Timeout lors de l'appel à SysON")
            return {"errors": [{"message": "Timeout lors de l'appel à SysON"}]}
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'appel à SysON : {e}")
            return {"errors": [{"message": str(e)}]}

    def create_project(self, project_name: str) -> dict:
        """
        Crée un nouveau projet dans SysON.

        Args:
            project_name: Nom du projet à créer.

        Returns:
            Dictionnaire avec les clés : project_id (str), success (bool), error (str).
        """
        mutation = """
        mutation CreateProject($input: CreateProjectInput!) {
          createProject(input: $input) {
            __typename
            ... on CreateProjectSuccessPayload {
              project {
                id
              }
            }
            ... on ErrorPayload {
              message
            }
          }
        }
        """
        variables = {"input": {"id": str(uuid4()), "name": project_name, "templateId": "sysmlv2-template", "libraryIds": []}}
        result = self._execute_graphql(mutation, variables)

        if "errors" in result:
            msg = result["errors"][0].get("message", "Erreur inconnue")
            logger.error(f"Erreur création projet SysON : {msg}")
            return {"project_id": None, "success": False, "error": msg}

        payload = result.get("data", {}).get("createProject", {})
        if payload.get("__typename") == "CreateProjectSuccessPayload":
            project_id = payload.get("project", {}).get("id")
            logger.info(f"Projet SysON créé : {project_id}")
            return {"project_id": project_id, "success": True, "error": ""}
        else:
            msg = payload.get("message", "Erreur inconnue")
            logger.error(f"Échec création projet SysON : {msg}")
            return {"project_id": None, "success": False, "error": msg}

    def get_editing_context(self, project_id: str) -> str:
        """
        Récupère l'identifiant du contexte d'édition d'un projet.

        Args:
            project_id: Identifiant du projet SysON.

        Returns:
            L'editing_context_id sous forme de chaîne, ou None en cas d'erreur.
        """
        query = """
        query GetEditingContext($projectId: ID!) {
          viewer {
            project(projectId: $projectId) {
              currentEditingContext {
                id
              }
            }
          }
        }
        """
        variables = {"projectId": project_id}
        result = self._execute_graphql(query, variables)

        if "errors" in result:
            logger.error(f"Erreur récupération editing context : {result['errors']}")
            return None

        try:
            editing_context_id = (
                result["data"]["viewer"]["project"]["currentEditingContext"]["id"]
            )
            logger.info(f"Editing context récupéré : {editing_context_id}")
            return editing_context_id
        except (KeyError, TypeError) as e:
            logger.error(f"Structure de réponse inattendue pour l'editing context : {e}")
            return None

    def create_document(self, editing_context_id: str, document_name: str) -> str:
        """
        Crée un document SysML dans le contexte d'édition du projet.

        Args:
            editing_context_id: Identifiant du contexte d'édition.
            document_name: Nom du document (sans extension, .sysml sera ajouté).

        Returns:
            Le document_id sous forme de chaîne, ou None en cas d'erreur.
        """
        mutation = """
        mutation CreateDocument($input: CreateDocumentInput!) {
          createDocument(input: $input) {
            __typename
            ... on CreateDocumentSuccessPayload {
              document {
                id
              }
            }
            ... on ErrorPayload {
              message
            }
          }
        }
        """
        variables = {
            "input": {
                "id": str(uuid4()),
                "editingContextId": editing_context_id,
                "stereotypeId": "empty_sysmlv2",
                "name": document_name + ".sysml"
            }
        }
        result = self._execute_graphql(mutation, variables)

        if "errors" in result:
            logger.error(f"Erreur création document SysON : {result['errors']}")
            return None

        payload = result.get("data", {}).get("createDocument", {})
        if payload.get("__typename") == "CreateDocumentSuccessPayload":
            document_id = payload.get("document", {}).get("id")
            logger.info(f"Document SysON créé : {document_id}")
            return document_id
        else:
            msg = payload.get("message", "Erreur inconnue")
            logger.error(f"Échec création document SysON : {msg}")
            return None

    def get_root_namespace_id(self, editing_context_id: str, document_id: str) -> str:
        """
        Crée un Package racine dans le document SysML et retourne son ID.

        Utilise la mutation createRootObject avec le descripteur SysMLv2EditService-Package.

        Args:
            editing_context_id: Identifiant du contexte d'édition.
            document_id: Identifiant du document où créer le Package.

        Returns:
            L'identifiant du Package racine créé, ou None en cas d'erreur.
        """
        mutation = """
        mutation CreateRootObject($input: CreateRootObjectInput!) {
          createRootObject(input: $input) {
            __typename
            ... on CreateRootObjectSuccessPayload {
              object {
                id
                label
              }
            }
            ... on ErrorPayload {
              message
            }
          }
        }
        """
        variables = {
            "input": {
                "id": str(uuid4()),
                "editingContextId": editing_context_id,
                "documentId": document_id,
                "domainId": "http://www.eclipse.org/syson/sysml",
                "rootObjectCreationDescriptionId": "SysMLv2EditService-Package"
            }
        }
        result = self._execute_graphql(mutation, variables)

        if "errors" in result:
            logger.warning(f"Erreur création Package racine : {result['errors']}")
            return None

        payload = result.get("data", {}).get("createRootObject", {})
        if payload.get("__typename") == "CreateRootObjectSuccessPayload":
            obj_id = payload.get("object", {}).get("id")
            logger.info(f"Package racine SysML créé : {obj_id}")
            return obj_id
        else:
            msg = payload.get("message", "Erreur inconnue")
            logger.warning(f"Échec création Package racine : {msg}")
            return None

    def import_sysml_code(
        self, editing_context_id: str, parent_object_id: str, sysml_code: str
    ) -> dict:
        """
        Importe du code SysML v2 textuel dans SysON.

        Args:
            editing_context_id: Identifiant du contexte d'édition.
            parent_object_id: Identifiant de l'objet parent (namespace racine).
            sysml_code: Code SysML v2 textuel à importer.

        Returns:
            Dictionnaire avec les clés : success (bool), error (str).
        """
        mutation = """
        mutation InsertTextualSysMLv2($input: InsertTextualSysMLv2Input!) {
          insertTextualSysMLv2(input: $input) {
            __typename
            ... on SuccessPayload {
              id
            }
            ... on ErrorPayload {
              message
            }
          }
        }
        """
        variables = {
            "input": {
                "id": str(uuid4()),
                "editingContextId": editing_context_id,
                "objectId": parent_object_id,
                "textualContent": sysml_code
            }
        }
        result = self._execute_graphql(mutation, variables)

        if "errors" in result:
            msg = result["errors"][0].get("message", "Erreur inconnue")
            logger.error(f"Erreur import SysML dans SysON : {msg}")
            return {"success": False, "error": msg}

        payload = result.get("data", {}).get("insertTextualSysMLv2", {})
        if payload.get("__typename") == "SuccessPayload":
            logger.info("Code SysML v2 importé avec succès dans SysON")
            return {"success": True, "error": ""}
        else:
            msg = payload.get("message", "Erreur inconnue")
            logger.error(f"Échec import SysML dans SysON : {msg}")
            return {"success": False, "error": msg}

    def push_sysml_to_syson(
        self, sysml_code: str, project_name: str = "SysML Agent Import"
    ) -> dict:
        """
        Méthode principale : orchestre l'envoi complet du code SysML v2 vers SysON.

        Étapes :
        1. Crée un projet SysON
        2. Récupère l'editing context
        3. Crée un document SysML
        4. Récupère le namespace racine
        5. Importe le code SysML v2

        Args:
            sysml_code: Code SysML v2 textuel à envoyer.
            project_name: Nom du projet à créer dans SysON.

        Returns:
            Dictionnaire avec les clés : success (bool), project_id (str), syson_url (str), error (str).
        """
        # Étape 1 : créer le projet
        logger.info(f"Création du projet SysON : {project_name}")
        project_result = self.create_project(project_name)
        if not project_result["success"]:
            return {
                "success": False,
                "project_id": None,
                "syson_url": None,
                "error": f"Échec création projet : {project_result['error']}"
            }
        project_id = project_result["project_id"]

        # Étape 2 : récupérer l'editing context
        logger.info(f"Récupération de l'editing context pour le projet {project_id}")
        editing_context_id = self.get_editing_context(project_id)
        if not editing_context_id:
            return {
                "success": False,
                "project_id": project_id,
                "syson_url": self.get_project_url(project_id),
                "error": "Impossible de récupérer l'editing context"
            }

        # Étape 3 : créer un document
        logger.info("Création du document SysML")
        document_id = self.create_document(editing_context_id, project_name)
        if not document_id:
            return {
                "success": False,
                "project_id": project_id,
                "syson_url": self.get_project_url(project_id),
                "error": "Impossible de créer le document SysML"
            }

        # Étape 4 : récupérer le namespace racine (fallback sur document_id)
        logger.info("Récupération du namespace racine")
        parent_object_id = self.get_root_namespace_id(editing_context_id, document_id)
        if not parent_object_id:
            logger.info("Namespace racine non trouvé, utilisation du document_id comme objectId")
            parent_object_id = document_id

        # Étape 5 : importer le code SysML v2
        logger.info("Import du code SysML v2 dans SysON")
        import_result = self.import_sysml_code(editing_context_id, parent_object_id, sysml_code)

        syson_url = self.get_project_url(project_id)
        if import_result["success"]:
            logger.info(f"Import SysON réussi. Lien projet : {syson_url}")
            return {
                "success": True,
                "project_id": project_id,
                "syson_url": syson_url,
                "error": ""
            }
        else:
            return {
                "success": False,
                "project_id": project_id,
                "syson_url": syson_url,
                "error": f"Échec import : {import_result['error']}"
            }

    def get_project_url(self, project_id: str) -> str:
        """
        Retourne le lien direct vers un projet dans SysON (accessible depuis le navigateur).

        Note : utilise localhost:8085 au lieu de syson:8080 pour l'accès navigateur.

        Args:
            project_id: Identifiant du projet SysON.

        Returns:
            URL complète vers le projet dans l'interface SysON.
        """
        return f"http://localhost:8085/projects/{project_id}/edit"

    def list_projects(self) -> list:
        """
        Liste tous les projets disponibles dans SysON.

        Returns:
            Liste de dicts {"id": str, "name": str}, vide si erreur.
        """
        query = """
        query {
          viewer {
            projects(first: 50) {
              edges {
                node {
                  id
                  name
                }
              }
            }
          }
        }
        """
        result = self._execute_graphql(query)
        try:
            edges = result["data"]["viewer"]["projects"]["edges"]
            return [{"id": e["node"]["id"], "name": e["node"]["name"]} for e in edges]
        except (KeyError, TypeError) as e:
            logger.error(f"Erreur listage projets SysON : {e}")
            return []

    def export_sysml_from_syson(self, project_id: str) -> dict:
        """
        Récupère le contenu d'un projet SysON au format EMF JSON (format natif SysON).

        Note : SysON v2026.1.0 ne fournit pas d'export textuel SysML v2 via API.
        Le contenu retourné est le modèle EMF JSON interne (format propriétaire Eclipse).
        Un outil de conversion EMF JSON → SysML v2 textuel serait nécessaire pour
        obtenir du SysML v2 lisible.

        Utilise l'endpoint REST Sirius Web :
        GET /api/projects/{projectId} avec Accept: application/octet-stream
        qui retourne un fichier ZIP contenant les documents du projet.

        Args:
            project_id: Identifiant du projet SysON.

        Returns:
            Dictionnaire avec les clés :
            - success (bool)
            - project_id (str)
            - documents (list) : liste de {"name": str, "content": dict}
            - format (str) : "emf_json" (pas du SysML v2 textuel)
            - download_url (str) : URL pour télécharger le ZIP depuis le navigateur
            - error (str)
        """
        import io
        import zipfile

        try:
            response = requests.get(
                f"{self.syson_url}/api/projects/{project_id}",
                headers={"Accept": "application/octet-stream"},
                timeout=30
            )
            if response.status_code != 200:
                return {
                    "success": False,
                    "project_id": project_id,
                    "documents": [],
                    "format": "emf_json",
                    "download_url": f"http://localhost:8085/api/projects/{project_id}",
                    "error": f"HTTP {response.status_code}"
                }

            # Extraire le ZIP en mémoire
            zip_data = io.BytesIO(response.content)
            documents = []
            with zipfile.ZipFile(zip_data, "r") as zf:
                for name in zf.namelist():
                    if name.endswith(".json") and "/documents/" in name:
                        doc_content = json.loads(zf.read(name).decode("utf-8"))
                        doc_name = name.split("/")[-1].replace(".json", "")
                        documents.append({"name": doc_name, "content": doc_content})
                        logger.info(f"Document extrait : {name}")

            logger.info(f"Export SysON réussi : {len(documents)} document(s) pour le projet {project_id}")
            return {
                "success": True,
                "project_id": project_id,
                "documents": documents,
                "format": "emf_json",
                "download_url": f"http://localhost:8085/api/projects/{project_id}",
                "error": ""
            }

        except requests.ConnectionError as e:
            logger.error(f"Connexion SysON impossible lors de l'export : {e}")
            return {"success": False, "project_id": project_id, "documents": [], "format": "emf_json",
                    "download_url": "", "error": f"Connexion impossible : {e}"}
        except zipfile.BadZipFile as e:
            logger.error(f"Réponse SysON n'est pas un ZIP valide : {e}")
            return {"success": False, "project_id": project_id, "documents": [], "format": "emf_json",
                    "download_url": "", "error": f"Format ZIP invalide : {e}"}
        except Exception as e:
            logger.error(f"Erreur export SysON : {e}")
            return {"success": False, "project_id": project_id, "documents": [], "format": "emf_json",
                    "download_url": "", "error": str(e)}
