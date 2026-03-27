#!/bin/bash
# Leads Scraper v2.0 — Start Script
# Usage: ./start.sh

set -e

echo "╔══════════════════════════════════════════════════════╗"
echo "║         LEADS SCRAPER v2.0 — Dashboard Mode          ║"
echo "╚══════════════════════════════════════════════════════╝"

# Navigate to project root
cd "$(dirname "$0")"

# Check Python dependencies
python -c "import fastapi, uvicorn, sqlalchemy" 2>/dev/null || {
    echo "[!] Installing Python dependencies..."
    pip install -r requirements.txt --break-system-packages -q
}

# Initialize DB + migrate if first run
if [ ! -f "/tmp/leads_scraper/leads.db" ] && [ ! -f "data/leads.db" ]; then
    echo "[*] First run detected. Migrating Excel data..."
    python -c "
import sys; sys.path.insert(0, '.')
from backend.services.migrate_excel import migrate
migrate()
"
fi

# Check if frontend is built
if [ ! -d "frontend/dist" ]; then
    echo "[*] Building frontend..."
    cd frontend && npm install && npx vite build && cd ..
fi

echo ""
echo "  API:       http://localhost:8000/api"
echo "  Dashboard: http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "  WebSocket: ws://localhost:8000/ws"
echo ""

# Start the server
python run.py
