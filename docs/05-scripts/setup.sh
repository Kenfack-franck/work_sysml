#!/bin/bash
set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  SysAgent — Installation locale            ║${NC}"
echo -e "${BLUE}║  Generateur SysML v2 par LLM               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Determiner le repertoire racine du projet
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"
echo -e "${BLUE}Repertoire du projet : $PROJECT_ROOT${NC}"
echo ""

# ============================================
# ETAPE 1 : Verification des prerequis
# ============================================
echo -e "${YELLOW}[1/5] Verification des prerequis...${NC}"
ERRORS=0

# Python 3.10+
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
        echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION"
    else
        echo -e "  ${RED}✗ Python $PYTHON_VERSION detecte, 3.10+ requis${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "  ${RED}✗ Python3 non trouve${NC}"
    echo -e "    Installer : sudo apt install python3 python3-venv python3-pip"
    ERRORS=$((ERRORS + 1))
fi

# pip
if command -v pip3 &> /dev/null || python3 -m pip --version &> /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} pip"
else
    echo -e "  ${RED}✗ pip non trouve${NC}"
    echo -e "    Installer : sudo apt install python3-pip"
    ERRORS=$((ERRORS + 1))
fi

# python3-venv
if python3 -m venv --help &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} python3-venv"
else
    echo -e "  ${RED}✗ python3-venv non trouve${NC}"
    echo -e "    Installer : sudo apt install python3-venv"
    ERRORS=$((ERRORS + 1))
fi

# git (optionnel)
if command -v git &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} git"
else
    echo -e "  ${YELLOW}! git non trouve (optionnel)${NC}"
fi

if [ $ERRORS -gt 0 ]; then
    echo ""
    echo -e "${RED}$ERRORS prerequis manquant(s). Installez-les et relancez ce script.${NC}"
    exit 1
fi

# ============================================
# ETAPE 2 : Creation de l'environnement virtuel
# ============================================
echo ""
echo -e "${YELLOW}[2/5] Creation de l'environnement virtuel...${NC}"

if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "  ${GREEN}✓${NC} .venv/ existe deja"
else
    python3 -m venv "$PROJECT_ROOT/.venv"
    echo -e "  ${GREEN}✓${NC} .venv/ cree"
fi

# shellcheck source=/dev/null
source "$PROJECT_ROOT/.venv/bin/activate"
echo -e "  ${GREEN}✓${NC} Environnement active ($(python3 --version))"

# ============================================
# ETAPE 3 : Installation des dependances
# ============================================
echo ""
echo -e "${YELLOW}[3/5] Installation des dependances...${NC}"
echo -e "  Installation en cours (peut prendre 2-3 min la premiere fois)..."

pip install --upgrade pip --quiet 2>&1 | tail -1 || true

echo -e "  Installation des dependances backend..."
pip install -r "$PROJECT_ROOT/backend/requirements.txt" --quiet 2>&1 | tail -3 || {
    echo -e "  ${RED}✗ Erreur lors de l'installation des dependances backend${NC}"
    exit 1
}
echo -e "  ${GREEN}✓${NC} Dependances backend installees"

echo -e "  Installation des dependances frontend..."
pip install -r "$PROJECT_ROOT/frontend/requirements.txt" --quiet 2>&1 | tail -3 || {
    echo -e "  ${RED}✗ Erreur lors de l'installation des dependances frontend${NC}"
    exit 1
}
echo -e "  ${GREEN}✓${NC} Dependances frontend installees"

# ============================================
# ETAPE 4 : Configuration .env
# ============================================
echo ""
echo -e "${YELLOW}[4/5] Configuration...${NC}"

if [ -f "$PROJECT_ROOT/.env" ]; then
    echo -e "  ${GREEN}✓${NC} .env existe"
else
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        echo -e "  ${GREEN}✓${NC} .env cree depuis .env.example"
    else
        cat > "$PROJECT_ROOT/.env" << 'ENVEOF'
# === LLM Provider ===
# Choisir : "gemini" ou "claude"
LLM_PROVIDER=claude

# === Claude (Anthropic) ===
# Obtenir une cle : https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-haiku-4-5-20251001

# === Gemini (Google) ===
# Obtenir une cle : https://aistudio.google.com/apikey
GEMINI_API_KEYS=
LLM_MODEL=gemini-2.5-flash
ENVEOF
        echo -e "  ${GREEN}✓${NC} .env cree (template minimal)"
    fi
fi

# Creer les dossiers data necessaires au backend local
mkdir -p "$PROJECT_ROOT/backend/data/state"
mkdir -p "$PROJECT_ROOT/backend/data/chroma"
echo -e "  ${GREEN}✓${NC} Dossiers backend/data/ crees"

# Verifier si SysML-v2-Release est disponible pour le RAG
if [ -d "$PROJECT_ROOT/../SysML-v2-Release" ]; then
    echo -e "  ${GREEN}✓${NC} SysML-v2-Release trouve (RAG complet)"
else
    echo -e "  ${YELLOW}! SysML-v2-Release non trouve (RAG desactive, generation fonctionnelle)${NC}"
    echo -e "    Pour activer le RAG, cloner dans le dossier parent :"
    echo -e "    git clone https://github.com/Systems-Modeling/SysML-v2-Release.git ../SysML-v2-Release"
fi

# ============================================
# ETAPE 5 : Verification de la cle API
# ============================================
echo ""
echo -e "${YELLOW}[5/5] Verification de la cle API...${NC}"

# Lire les variables du .env
LLM_PROVIDER=""
ANTHROPIC_API_KEY=""
GEMINI_API_KEYS=""
while IFS='=' read -r key value; do
    key=$(echo "$key" | xargs)
    # Ignorer commentaires et lignes vides
    [[ "$key" =~ ^# ]] && continue
    [[ -z "$key" ]] && continue
    value=$(echo "$value" | xargs)
    case "$key" in
        LLM_PROVIDER) LLM_PROVIDER="$value" ;;
        ANTHROPIC_API_KEY) ANTHROPIC_API_KEY="$value" ;;
        GEMINI_API_KEYS) GEMINI_API_KEYS="$value" ;;
    esac
done < "$PROJECT_ROOT/.env"

API_OK=0
if [ "$LLM_PROVIDER" = "claude" ] && [ -n "$ANTHROPIC_API_KEY" ] && [ "$ANTHROPIC_API_KEY" != "sk-ant-VOTRE_CLE" ]; then
    echo -e "  ${GREEN}✓${NC} Cle Anthropic configuree (provider: claude)"
    API_OK=1
elif [ "$LLM_PROVIDER" = "gemini" ] && [ -n "$GEMINI_API_KEYS" ] && [[ "$GEMINI_API_KEYS" != *"VOTRE_CLE"* ]]; then
    echo -e "  ${GREEN}✓${NC} Cle Gemini configuree (provider: gemini)"
    API_OK=1
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════${NC}"

if [ $API_OK -eq 1 ]; then
    echo -e "${GREEN}Installation terminee avec succes !${NC}"
    echo ""
    echo -e "Pour lancer le systeme :"
    echo -e "  ${BLUE}./docs/05-scripts/start.sh${NC}"
    echo ""
    echo -e "Puis ouvrir : ${BLUE}http://localhost:8501${NC}"
else
    echo -e "${YELLOW}Installation terminee. Il reste a configurer la cle API.${NC}"
    echo ""
    echo -e "Editez le fichier ${BLUE}.env${NC} et ajoutez votre cle :"
    echo ""
    echo -e "  ${YELLOW}Option A — Claude (Anthropic) :${NC}"
    echo -e "    LLM_PROVIDER=claude"
    echo -e "    ANTHROPIC_API_KEY=sk-ant-votre-cle-ici"
    echo ""
    echo -e "  ${YELLOW}Option B — Gemini (Google) :${NC}"
    echo -e "    LLM_PROVIDER=gemini"
    echo -e "    GEMINI_API_KEYS=votre-cle-ici"
    echo ""
    echo -e "  Obtenir une cle :"
    echo -e "    Anthropic : https://console.anthropic.com/settings/keys"
    echo -e "    Google    : https://aistudio.google.com/apikey"
    echo ""
    echo -e "Ensuite, lancez :"
    echo -e "  ${BLUE}./docs/05-scripts/start.sh${NC}"
fi
