"""Scraper plugin registry — maps slugs to scraper classes."""

from backend.scrapers.base import BaseScraper
from backend.scrapers.linkedin import LinkedInScraper
from backend.scrapers.artstation import ArtStationScraper
from backend.scrapers.wamda import WamdaScraper
from backend.scrapers.upwork import UpworkScraper

# Register all available scrapers here
SCRAPER_REGISTRY: dict[str, type[BaseScraper]] = {
    "linkedin": LinkedInScraper,
    "artstation": ArtStationScraper,
    "wamda": WamdaScraper,
    "upwork": UpworkScraper,
}


def get_scraper(slug: str, config: dict | None = None) -> BaseScraper:
    """Get a scraper instance by slug."""
    cls = SCRAPER_REGISTRY.get(slug)
    if not cls:
        raise ValueError(f"Unknown scraper: {slug}. Available: {list(SCRAPER_REGISTRY.keys())}")
    return cls(config=config)


def list_scrapers() -> list[dict]:
    """List all registered scrapers with metadata."""
    result = []
    for slug, cls in SCRAPER_REGISTRY.items():
        instance = cls()
        result.append({
            "slug": slug,
            "name": instance.name,
            "description": instance.description,
            "fetcher_type": instance.default_fetcher,
            "default_config": instance.get_default_config(),
        })
    return result
