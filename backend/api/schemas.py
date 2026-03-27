"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Sources ──────────────────────────────────────────────

class SourceOut(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    base_url: str
    enabled: bool
    fetcher_type: str
    total_leads: int
    last_scraped_at: Optional[datetime] = None
    default_config: dict = {}

    model_config = {"from_attributes": True}


class SourceToggle(BaseModel):
    enabled: bool


# ── Leads ────────────────────────────────────────────────

class LeadOut(BaseModel):
    id: int
    company: str
    lead_type: str
    country: str
    city: str
    region: str
    category: str
    priority: str
    status: str
    score: float
    source_name: str
    job_title: str
    job_url: str
    job_posted_date: str
    demand_signal: str
    service_needed: str
    website: str
    decision_maker_name: str
    decision_maker_title: str
    decision_maker_linkedin: str
    decision_maker_email: str
    outreach_date: Optional[datetime] = None
    outreach_channel: str
    follow_up_date: Optional[datetime] = None
    revenue_potential: str
    budget: str
    project_type: str
    duration: str
    experience_level: str
    skills: str
    description: str
    notes: str
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadCreate(BaseModel):
    company: str
    job_title: Optional[str] = None
    source_name: Optional[str] = "manual"
    country: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "new"
    priority: Optional[str] = "B"
    description: Optional[str] = None
    service_needed: Optional[str] = None
    budget: Optional[str] = None
    skills: Optional[str] = None
    demand_signal: Optional[str] = None


class LeadUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    decision_maker_name: Optional[str] = None
    decision_maker_title: Optional[str] = None
    decision_maker_linkedin: Optional[str] = None
    decision_maker_email: Optional[str] = None
    outreach_channel: Optional[str] = None
    revenue_potential: Optional[str] = None
    category: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None
    budget: Optional[str] = None
    skills: Optional[str] = None
    description: Optional[str] = None
    service_needed: Optional[str] = None
    demand_signal: Optional[str] = None


class LeadListResponse(BaseModel):
    leads: list[LeadOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class LeadFilters(BaseModel):
    """Query parameters for filtering leads."""
    source: Optional[str] = None
    source_name: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    country: Optional[str] = None
    lead_type: Optional[str] = None
    search: Optional[str] = None
    sort_by: str = "created_at"
    sort_dir: str = "desc"
    page: int = 1
    per_page: int = 50


# ── Scrape Jobs ──────────────────────────────────────────

class ScrapeRequest(BaseModel):
    """Request to start a new scrape."""
    source_slug: str
    queries: list[str] = Field(default_factory=list)
    regions: list[str] = Field(default_factory=list)
    job_titles: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    page_limit: int = 3
    use_llm: bool = True


class ScrapeJobOut(BaseModel):
    id: int
    source_name: str
    status: str
    query: str
    regions: list = []
    filters: dict = {}
    total_found: int
    new_leads: int
    duplicates_skipped: int
    errors: int
    error_log: str
    progress: int
    progress_message: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Tags ─────────────────────────────────────────────────

class TagCreate(BaseModel):
    name: str
    color: Optional[str] = "#6366f1"  # default indigo


class TagOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    color: Optional[str] = None
    created_at: Optional[datetime] = None


class LeadTagUpdate(BaseModel):
    tag_ids: list[int]  # replaces all tags on a lead


# ── Stats ────────────────────────────────────────────────

class BulkUpdateRequest(BaseModel):
    lead_ids: list[int]
    status: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[list[str]] = None


class BulkDeleteRequest(BaseModel):
    lead_ids: list[int]


class StatsOut(BaseModel):
    status_breakdown: dict[str, int]


class DashboardStats(BaseModel):
    total_leads: int
    leads_today: int
    leads_this_week: int
    by_source: dict[str, int]
    by_priority: dict[str, int]
    by_status: dict[str, int]
    by_country: dict[str, int]
    recent_jobs: list[ScrapeJobOut]
    status_breakdown: dict[str, int] = {}
