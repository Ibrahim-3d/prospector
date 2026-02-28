# Claude — Project Instructions: Companies Data Scraping

## Master Automation Suite

The project is fully automated via a modular suite and a central command center, powered by dynamic strategies and local LLM enrichment.

### Running the Suite:
```bash
python main.py
```

### Clean Architecture:
- `main.py` — **The Command Center**. Loads strategy, orchestrates scrapers, generates backups, and updates Excel tracker.
- `scrapers/` — Modular Python scrapers for specific platforms.
  - `strategy_loader.py` — **Dynamic Execution Engine**. Parses the Master Excel sheet for regions and Boolean queries.
  - `llm_enricher.py` — **AI Extraction Layer**. Calls local `gemini` CLI to clean data, extract exact cities/countries, and score lead priority (`A+` or `A`).
  - `utils.py` — Shared utilities for Excel interaction, **JSON history**, and strict **absolute deduplication**.
  - `artstation.py`, `wamda.py`, `linkedin.py`, `upwork.py` — Individual source modules.
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
