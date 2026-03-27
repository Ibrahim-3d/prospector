# Leads Scraper

A modular B2B lead generation suite targeting studios and agencies in 3D, CGI, motion design, and related fields. Supports two operational modes: a **CLI scraper** for bulk Excel-based targeting, and a **web dashboard** for visual monitoring and control.

---

## Modes

### CLI Mode (Excel-driven, headless)
```bash
python main.py
```
Reads strategy queries and regions from `ibrahim_guerrilla_targeting_v2.xlsx`, runs all scrapers, enriches results via local Gemini LLM, and writes new leads back to the Excel tracker.

### Dashboard Mode (FastAPI + React)
```bash
python run.py          # Start API server (port 8000)
cd frontend && npm run dev   # Start frontend (port 5173)
```
- API:       `http://localhost:8000/api`
- Dashboard: `http://localhost:5173`
- API Docs:  `http://localhost:8000/docs`
- WebSocket: `ws://localhost:8000/ws`

---

## Architecture

```
main.py                        CLI orchestrator
run.py                         Dashboard entry point (uvicorn)
scrapers/
  strategy_loader.py           Reads regions & queries from Excel
  llm_enricher.py              Local Gemini CLI enrichment
  utils.py                     Excel I/O, JSON backups, deduplication
  artstation.py
  linkedin.py
  wamda.py
  upwork.py
backend/
  app.py                       FastAPI app, WebSocket broadcast
  api/routes.py                REST endpoints
  core/config.py, database.py  Settings, SQLAlchemy session
  models/                      Lead, ScrapeJob, Source ORM models
  services/                    Scrape service, lead service, seeding
  scrapers/                    Backend-side scraper wrappers
frontend/
  src/pages/
    Dashboard.jsx              Stats + charts
    LeadsTable.jsx             Paginated lead browser
    ScrapeControl.jsx          Trigger scrape jobs
    Settings.jsx               Source configuration
ibrahim_guerrilla_targeting_v2.xlsx   Master strategy tracker
outputs/json/                  Timestamped JSON backups per run
logs/                          Debug HTML snapshots per scrape
```

---

## Target Sources

| Source | Method | Focus |
|---|---|---|
| LinkedIn Jobs | `StealthyFetcher` | MENA + Europe studios hiring 3D/CGI roles |
| Wamda | `DynamicFetcher` | MENA startups with recent Seed/Series A funding |
| Upwork | `StealthyFetcher` (Cloudflare bypass) | Live 3D, animation, WebGL project posts |
| ArtStation Jobs | `DynamicFetcher` | Active studio job boards |

### Scrapling Toolbox

| Tool | When to use |
|---|---|
| `Fetcher.get()` | Static sites / directories |
| `DynamicFetcher.fetch()` | JS-rendered pages (ArtStation, Wamda) |
| `StealthyFetcher.fetch()` | Bot-protected sites (LinkedIn, Upwork) |

---

## Data Pipeline

1. `strategy_loader.py` pulls regions and Boolean queries from the Excel `🔎 Query Library (100+)` sheet.
2. Each scraper runs and returns raw lead dicts.
3. `llm_enricher.py` calls the local `gemini` CLI to clean company names, infer city/country, and assign `A+/A/B` priority.
4. `utils.py` deduplicates against both the module sheet and the `📋 Company Tracker` master sheet before writing.
5. Every run dumps a timestamped `.json` to `outputs/json/` as a backup.

---

## Requirements

```bash
pip install -r requirements.txt
# requirements.txt includes: fastapi, uvicorn, sqlalchemy, pydantic, openpyxl
# Scrapling is vendored in Scrapling/
```

---

## Known Tricky Sites

| Site | Notes |
|---|---|
| `linkedin.com` | `StealthyFetcher` — no strict wait selectors |
| `upwork.com` | `StealthyFetcher` with `solve_cloudflare=True` |
| `producthunt.com` | `StealthyFetcher` |
| `clutch.co` | Verify DOM paths periodically |
