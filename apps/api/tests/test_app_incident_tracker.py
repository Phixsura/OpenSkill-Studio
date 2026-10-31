"""Tests for App Incident Tracker — lifecycle, timeline, duration, components."""

import pytest

from app.services.app_incident_tracker import (
    AppIncidentTracker,
    IncidentSeverity,
    IncidentStatus,
)


class TestCreateIncident:
    def test_create(self):
        t = AppIncidentTracker()
        inc = t.create_incident("inst-1", "inc-1", "API Down", IncidentSeverity.CRITICAL,
                                affected_components=["api", "auth"], now=1000.0)
        assert inc.incident_id == "inc-1"
        assert inc.severity == IncidentSeverity.CRITICAL
        assert inc.status == IncidentStatus.INVESTIGATING
        assert len(inc.timeline) == 1
        assert inc.affected_components == ["api", "auth"]

    def test_duplicate(self):
        t = AppIncidentTracker()
        t.create_incident("inst-1", "inc-1", "Down", IncidentSeverity.MINOR)
        with pytest.raises(ValueError, match="already exists"):
            t.create_incident("inst-1", "inc-1", "Down2", IncidentSeverity.MINOR)

    def test_missing_title(self):
        t = AppIncidentTracker()
        with pytest.raises(ValueError, match="title"):
            t.create_incident("inst-1", "inc-1", "", IncidentSeverity.MINOR)


class TestUpdateStatus:
    def test_update_to_identified(self):
        t = AppIncidentTracker()
        t.create_incident("inst-1", "inc-1", "Slow", IncidentSeverity.MAJOR, now=1000.0)
        inc = t.update_status("inst-1", "inc-1", IncidentStatus.IDENTIFIED,
                              "Root cause found: DB connection pool", now=1010.0)
        assert inc.status == IncidentStatus.IDENTIFIED
        assert len(inc.timeline) == 2
        assert inc.timeline[1].message == "Root cause found: DB connection pool"

    def test_resolve(self):
        t = AppIncidentTracker()
        t.create_incident("inst-1", "inc-1", "Outage", IncidentSeverity.CRITICAL, now=1000.0)
        t.update_status("inst-1", "inc-1", IncidentStatus.IDENTIFIED, "Found issue", now=1010.0)
        inc = t.update_status("inst-1", "inc-1", IncidentStatus.RESOLVED, "Deployed fix", now=1020.0)
        assert inc.status == IncidentStatus.RESOLVED
        assert inc.resolved_at == 1020.0

    def test_cannot_update_resolved(self):
        t = AppIncidentTracker()
        t.create_incident("inst-1", "inc-1", "Down", IncidentSeverity.MINOR, now=1000.0)
        t.update_status("inst-1", "inc-1", IncidentStatus.RESOLVED, "Fixed", now=1010.0)
        with pytest.raises(ValueError, match="resolved"):
            t.update_status("inst-1", "inc-1", IncidentStatus.MONITORING, "Watching")

    def test_empty_message(self):
        t = AppIncidentTracker()
        t.create_incident("inst-1", "inc-1", "Down", IncidentSeverity.MINOR)
        with pytest.raises(ValueError, match="message"):
            t.update_status("inst-1", "inc-1", IncidentStatus.IDENTIFIED, "")


class TestTimeline:
    def test_full_timeline(self):
        t = AppIncidentTracker()
        t.create_incident("inst-1", "inc-1", "Issue", IncidentSeverity.MAJOR, now=1000.0)
        t.update_status("inst-1", "inc-1", IncidentStatus.IDENTIFIED, "Found", now=1010.0)
        t.update_status("inst-1", "inc-1", IncidentStatus.MONITORING, "Watching", now=1020.0)
        t.update_status("inst-1", "inc-1", IncidentStatus.RESOLVED, "Done", now=1030.0)
        inc = t.get_incident("inst-1", "inc-1")
        assert len(inc.timeline) == 4
        statuses = [e.status for e in inc.timeline]
        assert statuses == [
            IncidentStatus.INVESTIGATING,
            IncidentStatus.IDENTIFIED,
            IncidentStatus.MONITORING,
            IncidentStatus.RESOLVED,
        ]


class TestDuration:
    def test_resolved_duration(self):
        t = AppIncidentTracker()
        t.create_incident("inst-1", "inc-1", "Down", IncidentSeverity.CRITICAL, now=1000.0)
        t.update_status("inst-1", "inc-1", IncidentStatus.RESOLVED, "Fixed", now=1060.0)
        assert t.get_duration_seconds("inst-1", "inc-1") == 60.0

    def test_active_duration(self):
        t = AppIncidentTracker()
        t.create_incident("inst-1", "inc-1", "Down", IncidentSeverity.CRITICAL, now=1000.0)
        assert t.get_duration_seconds("inst-1", "inc-1", now=1030.0) == 30.0


class TestListIncidents:
    def test_list_all(self):
        t = AppIncidentTracker()
        t.create_incident("inst-1", "inc-1", "A", IncidentSeverity.MINOR, now=1000.0)
        t.create_incident("inst-1", "inc-2", "B", IncidentSeverity.MAJOR, now=1010.0)
        incs = t.list_incidents("inst-1")
        assert len(incs) == 2
        assert incs[0].incident_id == "inc-2"  # newest first

    def test_active_only(self):
        t = AppIncidentTracker()
        t.create_incident("inst-1", "inc-1", "A", IncidentSeverity.MINOR)
        t.create_incident("inst-1", "inc-2", "B", IncidentSeverity.MAJOR)
        t.update_status("inst-1", "inc-1", IncidentStatus.RESOLVED, "Fixed")
        incs = t.list_incidents("inst-1", active_only=True)
        assert len(incs) == 1
        assert incs[0].incident_id == "inc-2"


class TestAffectedComponents:
    def test_active_components(self):
        t = AppIncidentTracker()
        t.create_incident("inst-1", "inc-1", "A", IncidentSeverity.MINOR,
                          affected_components=["api", "db"])
        t.create_incident("inst-1", "inc-2", "B", IncidentSeverity.MAJOR,
                          affected_components=["auth"])
        components = t.get_affected_components("inst-1")
        assert components == ["api", "auth", "db"]

    def test_resolved_not_included(self):
        t = AppIncidentTracker()
        t.create_incident("inst-1", "inc-1", "A", IncidentSeverity.MINOR,
                          affected_components=["api"])
        t.update_status("inst-1", "inc-1", IncidentStatus.RESOLVED, "Fixed")
        components = t.get_affected_components("inst-1")
        assert components == []


class TestIsolation:
    def test_cross_installation(self):
        t = AppIncidentTracker()
        t.create_incident("inst-1", "inc-1", "A", IncidentSeverity.MINOR)
        with pytest.raises(KeyError):
            t.get_incident("inst-2", "inc-1")
