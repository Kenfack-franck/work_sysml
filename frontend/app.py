"""
SysML v2 Agent — Frontend Streamlit
Interface MBSE multi-niveaux avec sections guidées pour la génération progressive de modèles SysML v2.
"""

import streamlit as st
import requests
import os
import json
from datetime import datetime

# ============================================================================
# Configuration
# ============================================================================

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
API_TIMEOUT = 180

LEVELS_ORDER = ["operational", "functional", "logical", "technical"]
LEVEL_LABELS = {
    "operational": "🎯 Niveau Opérationnel",
    "functional": "⚙️ Niveau Fonctionnel",
    "logical": "🔧 Niveau Logique",
    "technical": "🏭 Niveau Technique",
}
LEVEL_SHORT = {
    "operational": "Opérationnel",
    "functional": "Fonctionnel",
    "logical": "Logique",
    "technical": "Technique",
}
LEVEL_ICONS = {
    "operational": "🎯",
    "functional": "⚙️",
    "logical": "🔧",
    "technical": "🏭",
}

TAB_SECTIONS = "📝 Sections"
TAB_RESULTS = "📊 Résultats"
TAB_CODE = "💻 Code SysML"
TAB_DEBUG = "🔍 Debug"
TAB_OPTIONS = [TAB_SECTIONS, TAB_RESULTS, TAB_CODE, TAB_DEBUG]

st.set_page_config(
    page_title="SysAgent — Pipeline SysML v2",
    page_icon="🏗️",
    layout="wide",
)


# ============================================================================
# Initialisation du session_state
# ============================================================================

def _init_state():
    """Initialise les clés du session_state si absentes."""
    defaults = {
        "session_id": None,
        "session_name": "",
        "current_level": "operational",
        "sections_data": {},       # {level: {section_id: content}}
        "level_results": {},       # {level: {model, sysml_code, summary, warnings, validation_result}}
        "level_status": {},        # {level: "empty"|"generated"|"validated"}
        "sections_definitions": None,  # chargé depuis GET /api/sections
        "active_tab": TAB_SECTIONS,    # onglet actif dans render_level
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

_init_state()


# ============================================================================
# Appels API
# ============================================================================

def api_call(method: str, endpoint: str, **kwargs):
    """
    Wrapper pour les appels API au backend.

    Returns:
        (success: bool, data: dict | None, error: str | None)
    """
    url = f"{BACKEND_URL}{endpoint}"
    timeout = kwargs.pop("timeout", API_TIMEOUT)
    try:
        resp = getattr(requests, method)(url, timeout=timeout, **kwargs)
        if resp.status_code == 200:
            return True, resp.json(), None
        else:
            detail = ""
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text
            return False, None, f"Erreur {resp.status_code}: {detail}"
    except requests.exceptions.Timeout:
        return False, None, "Timeout — le backend met trop de temps à répondre."
    except requests.exceptions.ConnectionError:
        return False, None, "Backend non accessible."
    except Exception as e:
        return False, None, str(e)


def load_sections_definitions():
    """Charge les définitions de sections depuis le backend (cache en session_state)."""
    if st.session_state.sections_definitions is not None:
        return st.session_state.sections_definitions
    ok, data, err = api_call("get", "/api/sections", timeout=10)
    if ok and data:
        st.session_state.sections_definitions = data.get("levels", {})
    else:
        st.session_state.sections_definitions = {}
    return st.session_state.sections_definitions


def load_level_status():
    """Charge le statut des niveaux depuis le backend."""
    if not st.session_state.session_id:
        return
    ok, data, _ = api_call("get", f"/api/v2/status/{st.session_state.session_id}", timeout=10)
    if ok and data:
        status = {}
        for level in LEVELS_ORDER:
            info = data.get(level, {})
            if info.get("validated"):
                status[level] = "validated"
            elif info.get("generated"):
                status[level] = "generated"
            else:
                status[level] = "empty"
        st.session_state.level_status = status


def format_timestamp(iso_ts):
    """Formate un timestamp ISO."""
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return iso_ts or ""


# ============================================================================
# Sidebar
# ============================================================================

def render_sidebar():
    """Affiche la sidebar : statut backend, sessions, navigation."""
    st.sidebar.title("🏗️ SysML v2 Agent")
    st.sidebar.caption("Workflow MBSE multi-niveaux")
    st.sidebar.markdown("---")

    # --- Statut backend ---
    _render_sidebar_status()
    st.sidebar.markdown("---")

    # --- Gestion des sessions ---
    _render_sidebar_sessions()
    st.sidebar.markdown("---")

    # --- Navigation niveaux ---
    if st.session_state.session_id:
        _render_sidebar_navigation()
        st.sidebar.markdown("---")
        _render_sidebar_syson()


def _render_sidebar_status():
    """Statut du backend, LLM, RAG."""
    st.sidebar.subheader("⚙️ Statut")
    ok, data, _ = api_call("get", "/api/health", timeout=5)
    if ok:
        st.sidebar.success("🟢 Backend opérationnel")
        with st.sidebar.expander("Détails", expanded=False):
            st.caption(f"LLM : {data.get('llm_model', '?')}")
            llm_status = data.get("llm_status", {})
            if llm_status:
                st.caption(f"Clés : {llm_status.get('available_keys', '?')}/{llm_status.get('total_keys', '?')}")
    else:
        st.sidebar.error("🔴 Backend non accessible")

    with st.sidebar.expander("📊 Stats RAG", expanded=False):
        ok_r, stats, _ = api_call("get", "/api/rag/stats", timeout=10)
        if ok_r and stats:
            st.metric("Chunks indexés", stats.get("total_chunks", 0))
            st.metric("Fichiers sources", stats.get("unique_files", 0))
        else:
            st.caption("Non disponible")


def _render_sidebar_sessions():
    """Liste et gestion des sessions."""
    st.sidebar.markdown("### 📁 Sessions")

    ok, data, _ = api_call("get", "/api/sessions", timeout=5)
    sessions_list = data.get("sessions", []) if ok and data else []

    options = ["➕ Nouvelle session"] + [
        s.get("name") or s.get("system_name") or f"Session {(s.get('id', ''))[:8]}"
        for s in sessions_list
    ]
    ids = ["new"] + [s.get("id", "") for s in sessions_list]

    selected = st.sidebar.selectbox(
        "Session active",
        range(len(options)),
        format_func=lambda i: options[i],
        key="session_selector",
    )

    if selected == 0:
        # Nouvelle session
        if st.session_state.session_id:
            if st.sidebar.button("➕ Nouveau projet", key="new_proj_btn"):
                _reset_state()
                st.rerun()
        else:
            st.sidebar.caption("Remplissez les sections ci-dessous pour démarrer.")
    else:
        sel_id = ids[selected]
        sel_session = sessions_list[selected - 1]

        if st.session_state.session_id != sel_id:
            _load_session(sel_id)
            st.rerun()

        current_name = sel_session.get("name") or sel_session.get("system_name") or ""

        # Renommer
        with st.sidebar.expander("✏️ Renommer", expanded=False):
            rename_val = st.text_input("Nouveau nom", value=current_name, key=f"rename_{sel_id}")
            if st.button("💾 Sauvegarder", key=f"rename_btn_{sel_id}"):
                if rename_val.strip():
                    ok_r, _, err = api_call("put", f"/api/v2/session/{sel_id}/name", json={"name": rename_val.strip()}, timeout=5)
                    if ok_r:
                        st.success("Renommé")
                        st.rerun()
                    else:
                        st.error(err)

        # Supprimer
        with st.sidebar.expander("🗑️ Supprimer", expanded=False):
            st.warning(f"Supprimer '{current_name or 'cette session'}' ?")
            if st.button("🗑️ Confirmer", key=f"del_btn_{sel_id}", type="primary"):
                ok_d, _, err = api_call("delete", f"/api/session/{sel_id}", timeout=5)
                if ok_d:
                    _reset_state()
                    st.rerun()
                else:
                    st.error(err)


def _render_sidebar_navigation():
    """Navigation entre les 4 niveaux."""
    st.sidebar.subheader("📈 Progression")
    load_level_status()

    for level in LEVELS_ORDER:
        status = st.session_state.level_status.get(level, "empty")
        icon = "✅" if status == "validated" else ("🔄" if status == "generated" else "⬜")
        label = f"{icon} {LEVEL_ICONS[level]} {LEVEL_SHORT[level]}"
        is_current = level == st.session_state.current_level

        if status != "empty":
            btn_type = "primary" if is_current else "secondary"
            if st.sidebar.button(label, key=f"nav_{level}", use_container_width=True, type=btn_type):
                st.session_state.current_level = level
                st.session_state.active_tab = TAB_RESULTS
                st.rerun()
        else:
            st.sidebar.markdown(f"{'**' if is_current else ''}{label}{'**' if is_current else ''}")

    st.sidebar.caption("✅ Validé | 🔄 Généré | ⬜ À faire")


def _render_sidebar_syson():
    """Statut SysON."""
    try:
        ok, data, _ = api_call("get", "/api/syson/status", timeout=2)
        if ok and data and data.get("available"):
            st.sidebar.success("🟢 SysON connecté")
            st.sidebar.markdown("[Ouvrir SysON ↗](http://localhost:8085)")
        else:
            st.sidebar.info("⚪ SysON non disponible")
    except Exception:
        pass


# ============================================================================
# Helpers de session
# ============================================================================

def _reset_state():
    """Remet le session_state à zéro."""
    st.session_state.session_id = None
    st.session_state.session_name = ""
    st.session_state.current_level = "operational"
    st.session_state.sections_data = {}
    st.session_state.level_results = {}
    st.session_state.level_status = {}
    st.session_state.active_tab = TAB_SECTIONS


def _load_session(session_id: str):
    """Charge une session depuis le backend et restaure le session_state."""
    ok, data, err = api_call("get", f"/api/session/{session_id}", timeout=10)
    if not ok:
        st.error(f"Impossible de charger la session : {err}")
        return

    st.session_state.session_id = session_id
    st.session_state.session_name = data.get("session_name", "")
    st.session_state.current_level = data.get("current_level", "operational")

    levels = data.get("levels", {})
    sections_data = {}
    level_results = {}
    level_status = {}

    for level in LEVELS_ORDER:
        lv_data = levels.get(level, {})

        # Restaurer les sections utilisateur
        user_inputs = lv_data.get("user_inputs", [])
        sec_map = {}
        for inp in user_inputs:
            sid = inp.get("section_id", "")
            if sid:
                sec_map[sid] = inp.get("content", "")
        sections_data[level] = sec_map

        # Restaurer les résultats
        model = lv_data.get("model", {})
        if model:
            level_results[level] = {
                "model": model,
                "sysml_code": lv_data.get("sysml_code", ""),
                "summary": lv_data.get("summary"),
                "warnings": lv_data.get("warnings", []),
                "validation_result": lv_data.get("validation_result"),
            }
            level_status[level] = "validated" if lv_data.get("validated") else "generated"
        else:
            level_status[level] = "empty"

    st.session_state.sections_data = sections_data
    st.session_state.level_results = level_results
    st.session_state.level_status = level_status

    # Ouvrir l'onglet pertinent
    current = st.session_state.current_level
    if level_status.get(current) in ("generated", "validated"):
        st.session_state.active_tab = TAB_RESULTS
    else:
        st.session_state.active_tab = TAB_SECTIONS


# ============================================================================
# Zone principale — Page d'accueil
# ============================================================================

def render_welcome():
    """Affiche la page d'accueil quand aucune session n'est active."""
    st.header("🚀 Nouveau projet MBSE")
    st.markdown("""
Bienvenue dans le **workflow MBSE multi-niveaux**. Vous allez générer votre modèle SysML v2
de manière **progressive** en 4 étapes :

1. **🎯 Opérationnel** — Qui utilise le système et pourquoi
2. **⚙️ Fonctionnel** — Que fait le système
3. **🔧 Logique** — Comment est structuré le système
4. **🏭 Technique** — Avec quoi est construit le système

**Remplissez les sections guidées du premier niveau pour commencer.**
""")
    st.markdown("---")

    # Afficher directement les sections du niveau opérationnel
    st.session_state.session_name = st.text_input(
        "📝 Nom du projet (optionnel)",
        value=st.session_state.session_name,
        placeholder="Ex: Bleed Air System, Drone de surveillance...",
    )

    defs = load_sections_definitions()
    op_defs = defs.get("operational", {})
    sections_list = op_defs.get("sections", [])

    if not sections_list:
        st.warning("Impossible de charger les sections depuis le backend.")
        return

    render_sections("operational", sections_list)

    st.markdown("---")
    use_rag = st.checkbox("🔍 Utiliser le RAG (exemples SysML v2)", value=True, key="rag_welcome")

    if st.button("🚀 Générer le niveau opérationnel", type="primary", use_container_width=True):
        _do_generate("operational", use_rag, is_new_session=True)


# ============================================================================
# Zone principale — Niveau actif avec onglets
# ============================================================================

def render_level(level: str):
    """Affiche l'interface complète pour un niveau avec navigation par onglets."""
    idx = LEVELS_ORDER.index(level) + 1
    st.header(f"Niveau {idx}/4 : {LEVEL_LABELS[level]}")
    if st.session_state.session_id:
        st.caption(f"Session : {st.session_state.session_id[:16]}...")

    status = st.session_state.level_status.get(level, "empty")

    # --- Navigation par onglets (radio horizontal) ---
    # Déterminer l'onglet par défaut
    default_idx = TAB_OPTIONS.index(st.session_state.active_tab) if st.session_state.active_tab in TAB_OPTIONS else 0

    tab = st.radio(
        "Navigation",
        TAB_OPTIONS,
        index=default_idx,
        horizontal=True,
        key=f"level_tab_{level}",
        label_visibility="collapsed",
    )

    st.markdown("---")

    # --- Contenu de l'onglet sélectionné ---
    if tab == TAB_SECTIONS:
        _render_tab_sections(level, status)
    elif tab == TAB_RESULTS:
        _render_tab_results(level, status)
    elif tab == TAB_CODE:
        _render_tab_code(level)
    elif tab == TAB_DEBUG:
        _render_tab_debug(level)


def _render_tab_sections(level: str, status: str):
    """Onglet Sections : résumé précédent, sections guidées, bouton générer."""
    # Résumé du niveau précédent
    render_previous_summary(level)

    # Sections guidées
    defs = load_sections_definitions()
    level_defs = defs.get(level, {})
    sections_list = level_defs.get("sections", [])

    if sections_list:
        render_sections(level, sections_list)
    else:
        st.warning("Sections non disponibles depuis le backend.")

    st.markdown("---")

    # Boutons d'action
    col1, col2 = st.columns([3, 1])
    with col1:
        if status == "empty":
            use_rag = st.checkbox("🔍 RAG", value=True, key=f"rag_{level}")
            if st.button("🚀 Générer", type="primary", use_container_width=True, key=f"gen_{level}"):
                _do_generate(level, use_rag)
        else:
            use_rag = st.checkbox("🔍 RAG", value=True, key=f"rag_patch_{level}")
            if st.button("🔄 Modifier & Régénérer", use_container_width=True, key=f"patch_{level}"):
                _do_patch(level, use_rag)
    with col2:
        if status == "validated":
            st.success("✅ Validé")


def _render_tab_results(level: str, status: str):
    """Onglet Résultats : résumé, warnings, validation, boutons."""
    result = st.session_state.level_results.get(level)

    if not result:
        st.info("Aucun résultat. Remplissez les sections et lancez la génération.")
        return

    # --- Résumé ---
    summary = result.get("summary")
    if summary:
        st.markdown("#### 📊 Ce qui a été compris")
        st.success(summary.get("summary_text", ""))
        key_elements = summary.get("key_elements", {})
        if key_elements:
            cols = st.columns(min(len(key_elements), 4))
            for i, (key, values) in enumerate(key_elements.items()):
                if values:
                    with cols[i % len(cols)]:
                        label = key.replace("_", " ").title()
                        st.markdown(f"**{label}**")
                        for v in values[:6]:
                            st.markdown(f"- {v}")
                        if len(values) > 6:
                            st.caption(f"... +{len(values) - 6}")

    # --- Warnings ---
    warnings = result.get("warnings", [])
    if warnings:
        st.markdown("#### ⚠️ Warnings")
        for w in warnings:
            if isinstance(w, dict):
                w_type = w.get("type", "info")
                w_msg = w.get("message", "")
                w_section = w.get("section", "")
                w_suggestion = w.get("suggestion", "")
                prefix = "⚠️" if w_type == "inconsistency" else ("ℹ️" if w_type == "missing_info" else "❓")
                text = f"{prefix} **[{w_type}]** {w_msg}"
                if w_section:
                    text += f" _(section: {w_section})_"
                if w_suggestion:
                    text += f"\n> 💡 {w_suggestion}"
                st.warning(text)
            else:
                st.warning(str(w))

    # --- Score de validation syntaxique ---
    validation = result.get("validation_result", {})
    if validation:
        st.markdown("#### 🔍 Validation syntaxique")
        score = validation.get("score", "?")
        valid = validation.get("valid", True)
        if valid:
            st.success(f"Score : **{score}/100** ✅")
        else:
            errors = validation.get("errors", [])
            st.warning(f"Score : **{score}/100** — {len(errors)} erreur(s)")
            for err in errors:
                line = err.get("line", "?")
                msg = err.get("message", "")
                st.error(f"Ligne {line} : {msg}")

    st.markdown("---")

    # --- Boutons d'action ---
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        if status == "generated":
            if st.button("✅ Valider et passer au suivant", type="primary", use_container_width=True, key=f"validate_{level}"):
                _do_validate(level)
        elif status == "validated":
            st.success("✅ Niveau validé")
    with col2:
        use_rag = st.checkbox("🔍 RAG", value=True, key=f"rag_result_{level}")
        if st.button("🔄 Modifier & Régénérer", use_container_width=True, key=f"patch_result_{level}"):
            _do_patch(level, use_rag)
    with col3:
        if st.button("🔍 Cohérence", key=f"coh_{level}"):
            _do_coherence(level)


def _render_tab_code(level: str):
    """Onglet Code SysML : code avec coloration, zone copiable, code complet."""
    result = st.session_state.level_results.get(level)

    if not result or not result.get("sysml_code"):
        st.info("Aucun code SysML généré. Lancez la génération depuis l'onglet Sections.")
        return

    sysml_code = result["sysml_code"]

    # --- Code SysML du niveau ---
    st.markdown(f"#### 📝 Code SysML v2 — {LEVEL_SHORT[level]}")
    st.code(sysml_code, language="text", line_numbers=True)

    st.text_area(
        "Code SysML v2 (sélectionner + copier)",
        value=sysml_code,
        height=200,
        key=f"copy_sysml_{level}",
        label_visibility="collapsed",
        disabled=True,
    )

    # --- Code complet tous niveaux ---
    st.markdown("---")
    st.markdown("#### 📦 Code SysML v2 complet (tous niveaux)")

    if st.button("📥 Charger le code complet", key="full_sysml_btn"):
        with st.spinner("Chargement..."):
            ok, data, err = api_call("get", f"/api/v2/full-sysml/{st.session_state.session_id}")
            if ok and data:
                code = data.get("sysml_code", "")
                if code and "Aucun niveau" not in code:
                    st.code(code, language="text", line_numbers=True)
                    st.text_area(
                        "Code complet (copier)",
                        value=code,
                        height=200,
                        key="copy_full_sysml",
                        label_visibility="collapsed",
                        disabled=True,
                    )
                else:
                    st.info("Aucun niveau généré pour le moment.")
            else:
                st.error(err)


def _render_tab_debug(level: str):
    """Onglet Debug : modèle JSON et échanges LLM (sans expanders imbriqués)."""
    result = st.session_state.level_results.get(level)

    # --- Modèle JSON ---
    st.markdown("#### 📋 Modèle JSON")
    if result and result.get("model"):
        st.json(result["model"])
    else:
        st.caption("Aucun modèle JSON disponible.")

    st.markdown("---")

    # --- Échanges LLM ---
    st.markdown("#### 🔍 Échanges LLM")
    if not st.session_state.session_id:
        st.caption("Pas de session active.")
        return

    ok, data, err = api_call("get", f"/api/v2/exchanges/{st.session_state.session_id}", timeout=10)
    if not ok:
        st.caption(f"Erreur : {err}")
        return

    exchanges = data.get("exchanges", [])
    if not exchanges:
        st.caption("Aucun échange enregistré.")
        return

    for i, ex in enumerate(reversed(exchanges)):
        op = ex.get("operation", "?")
        ex_level = ex.get("level", "?")
        ts = format_timestamp(ex.get("timestamp", ""))
        model_name = ex.get("llm_model", "?")
        success = ex.get("success", True)
        status_icon = "✅" if success else "❌"

        with st.expander(f"{status_icon} [{ex_level}] {op} — {ts} ({model_name})"):
            prompt = ex.get("prompt_sent", "")
            if prompt:
                st.text_area(
                    "Prompt envoyé",
                    value=prompt[:3000],
                    height=120,
                    key=f"ex_prompt_{i}",
                    disabled=True,
                )
            response = ex.get("llm_response_raw", "")
            if response:
                st.text_area(
                    "Réponse brute",
                    value=response[:3000],
                    height=120,
                    key=f"ex_resp_{i}",
                    disabled=True,
                )
            if ex.get("error_message"):
                st.error(ex["error_message"])


# ============================================================================
# Composants réutilisables
# ============================================================================

def render_previous_summary(level: str):
    """Affiche le résumé du niveau précédent validé."""
    idx = LEVELS_ORDER.index(level)
    if idx == 0:
        return

    prev_level = LEVELS_ORDER[idx - 1]
    prev_result = st.session_state.level_results.get(prev_level)
    if not prev_result:
        return

    summary = prev_result.get("summary")
    if not summary:
        return

    with st.container():
        st.markdown(f"#### 📋 Résumé du niveau {LEVEL_SHORT[prev_level]} (validé)")
        st.info(summary.get("summary_text", ""))
        key_elements = summary.get("key_elements", {})
        if key_elements:
            cols = st.columns(min(len(key_elements), 4))
            for i, (key, values) in enumerate(key_elements.items()):
                if values:
                    with cols[i % len(cols)]:
                        label = key.replace("_", " ").title()
                        st.markdown(f"**{label}** ({len(values)})")
                        for v in values[:8]:
                            st.markdown(f"- {v}")
                        if len(values) > 8:
                            st.caption(f"... et {len(values) - 8} autres")
        st.markdown("---")


def render_sections(level: str, sections_list: list):
    """Affiche les sections guidées avec question, exemples discrets et zone de texte."""
    if level not in st.session_state.sections_data:
        st.session_state.sections_data[level] = {}

    sec_data = st.session_state.sections_data[level]

    for sec in sections_list:
        sec_id = sec.get("section_id", "")
        title = sec.get("title", sec_id)
        question = sec.get("question", "")
        examples = sec.get("examples", [])

        with st.expander(f"📝 {title}", expanded=True):
            st.markdown(f"**❓ {question}**")

            if examples:
                examples_text = " · ".join(f"_{ex}_" for ex in examples)
                st.caption(f"💡 Exemples : {examples_text}")

            current_value = sec_data.get(sec_id, "")
            new_value = st.text_area(
                f"Votre réponse — {title}",
                value=current_value,
                height=150,
                key=f"section_{level}_{sec_id}",
                label_visibility="collapsed",
            )
            st.session_state.sections_data[level][sec_id] = new_value


# ============================================================================
# Actions (boutons)
# ============================================================================

def _do_generate(level: str, use_rag: bool, is_new_session: bool = False):
    """Génère un niveau via POST /api/v2/generate."""
    sections = _collect_sections(level)
    if not sections:
        st.error("Veuillez remplir au moins une section.")
        return

    body = {
        "session_id": None if is_new_session else st.session_state.session_id,
        "session_name": st.session_state.session_name,
        "level": level,
        "sections": sections,
        "use_rag": use_rag,
    }

    with st.spinner(f"⏳ Génération du niveau {LEVEL_SHORT[level]} en cours..."):
        ok, data, err = api_call("post", "/api/v2/generate", json=body)

    if ok and data:
        st.session_state.session_id = data.get("session_id")
        st.session_state.level_results[level] = {
            "model": data.get("model", {}),
            "sysml_code": data.get("sysml_code", ""),
            "summary": data.get("summary"),
            "warnings": data.get("warnings", []),
            "validation_result": data.get("validation_result"),
        }
        st.session_state.level_status[level] = "generated"
        st.session_state.active_tab = TAB_RESULTS
        st.success(f"✅ Niveau {LEVEL_SHORT[level]} généré !")
        st.rerun()
    else:
        st.error(f"Échec de la génération : {err}")


def _do_patch(level: str, use_rag: bool):
    """Régénère un niveau via POST /api/v2/patch."""
    sections = _collect_sections(level)
    if not sections:
        st.error("Veuillez remplir au moins une section.")
        return

    body = {
        "session_id": st.session_state.session_id,
        "level": level,
        "sections": sections,
        "use_rag": use_rag,
    }

    with st.spinner(f"⏳ Régénération du niveau {LEVEL_SHORT[level]}..."):
        ok, data, err = api_call("post", "/api/v2/patch", json=body)

    if ok and data:
        st.session_state.level_results[level] = {
            "model": data.get("model", {}),
            "sysml_code": data.get("sysml_code", ""),
            "summary": data.get("summary"),
            "warnings": data.get("warnings", []),
            "validation_result": data.get("validation_result"),
        }
        st.session_state.level_status[level] = "generated"
        st.session_state.active_tab = TAB_RESULTS
        st.success(f"✅ Niveau {LEVEL_SHORT[level]} régénéré !")
        st.rerun()
    else:
        st.error(f"Échec : {err}")


def _do_validate(level: str):
    """Valide un niveau et passe au suivant via POST /api/v2/validate."""
    body = {
        "session_id": st.session_state.session_id,
        "level": level,
    }

    with st.spinner("Validation..."):
        ok, data, err = api_call("post", "/api/v2/validate", json=body)

    if ok and data:
        st.session_state.level_status[level] = "validated"
        next_level = data.get("next_level")
        if next_level:
            st.session_state.current_level = next_level
            st.session_state.active_tab = TAB_SECTIONS
            st.success(f"✅ Niveau {LEVEL_SHORT[level]} validé. Passage à {LEVEL_SHORT[next_level]}.")
        else:
            st.balloons()
            st.success("🎉 Tous les niveaux sont complétés !")
        st.rerun()
    else:
        st.error(f"Échec de la validation : {err}")


def _do_coherence(level: str):
    """Vérifie la cohérence inter-niveaux."""
    with st.spinner("Vérification de cohérence..."):
        ok, data, err = api_call("get", f"/api/v2/coherence/{st.session_state.session_id}/{level}", timeout=30)

    if ok and data:
        if data.get("coherent"):
            st.success("✅ Aucune incohérence détectée.")
        else:
            issues = data.get("issues", [])
            for issue in issues:
                sev = issue.get("severity", "warning")
                desc = issue.get("description", "")
                if sev == "error":
                    st.error(f"🔴 {desc}")
                else:
                    st.warning(f"⚠️ {desc}")
    else:
        st.error(err)


def _collect_sections(level: str) -> list:
    """Collecte les sections remplies pour un niveau."""
    sec_data = st.session_state.sections_data.get(level, {})
    sections = []
    for sec_id, content in sec_data.items():
        if content and content.strip():
            sections.append({"section_id": sec_id, "content": content.strip()})
    return sections


# ============================================================================
# Main
# ============================================================================

def main():
    """Point d'entrée principal."""
    render_sidebar()

    if not st.session_state.session_id:
        render_welcome()
    else:
        level = st.session_state.current_level
        render_level(level)


if __name__ == "__main__":
    main()
