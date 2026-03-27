# Leads Engine Revamp: Phase 5 (Orchestration & Utilities)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the overarching runner script, setup the excel and strategy data flows, and prepare migration scripts.

**Architecture:** 
- **Storage:** SQLite (`leads.db`) with Excel as a rendered view. Includes real entity resolution.
- **Scraping:** Leverage Scrapling's `AsyncStealthySession` and `AsyncDynamicSession`.
- **Pipeline:** Deterministic normalization -> Probabilistic extraction (LLM) -> Probabilistic enrichment (LLM) -> Deterministic validation -> Deterministic scoring.
- **Orchestration:** Load full strategy -> Scrape -> Pipeline -> Store -> Excel -> Report. Includes CLI arguments and scheduling.

**Tech Stack:** Python 3.10+, Scrapling, Pydantic (or Dataclasses), SQLite3, openpyxl, pytest, rapidfuzz, dateutil.

---

### Task 8: Utilities (Strategy Loader & Excel Writer)

**Files:**
- Create: `leads_engine/utils/strategy_loader.py`
- Create: `leads_engine/output/excel_writer.py`

**Step 1: Write implementation**

```python
# leads_engine/utils/strategy_loader.py
import openpyxl
from leads_engine.logging.logger import get_logger

logger = get_logger(__name__)

def load_strategy(excel_path: str) -> dict:
    try:
        wb = openpyxl.load_workbook(excel_path, data_only=True)
        sheet = wb["🔎 Query Library (100+)"]
    except Exception as e:
        logger.error(f"Failed to load strategy excel: {e}")
        return {}
    
    strategy = {
        "linkedin_jobs_queries": [],
        "upwork_queries": [],
        "artstation_queries": [],
        "wamda_queries": [],
        "producthunt_queries": [],
        "crunchbase_queries": []
    }
    
    for row in sheet.iter_rows(min_row=2, values_only=True):
        platform, query = row[0], row[1]
        if not platform or not query: continue
        
        p = str(platform).lower()
        if "linkedin" in p and "job" in p: strategy["linkedin_jobs_queries"].append(query)
        elif "upwork" in p: strategy["upwork_queries"].append(query)
        elif "artstation" in p: strategy["artstation_queries"].append(query)
        elif "wamda" in p: strategy["wamda_queries"].append(query)
        elif "product" in p: strategy["producthunt_queries"].append(query)
        elif "crunchbase" in p: strategy["crunchbase_queries"].append(query)
        
    return strategy
```

```python
# leads_engine/output/excel_writer.py
import openpyxl
from leads_engine.db.store import get_all_leads

def generate_excel(db_path: str, output_path: str):
    wb = openpyxl.Workbook()
    
    sheets = {
        "📊 Dashboard": wb.active,
        "🔥 Hot Leads (A+ Priority)": wb.create_sheet(),
        "📋 All Leads (Master Registry)": wb.create_sheet(),
        "👔 LinkedIn Jobs": wb.create_sheet(),
        "🎨 ArtStation Jobs": wb.create_sheet(),
        "💰 MENA Funding": wb.create_sheet(),
        "🔧 Upwork Projects": wb.create_sheet(),
        "⚠️ Manual Review Queue": wb.create_sheet(),
        "📈 Run History": wb.create_sheet()
    }
    
    sheets["📊 Dashboard"].title = "📊 Dashboard"
    for title, ws in list(sheets.items())[1:]:
        ws.title = title
    
    headers = ["Lead ID", "Company", "Title", "Source", "Priority", "URL", "Status", "Confidence", "Issues"]
    
    for title in ["📋 All Leads (Master Registry)", "🔥 Hot Leads (A+ Priority)", "👔 LinkedIn Jobs", "🎨 ArtStation Jobs", "💰 MENA Funding", "🔧 Upwork Projects", "⚠️ Manual Review Queue"]:
        sheets[title].append(headers)
    
    leads = get_all_leads(db_path)
    for l in leads:
        row = [l.get("lead_id"), l.get("company"), l.get("title"), l.get("source"), l.get("priority"), l.get("url"), l.get("status"), l.get("overall_confidence"), l.get("validation_issues")]
        
        sheets["📋 All Leads (Master Registry)"].append(row)
        
        if l.get("priority") == "A+" and l.get("status") in ["new", "researching"]:
            sheets["🔥 Hot Leads (A+ Priority)"].append(row)
            
        if l.get("source") == "linkedin_jobs": sheets["👔 LinkedIn Jobs"].append(row)
        elif l.get("source") == "artstation": sheets["🎨 ArtStation Jobs"].append(row)
        elif l.get("source") == "wamda": sheets["💰 MENA Funding"].append(row)
        elif l.get("source") == "upwork": sheets["🔧 Upwork Projects"].append(row)
        
        if float(l.get("overall_confidence") or 1.0) < 0.5 or l.get("validation_issues"):
            sheets["⚠️ Manual Review Queue"].append(row)
            
    wb.save(output_path)
```

**Step 2: Commit**

```bash
git add leads_engine/utils leads_engine/output
git commit -m "feat: complete strategy loader and multi-sheet excel generator"
```

---

### Task 9: Data Migration Script

**Files:**
- Create: `leads_engine/scripts/migrate_data.py`

**Step 1: Write implementation**

```python
# leads_engine/scripts/migrate_data.py
import sqlite3
import openpyxl
import uuid
import json
from datetime import datetime
from leads_engine.db.store import init_db, resolve_entity, normalize_company, get_all_leads

def migrate():
    init_db("leads.db")
    
    try:
        wb = openpyxl.load_workbook("ibrahim_guerrilla_targeting_v2.xlsx", data_only=True)
    except FileNotFoundError:
        print("No old excel to migrate. Skipping.")
        return

    conn = sqlite3.connect("leads.db")
    existing_leads = get_all_leads("leads.db")
    migrated_count = 0
    
    if "📋 Company Tracker" in wb.sheetnames:
        sheet = wb["📋 Company Tracker"]
        for row in sheet.iter_rows(min_row=2, values_only=True):
            company = row[0]
            url = row[3] if len(row) > 3 else None
            if not company: continue
            
            lead_dict = {
                "company": company,
                "company_clean": company,
                "company_normalized": normalize_company(company),
                "url": url
            }
            
            if not resolve_entity(lead_dict, existing_leads):
                lead_id = f"LD-{uuid.uuid4().hex[:8].upper()}"
                conn.execute("""
                    INSERT INTO leads (
                        lead_id, company, company_clean, company_normalized, country, city,
                        title, priority, score_raw, source, url, status, overall_confidence,
                        first_seen, last_updated, run_id, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    lead_id, company, company, lead_dict["company_normalized"], "Unknown", "Unknown",
                    "Legacy Lead", "B", 0.0, "legacy", url or "Unknown", "new", 1.0,
                    datetime.now(), datetime.now(), "MIGRATION", "{}"
                ))
                existing_leads.append({"lead_id": lead_id, "company_normalized": lead_dict["company_normalized"], "url": url})
                migrated_count += 1
                
    conn.commit()
    conn.close()
    print(f"Migration complete. Migrated {migrated_count} leads.")

if __name__ == "__main__":
    migrate()
```

**Step 2: Commit**

```bash
git add leads_engine/scripts
git commit -m "feat: complete robust data migration script"
```

---

### Task 10: Orchestrator `main.py` & CLI arguments

**Files:**
- Create: `main.py`

**Step 1: Write implementation**

```python
# main.py
import asyncio
import yaml
import uuid
import argparse
from datetime import datetime
from leads_engine.db.store import init_db, resolve_entity, insert_lead, get_all_leads, record_run
from leads_engine.utils.strategy_loader import load_strategy
from leads_engine.scrapers.session_factory import create_session
from leads_engine.scrapers.linkedin import LinkedinJobsScraper
from leads_engine.scrapers.upwork import UpworkScraper
from leads_engine.scrapers.artstation import ArtstationScraper
from leads_engine.scrapers.wamda import WamdaScraper
from leads_engine.scrapers.producthunt import ProducthuntScraper
from leads_engine.scrapers.crunchbase import CrunchbaseScraper
from leads_engine.pipeline.normalizer import normalize_lead_data
from leads_engine.pipeline.extractor import extract_fields
from leads_engine.pipeline.enricher import enrich_leads
from leads_engine.pipeline.scorer import score_lead
from leads_engine.output.excel_writer import generate_excel
from leads_engine.logging.logger import get_logger, RunReport, log_rejected_lead

logger = get_logger(__name__)

SCRAPER_MAP = {
    "linkedin_jobs": LinkedinJobsScraper,
    "upwork": UpworkScraper,
    "artstation": ArtstationScraper,
    "wamda": WamdaScraper,
    "producthunt": ProducthuntScraper,
    "crunchbase": CrunchbaseScraper
}

async def run_source(source_name, scraper_cls, queries, config):
    scraper = scraper_cls(config)
    async with await create_session(config) as session:
        return await scraper.scrape(queries, session)

async def main(args):
    run_id = f"RUN-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    started_at = datetime.now()
    
    init_db()
    record_run("leads.db", run_id, started_at, args.source or "all")
    
    with open("leads_engine/config/source_registry.yaml") as f:
        registry = yaml.safe_load(f)
        
    strategy = load_strategy("ibrahim_guerrilla_targeting_v2.xlsx")
    
    tasks = []
    for source_name, scraper_cls in SCRAPER_MAP.items():
        if args.source and args.source != source_name:
            continue
            
        queries = strategy.get(f"{source_name}_queries", [])
        if queries:
            if args.test_limit:
                queries = queries[:args.test_limit]
            tasks.append(run_source(source_name, scraper_cls, queries, registry[source_name]))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_raw_leads = []
    for r in results:
        if not isinstance(r, Exception): all_raw_leads.extend(r)
        else: logger.error(f"Source runner failed: {r}")
        
    if args.dry_run:
        logger.info(f"Dry run complete. Extracted {len(all_raw_leads)} raw leads. Exiting.")
        return

    normalized = []
    for l in all_raw_leads:
        valid, reason = l.is_valid_for_enrichment()
        if valid:
            normalized.append(normalize_lead_data(l))
        else:
            log_rejected_lead(l.__dict__, reason)
            
    extracted = extract_fields(normalized)
    enriched = enrich_leads(extracted)
    scored = [score_lead(e) for e in enriched]
    
    existing_leads = get_all_leads("leads.db")
    inserted = 0
    for s in scored: 
        s.run_id = run_id
        if s.overall_confidence < 0.3:
            log_rejected_lead(s.__dict__, "CONFIDENCE_TOO_LOW")
            continue
            
        match_id = resolve_entity(s.__dict__, existing_leads)
        if not match_id:
            s.lead_id = f"LD-{uuid.uuid4().hex[:8].upper()}"
            insert_lead("leads.db", s)
            existing_leads.append(s.__dict__)
            inserted += 1
        else:
            logger.info(f"DEDUP_HIT: Dropping duplicate lead {s.company}")
    
    if not args.skip_excel:
        generate_excel("leads.db", "leads_engine_output.xlsx")
    
    report = RunReport(run_id=run_id, started_at=started_at, source=args.source or "all")
    report.raw_leads_extracted = len(all_raw_leads)
    report.leads_after_validation = len(normalized)
    report.leads_enriched = len(enriched)
    report.leads_after_dedup = inserted
    report.save()
    
    logger.info(f"Run {run_id} complete. Inserted {inserted} new leads.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Viral X Leads Engine")
    parser.add_argument("--source", type=str, help="Specific source to run (e.g., linkedin_jobs, upwork)")
    parser.add_argument("--dry-run", action="store_true", help="Scrape only, do not enrich or store")
    parser.add_argument("--test-limit", type=int, help="Limit number of queries per source for testing")
    parser.add_argument("--skip-excel", action="store_true", help="Skip excel generation")
    args = parser.parse_args()
    
    asyncio.run(main(args))
```

**Step 2: Commit**

```bash
git add main.py
git commit -m "feat: implement orchestrator with CLI arguments, full mapping, and reporting"
```

---

### Task 11: Windows Task Scheduler Helper

**Files:**
- Create: `leads_engine/scripts/schedule.bat`

**Step 1: Write implementation**

```bat
@echo off
REM Viral X Leads Engine Daily Scraper
cd /d "%~dp0\..\.."
call venv\Scripts\activate
python main.py
```

**Step 2: Commit**

```bash
git add leads_engine/scripts/schedule.bat
git commit -m "feat: add windows task scheduler bat script"
```