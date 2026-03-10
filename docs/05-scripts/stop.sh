#!/bin/bash

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PIDFILE="$PROJECT_ROOT/.sysagent.pids"

echo -e "${YELLOW}Arret de SysAgent...${NC}"

STOPPED=0

# Methode 1 : utiliser le fichier PID
if [ -f "$PIDFILE" ]; then
    while IFS= read -r pid; do
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            echo -e "  ${GREEN}✓${NC} Processus $pid arrete"
            STOPPED=$((STOPPED + 1))
        fi
    done < "$PIDFILE"
    rm -f "$PIDFILE"
fi

# Methode 2 (fallback) : tuer par nom de commande
if [ $STOPPED -eq 0 ]; then
    if pkill -f "uvicorn main:app.*--port 8000" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Backend arrete"
        STOPPED=$((STOPPED + 1))
    fi
    if pkill -f "streamlit run app.py" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Frontend arrete"
        STOPPED=$((STOPPED + 1))
    fi
fi

if [ $STOPPED -eq 0 ]; then
    echo -e "  Aucun processus SysAgent en cours."
else
    echo -e "${GREEN}SysAgent arrete ($STOPPED processus).${NC}"
fi
