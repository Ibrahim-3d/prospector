"""Base scraper interface — all scrapers extend this."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    """A single scraped lead before DB insertion."""
    company: str = ""
    job_title: str = ""
    job_url: str = ""
    job_posted_date: str = ""
    country: str = ""
    city: str = ""
    region: str = ""
    category: str = ""
    priority: str = "A"
    lead_type: str = "company"
    demand_signal: str = ""
    service_needed: str = ""
    website: str = ""
    budget: str = ""
    project_type: str = ""
    duration: str = ""
    experience_level: str = ""
    skills: str = ""
    description: str = ""
    notes: str = ""
    score: float = 0.0
    raw_data: dict = field(default_factory=dict)


@dataclass
class ScrapeProgress:
    """Progress update emitted during scraping."""
    percent: int = 0
    message: str = ""
    leads_found: int = 0
    errors: int = 0


class BaseScraper(ABC):
    """
    Base class for all scrapers.

    To add a new source:
    1. Create a file in backend/scrapers/ (e.g. clutch.py)
    2. Subclass BaseScraper
    3. Implement scrape() generator
    4. Register in SCRAPER_REGISTRY
    """

    name: str = "base"
    slug: str = "base"
    description: str = ""
    default_fetcher: str = "stealthy"  # "static", "dynamic", "stealthy"

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"scraper.{self.slug}")

    @abstractmethod
    async def scrape(
        self,
        queries: list[str],
        regions: list[str],
        filters: dict,
        page_limit: int = 3,
        use_llm: bool = True,
        on_progress: callable = None,
    ) -> AsyncGenerator[ScrapeResult, None]:
        """
        Yield ScrapeResult objects as they're found.

        Args:
            queries: Search queries to execute
            regions: Geographic regions to search in
            filters: Additional filters (job_titles, keywords, etc.)
            page_limit: Max pages to scrape per query
            use_llm: Whether to enrich with LLM
            on_progress: Callback for progress updates
        """
        yield  # type: ignore

    def get_default_config(self) -> dict:
        """Return default configuration for this scraper."""
        return {}
