"""
SysML v2 Agent — Backend FastAPI.
Point d'entrée de l'application.
"""

import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from services.llm_base import LLMBase
from services.llm_factory import create_llm
from services.rag_service import RAGService
from services.state_service import StateService
from services.level_service import LevelService
from services.sysml_validator import SysMLv2Validator
from services.syson_service import SysONService
from models.schemas import (
    GenerateLevelRequest, PatchLevelRequest, ValidateLevelRequest,
    RenameSessionRequest, LevelResponse, PatchLevelResponse,
    ModelLevel, LEVEL_SECTIONS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SysML v2 Agent API",
    description="Génération de modèles SysML v2 à partir de descriptions structurées",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services globaux (initialisés au démarrage)
rag_service: RAGService = None
level_service: LevelService = None
sysml_validator: SysMLv2Validator = None
state_service: StateService = None
llm: LLMBase = None
syson_service: SysONService = None


# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialise tous les services au démarrage."""
    global rag_service, level_service, sysml_validator, state_service, llm, syson_service

    # 1. RAG
    logger.info("Initialisation du service RAG...")
    rag_service = RAGService(
        chroma_dir=settings.CHROMA_DIR,
        embedding_model=settings.EMBEDDING_MODEL,
        sysml_repo_path=settings.SYSML_REPO_PATH,
    )
    result = rag_service.index_sysml_files(force=False)
    if result["status"] == "ok":
        logger.info(f"Indexation : {result['files_indexed']} fichiers, {result['chunks_total']} chunks")
    elif result["status"] == "skipped":
        logger.info(f"Collection existante : {result['existing_chunks']} chunks")

    # 2. LLM
    logger.info("Initialisation du service LLM...")
    if settings.LLM_PROVIDER == "claude":
        llm = create_llm(
            provider="claude",
            api_key=settings.ANTHROPIC_API_KEY,
            model_name=settings.ANTHROPIC_MODEL,
        )
    else:
        api_keys = []
        if settings.GEMINI_API_KEYS:
            api_keys = [k.strip() for k in settings.GEMINI_API_KEYS.split(",")]
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY not in api_keys:
            api_keys.insert(0, settings.GEMINI_API_KEY)
        llm = create_llm(
            provider=settings.LLM_PROVIDER,
            api_keys=api_keys,
            model_name=settings.LLM_MODEL,
        )
    logger.info(f"LLM prêt : {llm.get_provider_name()} / {llm.get_model_name()}")
    if hasattr(llm, "get_status"):
        status = llm.get_status()
        logger.info(f"  {status['available_keys']}/{status['total_keys']} clés disponibles")

    # 3. State
    logger.info("Initialisation du service d'état...")
    state_service = StateService(state_dir=settings.STATE_DIR)

    # 4. Validator
    sysml_validator = SysMLv2Validator()

    # 5. LevelService
    level_service = LevelService(llm=llm, rag=rag_service, state=state_service, validator=sysml_validator)

    # 6. SysON
    try:
        syson_service = SysONService()
        logger.info(f"Service SysON prêt : {syson_service.syson_url}")
    except Exception as e:
        logger.warning(f"Service SysON non disponible : {e}")
        syson_service = None

    logger.info("Backend prêt !")


# ============================================================================
# GROUPE 1 — Santé et configuration
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Vérifie que le backend est opérationnel."""
    info = {
        "status": "ok",
        "version": "0.2.0",
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL,
        "sysml_repo_exists": settings.SYSML_REPO_PATH.exists(),
    }
    if llm and hasattr(llm, "get_status"):
        info["llm_status"] = llm.get_status()
    return info


@app.get("/api/llm-status")
async def llm_status():
    """Retourne le statut détaillé du LLM."""
    if not llm:
        raise HTTPException(status_code=503, detail="LLM non initialisé")
    if not hasattr(llm, "get_status"):
        raise HTTPException(status_code=501, detail="get_status() non supporté")
    return llm.get_status()


@app.get("/api/test-llm")
async def test_llm():
    """Teste la connexion au LLM avec un prompt simple."""
    if not llm:
        raise HTTPException(status_code=503, detail="LLM non initialisé")
    try:
        response = llm.generate(
            prompt="Réponds uniquement par 'OK' si tu reçois ce message.",
            temperature=0.0, max_tokens=64,
        )
        response_text = (response or "").strip()
        if not response_text:
            raise HTTPException(status_code=502, detail="Réponse LLM vide")
        return {
            "status": "ok",
            "provider": llm.get_provider_name(),
            "model": llm.get_model_name(),
            "response": response_text,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur LLM: {e}")


# ============================================================================
# GROUPE 2 — Sections guidées
# ============================================================================

@app.get("/api/sections")
async def get_all_sections():
    """Retourne toutes les sections guidées pour les 4 niveaux MBSE."""
    return {
        "levels": {
            level: sections.model_dump()
            for level, sections in LEVEL_SECTIONS.items()
        }
    }


@app.get("/api/sections/{level}")
async def get_level_sections(level: str):
    """Retourne les sections guidées d'un niveau spécifique."""
    if level not in LEVEL_SECTIONS:
        raise HTTPException(status_code=404, detail=f"Niveau inconnu : {level}")
    sections_data = LEVEL_SECTIONS[level]
    return {
        "level": level,
        "sections": [s.model_dump() for s in sections_data.sections],
    }


# ============================================================================
# GROUPE 3 — Pipeline V2
# ============================================================================

@app.post("/api/v2/generate", response_model=LevelResponse)
async def generate_level(request: GenerateLevelRequest):
    """Génère un niveau MBSE à partir des sections utilisateur."""
    if level_service is None:
        raise HTTPException(status_code=503, detail="Service non initialisé")
    try:
        result = level_service.generate_level(
            sections=[{"section_id": s.section_id, "content": s.content} for s in request.sections],
            level=request.level.value,
            session_id=request.session_id,
            session_name=request.session_name,
            use_rag=request.use_rag,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur génération {request.level} : {e}", exc_info=True)
        error_msg = str(e)
        if any(kw in error_msg.lower() for kw in ("429", "resource_exhausted", "quota", "rate limit")):
            raise HTTPException(status_code=429, detail=f"Quota API dépassé : {error_msg}")
        raise HTTPException(status_code=500, detail=f"Erreur génération : {error_msg}")


@app.post("/api/v2/patch", response_model=PatchLevelResponse)
async def patch_level(request: PatchLevelRequest):
    """Régénère un niveau avec de nouvelles sections."""
    if level_service is None:
        raise HTTPException(status_code=503, detail="Service non initialisé")
    try:
        result = level_service.patch_level(
            session_id=request.session_id,
            level=request.level.value,
            sections=[{"section_id": s.section_id, "content": s.content} for s in request.sections],
            use_rag=request.use_rag,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session {request.session_id} introuvable")
    except Exception as e:
        logger.error(f"Erreur patch {request.level} : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur patch : {e}")


@app.post("/api/v2/validate")
async def validate_level(request: ValidateLevelRequest):
    """Valide un niveau pour permettre de passer au suivant."""
    if level_service is None:
        raise HTTPException(status_code=503, detail="Service non initialisé")
    try:
        return level_service.validate_level(
            session_id=request.session_id,
            level=request.level.value,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session {request.session_id} introuvable")
    except Exception as e:
        logger.error(f"Erreur validation {request.level} : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur validation : {e}")


@app.get("/api/v2/status/{session_id}")
async def get_level_status(session_id: str):
    """Retourne le statut de tous les niveaux d'une session."""
    if level_service is None:
        raise HTTPException(status_code=503, detail="Service non initialisé")
    try:
        return level_service.get_level_status(session_id)
    except Exception as e:
        logger.error(f"Erreur statut : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur statut : {e}")


@app.get("/api/v2/level/{session_id}/{level}")
async def get_level_data(session_id: str, level: str):
    """Retourne les données complètes d'un niveau."""
    if state_service is None:
        raise HTTPException(status_code=503, detail="Service non initialisé")
    try:
        level_data = state_service.get_level(session_id, level)
        return {
            "session_id": session_id,
            "level": level,
            "model": level_data.get("model", {}),
            "sysml_code": level_data.get("sysml_code", ""),
            "summary": level_data.get("summary"),
            "warnings": level_data.get("warnings", []),
            "user_inputs": level_data.get("user_inputs", []),
            "validation_result": level_data.get("validation_result"),
            "validated": level_data.get("validated", False),
            "history": level_data.get("history", []),
        }
    except (ValueError, FileNotFoundError):
        raise HTTPException(status_code=404, detail=f"Niveau {level} introuvable pour session {session_id}")
    except Exception as e:
        logger.error(f"Erreur récupération niveau : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur : {e}")


@app.get("/api/v2/full-sysml/{session_id}")
async def get_full_sysml(session_id: str):
    """Retourne le code SysML v2 complet de tous les niveaux."""
    if level_service is None:
        raise HTTPException(status_code=503, detail="Service non initialisé")
    try:
        sysml_code = level_service.get_full_sysml(session_id)
        return {"session_id": session_id, "sysml_code": sysml_code}
    except Exception as e:
        logger.error(f"Erreur full-sysml : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur : {e}")


@app.get("/api/v2/coherence/{session_id}/{level}")
async def check_level_coherence(session_id: str, level: str):
    """Vérifie la cohérence entre un niveau et ses niveaux adjacents."""
    if level_service is None:
        raise HTTPException(status_code=503, detail="Service non initialisé")
    try:
        return level_service.check_coherence(session_id, level)
    except Exception as e:
        logger.error(f"Erreur cohérence : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur : {e}")


# ============================================================================
# GROUPE 4 — Sessions
# ============================================================================

@app.get("/api/sessions")
async def list_sessions():
    """Liste toutes les sessions existantes."""
    if state_service is None:
        raise HTTPException(status_code=503, detail="Service non initialisé")
    try:
        sessions = state_service.list_sessions()
        return {"sessions": sessions, "total": len(sessions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur listage : {e}")


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Récupère les données complètes d'une session."""
    if state_service is None:
        raise HTTPException(status_code=503, detail="Service non initialisé")
    try:
        return state_service.load_session(session_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur : {e}")


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Supprime une session et toutes ses données."""
    if state_service is None:
        raise HTTPException(status_code=503, detail="Service non initialisé")
    try:
        deleted = state_service.delete_session(session_id)
        if deleted:
            return {"deleted": True, "message": f"Session {session_id} supprimée"}
        return {"deleted": False, "message": f"Session {session_id} introuvable"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur suppression : {e}")


@app.put("/api/v2/session/{session_id}/name")
async def rename_session(session_id: str, request: RenameSessionRequest):
    """Renomme une session."""
    if state_service is None:
        raise HTTPException(status_code=503, detail="Service non initialisé")
    try:
        state_service.rename_session(session_id, request.name)
        return {"session_id": session_id, "name": request.name}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur renommage : {e}")


# ============================================================================
# GROUPE 5 — Échanges LLM
# ============================================================================

@app.get("/api/v2/exchanges/{session_id}")
async def get_llm_exchanges(session_id: str, level: str = None):
    """Retourne les échanges LLM d'une session, optionnellement filtrés par niveau."""
    if state_service is None:
        raise HTTPException(status_code=503, detail="Service non initialisé")
    try:
        exchanges = state_service.get_exchanges(session_id, level=level)
        return {"session_id": session_id, "exchanges": exchanges, "total": len(exchanges)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur : {e}")


@app.get("/api/v2/export/{session_id}")
async def export_session(session_id: str):
    """Exporte toutes les données d'une session."""
    if state_service is None or level_service is None:
        raise HTTPException(status_code=503, detail="Services non initialisés")
    try:
        session_data = state_service.load_session(session_id)
        exchanges = state_service.get_exchanges(session_id)

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
                        "timestamp": e.get("timestamp", ""),
                    }
                    for e in lvl_exchanges
                ],
            }

        return {
            "session_id": session_id,
            "session_name": session_data.get("session_name", ""),
            "description": session_data.get("description", ""),
            "levels": levels_export,
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "total_exchanges": len(exchanges),
            },
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} introuvable")
    except Exception as e:
        logger.error(f"Erreur export : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur export : {e}")


# ============================================================================
# GROUPE 6 — RAG
# ============================================================================

@app.get("/api/rag/stats")
async def get_rag_stats():
    """Retourne les statistiques de la base vectorielle."""
    if rag_service is None:
        raise HTTPException(status_code=503, detail="Service RAG non initialisé")
    try:
        return rag_service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur stats RAG : {e}")


@app.get("/api/rag/search")
async def search_rag(query: str):
    """Recherche des exemples SysML v2 similaires à la requête."""
    if rag_service is None:
        raise HTTPException(status_code=503, detail="Service RAG non initialisé")
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Requête vide")
    try:
        results = rag_service.search(query, top_k=settings.RAG_TOP_K)
        return {"query": query, "top_k": settings.RAG_TOP_K, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recherche : {e}")


# ============================================================================
# GROUPE 7 — Validation SysML
# ============================================================================

@app.post("/api/validate-sysml")
async def validate_sysml_code(request: dict):
    """Valide un code SysML v2."""
    if sysml_validator is None:
        raise HTTPException(status_code=503, detail="Validateur non initialisé")
    try:
        if "sysml_code" in request:
            return sysml_validator.validate(request["sysml_code"])
        elif "session_id" in request and "level" in request:
            if state_service is None:
                raise HTTPException(status_code=503, detail="Service d'état non initialisé")
            level_data = state_service.get_level(request["session_id"], request["level"])
            sysml_code = level_data.get("sysml_code")
            if not sysml_code:
                raise HTTPException(status_code=400, detail=f"Pas de code SysML pour le niveau {request['level']}")
            return sysml_validator.validate(sysml_code)
        else:
            raise HTTPException(status_code=400, detail="Fournir 'sysml_code' ou 'session_id' + 'level'")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur validation SysML : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur validation : {e}")


@app.get("/api/validate-sysml/{session_id}")
async def validate_session_sysml(session_id: str):
    """Valide le code SysML v2 de tous les niveaux d'une session."""
    if sysml_validator is None or level_service is None:
        raise HTTPException(status_code=503, detail="Services non initialisés")
    try:
        results = {}
        for level in level_service.NIVEAUX_ORDER:
            try:
                level_data = state_service.get_level(session_id, level)
                sysml_code = level_data.get("sysml_code")
                if sysml_code:
                    results[level] = sysml_validator.validate(sysml_code)
                else:
                    results[level] = {"valid": None, "message": "Niveau non généré"}
            except ValueError:
                results[level] = {"valid": None, "message": "Niveau non trouvé"}
        return {"session_id": session_id, "levels": results}
    except Exception as e:
        logger.error(f"Erreur validation session : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur : {e}")


# ============================================================================
# GROUPE 8 — SysON
# ============================================================================

@app.get("/api/syson/status")
async def syson_status():
    """Vérifie si SysON est disponible."""
    available = syson_service.is_available() if syson_service else False
    return {
        "available": available,
        "url": syson_service.syson_url if syson_service else "",
    }


@app.post("/api/syson/push")
async def syson_push(request: dict):
    """Envoie le code SysML v2 d'une session vers SysON."""
    if syson_service is None or state_service is None or level_service is None:
        raise HTTPException(status_code=503, detail="Services non initialisés")

    session_id = request.get("session_id", "")
    level = request.get("level", None)
    project_name = request.get("project_name", "SysML Agent Import")

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id requis")

    try:
        if level:
            exchanges = state_service.get_exchanges(session_id, level=level)
            sysml_codes = [
                e.get("sysml_code", "")
                for e in exchanges
                if e.get("sysml_code") and e.get("operation") == "generate_sysml"
            ]
            sysml_code = sysml_codes[-1] if sysml_codes else ""
            if not sysml_code:
                session_data = state_service.load_session(session_id)
                level_data = session_data.get("levels", {}).get(level, {})
                sysml_code = level_data.get("sysml_code", "")
        else:
            sysml_code = level_service.get_full_sysml(session_id)

        if not sysml_code:
            return {
                "success": False,
                "project_id": None,
                "syson_url": None,
                "error": "Aucun code SysML v2 trouvé",
            }

        return syson_service.push_sysml_to_syson(sysml_code, project_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur push SysON : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/syson/project-url/{project_id}")
async def syson_project_url(project_id: str):
    """Retourne le lien direct vers un projet dans SysON."""
    if syson_service is None:
        raise HTTPException(status_code=503, detail="Service SysON non initialisé")
    return {"url": syson_service.get_project_url(project_id)}


@app.get("/api/syson/projects")
async def syson_list_projects():
    """Liste tous les projets disponibles dans SysON."""
    if syson_service is None:
        raise HTTPException(status_code=503, detail="Service SysON non initialisé")
    return {"projects": syson_service.list_projects()}


@app.post("/api/syson/pull")
async def syson_pull(request: dict):
    """Récupère le contenu d'un projet SysON (format EMF JSON natif)."""
    if syson_service is None:
        raise HTTPException(status_code=503, detail="Service SysON non initialisé")
    project_id = request.get("project_id", "")
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id requis")
    return syson_service.export_sysml_from_syson(project_id)


# ============================================================================
# Point d'entrée
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
