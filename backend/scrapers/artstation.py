"""ArtStation Jobs scraper plugin."""

import asyncio
from backend.scrapers.base import BaseScraper, ScrapeResult, ScrapeProgress
import logging

logger = logging.getLogger(__name__)


class ArtStationScraper(BaseScraper):
    name = "ArtStation Jobs"
    slug = "artstation"
    description = "Scrapes ArtStation job board for studio/agency hiring."
    default_fetcher = "dynamic"

    def get_default_config(self) -> dict:
        return {
            "base_url": "https://www.artstation.com/jobs/all",
            "selectors": {
                "job": "div.job-listing",
                "title": ".job-listing-header-title",
                "company": ".job-listing-header-company",
                "info": ".job-listing-header-info",
                "posted": ".text-small.text-white",
                "labels": ".job-item-info-label",
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
        from scrapling import DynamicFetcher

        cfg = {**self.get_default_config(), **self.config}
        sel = cfg["selectors"]
        fetcher = DynamicFetcher()

        for page_num in range(1, page_limit + 1):
            try:
                url = f"{cfg['base_url']}?page={page_num}"
                page = await asyncio.to_thread(fetcher.fetch, url, timeout=30000, wait_selector=sel["job"])

                jobs = page.css(sel["job"])
                if not jobs:
                    break

                for job in jobs:
                    title_el = job.css(sel["title"]).first
                    company_el = job.css(sel["company"]).first
                    info_el = job.css(sel["info"]).first
                    posted_el = job.css(sel["posted"]).first

                    if not title_el or not company_el:
                        continue

                    title = title_el.text.strip()
                    company = company_el.text.strip()
                    job_url = page.urljoin(title_el.attrib.get("href", ""))
                    company_url = page.urljoin(company_el.attrib.get("href", ""))
                    location = info_el.text.strip() if info_el else "Remote/Unknown"
                    posted = posted_el.text.strip() if posted_el else "Recently"

                    labels = [l.text.strip() for l in job.css(sel["labels"])]

                    # Location parsing
                    country = "Unknown"
                    city = location
                    if "," in location:
                        parts = [p.strip() for p in location.split(",")]
                        city = parts[0]
                        country = parts[-1]
                    elif location.lower() == "remote":
                        country = "Remote"
                        city = "Remote"

                    # Keyword-based priority
                    low_title = title.lower()
                    is_high = any(
                        kw in low_title
                        for kw in ["3d", "motion", "cgi", "unreal", "render", "animation"]
                    )

                    yield ScrapeResult(
                        company=company,
                        job_title=title,
                        job_url=job_url,
                        job_posted_date=posted,
                        country=country,
                        city=city,
                        category="Studio/Agency",
                        priority="A+" if is_high else "A",
                        lead_type="company",
                        demand_signal=f"Hiring: {title} ({posted})",
                        service_needed="3D/Motion Design",
                        website=company_url,
                        notes=f"Tags: {', '.join(labels)}",
                        source_name="ArtStation",
                    )

            except Exception as e:
                logger.error("ArtStation scraping failed on page %d: %s", page_num, e)
                break

            if on_progress:
                pct = int((page_num / page_limit) * 100)
                on_progress(ScrapeProgress(percent=pct, message=f"ArtStation page {page_num}"))

            await asyncio.sleep(1.0)
