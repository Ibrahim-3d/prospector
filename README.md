# Prospector

An open-source lead generation engine that scrapes job boards, funding news, and freelance platforms to surface companies actively hiring or buying services. Configure it for any industry, role, or region — then let it run.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB.svg)](https://react.dev)

## Features

- Scrapes LinkedIn Jobs, Upwork, ArtStation, and Wamda out of the box — pluggable architecture for adding more
- Config-driven defaults: set job titles, per-source queries, and target regions once in Settings — they auto-fill on every scrape and persist across sessions
- Optional LLM enrichment via local Gemini CLI — cleans company names, infers location, scores priority (A+ / A / B)
- Absolute deduplication across all sources and the master tracker
- Real-time WebSocket progress, paginated lead browser, CSV/Excel export, bulk operations, tagging
- Webhook notifications on job completion or new leads
- Two modes: a headless CLI for bulk runs and a full web dashboard for interactive use

## Installation

```sh
git clone https://github.com/Ibrahim-3d/prospector.git
cd prospector

pip install -r requirements.txt
cd frontend && npm install && cd ..
```

[Scrapling](https://github.com/D4Vinci/Scrapling) must be installed separately — it powers all browser automation. Follow the instructions in their repo to install it for your platform.

## Usage

Start the dashboard (recommended):

```sh
python run.py                    # API on http://localhost:8000
cd frontend && npm run dev       # UI  on http://localhost:5173
```

Or run headless from the CLI against an Excel strategy file:

```sh
python main.py
```

The dashboard gives you four pages:

- **Dashboard** — lead stats, source breakdown, priority distribution, trend charts
- **Leads** — filterable, sortable, paginated table with inline editing, bulk actions, and export
- **Scrape Control** — pick a source, review pre-filled queries/regions from config, launch a job, watch progress live
- **Settings** — all configuration in one place (details below)

## Configuration

Everything lives in `data/config.json`, editable from the Settings page or the API. Here's what you can set:

```json
{
  "job_titles": ["Software Engineer", "Product Designer", "Data Analyst"],
  "search_queries": {
    "linkedin": ["Software Engineer OR Backend Developer", "Product Designer"],
    "upwork": ["web-development", "data-analysis", "ui-ux-design"],
    "artstation": [],
    "wamda": []
  },
  "regions": ["United Arab Emirates", "London", "Berlin", "Remote"],
  "enabled_sources": ["linkedin", "upwork", "artstation", "wamda"],
  "default_page_limit": 3,
  "request_delay": 2.0,
  "gemini_command": "gemini",
  "webhook_url": null,
  "webhook_on_job_complete": false,
  "webhook_on_new_leads": false
}
```

When you launch a scrape, the dashboard pre-fills queries and regions from this config. You can adjust per-run without changing the saved defaults.

## Adding a New Source

1. Create a scraper class that implements the base interface in `backend/scrapers/`
2. Register it in `backend/scrapers/registry.py`
3. Add its slug to the `search_queries` dict in config if it uses queries

The registry auto-discovers your scraper and exposes it in the dashboard.

## Supported Sources

| Source | Signal | Method |
|---|---|---|
| LinkedIn Jobs | Active hiring — job postings across regions | `StealthyFetcher` (anti-detection) |
| Upwork | Active buying — freelance project listings | `StealthyFetcher` + Cloudflare bypass |
| ArtStation Jobs | Studio hiring — creative industry boards | `DynamicFetcher` (JS rendering) |
| Wamda | Startup funding — Seed/Series A news (MENA) | `DynamicFetcher` (JS rendering) |

All fetchers are powered by [Scrapling](https://github.com/D4Vinci/Scrapling), which provides three tiers: static (`Fetcher`), dynamic (`DynamicFetcher` for JS-rendered pages), and stealth (`StealthyFetcher` for bot-protected sites).

## API

The backend exposes a full REST API with interactive docs at [`/docs`](http://localhost:8000/docs) when running. Key endpoints:

```
GET    /api/leads           Paginated, filterable lead list
POST   /api/leads           Create a lead manually
POST   /api/scrape          Launch a scrape job
GET    /api/scrape/jobs     List recent jobs with progress
GET    /api/stats           Dashboard statistics
GET    /api/config          Current config
PUT    /api/config          Update config
GET    /api/leads/export    Export as CSV or Excel
POST   /api/leads/import    Import from CSV
```

## Project Structure

```
prospector/
├── main.py                     CLI orchestrator (Excel-driven)
├── run.py                      Dashboard server (FastAPI + uvicorn)
├── backend/
│   ├── app.py                  FastAPI app with WebSocket broadcast
│   ├── api/                    Routes and Pydantic schemas
│   ├── core/                   Config, database session
│   ├── models/                 Lead, ScrapeJob, Source (SQLAlchemy)
│   ├── services/               Business logic
│   └── scrapers/               Backend scraper wrappers + registry
├── scrapers/                   CLI scraper modules
│   ├── strategy_loader.py      Excel strategy parser
│   ├── llm_enricher.py         Gemini CLI integration
│   └── utils.py                Deduplication, I/O, backups
├── frontend/                   React + Vite + Tailwind
│   └── src/pages/              Dashboard, Leads, ScrapeControl, Settings
├── data/                       config.json, leads.db
└── outputs/json/               Timestamped lead backups
```

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide
- **Scraping**: [Scrapling](https://github.com/D4Vinci/Scrapling) by [Karim Shoair](https://github.com/D4Vinci) — undetectable browser automation with static, dynamic, and stealth fetchers
- **LLM**: Local Gemini CLI (optional, for data enrichment and priority scoring)
- **Database**: SQLite (zero-config)

## Acknowledgments

This project is built on [**Scrapling**](https://github.com/D4Vinci/Scrapling) by [Karim Shoair (D4Vinci)](https://github.com/D4Vinci) — a high-performance, undetectable Python web scraping library. All browser automation in Prospector runs through Scrapling's fetcher system. Check out their repo for documentation and contribution.

## Contributing

Pull requests welcome. For major changes, open an issue first to discuss the approach.

## License

[MIT](LICENSE)
