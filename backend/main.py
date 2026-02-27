"""
SysML v2 Agent — Backend FastAPI
Point d'entrée de l'application.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from services.llm_base import LLMBase
from services.llm_factory import create_llm
from services.rag_service import RAGService
from services.state_service import StateService
from services.sysml_service import SysMLService
from services.diagram_service import DiagramService
from services.level_service import LevelService
from services.fidelity_checker import FidelityChecker
from services.sysml_validator import SysMLv2Validator
from services.syson_service import SysONService
from models.schemas import (
    GenerateRequest, GenerateResponse, PatchRequest, PatchResponse,
    GenerateLevelRequest, PatchLevelRequest, ValidateLevelRequest,
    GenerateDiagramsRequest, RenameSessionRequest,
    LevelResponse, PatchLevelResponse, DiagramsResponse
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SysML v2 Agent API",
    description="Génération de modèles SysML v2 à partir de descriptions en langage naturel",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instances globales des services (initialisées au démarrage)
rag_service: RAGService = None
sysml_service: SysMLService = None
diagram_service: DiagramService = None
level_service: LevelService = None
sysml_validator: SysMLv2Validator = None
state_service: StateService = None
llm: LLMBase = None  # Référence globale pour accès au statut
syson_service: SysONService = None


@app.on_event("startup")
async def startup_event():
    """Initialise tous les services au démarrage de l'application."""
    global rag_service, sysml_service, diagram_service, level_service, sysml_validator, state_service, llm, syson_service
    
    # 1. Initialisation du service RAG
    logger.info("Initialisation du service RAG...")
    rag_service = RAGService(
        chroma_dir=settings.CHROMA_DIR,
        embedding_model=settings.EMBEDDING_MODEL,
        sysml_repo_path=settings.SYSML_REPO_PATH,
    )
    
    # Indexation automatique si pas encore fait
    logger.info("Vérification de l'indexation...")
    result = rag_service.index_sysml_files(force=False)
    
    if result["status"] == "ok":
        logger.info(f"✓ Indexation réussie : {result['files_indexed']} fichiers, {result['chunks_total']} chunks")
    elif result["status"] == "skipped":
        logger.info(f"✓ Collection déjà indexée : {result['existing_chunks']} chunks")
    else:
        logger.error(f"✗ Erreur d'indexation : {result}")
    
    # 2. Initialisation du service LLM avec multi-clés
    logger.info("Initialisation du service LLM...")
    
    # Charger les clés API (multi-clés prioritaire)
    api_keys = []
    if settings.GEMINI_API_KEYS:
        api_keys = [k.strip() for k in settings.GEMINI_API_KEYS.split(",")]
    # Ajouter GEMINI_API_KEY si elle n'est pas déjà dans la liste
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY not in api_keys:
        api_keys.insert(0, settings.GEMINI_API_KEY)
    
    # Déterminer le modèle à utiliser (LLM_MODEL prioritaire)
    model_name = getattr(settings, 'LLM_MODEL', None) or settings.GEMINI_MODEL
    
    llm = create_llm(
        provider=settings.LLM_PROVIDER,
        api_keys=api_keys,
        model_name=model_name,
    )
    logger.info(f"✓ LLM prêt : {llm.get_provider_name()} / {llm.get_model_name()}")
    
    # Afficher le statut des clés
    if hasattr(llm, 'get_status'):
        status = llm.get_status()
        logger.info(f"  → {status['available_keys']}/{status['total_keys']} clés disponibles")
    
    # 3. Initialisation du service d'état
    logger.info("Initialisation du service d'état...")
    state_service = StateService(state_dir=settings.STATE_DIR)
    logger.info(f"✓ État prêt : {settings.STATE_DIR}")
    
    # 4. Initialisation du fidelity checker
    fidelity_checker = FidelityChecker()
    logger.info("✓ Fidelity checker prêt")
    
    # 5. Initialisation du service SysML (ancien workflow)
    logger.info("Initialisation du service SysML...")
    sysml_service = SysMLService(llm=llm, rag=rag_service, state=state_service)
    logger.info("✓ Service SysML prêt")
    
    # 6. Initialisation du service de diagrammes
    logger.info("Initialisation du service de diagrammes...")
    diagram_service = DiagramService(plantuml_server_url=settings.PLANTUML_SERVER_URL)
    logger.info(f"✓ Service de diagrammes prêt : {settings.PLANTUML_SERVER_URL}")
    
    # 7. Initialisation du service de génération par niveaux (nouveau workflow)
    logger.info("Initialisation du service de génération par niveaux...")
    level_service = LevelService(
        llm=llm,
        rag=rag_service,
        state=state_service,
        fidelity_checker=fidelity_checker,
        diagram_service=diagram_service
    )
    logger.info("✓ Service de génération par niveaux prêt")
    
    # 8. Initialisation du validateur SysML v2
    logger.info("Initialisation du validateur SysML v2...")
    sysml_validator = SysMLv2Validator()
    logger.info("✓ Validateur SysML v2 prêt")

    # 9. Initialisation du service SysON
    logger.info("Initialisation du service SysON...")
    syson_service = SysONService()
    logger.info(f"✓ Service SysON prêt : {syson_service.syson_url}")

    logger.info("Backend prêt !")


@app.get("/api/health")
async def health_check():
    """Vérifie que le backend est opérationnel."""
    health_info = {
        "status": "ok",
        "version": "0.1.0",
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": getattr(settings, 'LLM_MODEL', settings.GEMINI_MODEL),
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "embedding_model": settings.EMBEDDING_MODEL,
        "sysml_repo_exists": settings.SYSML_REPO_PATH.exists(),
    }
    
    # Ajouter le statut des clés LLM si disponible
    if llm and hasattr(llm, 'get_status'):
        health_info["llm_status"] = llm.get_status()
    
    return health_info


@app.get("/api/llm-status")
async def llm_status():
    """Retourne le statut détaillé du LLM (nombre de clés disponibles, etc.)."""
    if not llm:
        raise HTTPException(status_code=503, detail="LLM non initialisé")
    
    if not hasattr(llm, 'get_status'):
        raise HTTPException(
            status_code=501, 
            detail="Le LLM actuel ne supporte pas get_status()"
        )
    
    return llm.get_status()


@app.get("/api/test-llm")
async def test_llm():
    """Teste la connexion au LLM avec un prompt simple."""
    try:
        llm = create_llm(
            provider=settings.LLM_PROVIDER,
            api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_MODEL,
        )
        response = llm.generate(
            prompt="Réponds uniquement par 'OK' si tu reçois ce message.",
            temperature=0.0,
            max_tokens=64,
        )
        response_text = (response or "").strip()
        if not response_text:
            raise HTTPException(
                status_code=502,
                detail="Le LLM a répondu sans texte (réponse vide ou bloquée).",
            )

        return {
            "status": "ok",
            "provider": llm.get_provider_name(),
            "model": llm.get_model_name(),
            "response": response_text,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur LLM: {str(e)}")


@app.get("/api/rag/stats")
async def get_rag_stats():
    """Retourne les statistiques de la base vectorielle."""
    if rag_service is None:
        raise HTTPException(status_code=503, detail="Service RAG non initialisé")
    
    try:
        stats = rag_service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des stats : {str(e)}")


@app.get("/api/rag/search")
async def search_rag(query: str):
    """
    Recherche des exemples SysML v2 similaires à la requête.
    
    Args:
        query: Requête de recherche en langage naturel
    """
    if rag_service is None:
        raise HTTPException(status_code=503, detail="Service RAG non initialisé")
    
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="La requête ne peut pas être vide")
    
    try:
        results = rag_service.search(query, top_k=settings.RAG_TOP_K)
        return {
            "query": query,
            "top_k": settings.RAG_TOP_K,
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche : {str(e)}")


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_system(request: GenerateRequest):
    """
    Génère un nouveau système SysML v2 à partir d'une description en langage naturel.
    
    Args:
        request: Requête de génération avec description et options
    
    Returns:
        Modèle généré avec session_id, system_model, sysml_code et sources RAG
    """
    if sysml_service is None:
        raise HTTPException(status_code=503, detail="Service SysML non initialisé")
    
    try:
        result = sysml_service.generate(
            description=request.description,
            session_id=request.session_id,
            use_rag=request.use_rag,
        )
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la génération : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération : {str(e)}")


@app.post("/api/patch", response_model=PatchResponse)
async def patch_system(request: PatchRequest):
    """
    Modifie un système existant selon une instruction.
    
    Args:
        request: Requête de modification avec session_id et instruction
    
    Returns:
        Modèle modifié avec session_id, system_model, sysml_code et résumé des changements
    """
    if sysml_service is None:
        raise HTTPException(status_code=503, detail="Service SysML non initialisé")
    
    try:
        result = sysml_service.patch(
            session_id=request.session_id,
            instruction=request.instruction,
            use_rag=request.use_rag,
        )
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session {request.session_id} introuvable")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors du patch : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors du patch : {str(e)}")


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """
    Récupère les données d'une session existante.
    
    Args:
        session_id: ID de la session
    
    Returns:
        Données complètes de la session
    """
    if sysml_service is None:
        raise HTTPException(status_code=503, detail="Service SysML non initialisé")
    
    try:
        session_data = sysml_service.state.load_session(session_id)
        return session_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération : {str(e)}")


@app.get("/api/sessions")
async def list_sessions():
    """
    Liste toutes les sessions existantes.
    
    Returns:
        Liste des sessions avec leurs métadonnées
    """
    if sysml_service is None:
        raise HTTPException(status_code=503, detail="Service SysML non initialisé")
    
    try:
        sessions = sysml_service.state.list_sessions()
        return {"sessions": sessions, "total": len(sessions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du listage : {str(e)}")


@app.post("/api/diagrams")
async def generate_all_diagrams(request: dict):
    """
    Génère tous les diagrammes disponibles pour une session.
    
    Args:
        request: {"session_id": "..."}
    
    Returns:
        Liste de tous les diagrammes avec leur code PlantUML et SVG
    """
    if sysml_service is None or diagram_service is None:
        raise HTTPException(status_code=503, detail="Services non initialisés")
    
    session_id = request.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id requis")
    
    try:
        # Charger la session
        session_data = sysml_service.state.load_session(session_id)
        system_model = session_data.get("system_model")
        
        if not system_model:
            raise HTTPException(status_code=400, detail="Session sans modèle système")
        
        # Générer tous les diagrammes
        result = diagram_service.generate_all(system_model)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} introuvable")
    except Exception as e:
        logger.error(f"Erreur lors de la génération des diagrammes : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération des diagrammes : {str(e)}")


@app.post("/api/diagrams/{diagram_type}")
async def generate_specific_diagram(diagram_type: str, request: dict):
    """
    Génère un diagramme spécifique pour une session.
    
    Args:
        diagram_type: Type de diagramme (bdd, ibd, context, requirements, use_cases)
        request: {"session_id": "..."}
    
    Returns:
        Diagramme demandé avec son code PlantUML et SVG
    """
    if sysml_service is None or diagram_service is None:
        raise HTTPException(status_code=503, detail="Services non initialisés")
    
    session_id = request.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id requis")
    
    # Vérifier que le type est valide
    valid_types = ["bdd", "ibd", "context", "requirements", "use_cases"]
    if diagram_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Type de diagramme invalide. Types supportés : {', '.join(valid_types)}")
    
    try:
        # Charger la session
        session_data = sysml_service.state.load_session(session_id)
        system_model = session_data.get("system_model")
        
        if not system_model:
            raise HTTPException(status_code=400, detail="Session sans modèle système")
        
        # Générer le diagramme demandé
        method_name = f"generate_{diagram_type}"
        if not hasattr(diagram_service, method_name):
            raise HTTPException(status_code=400, detail=f"Type de diagramme non supporté : {diagram_type}")
        
        generate_method = getattr(diagram_service, method_name)
        diagram = generate_method(system_model)
        
        if diagram is None:
            raise HTTPException(status_code=400, detail=f"Impossible de générer le diagramme {diagram_type} pour ce modèle")
        
        return diagram
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} introuvable")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la génération du diagramme {diagram_type} : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération du diagramme : {str(e)}")


# ============================================================================
# ENDPOINTS API V2 — WORKFLOW MULTI-NIVEAUX
# ============================================================================

@app.post("/api/v2/generate", response_model=LevelResponse)
async def generate_level(request: GenerateLevelRequest):
    """
    Génère un niveau spécifique du modèle MBSE.
    
    Args:
        request: Requête avec session_id, session_name, description, level, use_rag
    
    Returns:
        Résultat avec model, sysml_code, rag_sources, warnings, available_diagrams
    """
    if level_service is None:
        raise HTTPException(status_code=503, detail="Service de génération par niveaux non initialisé")
    
    try:
        result = level_service.generate_level(
            description=request.description,
            level=request.level.value,
            session_id=request.session_id,
            session_name=request.session_name,
            use_rag=request.use_rag
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Erreur lors de la génération du niveau {request.level} : {error_msg}", exc_info=True)
        
        # Détection d'erreur de quota
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            raise HTTPException(
                status_code=429, 
                detail=f"Quota API dépassé. La rotation de clé a été tentée. Détails : {error_msg}"
            )
        
        # Autre erreur
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération : {error_msg}")


@app.post("/api/v2/patch", response_model=PatchLevelResponse)
async def patch_level(request: PatchLevelRequest):
    """
    Modifie un niveau existant.
    
    Args:
        request: Requête avec session_id, level, instruction, use_rag
    
    Returns:
        Résultat avec model, sysml_code, changes_summary, coherence_warnings
    """
    if level_service is None:
        raise HTTPException(status_code=503, detail="Service de génération par niveaux non initialisé")
    
    try:
        result = level_service.patch_level(
            session_id=request.session_id,
            level=request.level.value,
            instruction=request.instruction,
            use_rag=request.use_rag
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session {request.session_id} introuvable")
    except Exception as e:
        logger.error(f"Erreur lors du patch du niveau {request.level} : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors du patch : {str(e)}")


@app.post("/api/v2/validate")
async def validate_level(request: ValidateLevelRequest):
    """
    Valide un niveau pour permettre de passer au suivant.
    
    Args:
        request: Requête avec session_id, level
    
    Returns:
        {"session_id", "level", "validated", "next_level"}
    """
    if level_service is None:
        raise HTTPException(status_code=503, detail="Service de génération par niveaux non initialisé")
    
    try:
        result = level_service.validate_level(
            session_id=request.session_id,
            level=request.level.value
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session {request.session_id} introuvable")
    except Exception as e:
        logger.error(f"Erreur lors de la validation du niveau {request.level} : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la validation : {str(e)}")


@app.put("/api/v2/session/{session_id}/name")
async def rename_session(session_id: str, request: RenameSessionRequest):
    """
    Renomme une session.
    
    Args:
        session_id: ID de la session
        request: Requête avec le nouveau nom
    
    Returns:
        {"session_id", "name", "message"}
    """
    if state_service is None:
        raise HTTPException(status_code=503, detail="Service d'état non initialisé")
    
    try:
        state_service.rename_session(session_id, request.name)
        return {
            "session_id": session_id,
            "name": request.name,
            "message": "Session renommée"
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} introuvable")
    except Exception as e:
        logger.error(f"Erreur lors du renommage de la session : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors du renommage : {str(e)}")


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """
    Supprime une session et toutes ses données.

    Args:
        session_id: ID de la session

    Returns:
        {"success": bool, "message": str}
    """
    if state_service is None:
        raise HTTPException(status_code=503, detail="Service d'état non initialisé")

    try:
        deleted = state_service.delete_session(session_id)
        if deleted:
            return {"success": True, "message": f"Session {session_id} supprimée"}
        else:
            return {"success": False, "message": f"Session {session_id} introuvable"}
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la session : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression : {str(e)}")


@app.get("/api/v2/coherence/{session_id}/{level}")
async def check_level_coherence(session_id: str, level: str):
    """
    Vérifie la cohérence entre un niveau et ses niveaux adjacents.
    
    Args:
        session_id: ID de session
        level: Niveau à vérifier
    
    Returns:
        {"coherent": bool, "issues": [...]}
    """
    if level_service is None:
        raise HTTPException(status_code=503, detail="Service de génération par niveaux non initialisé")
    
    try:
        result = level_service.check_coherence(session_id, level)
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de cohérence : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification : {str(e)}")


@app.get("/api/v2/status/{session_id}")
async def get_level_status(session_id: str):
    """
    Retourne le statut de tous les niveaux d'une session.
    
    Args:
        session_id: ID de session
    
    Returns:
        Statut de chaque niveau (generated, validated, has_diagrams, history_count)
    """
    if level_service is None:
        raise HTTPException(status_code=503, detail="Service de génération par niveaux non initialisé")
    
    try:
        result = level_service.get_level_status(session_id)
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du statut : {str(e)}")


@app.get("/api/v2/level/{session_id}/{level}")
async def get_level_data(session_id: str, level: str):
    """
    Retourne les données complètes d'un niveau.
    
    Args:
        session_id: ID de session
        level: Niveau (operational, functional, logical, technical)
    
    Returns:
        Données du niveau : model, sysml_code, llm_warnings, validation_result, diagrams, validated, history
    """
    if level_service is None:
        raise HTTPException(status_code=503, detail="Service non initialisé")
    
    try:
        level_data = level_service.state.get_level(session_id, level)
        
        return {
            "session_id": session_id,
            "level": level,
            "model": level_data.get("model", {}),
            "sysml_code": level_data.get("sysml_code", ""),
            "llm_warnings": level_data.get("llm_warnings", []),
            "validation_result": level_data.get("validation_result", {"valid": True, "errors": [], "warnings": [], "score": 100}),
            "diagrams": level_data.get("diagrams", []),
            "validated": level_data.get("validated", False),
            "history": level_data.get("history", [])
        }
    except (ValueError, FileNotFoundError):
        raise HTTPException(status_code=404, detail=f"Niveau {level} introuvable pour session {session_id}")
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du niveau : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur : {str(e)}")


@app.get("/api/v2/full-sysml/{session_id}")
async def get_full_sysml(session_id: str):
    """
    Retourne le code SysML v2 complet en concaténant tous les niveaux validés.
    
    Args:
        session_id: ID de session
    
    Returns:
        {"sysml_code": "..."}
    """
    if level_service is None:
        raise HTTPException(status_code=503, detail="Service de génération par niveaux non initialisé")
    
    try:
        sysml_code = level_service.get_full_sysml(session_id)
        return {"sysml_code": sysml_code}
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du code SysML complet : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération : {str(e)}")


@app.post("/api/v2/diagrams", response_model=DiagramsResponse)
async def generate_level_diagrams(request: GenerateDiagramsRequest):
    """
    Génère les diagrammes appropriés pour un niveau donné.
    
    Args:
        request: Requête avec session_id, level, diagram_types
    
    Returns:
        Liste des diagrammes générés
    """
    if level_service is None or diagram_service is None:
        raise HTTPException(status_code=503, detail="Services non initialisés")
    
    try:
        # Charger le modèle du niveau
        level_data = level_service.state.get_level(request.session_id, request.level.value)
        system_model = level_data.get("model")
        
        if not system_model:
            raise HTTPException(status_code=400, detail=f"Le niveau {request.level} n'a pas de modèle")
        
        # Générer les diagrammes pour ce niveau
        result = diagram_service.generate_for_level(system_model, request.level.value)
        
        # Sauvegarder seulement le code PlantUML (pas le SVG pour économiser de l'espace)
        diagrams_to_save = []
        for diagram in result["diagrams"]:
            diagrams_to_save.append({
                "type": diagram.get("type"),
                "title": diagram.get("title"),
                "plantuml_code": diagram.get("plantuml_code")
                # SVG n'est pas sauvegardé, il sera regénéré à la demande
            })
        
        level_data["diagrams"] = diagrams_to_save
        level_service.state.save_level(request.session_id, request.level.value, level_data)
        
        return {
            "session_id": request.session_id,
            "level": request.level,
            "diagrams": result["diagrams"]  # Retourner avec SVG pour affichage immédiat
        }
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Niveau {request.level} introuvable pour cette session")
    except Exception as e:
        logger.error(f"Erreur lors de la génération des diagrammes : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération des diagrammes : {str(e)}")


@app.get("/api/v2/diagrams/{session_id}/{level}")
async def get_level_diagrams(session_id: str, level: str):
    """
    Récupère les diagrammes d'un niveau (regénère les SVG depuis le code PlantUML stocké).
    
    Args:
        session_id: ID de session
        level: Niveau (operational, functional, logical, technical)
    
    Returns:
        Liste des diagrammes avec SVG regénérés
    """
    if level_service is None or diagram_service is None:
        raise HTTPException(status_code=503, detail="Services non initialisés")
    
    try:
        # Charger le niveau
        level_data = level_service.state.get_level(session_id, level)
        stored_diagrams = level_data.get("diagrams", [])
        
        if not stored_diagrams:
            return {
                "session_id": session_id,
                "level": level,
                "diagrams": []
            }
        
        # Regénérer les SVG depuis le code PlantUML
        diagrams_with_svg = []
        for diagram in stored_diagrams:
            plantuml_code = diagram.get("plantuml_code", "")
            if plantuml_code:
                svg = diagram_service._render_svg(plantuml_code)
                diagrams_with_svg.append({
                    "type": diagram.get("type"),
                    "title": diagram.get("title"),
                    "plantuml_code": plantuml_code,
                    "svg": svg
                })
        
        return {
            "session_id": session_id,
            "level": level,
            "diagrams": diagrams_with_svg
        }
    except (ValueError, FileNotFoundError):
        raise HTTPException(status_code=404, detail=f"Niveau {level} introuvable pour session {session_id}")
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des diagrammes : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur : {str(e)}")


@app.post("/api/validate-sysml")
async def validate_sysml_code(request: dict):
    """
    Valide un code SysML v2.
    
    Args:
        request: Soit {"sysml_code": "..."} soit {"session_id": "...", "level": "..."}
    
    Returns:
        Résultat de validation avec score, errors, warnings, info, summary
    """
    if sysml_validator is None:
        raise HTTPException(status_code=503, detail="Validateur non initialisé")
    
    try:
        # Cas 1 : Code fourni directement
        if "sysml_code" in request:
            sysml_code = request["sysml_code"]
            result = sysml_validator.validate(sysml_code)
            return result
        
        # Cas 2 : Charger depuis session_id + level
        elif "session_id" in request and "level" in request:
            session_id = request["session_id"]
            level = request["level"]
            
            if level_service is None:
                raise HTTPException(status_code=503, detail="Service de niveaux non initialisé")
            
            level_data = level_service.state.get_level(session_id, level)
            sysml_code = level_data.get("sysml_code")
            
            if not sysml_code:
                raise HTTPException(status_code=400, detail=f"Aucun code SysML v2 trouvé pour le niveau {level}")
            
            result = sysml_validator.validate(sysml_code)
            return result
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Requête invalide. Fournir soit 'sysml_code' soit 'session_id' + 'level'"
            )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la validation : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la validation : {str(e)}")


@app.get("/api/validate-sysml/{session_id}")
async def validate_session_sysml(session_id: str):
    """
    Valide le code SysML v2 de tous les niveaux d'une session.
    
    Args:
        session_id: ID de la session
    
    Returns:
        dict avec la validation par niveau
    """
    if sysml_validator is None or level_service is None:
        raise HTTPException(status_code=503, detail="Services non initialisés")
    
    try:
        results = {}
        
        for level in level_service.NIVEAUX_ORDER:
            try:
                level_data = level_service.state.get_level(session_id, level)
                sysml_code = level_data.get("sysml_code")
                
                if sysml_code:
                    validation = sysml_validator.validate(sysml_code)
                    results[level] = validation
                else:
                    results[level] = {"valid": None, "message": "Niveau non généré"}
            except ValueError:
                results[level] = {"valid": None, "message": "Niveau non trouvé"}
        
        return {
            "session_id": session_id,
            "levels": results
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la validation de session : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la validation : {str(e)}")


@app.get("/api/v2/exchanges/{session_id}")
async def get_llm_exchanges(session_id: str, level: str = None):
    """
    Retourne les échanges LLM d'une session.
    
    Args:
        session_id: ID de la session
        level: Niveau MBSE optionnel (operational, functional, logical, technical)
    
    Returns:
        {"session_id": str, "exchanges": list, "total": int}
    """
    if state_service is None:
        raise HTTPException(status_code=503, detail="Service non initialisé")
    
    try:
        exchanges = state_service.get_exchanges(session_id, level=level)
        return {
            "session_id": session_id,
            "exchanges": exchanges,
            "total": len(exchanges)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des échanges : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/export/{session_id}")
async def export_session(session_id: str):
    """
    Exporte toutes les données d'une session (modèles JSON + échanges LLM) dans un format structuré.
    
    Args:
        session_id: ID de la session
    
    Returns:
        Dictionnaire complet avec description, niveaux et échanges
    """
    if state_service is None or level_service is None:
        raise HTTPException(status_code=503, detail="Services non initialisés")
    
    try:
        session_data = state_service.load_session(session_id)
        exchanges = state_service.get_exchanges(session_id)
        
        # Regrouper les échanges par niveau
        levels_export = {}
        for lvl in level_service.NIVEAUX_ORDER:
            lvl_exchanges = [e for e in exchanges if e.get("level") == lvl]
            levels_export[lvl] = {
                "level": lvl,
                "exchanges": [
                    {
                        "operation": e.get("operation", ""),
                        "prompt_sent": e.get("prompt_sent", ""),
                        "llm_response_raw": e.get("llm_response_raw", ""),
                        "sysml_code": e.get("sysml_code", ""),
                        "success": e.get("success", True),
                        "timestamp": e.get("timestamp", "")
                    }
                    for e in lvl_exchanges
                ]
            }
        
        from datetime import datetime as _dt
        return {
            "session_id": session_id,
            "session_name": session_data.get("session_name", ""),
            "description": session_data.get("description", ""),
            "levels": levels_export,
            "metadata": {
                "exported_at": _dt.now().isoformat(),
                "total_exchanges": len(exchanges)
            }
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de l'export : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS SYSON
# ============================================================================

@app.get("/api/syson/status")
async def syson_status():
    """
    Vérifie si SysON est disponible.

    Returns:
        {"available": bool, "url": str}
    """
    available = syson_service.is_available() if syson_service else False
    return {
        "available": available,
        "url": syson_service.syson_url if syson_service else ""
    }


@app.post("/api/syson/push")
async def syson_push(request: dict):
    """
    Envoie le code SysML v2 d'une session vers SysON.

    Body:
        session_id (str): Identifiant de la session
        level (str, optionnel): Niveau MBSE à envoyer (operational/functional/logical/technical)
        project_name (str, optionnel): Nom du projet dans SysON

    Returns:
        {"success": bool, "project_id": str, "syson_url": str, "error": str}
    """
    if syson_service is None or state_service is None or level_service is None:
        raise HTTPException(status_code=503, detail="Services non initialisés")

    session_id = request.get("session_id", "")
    level = request.get("level", None)
    project_name = request.get("project_name", "SysML Agent Import")

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id requis")

    try:
        # Récupérer le code SysML de la session
        if level:
            # Un seul niveau demandé
            exchanges = state_service.get_exchanges(session_id, level=level)
            sysml_codes = [
                e.get("sysml_code", "")
                for e in exchanges
                if e.get("sysml_code") and e.get("operation") == "generate_sysml"
            ]
            sysml_code = sysml_codes[-1] if sysml_codes else ""
            if not sysml_code:
                # Fallback : chercher dans les données de session
                session_data = state_service.load_session(session_id)
                level_data = session_data.get("levels", {}).get(level, {})
                sysml_code = level_data.get("sysml_code", "")
        else:
            # Tous les niveaux : utilise get_full_sysml du level_service
            sysml_code = level_service.get_full_sysml(session_id)

        if not sysml_code:
            return {
                "success": False,
                "project_id": None,
                "syson_url": None,
                "error": "Aucun code SysML v2 trouvé pour cette session/niveau"
            }

        result = syson_service.push_sysml_to_syson(sysml_code, project_name)
        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors du push SysON : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/syson/project-url/{project_id}")
async def syson_project_url(project_id: str):
    """
    Retourne le lien direct vers un projet dans SysON.

    Args:
        project_id: Identifiant du projet SysON

    Returns:
        {"url": str}
    """
    if syson_service is None:
        raise HTTPException(status_code=503, detail="Service SysON non initialisé")

    return {"url": syson_service.get_project_url(project_id)}


@app.get("/api/syson/projects")
async def syson_list_projects():
    """
    Liste tous les projets disponibles dans SysON.

    Returns:
        {"projects": [{"id": str, "name": str}]}
    """
    if syson_service is None:
        raise HTTPException(status_code=503, detail="Service SysON non initialisé")

    projects = syson_service.list_projects()
    return {"projects": projects}


@app.post("/api/syson/pull")
async def syson_pull(request: dict):
    """
    Récupère le contenu d'un projet SysON (format EMF JSON natif).

    Note : SysON v2026.1.0 ne fournit pas d'export SysML v2 textuel via API.
    Le contenu retourné est le modèle interne EMF JSON de SysON.

    Body:
        project_id (str): Identifiant du projet SysON
        session_id (str, optionnel): Session à associer au résultat

    Returns:
        {"success": bool, "project_id": str, "documents": list,
         "format": str, "download_url": str, "error": str}
    """
    if syson_service is None:
        raise HTTPException(status_code=503, detail="Service SysON non initialisé")

    project_id = request.get("project_id", "")
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id requis")

    result = syson_service.export_sysml_from_syson(project_id)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
