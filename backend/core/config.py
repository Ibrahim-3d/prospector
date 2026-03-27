"""Application configuration."""

from pathlib import Path
from pydantic import BaseModel
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SQLite needs a filesystem that supports proper locking.
# Use /tmp for runtime DB, persist to project dir on demand.
import platform
import shutil

_RUNTIME_DB_DIR = Path("/tmp/leads_scraper") if platform.system() != "Windows" else BASE_DIR / "data"
_RUNTIME_DB_DIR.mkdir(parents=True, exist_ok=True)

# On startup, copy persisted DB into runtime location if it exists
_PERSIST_DB = BASE_DIR / "data" / "leads.db"
DB_PATH = _RUNTIME_DB_DIR / "leads.db"

if _PERSIST_DB.exists() and not DB_PATH.exists():
    _PERSIST_DB.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(str(_PERSIST_DB), str(DB_PATH))
    except Exception as e:
        logger.error("Failed to copy database: %s", e, exc_info=True)

CONFIG_PATH = BASE_DIR / "data" / "config.json"
LOGS_DIR = BASE_DIR / "logs"
BACKUP_DIR = BASE_DIR / "outputs" / "json"


def persist_db():
    """Copy runtime DB back to project directory for persistence."""
    if DB_PATH.exists():
        _PERSIST_DB.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(str(DB_PATH), str(_PERSIST_DB))
        except Exception as e:
            logger.error("Failed to persist database: %s", e, exc_info=True)


class AppConfig(BaseModel):
    """Global application settings."""

    db_url: str = f"sqlite:///{DB_PATH}"
    gemini_command: str = "gemini"
    gemini_timeout: int = 30
    default_page_limit: int = 3
    request_delay: float = 2.0  # seconds between requests
    max_retries: int = 3
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    webhook_url: Optional[str] = None
    webhook_on_job_complete: bool = False
    webhook_on_new_leads: bool = False

    # ── Search Preferences (one-time setup, used as defaults) ──
    job_titles: list[str] = [
        "3D Artist", "Motion Designer", "CGI Artist",
        "Unreal Engine Developer", "3D Animator",
        "Motion Graphics Designer", "Creative Director 3D",
        "WebGL Developer", "VFX Artist",
        "Product Visualization Specialist",
        "Architectural Visualization Artist",
    ]
    search_queries: dict[str, list[str]] = {
        "linkedin": [
            "3D Artist OR Motion Designer OR CGI",
            "Unreal Engine Developer",
            "3D Animator",
            "Motion Graphics Designer",
            "Creative Director 3D",
            "WebGL Developer",
            "Product Visualization",
            "Architectural Visualization",
            "VFX Artist",
            "Real-time 3D",
        ],
        "upwork": [
            "3d-animation", "3d-rendering", "motion-graphics",
            "unreal-engine", "webgl", "product-visualization",
            "architectural-visualization",
        ],
        "artstation": [],
        "wamda": [],
    }
    regions: list[str] = [
        "United Arab Emirates", "Kuwait", "Saudi Arabia",
        "Qatar", "Bahrain", "Oman",
        "London", "Berlin", "Paris", "Amsterdam",
        "New York", "Los Angeles", "Toronto",
        "Sydney", "Singapore", "Remote",
    ]
    enabled_sources: list[str] = ["linkedin", "artstation", "wamda", "upwork"]


def load_config() -> AppConfig:
    """Load config from file, falling back to defaults."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            data = json.load(f)
        return AppConfig(**data)
    return AppConfig()


def save_config(config: AppConfig):
    """Persist config to disk."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config.model_dump(), f, indent=2)
