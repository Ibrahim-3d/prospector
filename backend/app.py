"""FastAPI application entry point."""

import asyncio
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.core.config import load_config
from backend.core.database import init_db, SessionLocal
from backend.api.routes import router
from backend.services.scrape_service import set_progress_callback
from backend.services.seed import seed_sources

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# WebSocket connections
_ws_clients: set[WebSocket] = set()
_ws_lock = asyncio.Lock()


async def broadcast_to_ws(data: dict):
    """Broadcast progress updates to all connected WebSocket clients."""
    message = json.dumps(data, default=str)
    async with _ws_lock:
        disconnected = set()
        for ws in list(_ws_clients):
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.add(ws)
        _ws_clients -= disconnected


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Starting Leads Scraper API...")
    init_db()
    seed_sources()
    def _sync_broadcast(data: dict):
        asyncio.create_task(broadcast_to_ws(data))
    set_progress_callback(_sync_broadcast)
    logger.info("Database initialized, sources seeded.")
    yield
    logger.info("Shutting down...")


config = load_config()

app = FastAPI(
    title="Leads Scraper",
    description="Universal lead scraping and management dashboard",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# API routes
app.include_router(router, prefix="/api")


# WebSocket for live scrape progress
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    async with _ws_lock:
        _ws_clients.add(websocket)
    logger.info("WebSocket client connected (%d total)", len(_ws_clients))
    try:
        while True:
            # Keep connection alive, listen for client messages
            data = await websocket.receive_text()
            # Client can send ping/pong or commands
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        async with _ws_lock:
            _ws_clients.discard(websocket)
        logger.info("WebSocket client disconnected (%d remaining)", len(_ws_clients))


@router.get("/health")
def health_check():
    return {"status": "ok", "version": "2.0"}


# Serve frontend static files in production
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
