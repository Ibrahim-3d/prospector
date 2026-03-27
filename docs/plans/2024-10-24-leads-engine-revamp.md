# Leads Engine Revamp Implementation Plan (Master Index)

**Goal:** Completely rebuild the Viral X leads engine into a robust, contract-driven architecture using SQLite as the source of truth, a multi-pass Gemini LLM pipeline, and natively leveraging Scrapling's built-in session pooling and adaptive element tracking. 

**Architecture:** 
- **Storage:** SQLite (`leads.db`) with Excel as a rendered view. Includes real entity resolution.
- **Scraping:** Leverage Scrapling's `AsyncStealthySession` and `AsyncDynamicSession`.
- **Pipeline:** Deterministic normalization -> Probabilistic extraction (LLM) -> Probabilistic enrichment (LLM) -> Deterministic validation -> Deterministic scoring.
- **Orchestration:** Load full strategy -> Scrape -> Pipeline -> Store -> Excel -> Report. Includes CLI arguments and scheduling.

**Tech Stack:** Python 3.10+, Scrapling, Pydantic (or Dataclasses), SQLite3, openpyxl, pytest, rapidfuzz, dateutil.

---

This plan has been broken down into smaller, cleaner phases. Please follow these plans in order:

- [Phase 1: Setup & Models](./2024-10-24-leads-engine-revamp-phase-1-setup.md)
  - Task 1: Project Skeleton & Configuration
  - Task 2: Data Models (Dataclasses)

- [Phase 2: Database & Logging](./2024-10-24-leads-engine-revamp-phase-2-db-logging.md)
  - Task 3: SQLite Database Schema & Store Operations
  - Task 4: Logging & Reporting

- [Phase 3: LLM Pipeline](./2024-10-24-leads-engine-revamp-phase-3-llm-pipeline.md)
  - Task 5: LLM Client & Prompts
  - Task 6: Pipeline Implementation (Normalizer, Extractor, Enricher, Scorer)

- [Phase 4: Scrapers](./2024-10-24-leads-engine-revamp-phase-4-scrapers.md)
  - Task 7: Scrapers (Base, Session Factory, and Concrete Implementations)

- [Phase 5: Orchestration & Utilities](./2024-10-24-leads-engine-revamp-phase-5-orchestration.md)
  - Task 8: Utilities (Strategy Loader & Excel Writer)
  - Task 9: Data Migration Script
  - Task 10: Orchestrator `main.py` & CLI arguments
  - Task 11: Windows Task Scheduler Helper
