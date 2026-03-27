"""Wamda (MENA funding news) scraper plugin."""

import asyncio
from backend.scrapers.base import BaseScraper, ScrapeResult, ScrapeProgress
from backend.scrapers.llm_enricher import enrich_startup_lead
import logging

logger = logging.getLogger(__name__)


class WamdaScraper(BaseScraper):
    name = "Wamda (MENA Funding)"
    slug = "wamda"
    description = "Scrapes Wamda.com for MENA startup funding news."
    default_fetcher = "stealthy"

    def get_default_config(self) -> dict:
        return {
            "base_url": "https://www.wamda.com/news",
            "selectors": {
                "article": "div.c-media, .c-media",
                "title": "h2.c-media__title a",
                "meta": ".c-media__meta",
            },
        }

    async def scrape(
        self,
        queries: list[str],
        regions: list[str],
        filters: dict,
        page_limit: int = 3,
        use_llm: bool = True,
        on_progress=None,
    ):
        from scrapling import StealthyFetcher

        cfg = {**self.get_default_config(), **self.config}
        sel = cfg["selectors"]
        fetcher = StealthyFetcher()

        try:
            page = await asyncio.to_thread(fetcher.fetch, cfg["base_url"], timeout=40000)
            articles = page.css(sel["article"])

            if not articles:
                return

            total = len(articles)
            for idx, article in enumerate(articles):
                title_el = article.css(sel["title"]).first
                meta_el = article.css(sel["meta"]).first

                if not title_el:
                    continue

                headline = title_el.text.strip()
                meta_text = meta_el.text.strip() if meta_el else "Recent"
                date = meta_text.split("|")[-1].strip() if "|" in meta_text else meta_text
                article_url = page.urljoin(title_el.attrib.get("href", ""))

                # LLM enrichment
                if use_llm:
                    enriched = await asyncio.to_thread(
                        enrich_startup_lead, headline, date, article_url
                    )
                else:
                    enriched = {
                        "company": headline[:50],
                        "country": "MENA",
                        "city": "Unknown",
                        "demand_signal": headline,
                    }

                company = enriched.get("company", headline)
                country = enriched.get("country", "MENA")
                city = enriched.get("city", "Unknown")
                demand_signal = enriched.get("demand_signal", headline)

                if len(company) < 2 or len(company) > 40:
                    continue

                yield ScrapeResult(
                    company=company,
                    country=country,
                    city=city,
                    region="MENA",
                    category="Funded Startup",
                    priority="A+",
                    lead_type="startup",
                    demand_signal=f"Funding News: {demand_signal}",
                    service_needed="3D/CGI Ads / Branding",
                    job_url=article_url,
                    job_posted_date=date,
                    notes=f"Headline: {headline}",
                    source_name="Wamda",
                )

                if on_progress:
                    pct = int(((idx + 1) / total) * 100)
                    on_progress(ScrapeProgress(percent=pct, message=f"Wamda: {company}"))

        except Exception as e:
            logger.error("Wamda scraping failed: %s", e)
