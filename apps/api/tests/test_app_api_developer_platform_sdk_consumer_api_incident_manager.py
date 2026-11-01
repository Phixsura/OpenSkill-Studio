"""Tests for Incident Manager service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_incident_manager import IncidentManager


class TestIncidentManager:
    def test_create_incident(self):
        svc = IncidentManager()
        result = svc.create("inc-1", "API Down", "critical", ["ep1", "ep2"])
        assert result["severity"] == "critical"
        assert result["status"] == "open"

    def test_update_status(self):
        svc = IncidentManager()
        svc.create("inc-1", "Slow API", "high")
        svc.update_status("inc-1", "investigating", "Looking into it", "alice")
        inc = svc.get_incident("inc-1")
        assert inc["status"] == "investigating"

    def test_resolve(self):
        svc = IncidentManager()
        svc.create("inc-1", "Bug", "medium")
        svc.update_status("inc-1", "resolved", "Fixed")
        inc = svc.get_incident("inc-1")
        assert inc["status"] == "resolved"
        assert inc["resolved_at"] is not None

    def test_timeline(self):
        svc = IncidentManager()
        svc.create("inc-1", "Issue", "low")
        svc.update_status("inc-1", "investigating")
        svc.update_status("inc-1", "resolved")
        timeline = svc.get_timeline("inc-1")
        assert len(timeline) == 3
        assert timeline[0]["status"] == "open"
        assert timeline[2]["status"] == "resolved"

    def test_list_by_status(self):
        svc = IncidentManager()
        svc.create("inc-1", "A", "high")
        svc.create("inc-2", "B", "low")
        svc.update_status("inc-2", "resolved")
        open_list = svc.list_incidents(status="open")
        assert len(open_list) == 1

    def test_list_by_severity(self):
        svc = IncidentManager()
        svc.create("inc-1", "A", "critical")
        svc.create("inc-2", "B", "low")
        critical = svc.list_incidents(severity="critical")
        assert len(critical) == 1

    def test_invalid_severity(self):
        svc = IncidentManager()
        with pytest.raises(ValueError):
            svc.create("inc-1", "X", "catastrophic")

    def test_invalid_status(self):
        svc = IncidentManager()
        svc.create("inc-1", "X", "high")
        with pytest.raises(ValueError):
            svc.update_status("inc-1", "unknown_status")

    def test_stats(self):
        svc = IncidentManager()
        svc.create("inc-1", "A", "critical")
        svc.create("inc-2", "B", "high")
        svc.update_status("inc-2", "resolved")
        stats = svc.get_stats()
        assert stats["open"] == 1
        assert stats["resolved"] == 1
        assert stats["by_severity"]["critical"] == 1

    def test_duplicate_incident(self):
        svc = IncidentManager()
        svc.create("inc-1", "A", "low")
        with pytest.raises(ValueError):
            svc.create("inc-1", "B", "low")

    def test_isolation(self):
        a, b = IncidentManager(), IncidentManager()
        a.create("inc-1", "A", "low")
        assert b.get_incident("inc-1") is None
