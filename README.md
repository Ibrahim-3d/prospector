<p align="center">
  <h1 align="center">Prospector</h1>
  <p align="center">
    <strong>Find companies that need your services — automatically.</strong>
    <br />
    Prospector scrapes job boards, funding news, and freelance platforms to build you a pipeline of warm leads. Set your target roles, industries, and regions once — then let it run.
  </p>
  <p align="center">
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License" /></a>
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" alt="Python 3.10+" />
    <img src="https://img.shields.io/badge/Self--Hosted-Yes-green.svg" alt="Self Hosted" />
    <img src="https://img.shields.io/badge/Cost-Free-brightgreen.svg" alt="Free" />
  </p>
</p>

<br />

<!--
  Add your own screenshots here! Take a screenshot of each page and save to docs/screenshots/
  Then uncomment these lines:

  <p align="center">
    <img src="docs/screenshots/dashboard.png" width="90%" alt="Dashboard" />
  </p>
-->

## The Problem

You need clients. You spend hours manually checking LinkedIn, Upwork, job boards, and startup news to find companies that might need your services. By the time you find them, compile their info, and reach out — the opportunity is cold.

## The Solution

Prospector does the hunting for you. It continuously scrapes multiple platforms, deduplicates results, enriches leads with AI, and delivers a clean, prioritized list of companies that are **actively spending money** on what you offer.

> **Works for any industry.** Whether you're a freelance designer, a software agency, a marketing consultant, or a 3D studio — just configure your target job titles and regions.

<br />

## How It Works

| Step | What Happens |
|:---:|---|
| **1. Configure** | Tell Prospector what you're looking for — job titles, search queries, and target regions. Do this once in Settings. |
| **2. Scrape** | Hit "Launch" on any source. Prospector searches LinkedIn, Upwork, ArtStation, and Wamda for matching leads. Watch progress in real time. |
| **3. Review** | Browse your leads in a clean table. Filter by source, country, priority, or status. Export to Excel. Start outreach. |

<br />

## What You Get

### A Full Dashboard

| Page | What It Shows |
|---|---|
| **Dashboard** | Total leads, leads this week, breakdown by source, priority distribution, and daily trend charts |
| **Leads** | Searchable, filterable table of every lead — company, job title, location, priority score, status, and more. Edit inline, tag, bulk update, or export to CSV/Excel |
| **Scrape Control** | Pick a source, see your pre-filled search queries and regions, launch a job, and watch live progress with a real-time progress bar |
| **Settings** | Configure everything: target job titles, per-source search queries, regions, enabled sources, AI enrichment, webhooks |

### AI-Powered Lead Scoring

When enabled, Prospector uses a local AI model (Gemini) to automatically:
- Clean and standardize company names
- Extract city and country from messy job descriptions
- Score each lead's priority: **A+** (high urgency), **A** (strong signal), or **B** (worth watching)

### Smart Deduplication

No duplicates, ever. Prospector checks every new lead against all existing leads across all sources before adding it. Your database stays clean no matter how many times you run it.

### Webhook Notifications

Get notified via webhook when a scrape finishes or when new leads are found. Connect it to Slack, email, or any automation tool.

<br />

## Where It Looks

Prospector ships with four built-in sources. More can be added.

| Source | What It Finds | Why It Matters |
|---|---|---|
| **LinkedIn Jobs** | Job postings across any region | Companies posting jobs are actively spending. If they're hiring for a role you can fill or support, that's a warm lead. |
| **Upwork** | Freelance project listings | Direct demand — someone is literally looking to pay for the service you offer. |
| **ArtStation Jobs** | Creative industry job boards | Studios and agencies actively hiring signal growth and budget. |
| **Wamda** | Startup funding news (MENA) | Companies that just raised a Seed or Series A round have money to spend on services. |

<br />

## Quick Setup

You'll need **Python 3.10+** and **Node.js 18+** installed on your computer.

```sh
# 1. Download Prospector
git clone https://github.com/Ibrahim-3d/prospector.git
cd prospector

# 2. Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 3. Start the dashboard
python run.py                    # Starts the backend
cd frontend && npm run dev       # Starts the dashboard
```

Then open **http://localhost:5173** in your browser.

> **Note:** Prospector uses [Scrapling](https://github.com/D4Vinci/Scrapling) for web scraping. You'll need to install it separately — follow the instructions on their repo.

<br />

## Your Settings, Your Rules

Configure once, use forever. All settings persist and auto-fill when you launch scrapes.

| Setting | What It Controls | Example |
|---|---|---|
| **Job Titles** | Roles you're targeting across all platforms | "Product Designer", "Marketing Manager" |
| **Search Queries** | Source-specific search strings | LinkedIn: "UX Designer OR Product Designer" |
| **Regions** | Where to look | "London", "Remote", "UAE" |
| **Enabled Sources** | Which platforms to scrape | LinkedIn + Upwork only |
| **Page Limit** | How deep to scrape per query | 3 pages (about 30-75 results) |
| **AI Enrichment** | Automatic lead scoring and cleanup | On / Off |
| **Webhooks** | Get notified when scrapes finish | Your Slack webhook URL |

<br />

---

<details>
<summary><strong>For Developers</strong> — Architecture, API, and extending Prospector</summary>

<br />

### Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic, uvicorn
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide
- **Scraping**: [Scrapling](https://github.com/D4Vinci/Scrapling) by [Karim Shoair](https://github.com/D4Vinci)
- **LLM**: Local Gemini CLI (optional)
- **Database**: SQLite (zero-config, file-based)

### Project Structure

```
prospector/
├── main.py                     CLI orchestrator (headless mode)
├── run.py                      Dashboard server (FastAPI + uvicorn)
├── backend/
│   ├── app.py                  FastAPI app with WebSocket broadcast
│   ├── api/                    Routes and Pydantic schemas
│   ├── core/                   Config, database session
│   ├── models/                 Lead, ScrapeJob, Source (SQLAlchemy ORM)
│   ├── services/               Business logic layer
│   └── scrapers/               Scraper wrappers + registry
├── scrapers/                   CLI scraper modules
│   ├── strategy_loader.py      Excel strategy parser
│   ├── llm_enricher.py         Gemini CLI integration
│   └── utils.py                Deduplication, I/O, backups
├── frontend/                   React + Vite + Tailwind
│   └── src/pages/              Dashboard, Leads, ScrapeControl, Settings
├── data/                       config.json, leads.db
└── outputs/json/               Timestamped lead backups
```

### API Reference

Full interactive docs at [`localhost:8000/docs`](http://localhost:8000/docs) when running.

```
GET    /api/leads           Paginated, filterable lead list
POST   /api/leads           Create a lead manually
POST   /api/scrape          Launch a scrape job
GET    /api/scrape/jobs     List recent jobs with progress
GET    /api/stats           Dashboard statistics
GET    /api/config          Read config
PUT    /api/config          Update config
GET    /api/leads/export    Export as CSV or Excel
POST   /api/leads/import    Import from CSV
WS     /ws                  Real-time scrape progress
```

### Adding a New Source

1. Create a scraper in `backend/scrapers/` implementing the base interface
2. Register it in `backend/scrapers/registry.py`
3. Add a query list under its slug in `search_queries` config

The registry auto-discovers it and exposes it in the dashboard.

### CLI Mode

For power users who prefer headless operation with an Excel strategy file:

```sh
python main.py
```

Reads queries and regions from your Excel workbook, runs all enabled scrapers, enriches via LLM, and writes results back to the tracker.

</details>

<br />

## Acknowledgments

Built on [**Scrapling**](https://github.com/D4Vinci/Scrapling) by [Karim Shoair (D4Vinci)](https://github.com/D4Vinci) — a high-performance, undetectable Python web scraping library that powers all browser automation in this project. Give their repo a star.

## Contributing

Pull requests welcome. For major changes, open an issue first.

## License

[MIT](LICENSE) — free for personal and commercial use.
