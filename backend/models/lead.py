"""Lead model — the core data entity."""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float,
    ForeignKey, Table, Enum as SAEnum, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.core.database import Base
import enum


class Priority(str, enum.Enum):
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"


class LeadStatus(str, enum.Enum):
    NEW = "new"
    RESEARCHING = "researching"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"
    REPLIED = "replied"
    MEETING = "meeting"
    PROPOSAL = "proposal"
    WON = "won"
    LOST = "lost"
    ARCHIVED = "archived"


class LeadType(str, enum.Enum):
    COMPANY = "company"       # Companies hiring (LinkedIn, ArtStation)
    STARTUP = "startup"       # Funded startups (Wamda)
    PROJECT = "project"       # Direct projects (Upwork)


# Many-to-many: leads <-> tags
lead_tags = Table(
    "lead_tags",
    Base.metadata,
    Column("lead_id", Integer, ForeignKey("leads.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(7), default="#6366f1")  # hex color

    leads = relationship("Lead", secondary=lead_tags, back_populates="tags")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Core identity
    company = Column(String(300), nullable=False, index=True)
    company_normalized = Column(String(300), nullable=False, index=True)  # lowered, stripped for dedup
    lead_type = Column(SAEnum(LeadType), default=LeadType.COMPANY)

    # Location
    country = Column(String(100), default="")
    city = Column(String(100), default="")
    region = Column(String(100), default="")  # e.g. "MENA", "Europe"

    # Classification
    category = Column(String(100), default="")  # "Studio/Agency", "Funded Startup", etc.
    priority = Column(SAEnum(Priority), default=Priority.A)
    status = Column(SAEnum(LeadStatus), default=LeadStatus.NEW)
    score = Column(Float, default=0.0)  # Numeric score for ranking (0-100)

    # Source tracking
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    source_name = Column(String(100), default="")  # Denormalized for fast reads
    scrape_job_id = Column(Integer, ForeignKey("scrape_jobs.id"), nullable=True)

    # Job/project details
    job_title = Column(String(500), default="")
    job_url = Column(String(1000), default="")
    job_posted_date = Column(String(100), default="")

    # Demand signal
    demand_signal = Column(Text, default="")
    service_needed = Column(String(300), default="")

    # Contact info
    website = Column(String(500), default="")
    decision_maker_name = Column(String(200), default="")
    decision_maker_title = Column(String(200), default="")
    decision_maker_linkedin = Column(String(500), default="")
    decision_maker_email = Column(String(300), default="")

    # Outreach tracking
    outreach_date = Column(DateTime, nullable=True)
    outreach_channel = Column(String(100), default="")
    response_received = Column(String(50), default="")
    follow_up_date = Column(DateTime, nullable=True)
    revenue_potential = Column(String(100), default="")

    # Upwork-specific (nullable)
    budget = Column(String(100), default="")
    project_type = Column(String(50), default="")  # Fixed/Hourly
    duration = Column(String(100), default="")
    experience_level = Column(String(50), default="")
    skills = Column(Text, default="")
    description = Column(Text, default="")

    # Meta
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    source_rel = relationship("Source", back_populates="leads")
    scrape_job_rel = relationship("ScrapeJob", back_populates="leads")
    tags = relationship("Tag", secondary=lead_tags, back_populates="leads")

    __table_args__ = (
        Index("ix_leads_company_source", "company_normalized", "source_name"),
        Index("ix_leads_priority_status", "priority", "status"),
        Index("ix_leads_country", "country"),
        Index("ix_leads_created", "created_at"),
    )

    def __repr__(self):
        return f"<Lead {self.company} [{self.priority}]>"


# Alias for backwards compatibility
LeadTag = lead_tags
