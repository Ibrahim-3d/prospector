"""Lead CRUD operations and deduplication."""

from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc, asc
from backend.models.lead import Lead, Tag, lead_tags, Priority, LeadStatus
from backend.api.schemas import LeadFilters, LeadUpdate
from datetime import datetime, timezone, timedelta
import re


def normalize_company(name: str) -> str:
    """Normalize company name for deduplication."""
    if not name:
        return ""
    # Lowercase, strip whitespace
    n = name.lower().strip()
    # Remove common suffixes
    for suffix in [" inc.", " inc", " ltd.", " ltd", " llc", " gmbh", " co.", " corp.", " corp"]:
        if n.endswith(suffix):
            n = n[: -len(suffix)].strip()
    # Remove extra whitespace
    n = re.sub(r"\s+", " ", n)
    return n



def add_lead(db: Session, data: dict) -> Lead | None:
    """Add a new lead with deduplication. Returns None if duplicate."""
    company = data.get("company", "").strip()
    if not company or company.lower() == "unknown":
        return None

    norm = normalize_company(company)
    if db.query(Lead).filter(Lead.company_normalized == norm).first():
        return None  # Duplicate

    lead = Lead(
        company=company,
        company_normalized=norm,
        lead_type=data.get("lead_type", "company"),
        country=data.get("country", ""),
        city=data.get("city", ""),
        region=data.get("region", ""),
        category=data.get("category", ""),
        priority=data.get("priority", Priority.A),
        status=LeadStatus.NEW,
        source_id=data.get("source_id"),
        source_name=data.get("source_name", ""),
        scrape_job_id=data.get("scrape_job_id"),
        job_title=data.get("job_title", ""),
        job_url=data.get("job_url", ""),
        job_posted_date=data.get("job_posted_date", ""),
        demand_signal=data.get("demand_signal", ""),
        service_needed=data.get("service_needed", ""),
        website=data.get("website", ""),
        budget=data.get("budget", ""),
        project_type=data.get("project_type", ""),
        duration=data.get("duration", ""),
        experience_level=data.get("experience_level", ""),
        skills=data.get("skills", ""),
        description=data.get("description", ""),
        notes=data.get("notes", ""),
        score=data.get("score", 0.0),
    )
    db.add(lead)
    db.flush()
    return lead


def get_leads(db: Session, filters: LeadFilters, options: list = None) -> tuple[list[Lead], int]:
    """Query leads with filtering, sorting, and pagination."""
    q = db.query(Lead)
    if options:
        q = q.options(*options)

    if filters.source:
        q = q.filter(Lead.source_name == filters.source)
    if filters.source_name:
        q = q.filter(Lead.source_name == filters.source_name)
    if filters.priority:
        q = q.filter(Lead.priority == filters.priority)
    if filters.status:
        q = q.filter(Lead.status == filters.status)
    if filters.country:
        q = q.filter(Lead.country.ilike(f"%{filters.country}%"))
    if filters.lead_type:
        q = q.filter(Lead.lead_type == filters.lead_type)
    if filters.search:
        escaped = filters.search.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        term = f"%{escaped}%"
        q = q.filter(
            or_(
                Lead.company.ilike(term),
                Lead.job_title.ilike(term),
                Lead.demand_signal.ilike(term),
                Lead.notes.ilike(term),
                Lead.city.ilike(term),
            )
        )

    total = q.count()

    # Sorting
    ALLOWED_SORT_COLUMNS = {"created_at", "company", "priority", "status", "country", "source_name", "score"}
    sort_key = filters.sort_by if filters.sort_by in ALLOWED_SORT_COLUMNS else "created_at"
    sort_col = getattr(Lead, sort_key)
    if filters.sort_dir == "asc":
        q = q.order_by(asc(sort_col))
    else:
        q = q.order_by(desc(sort_col))

    # Pagination
    offset = (filters.page - 1) * filters.per_page
    leads = q.offset(offset).limit(filters.per_page).all()

    return leads, total


def update_lead(db: Session, lead_id: int, data: LeadUpdate) -> Lead | None:
    """Update a lead's fields."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(lead, key, value)
    lead.updated_at = datetime.now(timezone.utc)
    db.flush()
    return lead


def delete_lead(db: Session, lead_id: int) -> bool:
    """Delete a lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return False
    db.delete(lead)
    return True


def get_stats(db: Session) -> dict:
    """Dashboard statistics."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())

    total = db.query(Lead).count()
    today = db.query(Lead).filter(Lead.created_at >= today_start).count()
    week = db.query(Lead).filter(Lead.created_at >= week_start).count()

    by_source = dict(
        db.query(Lead.source_name, func.count(Lead.id))
        .group_by(Lead.source_name)
        .all()
    )
    by_priority = dict(
        db.query(Lead.priority, func.count(Lead.id))
        .group_by(Lead.priority)
        .all()
    )
    by_status = dict(
        db.query(Lead.status, func.count(Lead.id))
        .group_by(Lead.status)
        .all()
    )
    by_country = dict(
        db.query(Lead.country, func.count(Lead.id))
        .group_by(Lead.country)
        .order_by(func.count(Lead.id).desc())
        .limit(20)
        .all()
    )

    return {
        "total_leads": total,
        "leads_today": today,
        "leads_this_week": week,
        "by_source": by_source,
        "by_priority": by_priority,
        "by_status": by_status,
        "by_country": by_country,
    }


def get_filter_options(db: Session) -> dict:
    """Get distinct values for filter dropdowns."""
    sources = [r[0] for r in db.query(Lead.source_name).distinct().all() if r[0]]
    countries = [r[0] for r in db.query(Lead.country).distinct().order_by(Lead.country).all() if r[0]]
    categories = [r[0] for r in db.query(Lead.category).distinct().all() if r[0]]
    return {
        "sources": sources,
        "countries": countries,
        "categories": categories,
        "priorities": ["A+", "A", "B", "C"],
        "statuses": [s.value for s in LeadStatus],
        "lead_types": ["company", "startup", "project"],
    }


def create_lead(db: Session, lead_data) -> Lead:
    """Create a new lead manually (no deduplication block)."""
    norm = normalize_company(lead_data.company)
    lead = Lead(
        company=lead_data.company,
        company_normalized=norm,
        source_name=lead_data.source_name or "manual",
        job_title=lead_data.job_title,
        country=lead_data.country,
        city=lead_data.city,
        website=lead_data.website,
        notes=lead_data.notes,
        status=lead_data.status or "new",
        priority=lead_data.priority or "B",
        description=lead_data.description,
        service_needed=lead_data.service_needed,
        budget=lead_data.budget,
        skills=lead_data.skills,
        demand_signal=lead_data.demand_signal,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def export_leads(db: Session, filters: LeadFilters) -> list:
    """Return all matching leads without pagination (for export)."""
    # Temporarily override pagination to fetch everything
    unlimited_filters = LeadFilters(
        source=filters.source,
        source_name=filters.source_name,
        priority=filters.priority,
        status=filters.status,
        country=filters.country,
        lead_type=filters.lead_type,
        search=filters.search,
        sort_by=filters.sort_by,
        sort_dir=filters.sort_dir,
        page=1,
        per_page=999999,
    )
    leads, _ = get_leads(db, unlimited_filters)
    return leads


def bulk_update_leads(db: Session, lead_ids: list, status: str | None, priority: str | None) -> int:
    """Bulk update status and/or priority for a list of lead IDs. Returns count updated."""
    if not lead_ids:
        return 0
    q = db.query(Lead).filter(Lead.id.in_(lead_ids))
    updates = {}
    if status is not None:
        updates["status"] = status
    if priority is not None:
        updates["priority"] = priority
    if not updates:
        return 0
    count = q.update(updates, synchronize_session=False)
    db.commit()
    return count


def bulk_delete_leads(db: Session, lead_ids: list) -> int:
    """Bulk delete leads by ID list. Returns count deleted."""
    if not lead_ids:
        return 0
    count = db.query(Lead).filter(Lead.id.in_(lead_ids)).delete(synchronize_session=False)
    db.commit()
    return count


def get_status_breakdown(db: Session) -> dict:
    """Return count of leads per status."""
    results = db.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
    return {status: count for status, count in results}


def get_leads_trend(db: Session, days: int = 30) -> list[dict]:
    """Returns daily lead counts for the last N days."""
    from datetime import datetime, timedelta
    from sqlalchemy import func, cast, Date

    since = datetime.utcnow() - timedelta(days=days)

    results = (
        db.query(
            cast(Lead.created_at, Date).label("date"),
            func.count(Lead.id).label("count")
        )
        .filter(Lead.created_at >= since)
        .group_by(cast(Lead.created_at, Date))
        .order_by(cast(Lead.created_at, Date))
        .all()
    )

    # Fill in missing days with 0
    date_map = {str(r.date): r.count for r in results}
    today = datetime.utcnow().date()
    trend = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        date_str = str(d)
        trend.append({
            "date": date_str,
            "label": d.strftime("%b %d"),
            "count": date_map.get(date_str, 0),
        })
    return trend


# ── Tag operations ────────────────────────────────────────

def get_tags(db: Session) -> list:
    return db.query(Tag).order_by(Tag.name).all()


def create_tag(db: Session, name: str, color: str = "#6366f1"):
    """Return existing tag if name already exists, otherwise create it."""
    existing = db.query(Tag).filter(Tag.name == name).first()
    if existing:
        return existing
    tag = Tag(name=name, color=color)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag_id: int) -> bool:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return False
    db.delete(tag)
    db.commit()
    return True


def import_leads_from_csv(db: Session, content: str) -> dict:
    """Parse CSV content and import leads. Returns {imported, skipped, errors}."""
    import csv, io
    reader = csv.DictReader(io.StringIO(content))
    imported = 0
    skipped = 0
    errors = []

    for i, row in enumerate(reader, 1):
        try:
            company = row.get("company", "").strip()
            if not company:
                errors.append(f"Row {i}: missing company name")
                continue

            data = {
                "company": company,
                "job_title": row.get("job_title", "").strip() or None,
                "source_name": row.get("source_name", "manual").strip() or "manual",
                "country": row.get("country", "").strip() or None,
                "city": row.get("city", "").strip() or None,
                "website": row.get("website", "").strip() or None,
                "notes": row.get("notes", "").strip() or None,
                "status": row.get("status", "new").strip() or "new",
                "priority": row.get("priority", "B").strip() or "B",
                "demand_signal": row.get("demand_signal", "").strip() or None,
                "description": row.get("description", "").strip() or None,
                "service_needed": row.get("service_needed", "").strip() or None,
                "budget": row.get("budget", "").strip() or None,
                "skills": row.get("skills", "").strip() or None,
            }
            result = add_lead(db, data)
            if result is None:
                skipped += 1
            else:
                imported += 1
                db.commit()
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")

    return {"imported": imported, "skipped": skipped, "errors": errors[:10]}  # cap errors


def update_lead_tags(db: Session, lead_id: int, tag_ids: list[int]) -> Lead | None:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return None
    tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
    lead.tags = tags
    db.commit()
    db.refresh(lead)
    return lead
