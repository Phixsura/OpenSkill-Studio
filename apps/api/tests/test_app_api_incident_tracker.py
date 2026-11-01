"""Tests for App API Incident Tracker — create, status, active."""

import pytest
from app.services.app_api_incident_tracker import AppAPIIncidentTracker, IncidentSeverity, IncidentStatus


class TestCreate:
    def test_create(self):
        t = AppAPIIncidentTracker()
        i = t.create("inst-1", "inc-1", "API Down", IncidentSeverity.CRITICAL, ["/api/users"])
        assert i.severity == IncidentSeverity.CRITICAL

    def test_duplicate(self):
        t = AppAPIIncidentTracker()
        t.create("inst-1", "inc-1", "A", IncidentSeverity.LOW)
        with pytest.raises(ValueError):
            t.create("inst-1", "inc-1", "B", IncidentSeverity.LOW)


class TestLifecycle:
    def test_resolve(self):
        t = AppAPIIncidentTracker()
        t.create("inst-1", "inc-1", "Issue", IncidentSeverity.MEDIUM)
        i = t.update_status("inst-1", "inc-1", IncidentStatus.RESOLVED)
        assert i.resolved_at is not None
        assert t.active_incidents("inst-1") == []

    def test_active(self):
        t = AppAPIIncidentTracker()
        t.create("inst-1", "inc-1", "A", IncidentSeverity.HIGH)
        t.create("inst-1", "inc-2", "B", IncidentSeverity.LOW)
        t.update_status("inst-1", "inc-2", IncidentStatus.RESOLVED)
        assert len(t.active_incidents("inst-1")) == 1


class TestIsolation:
    def test_cross(self):
        t = AppAPIIncidentTracker()
        t.create("inst-1", "inc-1", "A", IncidentSeverity.LOW)
        assert t.list_incidents("inst-2") == []
