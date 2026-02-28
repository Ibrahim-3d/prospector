# Claude — Project Instructions: Companies Data Scraping

## Master Automation Suite

The project is fully automated via a modular suite and a central command center.

### Running the Suite:
```bash
python main.py
```

### Clean Architecture:
- `main.py` — **The Command Center**. One-button trigger for all scrapers.
- `scrapers/` — Modular Python scrapers for specific platforms.
- `scrapers/utils.py` — Shared utilities for Excel interaction, **JSON history**, and **deduplication**.
- `outputs/json/` — Every run creates timestamped JSON backups of new leads.
- `logs/` — Centralized debug text files for troubleshooting scrapes.
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
- **ArtStation Jobs** — Studio hiring signals.
- **LinkedIn Jobs** — 14-30+ day old 3D/Motion roles in UAE.
- **Wamda (MENA)** — Recent funding news for MENA startups.
- **Crunchbase** — Seed/Series A funded startups.

---

## Data Management
- **Central Tracker**: `ibrahim_guerrilla_targeting_v2.xlsx` -> `📋 Company Tracker`
- **Deduplication**: `utils.py` ensures no duplicate company/job entries.
- **Historical Backups**: Every source run results in a timestamped `.json` file in `outputs/json/`.

---

## Workflow

1. Run `python main.py` to trigger all enabled modules.
2. Review the `📋 Company Tracker` sheet.
3. Check the `outputs/json/` folder for the latest raw data.
4. Execute the Outreach Strategy from the Strategy sheet.

---

## Known Blocked/Tricky Sites

- `linkedin.com` — use `StealthyFetcher` + `wait`
- `producthunt.com` — use `StealthyFetcher`
- `clutch.co` — verify paths periodically
