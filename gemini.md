# Gemini — Project Instructions: Companies Data Scraping

## What This Project Is

Ibrahim's guerrilla client acquisition system for his 3D/CGI/motion design freelance business (Viral X studio, Dubai).
Goal: find companies that need 3D work RIGHT NOW and get in front of them before they post a job or while their job is unfilled.

Strategy file: `ibrahim_guerrilla_targeting_v2.xlsx` sheets(🎯 Strategy Framework,🔎 Query Library (100+).🌍 Regional Discovery)

---

## Automation & Master Suite

The project features a modular **Master Scraping Suite** for one-button operation and organized output.

### Running the Suite
```bash
python main.py
```

### Project Architecture
- `main.py` — **The Command Center**. Orchestrates scrapers, generates backups, and updates Excel.
- `scrapers/` — Modular scraper package.
  - `utils.py` — Centralized Excel/JSON handling and **deduplication**.
  - `artstation.py`, `wamda.py`, `linkedin.py`, `upwork.py` — Individual source modules.
- `outputs/json/` — **Lead History**. Stores timestamped JSON backups of every scrape.
- `logs/` — **Debug Center**. Stores raw text dumps from protected sites (LinkedIn/Crunchbase).
- `archive/` — **Legacy Scripts**. Stores old test versions and single-use agents.

### Deduplication & Data Safety
1. **Deduplication**: The suite cross-references the `📋 Company Tracker` before saving to prevent duplicate leads.
2. **JSON Backups**: Every scrape automatically generates a timestamped JSON file in `outputs/json/` before the Excel update.

---

## Target Sources (Priority Order)

### Priority A+ (Daily)
- **ArtStation Jobs** — Active studio hiring.
- **LinkedIn Jobs** — UAE-based 3D/Motion roles unfilled for 14+ days.
- **Wamda (MENA)** — Recent funding news for startups in UAE/KSA/Egypt.
- **Crunchbase** — Seed/Series A funded startups.

---

## Workflow

1. **Run `python main.py`**: Fetches new leads from all sources.
2. **Check `outputs/json/`**: Verify the latest backup if needed.
3. **Review Excel Tracker**: Focus on "Priority A+" leads first.
4. **Outreach**: Use the `Outreach Templates` sheet to contact decision makers.
5. **Update Status**: Track your pipeline directly in the Excel file.

---

## Scraping Setup (Technical)

Scrapling v0.4.1 is used across all modules.
- **`DynamicFetcher`**: Used for JS-heavy sites like ArtStation and Wamda.
- **`StealthyFetcher`**: Used for high-protection sites like LinkedIn and Upwork.

## MCP Servers
"ScraplingServer": {
  "command": "scrapling",
  "args": [
    "mcp"
  ]
}
