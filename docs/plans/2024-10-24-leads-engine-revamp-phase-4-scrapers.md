# Leads Engine Revamp: Phase 4 (Scrapers)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the scraper models natively using Scrapling's APIs for various target platforms.

**Architecture:** 
- **Storage:** SQLite (`leads.db`) with Excel as a rendered view. Includes real entity resolution.
- **Scraping:** Leverage Scrapling's `AsyncStealthySession` and `AsyncDynamicSession`.
- **Pipeline:** Deterministic normalization -> Probabilistic extraction (LLM) -> Probabilistic enrichment (LLM) -> Deterministic validation -> Deterministic scoring.
- **Orchestration:** Load full strategy -> Scrape -> Pipeline -> Store -> Excel -> Report. Includes CLI arguments and scheduling.

**Tech Stack:** Python 3.10+, Scrapling, Pydantic (or Dataclasses), SQLite3, openpyxl, pytest, rapidfuzz, dateutil.

---

### Task 7: Scrapers (Base, Session Factory, and Concrete Implementations)

**Files:**
- Create: `leads_engine/scrapers/session_factory.py`
- Create: `leads_engine/scrapers/base.py`
- Create: `leads_engine/scrapers/linkedin.py`
- Create: `leads_engine/scrapers/upwork.py`
- Create: `leads_engine/scrapers/artstation.py`
- Create: `leads_engine/scrapers/wamda.py`
- Create: `leads_engine/scrapers/producthunt.py`
- Create: `leads_engine/scrapers/crunchbase.py`

**Step 1: Write implementation**

```python
# leads_engine/scrapers/session_factory.py
from scrapling import AsyncStealthySession, AsyncDynamicSession

async def create_session(source_config: dict):
    session_type = source_config["session_type"]
    if session_type == "stealthy_async":
        return AsyncStealthySession(
            max_pages=source_config.get("max_pages", 1),
            **source_config.get("stealthy_opts", {})
        )
    elif session_type == "dynamic_async":
        return AsyncDynamicSession(
            max_pages=source_config.get("max_pages", 1),
            **source_config.get("dynamic_opts", {})
        )
    raise ValueError(f"Unknown session type: {session_type}")
```

```python
# leads_engine/scrapers/base.py
import asyncio
import random
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List
from leads_engine.models.lead import RawLead
from leads_engine.logging.logger import get_logger

logger = get_logger(__name__)

class BaseScraper(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.source_name = self.__class__.__name__.lower().replace("scraper", "")
        self.consecutive_failures = 0
        
    def save_debug_html(self, response, query: str):
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        safe_query = query.replace(' ', '_').replace('/', '-')
        filename = f"logs/html_dumps/debug_{self.source_name}_{safe_query}_{timestamp}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        logger.warning(f"SELECTOR_DRIFT_SUSPECT: Saved debug HTML to {filename}")

    @abstractmethod
    def extract_leads(self, response) -> List[RawLead]:
        pass
        
    async def scrape(self, queries: list[str], session) -> List[RawLead]:
        results = []
        for query in queries:
            if self.consecutive_failures >= self.config.get("circuit_breaker_threshold", 5):
                logger.critical(f"CIRCUIT_BREAK: {self.source_name} stopped due to consecutive failures")
                break
                
            delay = random.uniform(*self.config.get("delay_range", (2, 5)))
            await asyncio.sleep(delay)
            
            try:
                for page_num in range(1, self.config.get("max_pages_per_query", 1) + 1):
                    url = self.build_url(query, page_num)
                    # Scrapling handles: anti-detection, retries, proxy rotation, tab management
                    response = await session.fetch(url)
                    
                    if response.status != 200:
                        self.consecutive_failures += 1
                        logger.warning(f"FETCH_BLOCKED: {self.source_name} returned status {response.status}")
                        continue
                        
                    leads = self.extract_leads(response)
                    if not leads and page_num == 1:
                        self.save_debug_html(response, query)
                        logger.warning(f"SELECTOR_DRIFT_SUSPECT: {self.source_name}, query={query}")
                        self.consecutive_failures += 1
                        break
                        
                    results.extend(leads)
                    self.consecutive_failures = 0
                    
                    if len(leads) == 0:
                        break  # No more results
            except Exception as e:
                self.consecutive_failures += 1
                logger.error(f"FETCH_ERROR {self.source_name}: {e}")
                
        return results

    @abstractmethod
    def build_url(self, query: str, page_num: int) -> str:
        pass
```

```python
# leads_engine/scrapers/linkedin.py
from leads_engine.scrapers.base import BaseScraper
from leads_engine.models.lead import RawLead
import urllib.parse

class LinkedinJobsScraper(BaseScraper):
    def build_url(self, query: str, page_num: int) -> str:
        encoded = urllib.parse.quote(query)
        start_offset = (page_num - 1) * 25
        return f"https://www.linkedin.com/jobs/search?keywords={encoded}&f_TPR=r86400&start={start_offset}"
        
    def extract_leads(self, response) -> list[RawLead]:
        leads = []
        is_adaptive = self.config.get("adaptive_tracking", True)
        containers = response.css("div.job-card", identifier="linkedin_job_card", adaptive=is_adaptive, auto_save=True)
        if not containers:
            containers = response.css("li.result-card")
            
        for c in containers:
            title_el = c.css("h3.base-search-card__title")
            comp_el = c.css("h4.base-search-card__subtitle")
            loc_el = c.css("span.job-search-card__location")
            url_el = c.css("a.base-card__full-link")
            
            if title_el and comp_el and url_el:
                leads.append(RawLead(
                    source="linkedin_jobs",
                    title=title_el[0].text.strip(),
                    company=comp_el[0].text.strip(),
                    location_raw=loc_el[0].text.strip() if loc_el else None,
                    url=url_el[0].attrib.get("href")
                ))
        return leads
```

```python
# leads_engine/scrapers/upwork.py
from leads_engine.scrapers.base import BaseScraper
from leads_engine.models.lead import RawLead
import urllib.parse

class UpworkScraper(BaseScraper):
    def build_url(self, query: str, page_num: int) -> str:
        encoded = urllib.parse.quote(query)
        return f"https://www.upwork.com/nx/jobs/search/?q={encoded}&sort=recency&page={page_num}"
        
    def extract_leads(self, response) -> list[RawLead]:
        leads = []
        is_adaptive = self.config.get("adaptive_tracking", True)
        containers = response.css("section.up-card-section", identifier="upwork_job_card", adaptive=is_adaptive, auto_save=True)
        for c in containers:
            title_el = c.css("h2.job-tile-title a")
            desc_el = c.css("span.up-text-break")
            budget_el = c.css("li[data-test='job-type'] strong")
            
            if title_el:
                leads.append(RawLead(
                    source="upwork",
                    title=title_el[0].text.strip(),
                    company="Unknown (Upwork Client)",
                    url=response.urljoin(str(title_el[0].attrib.get("href", ""))),
                    description=desc_el[0].text.strip() if desc_el else None,
                    budget_raw=budget_el[0].text.strip() if budget_el else None
                ))
        return leads
```

```python
# leads_engine/scrapers/artstation.py
from leads_engine.scrapers.base import BaseScraper
from leads_engine.models.lead import RawLead
import urllib.parse

class ArtstationScraper(BaseScraper):
    def build_url(self, query: str, page_num: int) -> str:
        encoded = urllib.parse.quote(query)
        return f"https://www.artstation.com/jobs/c/all/type/all?q={encoded}&page={page_num}"
        
    def extract_leads(self, response) -> list[RawLead]:
        leads = []
        is_adaptive = self.config.get("adaptive_tracking", True)
        containers = response.css("div.job-listing", identifier="artstation_job_card", adaptive=is_adaptive, auto_save=True)
        for c in containers:
            title_el = c.css("h3.job-title")
            comp_el = c.css("div.company-name")
            url_el = c.css("a.job-link")
            
            if title_el and comp_el and url_el:
                leads.append(RawLead(
                    source="artstation",
                    title=title_el[0].text.strip(),
                    company=comp_el[0].text.strip(),
                    url=response.urljoin(str(url_el[0].attrib.get("href", "")))
                ))
        return leads
```

```python
# leads_engine/scrapers/wamda.py
from leads_engine.scrapers.base import BaseScraper
from leads_engine.models.lead import RawLead

class WamdaScraper(BaseScraper):
    def build_url(self, query: str, page_num: int) -> str:
        return f"https://www.wamda.com/news/investments?page={page_num}"
        
    def extract_leads(self, response) -> list[RawLead]:
        leads = []
        is_adaptive = self.config.get("adaptive_tracking", False)
        containers = response.css("article.news-item", identifier="wamda_news_card", adaptive=is_adaptive, auto_save=True)
        for c in containers:
            title_el = c.css("h2 a")
            date_el = c.css("span.date")
            
            if title_el:
                leads.append(RawLead(
                    source="wamda",
                    title=title_el[0].text.strip(),
                    company="Extract from Title",
                    url=response.urljoin(str(title_el[0].attrib.get("href", ""))),
                    posted_raw=date_el[0].text.strip() if date_el else None
                ))
        return leads
```

```python
# leads_engine/scrapers/producthunt.py
from leads_engine.scrapers.base import BaseScraper
from leads_engine.models.lead import RawLead

class ProducthuntScraper(BaseScraper):
    def build_url(self, query: str, page_num: int) -> str:
        return f"https://www.producthunt.com/search?q={query}&page={page_num}"
        
    def extract_leads(self, response) -> list[RawLead]:
        leads = []
        is_adaptive = self.config.get("adaptive_tracking", True)
        containers = response.css("div[data-test='post-item']", identifier="producthunt_post_card", adaptive=is_adaptive, auto_save=True)
        for c in containers:
            title_el = c.css("a[data-test='post-name']")
            desc_el = c.css("a[data-test='post-tagline']")
            
            if title_el:
                leads.append(RawLead(
                    source="producthunt",
                    title="Launch",
                    company=title_el[0].text.strip(),
                    description=desc_el[0].text.strip() if desc_el else None,
                    url=response.urljoin(str(title_el[0].attrib.get("href", "")))
                ))
        return leads
```

```python
# leads_engine/scrapers/crunchbase.py
from leads_engine.scrapers.base import BaseScraper
from leads_engine.models.lead import RawLead

class CrunchbaseScraper(BaseScraper):
    def build_url(self, query: str, page_num: int) -> str:
        return f"https://www.crunchbase.com/discover/funding_rounds?page={page_num}"
        
    def extract_leads(self, response) -> list[RawLead]:
        leads = []
        is_adaptive = self.config.get("adaptive_tracking", True)
        containers = response.css("div.funding-round-row", identifier="crunchbase_funding_card", adaptive=is_adaptive, auto_save=True)
        for c in containers:
            comp_el = c.css("a.organization-name")
            desc_el = c.css("span.funding-type")
            
            if comp_el:
                leads.append(RawLead(
                    source="crunchbase",
                    title=desc_el[0].text.strip() if desc_el else "Funding Round",
                    company=comp_el[0].text.strip(),
                    url=response.urljoin(str(comp_el[0].attrib.get("href", "")))
                ))
        return leads
```

**Step 2: Commit**

```bash
git add leads_engine/scrapers
git commit -m "feat: complete all scrapers with scrapling DOM API including ProductHunt and Crunchbase"
```