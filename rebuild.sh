#!/bin/bash
# Script de rebuild qui supprime les anciennes images avant de reconstruire

echo "🛑 Arrêt des containers..."
docker compose down

echo "🗑️  Suppression des anciennes images du projet..."
docker rmi sysml-agent-backend sysml-agent-frontend 2>/dev/null || true

echo "🔨 Reconstruction des images..."
docker compose build --no-cache

echo "🚀 Démarrage..."
docker compose up -d

echo ""
echo "✅ Terminé !"
echo "   Backend:  http://localhost:8000/api/health"
echo "   Frontend: http://localhost:8501"
echo "   Logs:     docker compose logs -f"
