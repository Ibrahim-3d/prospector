"""Scraping source definitions — the extensible plugin registry."""

from sqlalchemy import Column, Integer, String, Boolean, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.core.database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g. "LinkedIn Jobs"
    slug = Column(String(50), unique=True, nullable=False)  # e.g. "linkedin"
    description = Column(Text, default="")
    base_url = Column(String(500), default="")
    scraper_module = Column(String(100), nullable=False)  # e.g. "linkedin"
    enabled = Column(Boolean, default=True)

    # Default config for this source (selectors, pagination, etc.)
    default_config = Column(JSON, default=dict)

    # Fetcher type: "static", "dynamic", "stealthy"
    fetcher_type = Column(String(20), default="stealthy")

    # Stats
    total_leads = Column(Integer, default=0)
    last_scraped_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    leads = relationship("Lead", back_populates="source_rel")
    scrape_jobs = relationship("ScrapeJob", back_populates="source_rel")

    def __repr__(self):
        return f"<Source {self.name}>"
