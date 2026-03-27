# Claude — Project Instructions: Companies Data Scraping

## Master Automation Suite

The project is fully automated via a modular suite and a central command center, powered by dynamic strategies and local LLM enrichment.

### Running the Suite:
```bash
python main.py
```

### Two Operational Modes:

**CLI Mode** (`python main.py`) — Headless Excel-driven bulk scraping.

**Dashboard Mode** (`python run.py` + `cd frontend && npm run dev`) — FastAPI + React UI.
- API: `http://localhost:8000/api` | Dashboard: `http://localhost:5173` | Docs: `http://localhost:8000/docs`

### Clean Architecture:
- `main.py` — **CLI Orchestrator**. Loads strategy, runs all scrapers, writes to Excel tracker.
- `run.py` — **Dashboard Entry Point**. Starts FastAPI/uvicorn server.
- `scrapers/` — Modular Python scrapers for the CLI pipeline.
  - `strategy_loader.py` — **Dynamic Execution Engine**. Parses Excel `🔎 Query Library` for regions and Boolean queries.
  - `llm_enricher.py` — **AI Extraction Layer**. Calls local `gemini` CLI to clean data, extract cities/countries, and score priority (`A+/A/B`).
  - `utils.py` — Shared utilities for Excel I/O, **JSON history**, and strict **absolute deduplication**.
  - `artstation.py`, `wamda.py`, `linkedin.py`, `upwork.py` — Individual source modules.
- `backend/` — FastAPI app for dashboard mode.
  - `app.py` — FastAPI app with WebSocket broadcast for live scrape progress.
  - `api/routes.py` — REST endpoints.
  - `core/` — Config, SQLAlchemy database session.
  - `models/` — Lead, ScrapeJob, Source ORM models.
  - `services/` — Scrape service, lead service, seeding.
  - `scrapers/` — Backend-side scraper wrappers with registry.
- `frontend/` — React + Vite + Tailwind dashboard.
  - `pages/Dashboard.jsx` — Stats and charts.
  - `pages/LeadsTable.jsx` — Paginated lead browser.
  - `pages/ScrapeControl.jsx` — Trigger scrape jobs.
  - `pages/Settings.jsx` — Source configuration.
- `outputs/json/` — Every run creates timestamped JSON backups of new leads.
- `logs/` — Centralized debug HTML files for troubleshooting scrapes.
- `archive/` — Historical scripts and experimental agents.

---

## Scrapling Toolbox (v0.4.1)

| Tool | Usage |
|-----------|---------------|
| `Fetcher.get()` | Static sites / Directories |
| `DynamicFetcher.fetch()` | JS-rendered boards (ArtStation, Wamda) |
| `StealthyFetcher.fetch()` | Protected sites (LinkedIn, Upwork, Product Hunt) |

---

## Target Sources (Priority Order)

### Priority A+ (High Desperation / High Budget)
- **LinkedIn Jobs** — Mass-executed across multiple regions (MENA, Europe, etc) natively from the Strategy Query Library.
- **Wamda (MENA)** — Recent funding news (Startups raising Seed/Series A).
- **Upwork** — Direct project posts (3D, Animation, DOOH, WebGL).
- **ArtStation Jobs** — Active studio hiring.

---

## Data Management
- **Central Tracker**: `ibrahim_guerrilla_targeting_v2.xlsx` -> `📋 Company Tracker`
- **Deduplication**: `utils.py` ensures absolutely no duplicate company/job entries by verifying both the individual module sheet and the master `📋 Company Tracker`.
- **Historical Backups**: Every source run results in a timestamped `.json` file in `outputs/json/`.
- **LLM Enrichment**: The `parse_with_gemini` layer strictly returns JSON payloads to map correctly to the tracker logic.

---

## Workflow

1. Update `ibrahim_guerrilla_targeting_v2.xlsx` with new queries/regions if desired.
2. Run `python main.py` to trigger all enabled modules.
3. Review the `📋 Company Tracker` sheet for newly injected and categorized leads.
4. Execute the Outreach Strategy from the Strategy sheet.

---

## Known Blocked/Tricky Sites

- `linkedin.com` — use `StealthyFetcher` without strict wait selectors.
- `upwork.com` — use `StealthyFetcher` with `solve_cloudflare=True`.
- `producthunt.com` — use `StealthyFetcher`
- `clutch.co` — verify paths periodically



## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update tasks/lessons.md with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes -- don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests -- then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

## Task Management

1. Plan First: Write plan to tasks/todo.md with checkable items
2. Verify Plan: Check in before starting implementation
3. Track Progress: Mark items complete as you go
4. Explain Changes: High-level summary at each step
5. Document Results: Add review section to tasks/todo.md
6. Capture Lessons: Update tasks/lessons.md after corrections

## Core Principles

- Simplicity First: Make every change as simple as possible. Impact minimal code.
- No Laziness: Find root causes. No temporary fixes. Senior developer standards.
- Minimal Impact: Only touch what's necessary. No side effects with new bugs.
