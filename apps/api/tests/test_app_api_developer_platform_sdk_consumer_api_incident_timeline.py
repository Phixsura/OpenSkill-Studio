"""Tests for Consumer API Incident Timeline service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_incident_timeline import (
    IncidentTimelineManager, IncidentImpact,
)


class TestIncidentTimelineManager:
    def test_create(self):
        svc = IncidentTimelineManager()
        result = svc.create("inc-1", "DB Outage", "p1")
        assert result["severity"] == "p1"

    def test_add_events(self):
        svc = IncidentTimelineManager()
        svc.create("inc-1", "API Slowdown", "p2")
        svc.add_event("inc-1", "investigating", "Checking logs", "alice")
        svc.add_event("inc-1", "identified", "Root cause: cache miss", "bob")
        timeline = svc.get_timeline("inc-1")
        assert timeline["duration_events"] == 3  # detected + 2 added

    def test_resolve(self):
        svc = IncidentTimelineManager()
        svc.create("inc-1", "Issue", "p3")
        svc.add_event("inc-1", "resolved", "Fixed")
        timeline = svc.get_timeline("inc-1")
        assert timeline["status"] == "resolved"

    def test_impact(self):
        svc = IncidentTimelineManager()
        impact = IncidentImpact(["ep1", "ep2"], affected_consumers=50, estimated_requests_lost=1000)
        svc.create("inc-1", "Outage", "p1", impact=impact)
        timeline = svc.get_timeline("inc-1")
        assert timeline["impact"]["consumers"] == 50
        assert timeline["impact"]["requests_lost"] == 1000

    def test_list_by_status(self):
        svc = IncidentTimelineManager()
        svc.create("inc-1", "A", "p2")
        svc.create("inc-2", "B", "p3")
        svc.add_event("inc-2", "resolved", "Done")
        active = svc.list_incidents(status="active")
        assert len(active) == 1

    def test_list_by_severity(self):
        svc = IncidentTimelineManager()
        svc.create("inc-1", "A", "p1")
        svc.create("inc-2", "B", "p3")
        p1 = svc.list_incidents(severity="p1")
        assert len(p1) == 1

    def test_stats(self):
        svc = IncidentTimelineManager()
        svc.create("inc-1", "A", "p1")
        svc.create("inc-2", "B", "p2")
        svc.add_event("inc-2", "resolved", "Done")
        stats = svc.get_stats()
        assert stats["active"] == 1
        assert stats["resolved"] == 1
        assert stats["by_severity"]["p1"] == 1

    def test_invalid_severity(self):
        svc = IncidentTimelineManager()
        with pytest.raises(ValueError):
            svc.create("inc-1", "X", "critical")

    def test_invalid_event_type(self):
        svc = IncidentTimelineManager()
        svc.create("inc-1", "X", "p2")
        with pytest.raises(ValueError):
            svc.add_event("inc-1", "escalated", "msg")

    def test_not_found(self):
        svc = IncidentTimelineManager()
        assert svc.get_timeline("missing") is None

    def test_isolation(self):
        a, b = IncidentTimelineManager(), IncidentTimelineManager()
        a.create("inc-1", "X", "p2")
        assert b.get_timeline("inc-1") is None
