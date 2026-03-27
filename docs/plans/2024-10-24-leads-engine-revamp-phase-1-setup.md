# Leads Engine Revamp: Phase 1 (Setup & Models)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Establish the project skeleton, configuration files, and core data models for the new Leads Engine.

**Architecture:** 
- **Storage:** SQLite (`leads.db`) with Excel as a rendered view. Includes real entity resolution.
- **Scraping:** Leverage Scrapling's `AsyncStealthySession` and `AsyncDynamicSession`.
- **Pipeline:** Deterministic normalization -> Probabilistic extraction (LLM) -> Probabilistic enrichment (LLM) -> Deterministic validation -> Deterministic scoring.
- **Orchestration:** Load full strategy -> Scrape -> Pipeline -> Store -> Excel -> Report. Includes CLI arguments and scheduling.

**Tech Stack:** Python 3.10+, Scrapling, Pydantic (or Dataclasses), SQLite3, openpyxl, pytest, rapidfuzz, dateutil.

---

### Task 1: Project Skeleton & Configuration

**Files:**
- Create: `requirements.txt`
- Create: `leads_engine/config/scoring_rubric.yaml`
- Create: `leads_engine/config/source_registry.yaml`
- Create: `leads_engine/config/countries.yaml`

**Step 1: Write implementation**

```bash
mkdir -p leads_engine/config tests leads_engine/prompts leads_engine/scripts logs/html_dumps logs/runs leads_engine/models leads_engine/db leads_engine/logging leads_engine/llm leads_engine/pipeline leads_engine/scrapers leads_engine/utils leads_engine/output
```

```text
# requirements.txt
scrapling
openpyxl
rapidfuzz
python-dateutil
pyyaml
pytest
pytest-asyncio
```

```yaml
# leads_engine/config/scoring_rubric.yaml
active_hiring: 30
recent_funding: 25
direct_project: 35
adjacent_hiring: 15
immediate: 1.5
short_term: 1.0
exploratory: 0.5
service_match_threshold_a_plus: 0.8
service_match_threshold_a: 0.5
service_match_threshold_b: 0.3
mena_bonus: 10
europe_bonus: 5
```

```yaml
# leads_engine/config/source_registry.yaml
linkedin_jobs:
  session_type: stealthy_async
  max_pages: 2
  stealthy_opts:
    solve_cloudflare: false
    hide_canvas: true
    block_webrtc: true
    google_search: true
    headless: true
    disable_resources: true
    network_idle: true
    timeout: 60000
  delay_range: [3, 8]
  max_pages_per_query: 3
  circuit_breaker_threshold: 5
  adaptive_tracking: true
upwork:
  session_type: stealthy_async
  max_pages: 1
  stealthy_opts:
    solve_cloudflare: true
    hide_canvas: true
    block_webrtc: true
    google_search: true
    headless: true
    disable_resources: true
    network_idle: true
    timeout: 60000
  delay_range: [5, 12]
  max_pages_per_query: 2
  circuit_breaker_threshold: 3
  adaptive_tracking: true
artstation:
  session_type: dynamic_async
  max_pages: 3
  dynamic_opts:
    headless: true
    disable_resources: true
    network_idle: true
    timeout: 30000
  delay_range: [1, 3]
  max_pages_per_query: 5
  circuit_breaker_threshold: 5
  adaptive_tracking: true
wamda:
  session_type: stealthy_async
  max_pages: 2
  stealthy_opts:
    solve_cloudflare: false
    hide_canvas: false
    google_search: true
    headless: true
    disable_resources: true
    network_idle: true
    timeout: 40000
  delay_range: [2, 5]
  max_pages_per_query: 3
  circuit_breaker_threshold: 3
  adaptive_tracking: false
producthunt:
  session_type: stealthy_async
  max_pages: 2
  stealthy_opts:
    solve_cloudflare: false
    headless: true
    timeout: 30000
  delay_range: [2, 6]
  max_pages_per_query: 2
  circuit_breaker_threshold: 3
  adaptive_tracking: true
crunchbase:
  session_type: stealthy_async
  max_pages: 1
  stealthy_opts:
    solve_cloudflare: true
    headless: true
    timeout: 45000
  delay_range: [5, 10]
  max_pages_per_query: 1
  circuit_breaker_threshold: 2
  adaptive_tracking: true
```

```yaml
# leads_engine/config/countries.yaml
United Arab Emirates:
  - uae
  - dubai
  - abu dhabi
  - sharjah
Saudi Arabia:
  - ksa
  - riyadh
  - jeddah
  - saudi
United States:
  - usa
  - united states
  - ny
  - ca
```

**Step 2: Commit**

```bash
git add requirements.txt leads_engine/config
git commit -m "feat: initial project skeleton, requirements, and full configuration YAMLs"
```

---

### Task 2: Data Models (Dataclasses)

**Files:**
- Create: `leads_engine/models/lead.py`
- Create: `leads_engine/models/enums.py`

**Step 1: Write implementation**

```python
# leads_engine/models/enums.py
from enum import Enum

class Priority(str, Enum):
    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"

class Status(str, Enum):
    NEW = "new"
    RESEARCHING = "researching"
    CONTACTED = "contacted"
    REPLIED = "replied"
    CONVERTED = "converted"
    DEAD = "dead"
```

```python
# leads_engine/models/lead.py
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class RawLead:
    source: str
    company: Optional[str] = None
    title: Optional[str] = None
    location_raw: Optional[str] = None
    url: Optional[str] = None
    posted_raw: Optional[str] = None
    description: Optional[str] = None
    budget_raw: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def is_valid_for_enrichment(self) -> tuple[bool, str]:
        if not self.company and not self.title:
            return False, "NO_IDENTIFIABLE_ENTITY"
        if self.url and not self.url.startswith("http"):
            return False, "INVALID_URL"
        return True, "OK"

@dataclass
class ExtractedLead(RawLead):
    company_clean: str = ""
    country: str = "Unknown"
    city: str = "Unknown"
    posted_date: str = "Unknown"
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None

@dataclass
class EnrichedLead(ExtractedLead):
    industry: str = "Unknown"
    estimated_size: str = "Unknown"
    service_match: str = "Unknown"
    service_match_score: float = 0.0
    demand_urgency: str = "exploratory"
    reasoning: str = ""

@dataclass
class Lead(EnrichedLead):
    lead_id: str = ""
    priority: str = ""
    score_raw: float = 0.0
    status: str = "new"
    overall_confidence: float = 1.0
    validation_issues: List[str] = field(default_factory=list)
    first_seen: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    run_id: str = ""
```

**Step 2: Commit**

```bash
git add leads_engine/models
git commit -m "feat: complete data models and enums"
```