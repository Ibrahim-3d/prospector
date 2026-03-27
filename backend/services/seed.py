"""Seed default sources into the database."""

from backend.core.database import SessionLocal
from backend.models.source import Source
from backend.scrapers.registry import list_scrapers
import logging

logger = logging.getLogger(__name__)


def seed_sources():
    """Insert default sources if they don't exist."""
    db = SessionLocal()
    try:
        for scraper_info in list_scrapers():
            existing = db.query(Source).filter(Source.slug == scraper_info["slug"]).first()
            if not existing:
                source = Source(
                    name=scraper_info["name"],
                    slug=scraper_info["slug"],
                    description=scraper_info["description"],
                    scraper_module=scraper_info["slug"],
                    fetcher_type=scraper_info["fetcher_type"],
                    default_config=scraper_info["default_config"],
                    enabled=True,
                )
                db.add(source)
                logger.info("Seeded source: %s", scraper_info["name"])
        db.commit()
    finally:
        db.close()
