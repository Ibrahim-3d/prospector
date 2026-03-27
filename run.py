"""Start the Leads Scraper application."""

import uvicorn
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("""
╔══════════════════════════════════════════════════════╗
║          LEADS SCRAPER v2.0 — Dashboard Mode         ║
╠══════════════════════════════════════════════════════╣
║  API:       http://localhost:8000/api                ║
║  Dashboard: http://localhost:5173  (dev)             ║
║  API Docs:  http://localhost:8000/docs               ║
║  WebSocket: ws://localhost:8000/ws                   ║
╚══════════════════════════════════════════════════════╝
    """)
    # Run with DEV_MODE=1 for auto-reload
    reload_mode = os.environ.get("DEV_MODE", "").lower() in ("1", "true", "yes")
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=reload_mode,
        log_level="info",
    )


if __name__ == "__main__":
    main()
