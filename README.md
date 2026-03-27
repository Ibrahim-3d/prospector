# Prospector

**Open-source lead generation engine** — scrape job boards, funding news, and freelance platforms to find companies that need your services. Configurable for any industry, any role, any region.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB.svg)](https://react.dev)

---

## What It Does

Prospector monitors multiple sources for hiring signals — job postings, startup funding rounds, freelance project listings — and turns them into a structured, deduplicated lead database. It works in two modes:

- **CLI Mode** — headless, Excel-driven bulk scraping for power users
- **Dashboard Mode** — a web UI (FastAPI + React) for visual control, live progress, and lead management

All search preferences (job titles, queries, regions, sources) are **configurable once** in Settings and persist across sessions, but can be overridden per-run.

---

## Features

- **Multi-source scraping** — LinkedIn Jobs, Upwork, ArtStation, Wamda (MENA funding news), with a pluggable scraper architecture for adding more
- **Config-driven search** — set your target job titles, boolean queries per source, and regions once; they auto-fill on every scrape
- **LLM enrichment** — optional local Gemini CLI integration to extract cities, countries, clean company names, and score lead priority (A+ / A / B)
- **Absolute deduplication** — no duplicate leads, ever, verified against both per-source and master trackers
- **Real-time dashboard** — WebSocket-powered live progress, paginated lead browser, CSV/Excel export, bulk actions, tagging
- **Webhook notifications** — get notified when scrape jobs complete or new leads are found
- **Timestamped backups** — every run creates a JSON snapshot in `outputs/json/`

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- [Scrapling](https://github.com/D4Vinci/Scrapling) (web scraping library)

### Install

```bash
git clone https://github.com/Ibrahim-3d/prospector.git
cd prospector

# Backend
pip install -r requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### Run — Dashboard Mode (recommended)

```bash
python run.py                    # API server on http://localhost:8000
cd frontend && npm run dev       # Dashboard on http://localhost:5173
```

- **Dashboard**: [http://localhost:5173](http://localhost:5173)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **WebSocket**: `ws://localhost:8000/ws`

### Run — CLI Mode (headless)

```bash
python main.py
```

Reads queries and regions from your Excel strategy file, runs all scrapers, enriches via LLM, and writes leads back to the tracker.

---

## Configuration

All preferences are stored in `data/config.json` and editable from the **Settings** page:

| Setting | Description |
|---|---|
| **Job Titles** | Target roles across all sources (e.g. "Software Engineer", "Product Designer") |
| **Search Queries** | Per-source queries — boolean strings for LinkedIn, skill slugs for Upwork, etc. |
| **Regions** | Target locations (cities, countries, "Remote") |
| **Enabled Sources** | Which scrapers are active |
| **LLM Enrichment** | Gemini CLI path and timeout |
| **Scraping Behavior** | Request delay, page limit, retries |
| **Webhooks** | Notification URL and triggers |

When you launch a scrape from the dashboard, your saved config **auto-fills** the queries and regions — you can still adjust per-run.

---

## Architecture

```
prospector/
├── main.py                  # CLI orchestrator
├── run.py                   # Dashboard server (FastAPI + uvicorn)
├── backend/
│   ├── app.py               # FastAPI app, WebSocket broadcast
│   ├── api/
│   │   ├── routes.py        # REST API endpoints
│   │   └── schemas.py       # Pydantic request/response models
│   ├── core/
│   │   ├── config.py        # AppConfig model, persistence
│   │   └── database.py      # SQLAlchemy session
│   ├── models/              # Lead, ScrapeJob, Source ORM models
│   ├── services/            # Business logic (scrape, leads, seeding)
│   └── scrapers/            # Backend scraper wrappers + registry
├── scrapers/                # CLI-side scraper modules
│   ├── strategy_loader.py   # Reads queries/regions from Excel
│   ├── llm_enricher.py      # Local Gemini CLI integration
│   ├── utils.py             # Excel I/O, JSON backups, deduplication
│   ├── linkedin.py
│   ├── upwork.py
│   ├── artstation.py
│   └── wamda.py
├── frontend/                # React + Vite + Tailwind dashboard
│   └── src/pages/
│       ├── Dashboard.jsx    # Stats and charts
│       ├── LeadsTable.jsx   # Paginated lead browser
│       ├── ScrapeControl.jsx # Launch and monitor scrapes
│       └── Settings.jsx     # All configuration
├── data/                    # config.json, SQLite database
├── outputs/json/            # Timestamped JSON backups
└── logs/                    # Debug HTML snapshots
```

---

## Supported Sources

| Source | Type | Scraping Method |
|---|---|---|
| **LinkedIn Jobs** | Job postings | `StealthyFetcher` — multi-region, boolean queries |
| **Upwork** | Freelance projects | `StealthyFetcher` with Cloudflare bypass |
| **ArtStation Jobs** | Studio hiring | `DynamicFetcher` — JS-rendered boards |
| **Wamda** | Startup funding (MENA) | `DynamicFetcher` — Seed/Series A news |

Adding a new source? Implement the base scraper interface and register it in `backend/scrapers/registry.py`.

---

## API

Full OpenAPI docs at `/docs` when running. Key endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/leads` | List leads (paginated, filterable) |
| `POST` | `/api/scrape` | Launch a scrape job |
| `GET` | `/api/stats` | Dashboard statistics |
| `GET` | `/api/config` | Get current config |
| `PUT` | `/api/config` | Update config |
| `GET` | `/api/leads/export` | Export as CSV or Excel |
| `POST` | `/api/leads/import` | Import from CSV |

---

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic, uvicorn
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide icons
- **Scraping**: [Scrapling](https://github.com/D4Vinci/Scrapling) — undetectable web scraping with static, dynamic, and stealth fetchers
- **LLM**: Local Gemini CLI for data enrichment (optional)
- **Database**: SQLite (zero-config, file-based)

---

## Acknowledgments

- **[Scrapling](https://github.com/D4Vinci/Scrapling)** by [Karim Shoair (D4Vinci)](https://github.com/D4Vinci) — the web scraping engine powering all fetchers in this project. Scrapling provides undetectable, high-performance browser automation with static, dynamic, and stealth modes. MIT licensed.

---

## License

[MIT](LICENSE)

---

## Contributing

Pull requests welcome. For major changes, open an issue first.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Push to the branch
5. Open a pull request
