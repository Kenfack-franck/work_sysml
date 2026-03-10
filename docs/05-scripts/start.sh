#!/bin/bash
set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  SysAgent — Demarrage local                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# ============================================
# Verifications
# ============================================

# Verifier que le venv existe
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${RED}Erreur : .venv/ non trouve. Lancez d'abord :${NC}"
    echo -e "  ./docs/05-scripts/setup.sh"
    exit 1
fi

# shellcheck source=/dev/null
source "$PROJECT_ROOT/.venv/bin/activate"

# Lire les variables du .env
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${RED}Erreur : .env non trouve. Lancez d'abord :${NC}"
    echo -e "  ./docs/05-scripts/setup.sh"
    exit 1
fi

LLM_PROVIDER=""
ANTHROPIC_API_KEY=""
GEMINI_API_KEYS=""
while IFS='=' read -r key value; do
    key=$(echo "$key" | xargs)
    [[ "$key" =~ ^# ]] && continue
    [[ -z "$key" ]] && continue
    value=$(echo "$value" | xargs)
    case "$key" in
        LLM_PROVIDER) LLM_PROVIDER="$value" ;;
        ANTHROPIC_API_KEY) ANTHROPIC_API_KEY="$value" ;;
        GEMINI_API_KEYS) GEMINI_API_KEYS="$value" ;;
    esac
done < "$PROJECT_ROOT/.env"

if [ "$LLM_PROVIDER" = "claude" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}Erreur : ANTHROPIC_API_KEY non configuree dans .env${NC}"
    exit 1
elif [ "$LLM_PROVIDER" = "gemini" ] && [ -z "$GEMINI_API_KEYS" ]; then
    echo -e "${RED}Erreur : GEMINI_API_KEYS non configuree dans .env${NC}"
    exit 1
elif [ -z "$LLM_PROVIDER" ]; then
    echo -e "${RED}Erreur : LLM_PROVIDER non configure dans .env${NC}"
    exit 1
fi

# Exporter les variables d'environnement depuis .env
set -a
# shellcheck source=/dev/null
source "$PROJECT_ROOT/.env"
set +a

# Configurer le chemin SysML-v2-Release pour le RAG (mode local)
if [ -d "$PROJECT_ROOT/../SysML-v2-Release" ]; then
    export SYSML_REPO_PATH="$PROJECT_ROOT/../SysML-v2-Release"
else
    export SYSML_REPO_PATH="$PROJECT_ROOT/data/sysml-training"
fi

# ============================================
# PID file pour le cleanup
# ============================================
PIDFILE="$PROJECT_ROOT/.sysagent.pids"
: > "$PIDFILE"

cleanup() {
    echo ""
    echo -e "${YELLOW}Arret des services...${NC}"
    if [ -f "$PIDFILE" ]; then
        while IFS= read -r pid; do
            if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null || true
                echo -e "  ${GREEN}✓${NC} Processus $pid arrete"
            fi
        done < "$PIDFILE"
        rm -f "$PIDFILE"
    fi
    echo -e "${GREEN}Services arretes.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# ============================================
# Lancer le backend
# ============================================
echo -e "${YELLOW}Demarrage du backend (FastAPI :8000)...${NC}"
cd "$PROJECT_ROOT/backend"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info &
BACKEND_PID=$!
echo "$BACKEND_PID" >> "$PIDFILE"
cd "$PROJECT_ROOT"

# Attendre que le backend soit pret
echo -e "  Attente du backend..."
READY=0
for i in $(seq 1 60); do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        READY=1
        break
    fi
    # Verifier que le processus tourne encore
    if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo -e "  ${RED}✗ Le backend s'est arrete. Verifiez les logs ci-dessus.${NC}"
        exit 1
    fi
    sleep 1
done

if [ $READY -eq 0 ]; then
    echo -e "  ${RED}✗ Backend non disponible apres 60s${NC}"
    exit 1
fi

# Afficher les infos du backend
HEALTH=$(curl -s http://localhost:8000/api/health 2>/dev/null)
LLM_INFO=$(echo "$HEALTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"{d.get('llm_provider','?')} / {d.get('llm_model','?')}\")" 2>/dev/null || echo "?")
echo -e "  ${GREEN}✓${NC} Backend pret (LLM: $LLM_INFO)"

# ============================================
# Lancer le frontend
# ============================================
echo -e "${YELLOW}Demarrage du frontend (Streamlit :8501)...${NC}"
cd "$PROJECT_ROOT/frontend"
BACKEND_URL=http://localhost:8000 python -m streamlit run app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false \
    2>&1 &
FRONTEND_PID=$!
echo "$FRONTEND_PID" >> "$PIDFILE"
cd "$PROJECT_ROOT"

# Attendre que le frontend soit pret
sleep 3
if kill -0 "$FRONTEND_PID" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} Frontend lance"
else
    echo -e "  ${RED}✗ Le frontend s'est arrete${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN}  SysAgent est pret !${NC}"
echo ""
echo -e "  Backend  : ${BLUE}http://localhost:8000${NC}"
echo -e "  Frontend : ${BLUE}http://localhost:8501${NC}"
echo -e "  API docs : ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "  LLM : ${YELLOW}$LLM_INFO${NC}"
echo ""
echo -e "${YELLOW}Appuyez sur Ctrl+C pour arreter les services${NC}"
echo ""

# Attendre que les processus se terminent
wait
