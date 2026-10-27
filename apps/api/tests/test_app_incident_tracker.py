"""Tests for App Incident Tracker — lifecycle, timeline, MTTR, filtering."""

import pytest

from app.services.app_incident_tracker import (
    AppIncidentTracker,
    IncidentStatus,
    Severity,
)


class TestCreate:
    def test_create_incident(self):
        t = AppIncidentTracker()
        inc = t.create("app-1", "API errors spike", Severity.MAJOR, ["api", "auth"])
        assert inc.title == "API errors spike"
        assert inc.severity == Severity.MAJOR
        assert inc.status == IncidentStatus.INVESTIGATING
        assert inc.affected_components == ["api", "auth"]
        assert len(inc.timeline) == 1

    def test_empty_title_rejected(self):
        t = AppIncidentTracker()
        with pytest.raises(ValueError, match="required"):
            t.create("app-1", "", Severity.MINOR)

    def test_auto_id(self):
        t = AppIncidentTracker()
        i1 = t.create("app-1", "A", Severity.MINOR)
        i2 = t.create("app-1", "B", Severity.MINOR)
        assert i1.incident_id != i2.incident_id


class TestStatusProgression:
    def test_investigating_to_identified(self):
        t = AppIncidentTracker()
        inc = t.create("app-1", "DB slow", Severity.MAJOR)
        updated = t.update_status(inc.incident_id, IncidentStatus.IDENTIFIED,
                                   "Root cause: connection pool exhaustion")
        assert updated.status == IncidentStatus.IDENTIFIED
        assert len(updated.timeline) == 2

    def test_resolve(self):
        t = AppIncidentTracker()
        inc = t.create("app-1", "Outage", Severity.CRITICAL)
        t.update_status(inc.incident_id, IncidentStatus.IDENTIFIED, "Found cause")
        t.update_status(inc.incident_id, IncidentStatus.MONITORING, "Fix deployed")
        t.update_status(inc.incident_id, IncidentStatus.RESOLVED, "Confirmed fixed")
        assert t.get(inc.incident_id).status == IncidentStatus.RESOLVED
        assert t.get(inc.incident_id).resolved_at is not None

    def test_resolved_cannot_update(self):
        t = AppIncidentTracker()
        inc = t.create("app-1", "Done", Severity.INFO)
        t.update_status(inc.incident_id, IncidentStatus.RESOLVED, "Done")
        result = t.update_status(inc.incident_id, IncidentStatus.INVESTIGATING, "Reopen?")
        assert result is None  # can't update resolved

    def test_update_nonexistent(self):
        t = AppIncidentTracker()
        assert t.update_status("nope", IncidentStatus.RESOLVED, "msg") is None


class TestTimeline:
    def test_timeline_records_events(self):
        t = AppIncidentTracker()
        inc = t.create("app-1", "Issue", Severity.MINOR, author="admin")
        t.update_status(inc.incident_id, IncidentStatus.IDENTIFIED, "Found it", author="eng")
        t.update_status(inc.incident_id, IncidentStatus.RESOLVED, "Fixed", author="eng")
        timeline = t.get(inc.incident_id).timeline
        assert len(timeline) == 3
        assert timeline[0].author == "admin"
        assert timeline[1].message == "Found it"
        assert timeline[2].status == IncidentStatus.RESOLVED

    def test_timeline_author(self):
        t = AppIncidentTracker()
        inc = t.create("app-1", "X", Severity.INFO, author="user-1")
        assert inc.timeline[0].author == "user-1"


class TestDuration:
    def test_duration_none_when_open(self):
        t = AppIncidentTracker()
        inc = t.create("app-1", "Open", Severity.MINOR)
        assert inc.duration_minutes is None

    def test_duration_set_on_resolve(self):
        t = AppIncidentTracker()
        inc = t.create("app-1", "Quick fix", Severity.MINOR)
        t.update_status(inc.incident_id, IncidentStatus.RESOLVED, "Fixed")
        assert inc.duration_minutes is not None
        assert inc.duration_minutes >= 0


class TestListing:
    def test_list_by_app(self):
        t = AppIncidentTracker()
        t.create("app-1", "A", Severity.MINOR)
        t.create("app-2", "B", Severity.MINOR)
        t.create("app-1", "C", Severity.MAJOR)
        assert len(t.list_incidents(app_id="app-1")) == 2

    def test_list_by_status(self):
        t = AppIncidentTracker()
        i1 = t.create("app-1", "A", Severity.MINOR)
        t.create("app-1", "B", Severity.MINOR)
        t.update_status(i1.incident_id, IncidentStatus.RESOLVED, "Done")
        open_list = t.list_incidents(app_id="app-1", status=IncidentStatus.INVESTIGATING)
        assert len(open_list) == 1

    def test_list_by_severity(self):
        t = AppIncidentTracker()
        t.create("app-1", "A", Severity.CRITICAL)
        t.create("app-1", "B", Severity.MINOR)
        crits = t.list_incidents(severity=Severity.CRITICAL)
        assert len(crits) == 1

    def test_newest_first(self):
        t = AppIncidentTracker()
        t.create("app-1", "First", Severity.MINOR)
        t.create("app-1", "Second", Severity.MINOR)
        incidents = t.list_incidents()
        assert incidents[0].title == "Second"

    def test_open_count(self):
        t = AppIncidentTracker()
        i1 = t.create("app-1", "A", Severity.MINOR)
        t.create("app-1", "B", Severity.MINOR)
        t.update_status(i1.incident_id, IncidentStatus.RESOLVED, "Done")
        assert t.get_open_count("app-1") == 1


class TestSummary:
    def test_summary_counts(self):
        t = AppIncidentTracker()
        i1 = t.create("app-1", "A", Severity.CRITICAL)
        t.create("app-1", "B", Severity.MINOR)
        t.update_status(i1.incident_id, IncidentStatus.RESOLVED, "Done")
        s = t.get_summary("app-1")
        assert s.total == 2
        assert s.resolved == 1
        assert s.open == 1
        assert s.by_severity["critical"] == 1
        assert s.by_severity["minor"] == 1

    def test_mttr(self):
        t = AppIncidentTracker()
        i1 = t.create("app-1", "Quick", Severity.MINOR)
        t.update_status(i1.incident_id, IncidentStatus.RESOLVED, "Done")
        s = t.get_summary("app-1")
        assert s.mttr_minutes is not None
        assert s.mttr_minutes >= 0

    def test_mttr_none_no_resolved(self):
        t = AppIncidentTracker()
        t.create("app-1", "Open", Severity.MINOR)
        s = t.get_summary("app-1")
        assert s.mttr_minutes is None

    def test_empty_summary(self):
        t = AppIncidentTracker()
        s = t.get_summary("app-x")
        assert s.total == 0
        assert s.open == 0
