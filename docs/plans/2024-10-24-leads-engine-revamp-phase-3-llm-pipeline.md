# Leads Engine Revamp: Phase 3 (LLM Pipeline)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the Gemini LLM client, data extraction, enrichment, validation, and scoring pipeline.

**Architecture:** 
- **Storage:** SQLite (`leads.db`) with Excel as a rendered view. Includes real entity resolution.
- **Scraping:** Leverage Scrapling's `AsyncStealthySession` and `AsyncDynamicSession`.
- **Pipeline:** Deterministic normalization -> Probabilistic extraction (LLM) -> Probabilistic enrichment (LLM) -> Deterministic validation -> Deterministic scoring.
- **Orchestration:** Load full strategy -> Scrape -> Pipeline -> Store -> Excel -> Report. Includes CLI arguments and scheduling.

**Tech Stack:** Python 3.10+, Scrapling, Pydantic (or Dataclasses), SQLite3, openpyxl, pytest, rapidfuzz, dateutil.

---

### Task 5: LLM Client & Prompts

**Files:**
- Create: `leads_engine/prompts/extraction.v1.txt`
- Create: `leads_engine/prompts/enrichment.v1.txt`
- Create: `leads_engine/llm/contracts.py`
- Create: `leads_engine/llm/gemini_client.py`

**Step 1: Write implementation**

```text
# leads_engine/prompts/extraction.v1.txt
You are a data extraction engine. Parse each entry below into the exact JSON schema.

Entries:
{batch_json}

Return a JSON array of objects, one per entry. Schema per object:
{{
  "id": <entry index>,
  "company_clean": <cleaned company name, no suffixes like Inc/Ltd unless part of brand>,
  "country": <ISO country name or "Unknown">,
  "city": <city name or "Unknown">,
  "posted_date": <ISO 8601 date or "Unknown">,
  "contact_name": <if visible in data, else null>,
  "contact_title": <if visible, else null>
}}

Rules:
- Return ONLY the JSON array. No markdown, no explanation.
- If a field cannot be determined, use "Unknown" for strings, null for optional fields.
- Do NOT invent information. Only extract what is explicitly present.
```

```text
# leads_engine/prompts/enrichment.v1.txt
You are a business intelligence analyst specializing in the creative services industry.

For each company below, provide enrichment based on your knowledge:

{batch_json}

Return a JSON array. Schema per object:
{{
  "id": <entry index>,
  "industry": <primary industry sector>,
  "estimated_size": <"startup" | "small" | "medium" | "enterprise">,
  "service_match": <how relevant is this company to 3D/CGI/motion design services>,
  "service_match_score": <0.0 to 1.0>,
  "demand_urgency": <"immediate" | "short_term" | "exploratory">,
  "reasoning": <1-sentence explanation of your assessment>
}}

Rules:
- service_match_score: 1.0 = explicitly hiring for 3D/CGI. 0.5 = adjacent creative. 0.0 = no relevance.
- demand_urgency: "immediate" = active job post or recent funding. "short_term" = likely to need soon. "exploratory" = speculative.
- If you don't recognize the company, base assessment purely on the job title and description provided.
- Do NOT hallucinate company details you don't know. Use the data provided.
```

```python
# leads_engine/llm/contracts.py
import json

def attempt_json_parse(raw_output: str) -> dict | list | None:
    try:
        raw_output = raw_output.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.startswith("```"):
            raw_output = raw_output[3:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]
        return json.loads(raw_output.strip())
    except json.JSONDecodeError:
        return None
```

```python
# leads_engine/llm/gemini_client.py
import subprocess
from leads_engine.logging.logger import get_logger
from leads_engine.llm.contracts import attempt_json_parse

logger = get_logger(__name__)

def invoke_gemini_cli(prompt: str, timeout: int = 30) -> str:
    """Raw wrapper to call local gemini CLI."""
    try:
        result = subprocess.run(
            ["gemini", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        logger.warning("LLM_TIMEOUT: Gemini call timed out")
        return ""
    except subprocess.CalledProcessError as e:
        logger.error(f"LLM_ERROR: Gemini CLI failed with code {e.returncode}")
        return ""

def call_gemini_with_contract(prompt: str, max_retries: int = 3, timeout: int = 30) -> tuple[dict | list | None, float]:
    for attempt in range(max_retries):
        raw_output = invoke_gemini_cli(prompt, timeout)
        parsed = attempt_json_parse(raw_output)

        if parsed is not None:
            return parsed, 1.0 - (attempt * 0.1)

        if attempt < max_retries - 1:
            logger.warning(f"LLM_MALFORMED: Attempt {attempt+1} failed to return valid JSON. Retrying.")
            prompt += "

Your previous response was not valid JSON. You MUST return ONLY valid JSON."

    logger.error("LLM_FAIL: Exhausted retries for valid JSON.")
    return None, 0.0
```

**Step 2: Commit**

```bash
git add leads_engine/prompts leads_engine/llm
git commit -m "feat: implement LLM pipeline prompts, contracts, and retry-aware client"
```

---

### Task 6: Pipeline Implementation (Normalizer, Extractor, Enricher, Scorer)

**Files:**
- Create: `leads_engine/pipeline/normalizer.py`
- Create: `leads_engine/pipeline/extractor.py`
- Create: `leads_engine/pipeline/enricher.py`
- Create: `leads_engine/pipeline/validator.py`
- Create: `leads_engine/pipeline/scorer.py`

**Step 1: Write implementation**

```python
# leads_engine/pipeline/normalizer.py
import urllib.parse
import yaml
from dateutil import parser
from leads_engine.models.lead import RawLead
from leads_engine.logging.logger import get_logger

logger = get_logger(__name__)

def load_countries():
    with open("leads_engine/config/countries.yaml", "r") as f:
        return yaml.safe_load(f)

def normalize_url(url: str) -> str:
    if not url: return ""
    parsed = urllib.parse.urlparse(url)
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

def normalize_location(loc: str) -> str:
    if not loc: return ""
    loc_lower = loc.lower()
    countries = load_countries()
    for country, aliases in countries.items():
        if any(a in loc_lower for a in aliases):
            return country
    return loc

def normalize_date(date_str: str) -> str:
    if not date_str: return ""
    try:
        dt = parser.parse(date_str, fuzzy=True)
        return dt.isoformat()
    except:
        return date_str

def normalize_lead_data(lead: RawLead) -> RawLead:
    if lead.url: lead.url = normalize_url(lead.url)
    if lead.company: lead.company = lead.company.strip()
    if lead.location_raw: lead.location_raw = normalize_location(lead.location_raw)
    if lead.posted_raw: lead.posted_raw = normalize_date(lead.posted_raw)
    return lead
```

```python
# leads_engine/pipeline/extractor.py
import json
from leads_engine.models.lead import RawLead, ExtractedLead
from leads_engine.llm.gemini_client import call_gemini_with_contract

def extract_fields(leads: list[RawLead]) -> list[ExtractedLead]:
    if not leads: return []
    with open("leads_engine/prompts/extraction.v1.txt", "r") as f:
        prompt_tmpl = f.read()
    
    batch_json = json.dumps([{"id": i, "company": l.company, "title": l.title, "location": l.location_raw} for i, l in enumerate(leads)])
    prompt = prompt_tmpl.replace("{batch_json}", batch_json)
    
    parsed, conf = call_gemini_with_contract(prompt)
    if parsed is None: parsed = []
    
    results = []
    for i, lead in enumerate(leads):
        match = next((p for p in parsed if isinstance(p, dict) and p.get("id") == i), {})
        extracted = ExtractedLead(**lead.__dict__)
        extracted.company_clean = match.get("company_clean", lead.company or "Unknown")
        extracted.country = match.get("country", "Unknown")
        extracted.city = match.get("city", "Unknown")
        results.append(extracted)
    return results
```

```python
# leads_engine/pipeline/enricher.py
import json
from leads_engine.models.lead import ExtractedLead, EnrichedLead
from leads_engine.llm.gemini_client import call_gemini_with_contract
from leads_engine.logging.logger import get_logger

logger = get_logger(__name__)

def enrich_leads(leads: list[ExtractedLead]) -> list[EnrichedLead]:
    if not leads: return []
    with open("leads_engine/prompts/enrichment.v1.txt", "r") as f:
        prompt_tmpl = f.read()
    
    batch_json = json.dumps([{"id": i, "company": l.company_clean, "title": l.title} for i, l in enumerate(leads)])
    prompt = prompt_tmpl.replace("{batch_json}", batch_json)
    
    parsed, conf = call_gemini_with_contract(prompt)
    
    if parsed and 0.5 <= conf <= 0.8:
        logger.info("Enrichment confidence 0.5-0.8. Retrying with stricter prompt.")
        prompt += "

Please ensure your service match score is highly accurate and conservative."
        parsed_retry, conf_retry = call_gemini_with_contract(prompt, max_retries=1)
        if parsed_retry:
            parsed, conf = parsed_retry, conf_retry
            
    if parsed is None: parsed = []
    
    results = []
    for i, lead in enumerate(leads):
        match = next((p for p in parsed if isinstance(p, dict) and p.get("id") == i), {})
        enriched = EnrichedLead(**lead.__dict__)
        enriched.industry = match.get("industry", "Unknown")
        enriched.estimated_size = match.get("estimated_size", "Unknown")
        try:
            enriched.service_match_score = float(match.get("service_match_score", 0.0))
        except:
            enriched.service_match_score = 0.0
        enriched.demand_urgency = match.get("demand_urgency", "exploratory")
        results.append(enriched)
    return results
```

```python
# leads_engine/pipeline/validator.py
from leads_engine.models.lead import EnrichedLead

def validate_enriched_lead(lead: EnrichedLead) -> tuple[bool, list[str]]:
    issues = []
    if lead.url and lead.country:
        if ".ae" in lead.url and lead.country != "United Arab Emirates":
            issues.append("COUNTRY_URL_MISMATCH")
    
    if not (0 <= lead.service_match_score <= 1):
        issues.append("SCORE_OUT_OF_RANGE")
        
    return len(issues) == 0, issues

def compute_confidence(lead: EnrichedLead, validation_issues: list[str]) -> float:
    score = 1.0
    score -= len(validation_issues) * 0.15
    unknowns = sum(1 for v in lead.__dict__.values() if v in ("Unknown", None, ""))
    score -= unknowns * 0.05
    if lead.demand_urgency == "immediate": score += 0.1
    return max(0.0, min(1.0, score))
```

```python
# leads_engine/pipeline/scorer.py
import yaml
from leads_engine.models.lead import EnrichedLead, Lead
from leads_engine.pipeline.validator import validate_enriched_lead, compute_confidence

def load_rubric():
    with open("leads_engine/config/scoring_rubric.yaml", "r") as f:
        return yaml.safe_load(f)

def score_lead(lead: EnrichedLead) -> Lead:
    rubric = load_rubric()
    base = 0.0
    
    if lead.source == "upwork": base += rubric.get("direct_project", 35)
    elif "hiring" in lead.demand_urgency.lower(): base += rubric.get("active_hiring", 30)
    
    urgency_mult = rubric.get(lead.demand_urgency, 1.0)
    base *= urgency_mult
    base *= lead.service_match_score or 0.5
    
    if base >= 35: prio = "A+"
    elif base >= 20: prio = "A"
    elif base >= 10: prio = "B+"
    else: prio = "B"
    
    is_valid, issues = validate_enriched_lead(lead)
    conf = compute_confidence(lead, issues)

    scored = Lead(**lead.__dict__)
    scored.priority = prio
    scored.score_raw = base
    scored.overall_confidence = conf
    scored.validation_issues = issues
    return scored
```

**Step 2: Commit**

```bash
git add leads_engine/pipeline
git commit -m "feat: completely implement pipeline normalizer, extractor, enricher, validator and scorer"
```