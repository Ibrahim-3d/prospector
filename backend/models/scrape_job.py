"""Scrape job model — tracks every scraping run."""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.core.database import Base
import enum


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    source_name = Column(String(100), default="")  # Denormalized

    status = Column(SAEnum(JobStatus), default=JobStatus.PENDING)

    # What was searched
    query = Column(String(500), default="")
    regions = Column(JSON, default=list)  # ["UAE", "Kuwait", ...]
    filters = Column(JSON, default=dict)  # {"job_titles": [...], "keywords": [...]}

    # Config overrides for this run
    config = Column(JSON, default=dict)  # page_limit, etc.

    # Results
    total_found = Column(Integer, default=0)
    new_leads = Column(Integer, default=0)
    duplicates_skipped = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    error_log = Column(Text, default="")

    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, default=0.0)

    # Progress (0-100)
    progress = Column(Integer, default=0)
    progress_message = Column(String(500), default="")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    source_rel = relationship("Source", back_populates="scrape_jobs")
    leads = relationship("Lead", back_populates="scrape_job_rel")

    def __repr__(self):
        return f"<ScrapeJob {self.id} [{self.status}] {self.source_name}>"
