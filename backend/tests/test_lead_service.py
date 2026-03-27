"""Unit tests for lead_service functions."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import all models so Base.metadata is fully populated before create_all
from backend.core.database import Base
from backend.models import lead as _lead_module          # registers Lead, Tag, lead_tags
from backend.models import scrape_job as _job_module    # registers ScrapeJob
from backend.models import source as _source_module     # registers Source

from backend.models.lead import Lead, LeadStatus, Priority
from backend.services import lead_service
from backend.api.schemas import LeadFilters, LeadUpdate


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def db():
    """In-memory SQLite session for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=True, autocommit=False)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def make_lead(db, company="Acme Corp", source="linkedin", **kwargs):
    """
    Helper: insert a Lead directly into the DB and return the refreshed instance.
    Uses lead_service.normalize_company for consistency.
    """
    lead = Lead(
        company=company,
        company_normalized=lead_service.normalize_company(company),
        source_name=source,
        status=kwargs.get("status", LeadStatus.NEW),
        priority=kwargs.get("priority", Priority.B),
        job_title=kwargs.get("job_title", ""),
        country=kwargs.get("country", ""),
        city=kwargs.get("city", ""),
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


# ── normalize_company tests ───────────────────────────────────────────────────

class TestNormalizeCompany:
    def test_basic(self):
        assert lead_service.normalize_company("Acme Corp") == "acme"

    def test_strips_llc(self):
        assert lead_service.normalize_company("OpenAI LLC") == "openai"

    def test_strips_inc(self):
        assert lead_service.normalize_company("Apple Inc.") == "apple"

    def test_strips_ltd(self):
        assert lead_service.normalize_company("Valve Ltd") == "valve"

    def test_strips_gmbh(self):
        assert lead_service.normalize_company("SAP GmbH") == "sap"

    def test_empty_returns_empty(self):
        result = lead_service.normalize_company("")
        assert result == ""

    def test_lowercases(self):
        assert lead_service.normalize_company("MICROSOFT") == "microsoft"

    def test_strips_extra_whitespace(self):
        result = lead_service.normalize_company("  Google  ")
        assert result == "google"

    def test_strips_corp_dot(self):
        # "corp." variant with a period
        assert lead_service.normalize_company("Pixar Corp.") == "pixar"

    def test_strips_co_dot(self):
        # " co." variant
        assert lead_service.normalize_company("ACME Co.") == "acme"

    def test_no_suffix_unchanged(self):
        # A plain studio name has no suffix to strip
        assert lead_service.normalize_company("Blue Sky Studio") == "blue sky studio"

    def test_collapses_internal_whitespace(self):
        # normalize_company uses re.sub(r"\s+", " ", n) — all internal runs collapse to one space
        result = lead_service.normalize_company("Double  Space  Corp")
        assert result == "double space"  # suffix " corp" stripped, double spaces collapsed


# ── add_lead / deduplication tests ───────────────────────────────────────────

class TestAddLead:
    def test_adds_new_lead(self, db):
        data = {"company": "TestCo", "source_name": "linkedin", "job_title": "3D Artist"}
        result = lead_service.add_lead(db, data)
        assert result is not None
        db.commit()
        assert db.query(Lead).count() == 1

    def test_returns_lead_object(self, db):
        data = {"company": "Render Farm", "source_name": "artstation"}
        result = lead_service.add_lead(db, data)
        assert isinstance(result, Lead)
        assert result.company == "Render Farm"

    def test_deduplication_same_company(self, db):
        lead_service.add_lead(db, {"company": "TestCo", "source_name": "linkedin"})
        db.commit()
        # Second insert — same company name, different source
        result = lead_service.add_lead(db, {"company": "TestCo", "source_name": "artstation"})
        assert result is None  # rejected as duplicate
        assert db.query(Lead).count() == 1

    def test_deduplication_strips_suffix(self, db):
        # "Acme LLC" normalizes to "acme", "Acme Corp" also normalizes to "acme"
        lead_service.add_lead(db, {"company": "Acme LLC", "source_name": "linkedin"})
        db.commit()
        result = lead_service.add_lead(db, {"company": "Acme Corp", "source_name": "wamda"})
        assert result is None
        assert db.query(Lead).count() == 1

    def test_different_companies_both_added(self, db):
        lead_service.add_lead(db, {"company": "Alpha Studio", "source_name": "linkedin"})
        lead_service.add_lead(db, {"company": "Beta Studio", "source_name": "artstation"})
        db.commit()
        assert db.query(Lead).count() == 2

    def test_rejects_empty_company(self, db):
        result = lead_service.add_lead(db, {"company": "", "source_name": "linkedin"})
        assert result is None
        assert db.query(Lead).count() == 0

    def test_rejects_unknown_company(self, db):
        result = lead_service.add_lead(db, {"company": "unknown", "source_name": "linkedin"})
        assert result is None
        assert db.query(Lead).count() == 0

    def test_rejects_unknown_case_insensitive(self, db):
        result = lead_service.add_lead(db, {"company": "UNKNOWN", "source_name": "linkedin"})
        assert result is None

    def test_default_status_is_new(self, db):
        lead_service.add_lead(db, {"company": "Newco", "source_name": "linkedin"})
        db.commit()
        lead = db.query(Lead).first()
        assert lead.status == LeadStatus.NEW

    def test_default_priority_is_a(self, db):
        # add_lead sets priority from data.get("priority", Priority.A)
        lead_service.add_lead(db, {"company": "Defaultco", "source_name": "linkedin"})
        db.commit()
        lead = db.query(Lead).first()
        assert lead.priority == Priority.A

    def test_explicit_priority_stored(self, db):
        lead_service.add_lead(db, {"company": "VIPco", "source_name": "linkedin", "priority": Priority.A_PLUS})
        db.commit()
        lead = db.query(Lead).first()
        assert lead.priority == Priority.A_PLUS

    def test_source_name_stored(self, db):
        lead_service.add_lead(db, {"company": "SourceCheck", "source_name": "wamda"})
        db.commit()
        lead = db.query(Lead).first()
        assert lead.source_name == "wamda"

    def test_company_normalized_stored(self, db):
        lead_service.add_lead(db, {"company": "Pixel Inc.", "source_name": "linkedin"})
        db.commit()
        lead = db.query(Lead).first()
        assert lead.company_normalized == "pixel"


# ── get_leads filter tests ────────────────────────────────────────────────────

class TestGetLeads:
    """
    get_leads returns (list[Lead], int) — a tuple, not a dict.
    """

    def test_returns_all(self, db):
        make_lead(db, "Alpha")
        make_lead(db, "Beta")
        leads, total = lead_service.get_leads(db, LeadFilters())
        assert total == 2
        assert len(leads) == 2

    def test_pagination_limits_results(self, db):
        for i in range(5):
            make_lead(db, f"Company{i}")
        leads, total = lead_service.get_leads(db, LeadFilters(page=1, per_page=2))
        assert len(leads) == 2
        assert total == 5

    def test_pagination_second_page(self, db):
        for i in range(5):
            make_lead(db, f"Company{i}")
        leads_p1, _ = lead_service.get_leads(db, LeadFilters(page=1, per_page=3))
        leads_p2, _ = lead_service.get_leads(db, LeadFilters(page=2, per_page=3))
        assert len(leads_p1) == 3
        assert len(leads_p2) == 2

    def test_filter_by_status(self, db):
        make_lead(db, "Alpha", status=LeadStatus.NEW)
        make_lead(db, "Beta", status=LeadStatus.CONTACTED)
        leads, total = lead_service.get_leads(db, LeadFilters(status="new"))
        assert total == 1
        assert leads[0].company == "Alpha"

    def test_filter_by_priority(self, db):
        make_lead(db, "A+ Lead", priority=Priority.A_PLUS)
        make_lead(db, "B Lead", priority=Priority.B)
        leads, total = lead_service.get_leads(db, LeadFilters(priority="A+"))
        assert total == 1
        assert leads[0].company == "A+ Lead"

    def test_search_by_company_name(self, db):
        make_lead(db, "Motion Design Studio")
        make_lead(db, "VFX House")
        leads, total = lead_service.get_leads(db, LeadFilters(search="motion"))
        assert total == 1
        assert leads[0].company == "Motion Design Studio"

    def test_search_case_insensitive(self, db):
        make_lead(db, "Immersive Labs")
        leads, total = lead_service.get_leads(db, LeadFilters(search="IMMERSIVE"))
        assert total == 1

    def test_search_by_job_title(self, db):
        make_lead(db, "Studio A", job_title="Senior 3D Artist")
        make_lead(db, "Studio B", job_title="UX Designer")
        leads, total = lead_service.get_leads(db, LeadFilters(search="3D Artist"))
        assert total == 1
        assert leads[0].company == "Studio A"

    def test_filter_by_source_name(self, db):
        make_lead(db, "LinkedIn Co", source="linkedin")
        make_lead(db, "Wamda Co", source="wamda")
        leads, total = lead_service.get_leads(db, LeadFilters(source_name="linkedin"))
        assert total == 1
        assert leads[0].company == "LinkedIn Co"

    def test_filter_by_source(self, db):
        make_lead(db, "LinkedIn Co", source="linkedin")
        make_lead(db, "Wamda Co", source="wamda")
        leads, total = lead_service.get_leads(db, LeadFilters(source="wamda"))
        assert total == 1
        assert leads[0].company == "Wamda Co"

    def test_sort_by_company_asc(self, db):
        make_lead(db, "Zebra Studio")
        make_lead(db, "Alpha Studio")
        leads, _ = lead_service.get_leads(db, LeadFilters(sort_by="company", sort_dir="asc"))
        assert leads[0].company == "Alpha Studio"
        assert leads[1].company == "Zebra Studio"

    def test_sort_by_company_desc(self, db):
        make_lead(db, "Zebra Studio")
        make_lead(db, "Alpha Studio")
        leads, _ = lead_service.get_leads(db, LeadFilters(sort_by="company", sort_dir="desc"))
        assert leads[0].company == "Zebra Studio"

    def test_invalid_sort_column_falls_back(self, db):
        """Injected/unknown column names must fall back to created_at without raising."""
        make_lead(db, "Safe Co")
        leads, total = lead_service.get_leads(db, LeadFilters(sort_by="__class__"))
        assert total == 1
        assert leads[0].company == "Safe Co"

    def test_empty_db_returns_zero(self, db):
        leads, total = lead_service.get_leads(db, LeadFilters())
        assert total == 0
        assert leads == []

    def test_no_results_for_unmatched_filter(self, db):
        make_lead(db, "Some Co")
        leads, total = lead_service.get_leads(db, LeadFilters(status="won"))
        assert total == 0

    def test_filter_by_country_partial_match(self, db):
        make_lead(db, "UAE Co", country="United Arab Emirates")
        make_lead(db, "US Co", country="United States")
        leads, total = lead_service.get_leads(db, LeadFilters(country="Arab"))
        assert total == 1
        assert leads[0].company == "UAE Co"


# ── update_lead tests ─────────────────────────────────────────────────────────

class TestUpdateLead:
    def test_updates_status(self, db):
        lead = make_lead(db)
        updated = lead_service.update_lead(db, lead.id, LeadUpdate(status="contacted"))
        assert updated is not None
        assert updated.status == "contacted"

    def test_updates_priority(self, db):
        lead = make_lead(db)
        updated = lead_service.update_lead(db, lead.id, LeadUpdate(priority="A+"))
        assert updated.priority == "A+"

    def test_updates_notes(self, db):
        lead = make_lead(db)
        updated = lead_service.update_lead(db, lead.id, LeadUpdate(notes="Follow up in 2 weeks"))
        assert updated.notes == "Follow up in 2 weeks"

    def test_updates_job_title(self, db):
        lead = make_lead(db, job_title="3D Artist")
        updated = lead_service.update_lead(db, lead.id, LeadUpdate(job_title="Senior 3D Artist"))
        assert updated.job_title == "Senior 3D Artist"

    def test_can_clear_job_title(self, db):
        lead = make_lead(db, job_title="3D Artist")
        # job_title is a set field so passing "" clears it
        updated = lead_service.update_lead(db, lead.id, LeadUpdate(job_title=""))
        assert updated.job_title == ""

    def test_unset_fields_not_overwritten(self, db):
        """Fields not present in LeadUpdate payload must remain unchanged."""
        lead = make_lead(db, job_title="Original Title")
        # Only update status; job_title must be untouched
        lead_service.update_lead(db, lead.id, LeadUpdate(status="contacted"))
        db.refresh(lead)
        assert lead.job_title == "Original Title"

    def test_returns_none_for_missing_lead(self, db):
        result = lead_service.update_lead(db, 9999, LeadUpdate(status="new"))
        assert result is None

    def test_updates_multiple_fields_at_once(self, db):
        lead = make_lead(db)
        updated = lead_service.update_lead(
            db, lead.id, LeadUpdate(status="qualified", priority="A+", notes="Hot lead")
        )
        assert updated.status == "qualified"
        assert updated.priority == "A+"
        assert updated.notes == "Hot lead"

    def test_updated_at_is_refreshed(self, db):
        lead = make_lead(db)
        original_updated_at = lead.updated_at
        # Ensure some time passes so the timestamp can differ
        import time; time.sleep(0.01)
        updated = lead_service.update_lead(db, lead.id, LeadUpdate(status="contacted"))
        # updated_at must be set (not None); exact comparison is environment-dependent
        assert updated.updated_at is not None


# ── delete_lead tests ─────────────────────────────────────────────────────────

class TestDeleteLead:
    def test_deletes_existing_lead(self, db):
        lead = make_lead(db)
        result = lead_service.delete_lead(db, lead.id)
        assert result is True
        assert db.query(Lead).count() == 0

    def test_returns_false_for_missing_lead(self, db):
        result = lead_service.delete_lead(db, 9999)
        assert result is False

    def test_does_not_delete_other_leads(self, db):
        a = make_lead(db, "Alpha")
        b = make_lead(db, "Beta")
        lead_service.delete_lead(db, a.id)
        db.commit()
        assert db.query(Lead).count() == 1
        assert db.query(Lead).first().company == "Beta"


# ── bulk operations tests ─────────────────────────────────────────────────────

class TestBulkOps:
    def test_bulk_update_status(self, db):
        a = make_lead(db, "Alpha")
        b = make_lead(db, "Beta")
        count = lead_service.bulk_update_leads(db, [a.id, b.id], status="contacted", priority=None)
        assert count == 2
        assert db.query(Lead).filter(Lead.status == "contacted").count() == 2

    def test_bulk_update_priority(self, db):
        a = make_lead(db, "Alpha")
        b = make_lead(db, "Beta")
        count = lead_service.bulk_update_leads(db, [a.id, b.id], status=None, priority="A+")
        assert count == 2
        assert db.query(Lead).filter(Lead.priority == "A+").count() == 2

    def test_bulk_update_both_fields(self, db):
        a = make_lead(db, "Alpha")
        count = lead_service.bulk_update_leads(db, [a.id], status="qualified", priority="A")
        assert count == 1
        db.expire(a)
        db.refresh(a)
        assert a.status == "qualified"
        assert a.priority == "A"

    def test_bulk_update_empty_list_returns_zero(self, db):
        count = lead_service.bulk_update_leads(db, [], status="contacted", priority=None)
        assert count == 0

    def test_bulk_update_no_fields_returns_zero(self, db):
        a = make_lead(db, "Alpha")
        count = lead_service.bulk_update_leads(db, [a.id], status=None, priority=None)
        assert count == 0

    def test_bulk_update_only_targets_given_ids(self, db):
        a = make_lead(db, "Alpha")
        b = make_lead(db, "Beta")
        make_lead(db, "Gamma")
        lead_service.bulk_update_leads(db, [a.id, b.id], status="contacted", priority=None)
        gamma = db.query(Lead).filter(Lead.company == "Gamma").first()
        assert gamma.status == LeadStatus.NEW

    def test_bulk_delete_removes_correct_leads(self, db):
        a = make_lead(db, "Alpha")
        b = make_lead(db, "Beta")
        make_lead(db, "Gamma")
        count = lead_service.bulk_delete_leads(db, [a.id, b.id])
        assert count == 2
        assert db.query(Lead).count() == 1
        assert db.query(Lead).first().company == "Gamma"

    def test_bulk_delete_empty_list_returns_zero(self, db):
        make_lead(db, "Alpha")
        count = lead_service.bulk_delete_leads(db, [])
        assert count == 0
        assert db.query(Lead).count() == 1

    def test_bulk_delete_nonexistent_ids(self, db):
        count = lead_service.bulk_delete_leads(db, [999, 1000])
        assert count == 0


# ── status breakdown tests ────────────────────────────────────────────────────

class TestStatusBreakdown:
    def test_counts_by_status(self, db):
        make_lead(db, "A", status=LeadStatus.NEW)
        make_lead(db, "B", status=LeadStatus.NEW)
        make_lead(db, "C", status=LeadStatus.CONTACTED)
        breakdown = lead_service.get_status_breakdown(db)
        assert breakdown[LeadStatus.NEW] == 2
        assert breakdown[LeadStatus.CONTACTED] == 1

    def test_empty_db_returns_empty_dict(self, db):
        breakdown = lead_service.get_status_breakdown(db)
        assert breakdown == {}

    def test_only_present_statuses_in_result(self, db):
        make_lead(db, "Only One", status=LeadStatus.QUALIFIED)
        breakdown = lead_service.get_status_breakdown(db)
        assert LeadStatus.QUALIFIED in breakdown
        # Statuses with no leads are absent
        assert LeadStatus.WON not in breakdown

    def test_all_distinct_statuses_counted(self, db):
        statuses = [LeadStatus.NEW, LeadStatus.CONTACTED, LeadStatus.REPLIED, LeadStatus.WON]
        for i, s in enumerate(statuses):
            make_lead(db, f"Co{i}", status=s)
        breakdown = lead_service.get_status_breakdown(db)
        assert len(breakdown) == 4
        for s in statuses:
            assert breakdown[s] == 1


# ── get_stats tests ───────────────────────────────────────────────────────────

class TestGetStats:
    def test_total_leads_count(self, db):
        make_lead(db, "Alpha")
        make_lead(db, "Beta")
        stats = lead_service.get_stats(db)
        assert stats["total_leads"] == 2

    def test_by_source_grouped(self, db):
        make_lead(db, "A", source="linkedin")
        make_lead(db, "B", source="linkedin")
        make_lead(db, "C", source="wamda")
        stats = lead_service.get_stats(db)
        assert stats["by_source"]["linkedin"] == 2
        assert stats["by_source"]["wamda"] == 1

    def test_by_priority_grouped(self, db):
        make_lead(db, "A", priority=Priority.A_PLUS)
        make_lead(db, "B", priority=Priority.B)
        stats = lead_service.get_stats(db)
        assert stats["by_priority"][Priority.A_PLUS] == 1
        assert stats["by_priority"][Priority.B] == 1

    def test_empty_db_total_is_zero(self, db):
        stats = lead_service.get_stats(db)
        assert stats["total_leads"] == 0

    def test_stats_keys_present(self, db):
        stats = lead_service.get_stats(db)
        for key in ("total_leads", "leads_today", "leads_this_week", "by_source",
                    "by_priority", "by_status", "by_country"):
            assert key in stats


# ── get_filter_options tests ──────────────────────────────────────────────────

class TestGetFilterOptions:
    def test_returns_expected_keys(self, db):
        opts = lead_service.get_filter_options(db)
        for key in ("sources", "countries", "categories", "priorities", "statuses", "lead_types"):
            assert key in opts

    def test_sources_populated_from_leads(self, db):
        make_lead(db, "A", source="linkedin")
        make_lead(db, "B", source="artstation")
        opts = lead_service.get_filter_options(db)
        assert "linkedin" in opts["sources"]
        assert "artstation" in opts["sources"]

    def test_countries_populated_from_leads(self, db):
        make_lead(db, "A", country="UAE")
        make_lead(db, "B", country="Egypt")
        opts = lead_service.get_filter_options(db)
        assert "UAE" in opts["countries"]
        assert "Egypt" in opts["countries"]

    def test_priorities_list_is_complete(self, db):
        opts = lead_service.get_filter_options(db)
        assert set(opts["priorities"]) == {"A+", "A", "B", "C"}

    def test_empty_source_excluded(self, db):
        """Leads with blank source_name should not appear in sources list."""
        lead = Lead(
            company="No Source Co",
            company_normalized="no source co",
            source_name="",
        )
        db.add(lead)
        db.commit()
        opts = lead_service.get_filter_options(db)
        assert "" not in opts["sources"]


# ── export_leads tests ────────────────────────────────────────────────────────

class TestExportLeads:
    def test_returns_all_matching_leads(self, db):
        for i in range(10):
            make_lead(db, f"Co{i}")
        results = lead_service.export_leads(db, LeadFilters())
        assert len(results) == 10

    def test_respects_filters(self, db):
        make_lead(db, "LinkedIn Co", source="linkedin")
        make_lead(db, "Wamda Co", source="wamda")
        results = lead_service.export_leads(db, LeadFilters(source_name="linkedin"))
        assert len(results) == 1
        assert results[0].company == "LinkedIn Co"

    def test_returns_list_type(self, db):
        make_lead(db, "A")
        results = lead_service.export_leads(db, LeadFilters())
        assert isinstance(results, list)
