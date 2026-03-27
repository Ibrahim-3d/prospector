"""Scrape orchestration — runs scraper jobs and persists results."""

import asyncio
import logging
import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.core.config import BACKUP_DIR
from backend.models.scrape_job import ScrapeJob, JobStatus
from backend.models.source import Source
from backend.scrapers.registry import get_scraper
from backend.scrapers.base import ScrapeProgress
from backend.services.lead_service import add_lead

logger = logging.getLogger(__name__)

# Active jobs tracking (job_id -> asyncio.Task)
_active_jobs: dict[int, asyncio.Task] = {}

# Progress broadcast callback (set by WebSocket manager)
_progress_callback = None


def set_progress_callback(callback):
    global _progress_callback
    _progress_callback = callback


async def run_scrape_job(job_id: int):
    """Execute a scrape job asynchronously."""
    db = SessionLocal()
    try:
        job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        if not job:
            logger.error("Job %d not found", job_id)
            return

        # Update status to running
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)
        job.progress = 0
        job.progress_message = "Starting..."
        db.commit()

        _broadcast_progress(job)

        # Get scraper instance
        source = db.query(Source).filter(Source.id == job.source_id).first()
        config = {**(source.default_config or {}), **(job.config or {})}
        scraper = get_scraper(source.slug, config=config)

        filters = job.filters or {}
        queries = filters.get("queries", []) or [job.query] if job.query else []
        regions = job.regions or []
        page_limit = filters.get("page_limit", 3)
        use_llm = filters.get("use_llm", True)

        total_found = 0
        new_leads = 0
        duplicates = 0
        errors = 0
        error_messages = []
        results_for_backup = []

        def on_progress(prog: ScrapeProgress):
            nonlocal job
            job.progress = prog.percent
            job.progress_message = prog.message
            db.commit()
            _broadcast_progress(job)

        try:
            async for result in scraper.scrape(
                queries=queries,
                regions=regions,
                filters=filters,
                page_limit=page_limit,
                use_llm=use_llm,
                on_progress=on_progress,
            ):
                total_found += 1

                lead_data = {
                    "company": result.company,
                    "lead_type": result.lead_type,
                    "country": result.country,
                    "city": result.city,
                    "region": result.region,
                    "category": result.category,
                    "priority": result.priority,
                    "source_id": source.id,
                    "source_name": source.name,
                    "scrape_job_id": job.id,
                    "job_title": result.job_title,
                    "job_url": result.job_url,
                    "job_posted_date": result.job_posted_date,
                    "demand_signal": result.demand_signal,
                    "service_needed": result.service_needed,
                    "website": result.website,
                    "budget": result.budget,
                    "project_type": result.project_type,
                    "duration": result.duration,
                    "experience_level": result.experience_level,
                    "skills": result.skills,
                    "description": result.description,
                    "notes": result.notes,
                    "score": result.score,
                }

                lead = add_lead(db, lead_data)
                if lead:
                    new_leads += 1
                    results_for_backup.append(lead_data)
                else:
                    duplicates += 1

                # Commit in batches of 10
                if total_found % 10 == 0:
                    db.commit()

        except Exception as e:
            errors += 1
            error_messages.append(str(e))
            logger.error("Scraper error in job %d: %s", job_id, e)

        # Final commit
        db.commit()

        # Save JSON backup
        _save_backup(source.slug, results_for_backup)

        # Update source stats
        source.total_leads = (source.total_leads or 0) + new_leads
        source.last_scraped_at = datetime.now(timezone.utc)

        # Finalize job
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        job.total_found = total_found
        job.new_leads = new_leads
        job.duplicates_skipped = duplicates
        job.errors = errors
        job.error_log = "\n".join(error_messages)
        job.progress = 100
        job.progress_message = f"Done: {new_leads} new leads ({duplicates} duplicates skipped)"
        if job.started_at:
            job.duration_seconds = (job.completed_at - job.started_at).total_seconds()
        db.commit()

        # Fire webhook if configured
        from backend.core.config import load_config
        cfg = load_config()
        if cfg.webhook_on_job_complete and cfg.webhook_url:
            await _trigger_webhook(cfg.webhook_url, {
                "event": "job_completed",
                "job_id": job.id,
                "source": job.source_name,
                "new_leads": job.new_leads,
                "total_found": job.leads_found,
                "status": "completed",
            })

        _broadcast_progress(job)
        logger.info(
            "Job %d completed: %d found, %d new, %d dupes, %d errors",
            job_id, total_found, new_leads, duplicates, errors,
        )

    except Exception as e:
        logger.error("Job %d failed: %s", job_id, e)
        try:
            job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
            if job:
                job.status = JobStatus.FAILED
                job.error_log = str(e)
                job.completed_at = datetime.now(timezone.utc)
                job.progress_message = f"Failed: {e}"
                db.commit()
                _broadcast_progress(job)
        except Exception:
            pass
    finally:
        db.close()
        _active_jobs.pop(job_id, None)


def start_job(db: Session, source_slug: str, request_data: dict) -> ScrapeJob:
    """Create and start a scrape job."""
    source = db.query(Source).filter(Source.slug == source_slug).first()
    if not source:
        raise ValueError(f"Source not found: {source_slug}")

    job = ScrapeJob(
        source_id=source.id,
        source_name=source.name,
        status=JobStatus.PENDING,
        query=", ".join(request_data.get("queries", [])),
        regions=request_data.get("regions", []),
        filters={
            "queries": request_data.get("queries", []),
            "job_titles": request_data.get("job_titles", []),
            "keywords": request_data.get("keywords", []),
            "page_limit": request_data.get("page_limit", 3),
            "use_llm": request_data.get("use_llm", True),
        },
        config=request_data.get("config", {}),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Launch async task
    task = asyncio.create_task(run_scrape_job(job.id))
    _active_jobs[job.id] = task

    return job


def cancel_job(job_id: int) -> bool:
    """Cancel a running job."""
    task = _active_jobs.get(job_id)
    if task and not task.done():
        task.cancel()
        db = SessionLocal()
        try:
            job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
            if job:
                job.status = JobStatus.CANCELLED
                job.completed_at = datetime.now(timezone.utc)
                job.progress_message = "Cancelled by user"
                db.commit()
        finally:
            db.close()
        return True
    return False


def _save_backup(source_slug: str, leads: list[dict]):
    """Save leads to timestamped JSON backup."""
    if not leads:
        return
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = BACKUP_DIR / f"leads_{source_slug}_{ts}.json"
    with open(path, "w") as f:
        json.dump(leads, f, indent=2, default=str)


async def _trigger_webhook(webhook_url: str, payload: dict):
    """Fire-and-forget webhook notification."""
    import asyncio, json, urllib.request

    def _send():
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            webhook_url, data=data,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            logging.getLogger(__name__).warning("Webhook failed: %s", e)

    await asyncio.to_thread(_send)


def _broadcast_progress(job: ScrapeJob):
    """Send progress update via WebSocket."""
    if _progress_callback:
        try:
            _progress_callback({
                "job_id": job.id,
                "source_name": job.source_name,
                "status": job.status.value if hasattr(job.status, "value") else str(job.status),
                "progress": job.progress,
                "message": job.progress_message,
                "total_found": job.total_found,
                "new_leads": job.new_leads,
                "duplicates_skipped": job.duplicates_skipped,
            })
        except Exception as e:
            logger.warning("Progress broadcast failed: %s", e)
