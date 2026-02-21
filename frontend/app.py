"""
SysML v2 Agent — Frontend Streamlit
Interface MBSE multi-niveaux pour la génération progressive de modèles SysML v2.
"""

import streamlit as st
import requests
import os
import json
from datetime import datetime
import streamlit.components.v1 as components

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
API_TIMEOUT = 120  # Timeout pour les appels API (génération peut être lente)

# Configuration de la page
st.set_page_config(
    page_title="SysML v2 Agent — MBSE",
    page_icon="🧪",
    layout="wide",
)

# Constantes pour les niveaux MBSE
NIVEAUX_ORDER = ["operational", "functional", "logical", "technical"]
LEVEL_NAMES = {
    "operational": "🔍 Opérationnel — QUI utilise le système et POURQUOI",
    "functional": "⚙️ Fonctionnel — QUE FAIT le système",
    "logical": "🧩 Logique — COMMENT est structuré le système",
    "technical": "🔧 Technique — AVEC QUOI est construit le système"
}
LEVEL_SHORT_NAMES = {
    "operational": "Opérationnel",
    "functional": "Fonctionnel",
    "logical": "Logique",
    "technical": "Technique"
}
DIAGRAM_LABELS = {
    "context": "📍 Diagramme de Contexte",
    "use_cases": "👤 Cas d'Utilisation",
    "actors_diagram": "🎭 Diagramme d'Acteurs",
    "operational_sequence": "🔁 Séquence Opérationnelle",
    "functional_breakdown": "🌳 Arborescence Fonctionnelle (FBS)",
    "functional_behavior": "🔄 Comportement Fonctionnel",
    "modes_diagram": "🔀 Modes Opératoires",
    "bdd": "📦 Block Definition Diagram (BDD)",
    "ibd": "🔌 Internal Block Diagram (IBD)",
    "technical_architecture": "🏗️ Architecture Technique"
}

# Initialisation du session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "current_level" not in st.session_state:
    st.session_state.current_level = "operational"
if "levels_data" not in st.session_state:
    st.session_state.levels_data = {}
if "system_description" not in st.session_state:
    st.session_state.system_description = ""
if "level_status" not in st.session_state:
    st.session_state.level_status = {}


def format_timestamp(iso_timestamp):
    """Formate un timestamp ISO en format lisible."""
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return iso_timestamp


def load_level_status():
    """Charge le statut de tous les niveaux pour la session active."""
    if not st.session_state.session_id:
        return
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v2/status/{st.session_state.session_id}",
            timeout=10
        )
        if response.status_code == 200:
            st.session_state.level_status = response.json()
    except Exception:
        pass


def get_level_icon(level):
    """Retourne l'icône appropriée pour un niveau selon son statut."""
    status = st.session_state.level_status.get(level, {})
    if status.get("validated"):
        return "✅"
    elif status.get("generated"):
        return "🔄"
    else:
        return "⬜"


# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.title("🧪 SysML v2 Agent")
st.sidebar.markdown("**Workflow MBSE Multi-Niveaux**")
st.sidebar.markdown("---")

# --- Statut du backend ---
st.sidebar.subheader("⚙️ Statut Backend")
try:
    response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
    if response.status_code == 200:
        st.sidebar.success("🟢 Backend opérationnel")
    else:
        st.sidebar.error(f"🔴 Erreur: {response.status_code}")
except requests.exceptions.ConnectionError:
    st.sidebar.error("🔴 Backend non accessible")
except Exception as e:
    st.sidebar.error(f"🔴 Erreur: {str(e)}")

st.sidebar.markdown("---")

# --- Stats RAG ---
st.sidebar.subheader("📊 Stats RAG")
try:
    response = requests.get(f"{BACKEND_URL}/api/rag/stats", timeout=10)
    if response.status_code == 200:
        stats = response.json()
        st.sidebar.metric("📦 Chunks indexés", stats["total_chunks"])
        st.sidebar.metric("📄 Fichiers sources", stats["unique_files"])
    else:
        st.sidebar.warning("Stats RAG non disponibles")
except Exception as e:
    st.sidebar.warning("Stats RAG non disponibles")

st.sidebar.markdown("---")

# --- Sessions précédentes ---
st.sidebar.subheader("🗂️ Sessions")
try:
    response = requests.get(f"{BACKEND_URL}/api/sessions", timeout=10)
    if response.status_code == 200:
        sessions_data = response.json()
        sessions = sessions_data.get("sessions", [])
        
        if sessions:
            for session in sessions[:5]:  # Limite à 5 dernières sessions
                session_name = session.get("system_name") or "Sans nom"
                session_date = format_timestamp(session.get("updated_at", ""))
                
                if st.sidebar.button(
                    f"📋 {session_name}",
                    key=f"load_{session['id']}",
                    help=f"Modifié: {session_date}"
                ):
                    st.session_state.session_id = session["id"]
                    load_level_status()
                    st.rerun()
        else:
            st.sidebar.info("Aucune session")
except Exception:
    st.sidebar.warning("Sessions non disponibles")

st.sidebar.markdown("---")

# --- Progression (si session active) ---
if st.session_state.session_id:
    st.sidebar.subheader("📈 Progression")
    load_level_status()
    
    # Icônes et noms pour la navigation
    LEVEL_ICONS = {
        "operational": "🔍",
        "functional": "⚙️",
        "logical": "🧩",
        "technical": "🔧"
    }
    
    for idx, level in enumerate(NIVEAUX_ORDER, 1):
        status = st.session_state.level_status.get(level, {})
        generated = status.get("generated", False)
        validated = status.get("validated", False)
        
        if generated:
            # Niveau généré : bouton cliquable
            icon = "✅" if validated else "🔄"
            label = f"{icon} {LEVEL_ICONS[level]} {LEVEL_SHORT_NAMES[level]}"
            
            # Highlight si c'est le niveau actuel
            button_type = "primary" if level == st.session_state.current_level else "secondary"
            
            if st.sidebar.button(
                label, 
                key=f"nav_{level}",
                use_container_width=True,
                type=button_type
            ):
                st.session_state.current_level = level
                st.rerun()
        else:
            # Niveau pas encore généré : texte statique
            st.sidebar.markdown(f"⬜ {LEVEL_ICONS[level]} {LEVEL_SHORT_NAMES[level]}")
    
    st.sidebar.caption("✅ Validé | 🔄 En cours | ⬜ À faire")
    
    st.sidebar.markdown("---")
    
    # --- Nom de session ---
    st.sidebar.subheader("📝 Nom du projet")
    try:
        # Charger les données de session pour obtenir le nom
        session_resp = requests.get(f"{BACKEND_URL}/api/session/{st.session_state.session_id}", timeout=10)
        if session_resp.status_code == 200:
            session_data = session_resp.json()
            current_name = session_data.get("session_name", "")
            
            # Champ pour modifier le nom
            new_name = st.sidebar.text_input(
                "Renommer",
                value=current_name,
                key="session_name_input",
                placeholder="Ex: Surveillance Bâtiment",
                label_visibility="collapsed"
            )
            
            # Si le nom a changé, mettre à jour
            if new_name != current_name and st.sidebar.button("💾 Sauvegarder", key="save_name"):
                try:
                    rename_resp = requests.put(
                        f"{BACKEND_URL}/api/v2/session/{st.session_state.session_id}/name",
                        json={"name": new_name},
                        timeout=10
                    )
                    if rename_resp.status_code == 200:
                        st.sidebar.success("✅ Nom sauvegardé")
                        st.rerun()
                    else:
                        st.sidebar.error("❌ Erreur de sauvegarde")
                except:
                    st.sidebar.error("❌ Erreur de sauvegarde")
    except:
        pass


# ============================================================================
# CONTENU PRINCIPAL
# ============================================================================

# Si aucune session active, afficher le formulaire de démarrage
if not st.session_state.session_id:
    st.header("🚀 Nouveau projet MBSE")
    st.markdown("""
    Bienvenue dans le **workflow MBSE multi-niveaux**. Vous allez générer votre modèle SysML v2 
    de manière **progressive** en 4 étapes :
    
    1. **🔍 Opérationnel** : Qui utilise le système et pourquoi (acteurs, cas d'utilisation, besoins)
    2. **⚙️ Fonctionnel** : Que fait le système (fonctions, flux, modes)
    3. **🧩 Logique** : Comment est structuré le système (composants, interfaces, architecture)
    4. **🔧 Technique** : Avec quoi est construit le système (technologies, implémentation)
    
    **Chaque niveau doit être validé avant de passer au suivant.**
    """)
    
    st.markdown("---")
    
    description = st.text_area(
        "📝 Description du système",
        height=200,
        placeholder="Décrivez votre système en langage naturel...",
        value="Un système de gestion de drone autonome pour la surveillance agricole. "
              "Les agriculteurs planifient des missions de surveillance. "
              "Le système contrôle le drone pour suivre les parcelles et détecter les anomalies. "
              "Le drone capture des images et les transmet au système de traitement. "
              "Le système analyse les données et génère des rapports pour l'agriculteur.",
        help="Décrivez le contexte, les acteurs, les objectifs et le périmètre du système."
    )
    
    session_name = st.text_input(
        "📝 Nom du projet (optionnel)",
        placeholder="Ex: Surveillance Bâtiment, Système de Drone, etc.",
        help="Donnez un nom à votre projet pour le retrouver facilement"
    )
    
    use_rag = st.checkbox(
        "🔍 Utiliser le RAG (Recherche d'exemples)",
        value=True,
        help="Recherche des exemples pertinents dans la base SysML v2"
    )
    
    if st.button("🚀 Démarrer le projet", type="primary", use_container_width=True):
        if len(description.strip()) < 20:
            st.error("❌ La description doit contenir au moins 20 caractères.")
        else:
            with st.spinner("⏳ Génération du niveau opérationnel en cours..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/v2/generate",
                        json={
                            "description": description,
                            "session_name": session_name,
                            "level": "operational",
                            "use_rag": use_rag
                        },
                        timeout=API_TIMEOUT
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.session_id = result["session_id"]
                        st.session_state.current_level = "operational"
                        st.session_state.system_description = description
                        load_level_status()
                        st.success(f"✅ Niveau opérationnel généré !")
                        st.rerun()
                    else:
                        error = response.json().get("detail", response.text)
                        st.error(f"❌ Erreur {response.status_code}: {error}")
                        
                except requests.exceptions.Timeout:
                    st.error("❌ Timeout (> 2 min)")
                except Exception as e:
                    st.error(f"❌ Erreur : {str(e)}")

# Si une session est active, afficher les onglets pour le niveau en cours
else:
    # Charger les données du niveau en cours
    load_level_status()
    current_level = st.session_state.current_level
    level_index = NIVEAUX_ORDER.index(current_level) + 1
    
    # En-tête avec nom du niveau
    st.header(f"Niveau {level_index}/4 : {LEVEL_NAMES[current_level]}")
    st.caption(f"Session : {st.session_state.session_id[:16]}...")
    
    # Tabs pour le niveau en cours
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Modèle", "💻 Code SysML v2", "📊 Diagrammes", "📖 Historique"])
    
    # ========================================================================
    # TAB 1 : MODÈLE
    # ========================================================================
    
    with tab1:
        # Charger le modèle du niveau actuel
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/session/{st.session_state.session_id}",
                timeout=10
            )
            if response.status_code == 200:
                session_data = response.json()
                levels = session_data.get("levels", {})
                current_level_data = levels.get(current_level, {})
                model = current_level_data.get("model", {})
                
                if model:
                    # Générer un résumé lisible selon le niveau
                    st.subheader("📋 Résumé du modèle")
                    
                    # Résumé selon le niveau
                    if current_level == "operational":
                        stakeholders = len(model.get("stakeholders", []))
                        systems = len(model.get("external_systems", []))
                        use_cases = len(model.get("use_cases", []))
                        requirements = len(model.get("requirements", []))
                        st.info(f"**Parties prenantes :** {stakeholders} | **Systèmes externes :** {systems} | **Use cases :** {use_cases} | **Exigences :** {requirements}")
                    
                    elif current_level == "functional":
                        functions = len(model.get("functions", []))
                        flows = len(model.get("functional_flows", []))
                        modes = len(model.get("operational_modes", []))
                        st.info(f"**Fonctions :** {functions} | **Flux fonctionnels :** {flows} | **Modes opérationnels :** {modes}")
                    
                    elif current_level == "logical":
                        parts = len(model.get("logical_parts", []))
                        connections = len(model.get("logical_connections", []))
                        allocated_req = len(model.get("allocated_requirements", []))
                        st.info(f"**Composants logiques :** {parts} | **Connexions :** {connections} | **Exigences allouées :** {allocated_req}")
                    
                    elif current_level == "technical":
                        tech_parts = len(model.get("technical_parts", []))
                        phys_conn = len(model.get("physical_connections", []))
                        tech_choices = len(model.get("technology_choices", []))
                        st.info(f"**Composants techniques :** {tech_parts} | **Connexions physiques :** {phys_conn} | **Choix technologiques :** {tech_choices}")
                    
                    # Notes du LLM (ambiguïtés et suppositions)
                    llm_warnings = current_level_data.get("llm_warnings", [])
                    # Filtrer les anciens warnings de validation (rétrocompatibilité)
                    llm_warnings = [w for w in llm_warnings if "erreur(s) syntaxique(s)" not in w and "syntaxique" not in w.lower()]
                    
                    if llm_warnings:
                        with st.expander(f"💡 Notes du LLM ({len(llm_warnings)})", expanded=False):
                            st.caption("L'IA signale des ambiguïtés ou des suppositions qu'elle a faites lors de la génération.")
                            for w in llm_warnings:
                                st.info(w)
                    
                    # JSON détaillé dans un expander fermé
                    with st.expander("📋 Modèle JSON détaillé", expanded=False):
                        st.json(model)
                    
                    st.markdown("---")
                    
                    # Section modification
                    st.subheader("✏️ Modifier ce niveau")
                    
                    # Warning si le niveau est déjà validé
                    status = st.session_state.level_status.get(current_level, {})
                    if status.get("validated", False):
                        st.warning("⚠️ Modifier un niveau déjà validé peut créer des incohérences avec les niveaux suivants.")
                    
                    instruction = st.text_area(
                        "Instruction de modification",
                        placeholder="Exemple : Ajouter un acteur 'Technicien de maintenance'",
                        height=100,
                        help="Décrivez la modification à apporter"
                    )
                    
                    use_rag_patch = st.checkbox("🔍 Utiliser le RAG", value=True, key="rag_patch")
                    
                    if st.button("✏️ Appliquer la modification", type="secondary"):
                        if len(instruction.strip()) < 5:
                            st.error("❌ Instruction trop courte")
                        else:
                            with st.spinner("⏳ Modification en cours..."):
                                try:
                                    response = requests.post(
                                        f"{BACKEND_URL}/api/v2/patch",
                                        json={
                                            "session_id": st.session_state.session_id,
                                            "level": current_level,
                                            "instruction": instruction,
                                            "use_rag": use_rag_patch
                                        },
                                        timeout=API_TIMEOUT
                                    )
                                    
                                    if response.status_code == 200:
                                        result = response.json()
                                        st.success(f"✅ {result.get('changes_summary', 'Modifié')}")
                                        st.rerun()
                                    else:
                                        error = response.json().get("detail", response.text)
                                        st.error(f"❌ Erreur : {error}")
                                except Exception as e:
                                    st.error(f"❌ Erreur : {str(e)}")
                    
                    st.markdown("---")
                    
                    # Section vérification de cohérence inter-niveaux
                    st.subheader("🔍 Cohérence inter-niveaux")
                    st.caption("Vérification de la cohérence entre ce niveau et les niveaux adjacents (traçabilité des exigences, couverture des fonctions, etc.)")
                    
                    if st.button("Vérifier la cohérence inter-niveaux"):
                        with st.spinner("⏳ Vérification..."):
                            try:
                                response = requests.get(
                                    f"{BACKEND_URL}/api/v2/coherence/{st.session_state.session_id}/{current_level}",
                                    timeout=30
                                )
                                
                                if response.status_code == 200:
                                    result = response.json()
                                    if result.get("coherent"):
                                        st.success("✅ Aucune incohérence détectée entre les niveaux")
                                    else:
                                        issues = result.get("issues", [])
                                        with st.expander(f"⚠️ Incohérences détectées ({len(issues)})", expanded=True):
                                            st.caption("Ces incohérences sont signalées à titre indicatif. C'est à l'architecte de décider des actions à prendre.")
                                            for issue in issues:
                                                severity = issue.get("severity", "warning")
                                                description = issue.get("description", "")
                                                if severity == "error":
                                                    st.error(f"🔴 {description}")
                                                else:
                                                    st.warning(f"⚠️ {description}")
                                else:
                                    st.error("❌ Erreur lors de la vérification")
                            except Exception as e:
                                st.error(f"❌ Erreur : {str(e)}")
                    
                    st.markdown("---")
                    
                    # Section validation
                    st.subheader("Validation")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Valider et passer au niveau suivant", type="primary", use_container_width=True):
                            with st.spinner("⏳ Validation..."):
                                try:
                                    # Valider le niveau actuel
                                    response = requests.post(
                                        f"{BACKEND_URL}/api/v2/validate",
                                        json={
                                            "session_id": st.session_state.session_id,
                                            "level": current_level
                                        },
                                        timeout=30
                                    )
                                    
                                    if response.status_code == 200:
                                        result = response.json()
                                        next_level = result.get("next_level")
                                        
                                        if next_level:
                                            # Générer le niveau suivant
                                            st.info(f"⏳ Génération du niveau {LEVEL_SHORT_NAMES[next_level]} en cours...")
                                            
                                            gen_response = requests.post(
                                                f"{BACKEND_URL}/api/v2/generate",
                                                json={
                                                    "session_id": st.session_state.session_id,
                                                    "description": st.session_state.system_description,
                                                    "level": next_level,
                                                    "use_rag": True
                                                },
                                                timeout=120  # Timeout plus long pour la génération
                                            )
                                            
                                            if gen_response.status_code == 200:
                                                st.session_state.current_level = next_level
                                                st.success(f"✅ Niveau {LEVEL_SHORT_NAMES[next_level]} généré avec succès !")
                                                st.rerun()
                                            else:
                                                error_detail = gen_response.json().get("detail", gen_response.text)
                                                st.error(f"❌ Erreur lors de la génération du niveau {LEVEL_SHORT_NAMES[next_level]} : {error_detail}")
                                                
                                                # Si c'est une erreur de quota, proposer de réessayer
                                                if "429" in str(error_detail) or "quota" in str(error_detail).lower() or "RESOURCE_EXHAUSTED" in str(error_detail):
                                                    st.warning("🔑 Quota API atteint. Le système va tenter une rotation de clé automatique.")
                                                    if st.button("🔄 Réessayer", key="retry_generation"):
                                                        st.rerun()
                                        else:
                                            # C'était le dernier niveau
                                            st.balloons()
                                            st.success("🎉 Tous les niveaux sont complétés !")
                                    else:
                                        error_detail = response.json().get("detail", response.text)
                                        st.error(f"❌ Erreur lors de la validation : {error_detail}")
                                except requests.exceptions.Timeout:
                                    st.error("⏱️ Timeout — La génération prend trop de temps. Réessayez.")
                                except Exception as e:
                                    st.error(f"❌ Erreur inattendue : {str(e)}")
                    
                    with col2:
                        if st.button("🔄 Régénérer ce niveau", use_container_width=True):
                            with st.spinner("⏳ Régénération..."):
                                try:
                                    response = requests.post(
                                        f"{BACKEND_URL}/api/v2/generate",
                                        json={
                                            "session_id": st.session_state.session_id,
                                            "description": st.session_state.system_description,
                                            "level": current_level,
                                            "use_rag": True
                                        },
                                        timeout=API_TIMEOUT
                                    )
                                    
                                    if response.status_code == 200:
                                        st.success("✅ Niveau régénéré !")
                                        st.rerun()
                                    else:
                                        st.error("❌ Erreur lors de la régénération")
                                except Exception as e:
                                    st.error(f"❌ Erreur : {str(e)}")
                
                else:
                    st.info("Ce niveau n'a pas encore été généré.")
        
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement : {str(e)}")
    
    # ========================================================================
    # TAB 2 : CODE SYSML V2
    # ========================================================================
    
    with tab2:
        st.subheader("💻 Code SysML v2")
        
        # Afficher le code du niveau actuel
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/session/{st.session_state.session_id}",
                timeout=10
            )
            if response.status_code == 200:
                session_data = response.json()
                levels = session_data.get("levels", {})
                current_level_data = levels.get(current_level, {})
                sysml_code = current_level_data.get("sysml_code", "")
                
                if sysml_code:
                    # Afficher le code
                    st.code(sysml_code, language="text", line_numbers=True)
                    
                    st.markdown("---")
                    
                    # Section validation syntaxique
                    st.subheader("🔍 Validation syntaxique")
                    
                    # Charger le résultat de validation s'il existe
                    validation = current_level_data.get("validation_result", {})
                    
                    if validation and validation.get("errors") is not None:
                        errors = validation.get("errors", [])
                        warnings = validation.get("warnings", [])
                        score = validation.get("score", 0)
                        
                        if not errors:
                            st.success(f"✅ Code syntaxiquement valide (score : {score}/100)")
                        else:
                            st.error(f"❌ {len(errors)} erreur(s) de syntaxe détectée(s)")
                            with st.expander("🔍 Détails des erreurs de syntaxe", expanded=True):
                                for err in errors:
                                    line = err.get("line", "?")
                                    msg = err.get("message", "Erreur inconnue")
                                    st.error(f"**Ligne {line}** : {msg}")
                        
                        if warnings:
                            with st.expander(f"⚠️ Bonnes pratiques ({len(warnings)})", expanded=False):
                                st.caption("Ces avertissements ne sont pas des erreurs mais des suggestions d'amélioration.")
                                for w in warnings:
                                    line = w.get("line", "?")
                                    msg = w.get("message", "")
                                    st.warning(f"**Ligne {line}** : {msg}")
                    else:
                        st.info("Aucune validation syntaxique n'a encore été effectuée.")
                        if st.button("🔍 Valider la syntaxe maintenant"):
                            with st.spinner("⏳ Validation en cours..."):
                                try:
                                    val_resp = requests.post(
                                        f"{BACKEND_URL}/api/validate-sysml",
                                        json={"sysml_code": sysml_code},
                                        timeout=30
                                    )
                                    if val_resp.status_code == 200:
                                        validation = val_resp.json()
                                        st.success("✅ Validation terminée")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Erreur : {val_resp.json().get('detail', 'Erreur inconnue')}")
                                except Exception as e:
                                    st.error(f"❌ Erreur : {str(e)}")
                    
                    st.markdown("---")
                    
                    # Bouton pour voir le code complet
                    if st.button("📄 Voir le code complet (tous les niveaux validés)"):
                        try:
                            full_resp = requests.get(
                                f"{BACKEND_URL}/api/v2/full-sysml/{st.session_state.session_id}",
                                timeout=30
                            )
                            if full_resp.status_code == 200:
                                full_code = full_resp.json().get("sysml_code", "")
                                if full_code:
                                    st.code(full_code, language="text", line_numbers=True)
                                else:
                                    st.info("Aucun niveau validé")
                            else:
                                st.error("Erreur lors du chargement")
                        except Exception as e:
                            st.error(f"Erreur : {str(e)}")
                else:
                    st.info("Ce niveau n'a pas encore été généré")
        
        except Exception as e:
            st.error(f"❌ Erreur : {str(e)}")
    
    # ========================================================================
    # TAB 3 : DIAGRAMMES
    # ========================================================================
    
    with tab3:
        st.subheader(f"📊 Diagrammes — {LEVEL_SHORT_NAMES[current_level]}")
        
        # Fonction pour afficher un diagramme avec modal
        def render_diagram_with_modal(svg_content: str, diagram_type: str, diagram_title: str, height: int = 500):
            """Affiche un diagramme SVG avec modal interactif."""
            import hashlib
            
            # Générer un ID unique pour ce diagramme
            unique_id = hashlib.md5(f"{diagram_type}_{diagram_title}".encode()).hexdigest()[:8]
            
            html_code = f"""
            <style>
                .diagram-container-{unique_id} {{
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 10px;
                    background: white;
                    overflow: auto;
                    max-height: {height}px;
                    cursor: pointer;
                    position: relative;
                }}
                .diagram-container-{unique_id}:hover {{
                    border-color: #4CAF50;
                    box-shadow: 0 0 8px rgba(76, 175, 80, 0.3);
                }}
                .diagram-container-{unique_id}:hover::after {{
                    content: '🔍 Cliquer pour agrandir';
                    position: absolute;
                    top: 8px;
                    right: 8px;
                    background: rgba(0,0,0,0.7);
                    color: white;
                    padding: 4px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                }}
                .modal-overlay-{unique_id} {{
                    display: none;
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100vw;
                    height: 100vh;
                    background: rgba(0, 0, 0, 0.85);
                    z-index: 999999;
                    justify-content: center;
                    align-items: center;
                    flex-direction: column;
                }}
                .modal-overlay-{unique_id}.active {{
                    display: flex;
                }}
                .modal-content-{unique_id} {{
                    background: white;
                    border-radius: 12px;
                    padding: 20px;
                    max-width: 95vw;
                    max-height: 85vh;
                    overflow: auto;
                    position: relative;
                }}
                .modal-toolbar-{unique_id} {{
                    display: flex;
                    gap: 8px;
                    margin-bottom: 12px;
                    justify-content: space-between;
                    align-items: center;
                }}
                .modal-toolbar-{unique_id} button {{
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: 1px solid #ccc;
                    background: #f0f0f0;
                    cursor: pointer;
                    font-size: 14px;
                }}
                .modal-toolbar-{unique_id} button:hover {{
                    background: #e0e0e0;
                }}
                .modal-close-{unique_id} {{
                    background: #ff5252 !important;
                    color: white !important;
                    border: none !important;
                    font-size: 18px !important;
                    padding: 8px 14px !important;
                }}
                .modal-title-{unique_id} {{
                    font-weight: bold;
                    font-size: 16px;
                    color: #333;
                }}
                .modal-svg-{unique_id} {{
                    transform-origin: top left;
                    transition: transform 0.2s ease;
                }}
            </style>
            
            <div class="diagram-container-{unique_id}" onclick="document.querySelector('.modal-overlay-{unique_id}').classList.add('active')">
                {svg_content}
            </div>
            
            <div class="modal-overlay-{unique_id}" onclick="if(event.target===this) this.classList.remove('active')">
                <div class="modal-content-{unique_id}">
                    <div class="modal-toolbar-{unique_id}">
                        <span class="modal-title-{unique_id}">{diagram_title}</span>
                        <div style="display:flex;gap:6px;">
                            <button onclick="zoomDiagram_{unique_id}(-0.25)">🔍 Zoom −</button>
                            <button onclick="zoomDiagram_{unique_id}(0.25)">🔎 Zoom +</button>
                            <button onclick="resetZoom_{unique_id}()">↺ Reset</button>
                            <button class="modal-close-{unique_id}" onclick="document.querySelector('.modal-overlay-{unique_id}').classList.remove('active')">✕</button>
                        </div>
                    </div>
                    <div style="overflow:auto;max-height:75vh;">
                        <div class="modal-svg-{unique_id}" id="modal-svg-{unique_id}">
                            {svg_content}
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                var currentZoom_{unique_id} = 1;
                function zoomDiagram_{unique_id}(delta) {{
                    currentZoom_{unique_id} = Math.max(0.25, Math.min(4, currentZoom_{unique_id} + delta));
                    document.getElementById('modal-svg-{unique_id}').style.transform = 'scale(' + currentZoom_{unique_id} + ')';
                }}
                function resetZoom_{unique_id}() {{
                    currentZoom_{unique_id} = 1;
                    document.getElementById('modal-svg-{unique_id}').style.transform = 'scale(1)';
                }}
            </script>
            """
            
            components.html(html_code, height=height + 50, scrolling=True)
        
        # Charger les diagrammes existants au chargement de la page
        if "loaded_diagrams_for_level" not in st.session_state or st.session_state.get("loaded_diagrams_for_level") != current_level:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/api/v2/diagrams/{st.session_state.session_id}/{current_level}",
                    timeout=30
                )
                if response.status_code == 200:
                    result = response.json()
                    diagrams = result.get("diagrams", [])
                    if diagrams:
                        st.session_state.current_diagrams = diagrams
                        st.session_state.loaded_diagrams_for_level = current_level
                    else:
                        # Pas de diagrammes existants
                        st.session_state.current_diagrams = None
                        st.session_state.loaded_diagrams_for_level = current_level
            except:
                pass
        
        # Afficher bouton de génération si pas de diagrammes
        if not st.session_state.get("current_diagrams"):
            if st.button("🎨 Générer les diagrammes de ce niveau", type="primary", use_container_width=True):
                with st.spinner("⏳ Génération des diagrammes..."):
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/api/v2/diagrams",
                            json={
                                "session_id": st.session_state.session_id,
                                "level": current_level
                            },
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            diagrams = result.get("diagrams", [])
                            
                            if diagrams:
                                st.success(f"✅ {len(diagrams)} diagramme(s) généré(s) !")
                                st.session_state.current_diagrams = diagrams
                                st.rerun()
                            else:
                                st.info("Aucun diagramme disponible pour ce niveau")
                        else:
                            error = response.json().get("detail", response.text)
                            st.error(f"❌ Erreur : {error}")
                    
                    except Exception as e:
                        st.error(f"❌ Erreur : {str(e)}")
        else:
            # Diagrammes existants, offrir de regénérer
            if st.button("🔄 Regénérer les diagrammes", type="secondary"):
                with st.spinner("⏳ Regénération des diagrammes..."):
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/api/v2/diagrams",
                            json={
                                "session_id": st.session_state.session_id,
                                "level": current_level
                            },
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            diagrams = result.get("diagrams", [])
                            
                            if diagrams:
                                st.success(f"✅ {len(diagrams)} diagramme(s) regénéré(s) !")
                                st.session_state.current_diagrams = diagrams
                                st.rerun()
                        else:
                            error = response.json().get("detail", response.text)
                            st.error(f"❌ Erreur : {error}")
                    except Exception as e:
                        st.error(f"❌ Erreur : {str(e)}")
        
        # Afficher les diagrammes
        if st.session_state.get("current_diagrams"):
            st.markdown("---")
            
            for diagram in st.session_state.current_diagrams:
                diagram_type = diagram.get("type", "unknown")
                title = diagram.get("title", "Diagramme")
                plantuml_code = diagram.get("plantuml_code", "")
                svg_content = diagram.get("svg", "")
                
                label = DIAGRAM_LABELS.get(diagram_type, title)
                st.subheader(label)
                
                # Afficher le SVG avec modal
                if svg_content and svg_content.strip():
                    try:
                        render_diagram_with_modal(svg_content, diagram_type, label, height=500)
                    except Exception:
                        st.warning("⚠️ Impossible d'afficher le SVG")
                
                # Code PlantUML dans un expander fermé
                with st.expander("📝 Code PlantUML", expanded=False):
                    st.code(plantuml_code, language="text")
                
                st.markdown("---")
        
        # Diagrammes des niveaux précédents
        previous_levels = [l for l in NIVEAUX_ORDER if NIVEAUX_ORDER.index(l) < NIVEAUX_ORDER.index(current_level)]
        if previous_levels:
            st.divider()
            st.subheader("📂 Diagrammes des niveaux précédents")
            
            try:
                response = requests.get(
                    f"{BACKEND_URL}/api/session/{st.session_state.session_id}",
                    timeout=10
                )
                if response.status_code == 200:
                    session_data = response.json()
                    levels = session_data.get("levels", {})
                    
                    for prev_level in previous_levels:
                        level_data = levels.get(prev_level, {})
                        diagrams = level_data.get("diagrams", [])
                        
                        if diagrams:
                            level_icon = LEVEL_ICONS.get(prev_level, "📊")
                            with st.expander(f"{level_icon} {LEVEL_SHORT_NAMES[prev_level]} ({len(diagrams)} diagrammes)", expanded=False):
                                for diagram in diagrams:
                                    diagram_type = diagram.get("type", "unknown")
                                    title = diagram.get("title", "Diagramme")
                                    svg_content = diagram.get("svg", "")
                                    plantuml_code = diagram.get("plantuml_code", "")
                                    
                                    label = DIAGRAM_LABELS.get(diagram_type, title)
                                    st.markdown(f"**{label}**")
                                    
                                    # Afficher le SVG avec modal
                                    if svg_content and svg_content.strip():
                                        try:
                                            render_diagram_with_modal(svg_content, f"{prev_level}_{diagram_type}", label, height=400)
                                        except Exception:
                                            st.warning("⚠️ Impossible d'afficher le SVG")
                                    
                                    st.markdown("---")
            except Exception:
                pass
    
    # ========================================================================
    # TAB 4 : HISTORIQUE
    # ========================================================================
    
    with tab4:
        st.subheader("📖 Historique")
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/session/{st.session_state.session_id}",
                timeout=10
            )
            if response.status_code == 200:
                session_data = response.json()
                levels = session_data.get("levels", {})
                
                # Pour chaque niveau
                for level in NIVEAUX_ORDER:
                    level_data = levels.get(level, {})
                    history = level_data.get("history", [])
                    
                    if history:
                        with st.expander(f"{LEVEL_SHORT_NAMES[level]}", expanded=(level == current_level)):
                            for entry in reversed(history):
                                action = entry.get("action", "unknown")
                                timestamp = format_timestamp(entry.get("timestamp", ""))
                                instruction = entry.get("instruction", entry.get("description", ""))
                                
                                st.markdown(f"**{action.upper()}** — {timestamp}")
                                if instruction:
                                    st.markdown(f"> {instruction}")
                                st.markdown("---")
        
        except Exception as e:
            st.error(f"❌ Erreur : {str(e)}")
