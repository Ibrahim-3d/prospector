# Gemini — Project Instructions: Companies Data Scraping

## What This Project Is

Ibrahim's guerrilla client acquisition system for his 3D/CGI/motion design freelance business (Viral X studio, Dubai).
Goal: find companies that need 3D work RIGHT NOW and get in front of them before they post a job or while their job is unfilled.

Strategy file: `ibrahim_guerrilla_targeting_v2.xlsx` sheets(🎯 Strategy Framework,🔎 Query Library (100+).🌍 Regional Discovery)

---

## Automation & Master Suite

The project features a modular **Master Scraping Suite** for one-button operation and organized output, powered by dynamic strategies and local LLM enrichment.

### Running the Suite
```bash
python main.py
```

### Project Architecture
- `main.py` — **The Command Center**. Loads strategy, orchestrates scrapers, generates backups, and updates Excel.
- `scrapers/` — Modular scraper package.
  - `strategy_loader.py` — **Dynamic Execution Engine**. Parses the Master Excel sheet for regions and Boolean queries.
  - `llm_enricher.py` — **Gemini AI Layer**. Calls local `gemini` CLI to clean data, extract exact cities/countries, and score lead priority.
  - `utils.py` — Centralized Excel/JSON handling and strict cross-platform **deduplication**.
  - `artstation.py`, `wamda.py`, `linkedin.py`, `upwork.py` — Specific platform modules utilizing strategy queries.
- `outputs/json/` — **Lead History**. Stores timestamped JSON backups of every scrape.
- `logs/` — **Debug Center**. Stores raw HTML dumps.
- `archive/` — **Legacy Scripts**.

### Deduplication & Data Safety
1. **Absolute Deduplication**: Filtered against BOTH individual module sheets AND the `📋 Company Tracker` master database to guarantee no redundant leads.
2. **JSON Backups**: Every scrape automatically generates JSON backups.

---

## Target Sources (Priority Order)

### Priority A+ (Daily)
- **LinkedIn Jobs** — Mass-executed across multiple regions (MENA, Europe, etc) natively from the Strategy Query Library.
- **Wamda (MENA)** — Recent funding news (Startups raising Seed/Series A).
- **Upwork** — Direct project posts (3D, Animation, DOOH, WebGL).
- **ArtStation Jobs** — Active studio hiring.

---

## Workflow

1. **Update Strategy Excel**: If you want to search new regions/queries, update `ibrahim_guerrilla_targeting_v2.xlsx`.
2. **Run `python main.py`**: Fetches, LLM enriches, and dedups new leads from all regions.
3. **Review Excel Tracker**: Focus on "Priority A+" leads first.
4. **Outreach**: Target decision makers using customized outreach.

---

## Scraping & LLM Setup (Technical)

- **Scrapling v0.4.1**: Used across modules.
  - `DynamicFetcher` / `StealthyFetcher`: Handle high-protection sites.
- **Local Gemini CLI Engine**: Used as a data extractor. Raw data is parsed via CSS, packed into a prompt, and pushed to `gemini.cmd -p`. The LLM returns a strict JSON payload predicting lead priority and demand context. 

## MCP Servers
"ScraplingServer": {
  "command": "scrapling",
  "args": [
    "mcp"
  ]
}
