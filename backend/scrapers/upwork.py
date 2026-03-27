"""Upwork projects scraper plugin."""

import asyncio
from urllib.parse import quote_plus
from backend.scrapers.base import BaseScraper, ScrapeResult, ScrapeProgress
from backend.scrapers.llm_enricher import enrich_job_lead
import logging

logger = logging.getLogger(__name__)


class UpworkScraper(BaseScraper):
    name = "Upwork Projects"
    slug = "upwork"
    description = "Scrapes Upwork freelance job postings with Cloudflare bypass."
    default_fetcher = "stealthy"

    def get_default_config(self) -> dict:
        return {
            "base_url": "https://www.upwork.com/freelance-jobs",
            "selectors": {
                "job": "div.job-tile, .job-tile",
                "title": "h3.job-tile-title a, h2.job-tile-title a",
                "type": "strong[data-test='job-type']",
                "budget": "span[data-test='budget']",
                "duration": "span[data-test='duration']",
                "experience": "span[data-test='experience-level']",
                "description": "p.job-tile-description, div[data-test='job-description-text']",
                "posted": "time, span[data-test='posted-on']",
                "skills": ".air3-token-container span.air3-token",
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
            queries = ["3d-animation"]

        total_work = len(queries) * page_limit
        completed = 0

        for query in queries:
            safe_query = quote_plus(query)
            base_url = f"{cfg['base_url']}/{safe_query}/"

            for page_num in range(1, page_limit + 1):
                url = base_url if page_num == 1 else f"{base_url}?page={page_num}"

                try:
                    page = await asyncio.to_thread(fetcher.fetch, url, timeout=60000, solve_cloudflare=True)
                    jobs = page.css(sel["job"])

                    if not jobs:
                        completed += page_limit - page_num + 1
                        break

                    for job in jobs:
                        title_el = job.css(sel["title"]).first
                        if not title_el:
                            continue

                        raw_title = title_el.text.strip()
                        job_url = page.urljoin(title_el.attrib.get("href", ""))

                        type_el = job.css(sel["type"]).first
                        budget_el = job.css(sel["budget"]).first
                        duration_el = job.css(sel["duration"]).first
                        exp_el = job.css(sel["experience"]).first
                        desc_el = job.css(sel["description"]).first
                        posted_el = job.css(sel["posted"]).first

                        job_type = type_el.text.strip() if type_el else "Fixed-price"
                        budget = budget_el.text.strip() if budget_el else ""
                        duration = duration_el.text.strip() if duration_el else ""
                        experience = exp_el.text.strip() if exp_el else ""
                        description = desc_el.text.strip() if desc_el else ""
                        posted = posted_el.text.strip() if posted_el else "Recent"
                        skills = [s.text.strip() for s in job.css(sel["skills"])]

                        # LLM enrichment
                        if use_llm:
                            enriched = await asyncio.to_thread(
                                enrich_job_lead, raw_title, "Unknown Client", "Remote", description
                            )
                        else:
                            enriched = {
                                "clean_title": raw_title,
                                "priority": "A",
                                "service_needed": "3D Animation",
                            }

                        clean_title = enriched.get("clean_title", raw_title)
                        desc_short = (description[:300] + "...") if len(description) > 300 else description

                        yield ScrapeResult(
                            company=f"Upwork: {clean_title[:80]}",
                            job_title=clean_title,
                            job_url=job_url,
                            job_posted_date=posted,
                            country="Remote",
                            city="Remote",
                            category="Freelance Project",
                            priority=enriched.get("priority", "A"),
                            lead_type="project",
                            demand_signal=f"Project: {clean_title}",
                            service_needed=enriched.get("service_needed", "3D Animation"),
                            budget=budget,
                            project_type=job_type,
                            duration=duration,
                            experience_level=experience,
                            skills=", ".join(skills),
                            description=desc_short,
                            notes=f"Service: {enriched.get('service_needed', '')} | Direct pitch target.",
                            source_name="Upwork",
                        )

                except Exception as e:
                    logger.error("Upwork scraping failed for %s page %d: %s", query, page_num, e)
                    completed += page_limit - page_num + 1
                    break

                completed += 1
                if on_progress:
                    pct = int((completed / total_work) * 100)
                    on_progress(ScrapeProgress(percent=pct, message=f"Upwork: {query} p{page_num}"))

                await asyncio.sleep(2.0)
