# Leads Engine Revamp: Phase 2 (Database & Logging)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the SQLite database schema, store operations, and structured logging.

**Architecture:** 
- **Storage:** SQLite (`leads.db`) with Excel as a rendered view. Includes real entity resolution.
- **Scraping:** Leverage Scrapling's `AsyncStealthySession` and `AsyncDynamicSession`.
- **Pipeline:** Deterministic normalization -> Probabilistic extraction (LLM) -> Probabilistic enrichment (LLM) -> Deterministic validation -> Deterministic scoring.
- **Orchestration:** Load full strategy -> Scrape -> Pipeline -> Store -> Excel -> Report. Includes CLI arguments and scheduling.

**Tech Stack:** Python 3.10+, Scrapling, Pydantic (or Dataclasses), SQLite3, openpyxl, pytest, rapidfuzz, dateutil.

---

### Task 3: SQLite Database Schema & Store Operations

**Files:**
- Create: `leads_engine/db/schema.sql`
- Create: `leads_engine/db/store.py`

**Step 1: Write implementation**

```sql
-- leads_engine/db/schema.sql
CREATE TABLE IF NOT EXISTS leads (
    lead_id TEXT PRIMARY KEY,
    company TEXT,
    company_clean TEXT NOT NULL,
    company_normalized TEXT NOT NULL,
    country TEXT NOT NULL,
    city TEXT,
    title TEXT,
    priority TEXT NOT NULL,
    score_raw REAL NOT NULL,
    source TEXT NOT NULL,
    url TEXT NOT NULL,
    status TEXT NOT NULL,
    overall_confidence REAL NOT NULL,
    first_seen DATETIME NOT NULL,
    last_updated DATETIME NOT NULL,
    run_id TEXT NOT NULL,
    raw_data TEXT
);

CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    started_at DATETIME NOT NULL,
    completed_at DATETIME,
    source TEXT NOT NULL,
    metrics TEXT
);
```

```python
# leads_engine/db/store.py
import sqlite3
import os
import json
from datetime import datetime
from rapidfuzz import fuzz
from leads_engine.models.lead import Lead

def init_db(db_path: str = "leads.db"):
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    
    conn = sqlite3.connect(db_path)
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()

def record_run(db_path: str, run_id: str, started_at: datetime, source: str):
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT OR REPLACE INTO runs (run_id, started_at, source) VALUES (?, ?, ?)", 
                 (run_id, started_at, source))
    conn.commit()
    conn.close()

def normalize_company(name: str) -> str:
    if not name: return ""
    name = name.lower().strip()
    for suffix in [" inc", " llc", " ltd", " gmbh", " inc.", " ltd."]:
        if name.endswith(suffix):
            name = name[:-len(suffix)].strip()
    return name

def resolve_entity(new_lead: dict, existing_leads: list[dict]) -> str | None:
    candidates = []
    new_comp = normalize_company(new_lead.get("company_clean") or new_lead.get("company", ""))
    
    for existing in existing_leads:
        score = 0.0
        ex_comp = existing.get("company_normalized", "")
        
        if new_comp and new_comp == ex_comp:
            score += 0.5
        elif new_comp and ex_comp and fuzz.ratio(new_comp, ex_comp) > 85:
            score += 0.35
            
        if new_lead.get("url") and new_lead.get("url") == existing.get("url"):
            score += 0.8
            
        if score >= 0.5:
            candidates.append((existing.get("lead_id"), score))
            
    if candidates:
        return max(candidates, key=lambda x: x[1])[0]
    return None

def insert_lead(db_path: str, lead: Lead):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        INSERT INTO leads (
            lead_id, company, company_clean, company_normalized, country, city,
            title, priority, score_raw, source, url, status, overall_confidence,
            first_seen, last_updated, run_id, raw_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lead.lead_id, lead.company, lead.company_clean, normalize_company(lead.company_clean),
        lead.country, lead.city, lead.title, lead.priority, lead.score_raw, lead.source,
        lead.url, lead.status, lead.overall_confidence, 
        lead.first_seen or datetime.now(), lead.last_updated or datetime.now(), lead.run_id,
        json.dumps(lead.__dict__, default=str)
    ))
    conn.commit()
    conn.close()

def get_all_leads(db_path: str) -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM leads").fetchall()
    conn.close()
    return [dict(r) for r in rows]
```

**Step 2: Commit**

```bash
git add leads_engine/db
git commit -m "feat: complete sqlite schema, db store, and robust entity resolution"
```

---

### Task 4: Logging & Reporting

**Files:**
- Create: `leads_engine/logging/logger.py`

**Step 1: Write implementation**

```python
# leads_engine/logging/logger.py
import logging
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict

def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

@dataclass
class RunReport:
    run_id: str
    started_at: datetime
    source: str
    completed_at: datetime | None = None
    queries_executed: int = 0
    pages_fetched: int = 0
    pages_failed: int = 0
    failure_reasons: Dict[str, int] = field(default_factory=dict)
    raw_leads_extracted: int = 0
    leads_after_validation: int = 0
    leads_after_dedup: int = 0
    leads_enriched: int = 0
    circuit_breaks: int = 0
    avg_fetch_time_ms: float = 0.0
    avg_enrichment_time_ms: float = 0.0
    
    def save(self):
        self.completed_at = datetime.now()
        path = f"logs/runs/{self.run_id}.json"
        with open(path, "w") as f:
            data = self.__dict__.copy()
            data["started_at"] = self.started_at.isoformat()
            data["completed_at"] = self.completed_at.isoformat()
            json.dump(data, f, indent=2)

def log_rejected_lead(lead_dict: dict, reason: str):
    with open("logs/runs/rejected_leads.jsonl", "a") as f:
        lead_dict["_rejection_reason"] = reason
        lead_dict["_timestamp"] = datetime.now().isoformat()
        f.write(json.dumps(lead_dict, default=str) + "
")
```

**Step 2: Commit**

```bash
git add leads_engine/logging
git commit -m "feat: structured logger, run reporting, and rejected leads logging"
```