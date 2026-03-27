"""LinkedIn Jobs scraper plugin."""

import asyncio
from urllib.parse import quote_plus
from backend.scrapers.base import BaseScraper, ScrapeResult, ScrapeProgress
from backend.scrapers.llm_enricher import enrich_job_lead
import logging

logger = logging.getLogger(__name__)


class LinkedInScraper(BaseScraper):
    name = "LinkedIn Jobs"
    slug = "linkedin"
    description = "Scrapes LinkedIn public job listings across regions and queries."
    default_fetcher = "stealthy"

    def get_default_config(self) -> dict:
        return {
            "base_url": "https://www.linkedin.com/jobs/search/",
            "time_filter": "r2592000",  # past 30 days
            "selectors": {
                "card": "div.base-card, .base-search-card",
                "title": "h3.base-search-card__title",
                "company": "h4.base-search-card__subtitle a",
                "location": "span.job-search-card__location",
                "date": "time.job-search-card__listdate",
                "date_new": "time.job-search-card__listdate--new",
                "link": "a.base-card__full-link",
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

        if not queries:
            queries = ["3D Artist OR Motion Designer OR CGI"]
        if not regions:
            regions = ["United Arab Emirates"]

        total_combos = len(queries) * len(regions)
        completed = 0

        for region in regions:
            for query in queries:
                try:
                    safe_query = quote_plus(query)
                    safe_region = quote_plus(region)
                    url = (
                        f"{cfg['base_url']}?keywords={safe_query}"
                        f"&location={safe_region}"
                        f"&f_TPR={cfg['time_filter']}"
                    )

                    page = await asyncio.to_thread(fetcher.fetch, url, timeout=60000)
                    cards = page.css(sel["card"])

                    if not cards:
                        completed += 1
                        continue

                    for card in cards:
                        title_el = card.css(sel["title"]).first
                        company_el = card.css(sel["company"]).first
                        location_el = card.css(sel["location"]).first
                        date_el = (
                            card.css(sel["date"]).first
                            or card.css(sel["date_new"]).first
                        )
                        link_el = card.css(sel["link"]).first

                        if not title_el or not company_el:
                            continue

                        raw_title = title_el.text.strip()
                        raw_company = company_el.text.strip()
                        raw_location = location_el.text.strip() if location_el else region
                        posted_date = (
                            date_el.attrib.get("datetime", "Unknown")
                            if date_el
                            else "Recent"
                        )
                        job_url = (
                            link_el.attrib.get("href", "").split("?")[0]
                            if link_el
                            else ""
                        )

                        # LLM enrichment
                        if use_llm:
                            enriched = await asyncio.to_thread(
                                enrich_job_lead, raw_title, raw_company, raw_location, ""
                            )
                        else:
                            enriched = {
                                "clean_title": raw_title,
                                "country": region,
                                "city": raw_location,
                                "priority": "A",
                                "service_needed": "3D/Motion Design",
                            }

                        yield ScrapeResult(
                            company=raw_company,
                            job_title=enriched.get("clean_title", raw_title),
                            job_url=job_url,
                            job_posted_date=posted_date,
                            country=enriched.get("country", region),
                            city=enriched.get("city", raw_location),
                            category="LinkedIn Target",
                            priority=enriched.get("priority", "A"),
                            lead_type="company",
                            demand_signal=f"Hiring: {enriched.get('clean_title', raw_title)} ({posted_date})",
                            service_needed=enriched.get("service_needed", "3D/Motion Design"),
                            notes=f"Location: {raw_location} | Link: {job_url}",
                            source_name="LinkedIn",
                        )

                except Exception as e:
                    logger.error("LinkedIn scraping failed for %s in %s: %s", query, region, e)

                completed += 1
                if on_progress:
                    pct = int((completed / total_combos) * 100)
                    on_progress(ScrapeProgress(
                        percent=pct,
                        message=f"LinkedIn: {query} in {region}",
                    ))

                # Rate limiting
                await asyncio.sleep(1.5)
