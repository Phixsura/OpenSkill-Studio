"""Tests for Consumer API Status Page service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_status_page import (
    StatusPage, Component, MaintenanceWindow,
)


class TestStatusPage:
    def test_add_and_get_page(self):
        svc = StatusPage()
        svc.add_component(Component("api", "API", "Core"))
        svc.add_component(Component("db", "Database", "Core"))
        page = svc.get_page()
        assert page["overall_status"] == "all_systems_operational"
        assert page["component_count"] == 2

    def test_degraded_overall(self):
        svc = StatusPage()
        svc.add_component(Component("api", "API", status="operational"))
        svc.add_component(Component("search", "Search", status="degraded_performance"))
        page = svc.get_page()
        assert page["overall_status"] == "degraded_performance"

    def test_major_outage(self):
        svc = StatusPage()
        svc.add_component(Component("db", "DB", status="major_outage"))
        assert svc.get_page()["overall_status"] == "major_outage"

    def test_update_status_history(self):
        svc = StatusPage()
        svc.add_component(Component("api", "API"))
        svc.update_status("api", "partial_outage", "Investigating issue")
        page = svc.get_page()
        assert len(page["recent_updates"]) == 1
        assert page["recent_updates"][0]["to"] == "partial_outage"

    def test_maintenance_window(self):
        svc = StatusPage()
        svc.add_component(Component("api", "API"))
        svc.schedule_maintenance(MaintenanceWindow(
            "m1", "DB Upgrade", "2024-01-15T02:00:00Z", "2024-01-15T04:00:00Z",
            affected_components=["api"],
        ))
        page = svc.get_page()
        assert len(page["scheduled_maintenance"]) == 1

    def test_groups(self):
        svc = StatusPage()
        svc.add_component(Component("api", "API", "Core"))
        svc.add_component(Component("cdn", "CDN", "Edge"))
        page = svc.get_page()
        assert "Core" in page["groups"]
        assert "Edge" in page["groups"]

    def test_uptime(self):
        svc = StatusPage()
        svc.add_component(Component("a", "A", status="operational"))
        svc.add_component(Component("b", "B", status="major_outage"))
        uptime = svc.get_uptime()
        assert uptime["uptime_pct"] == 50.0

    def test_invalid_status(self):
        svc = StatusPage()
        svc.add_component(Component("api", "API"))
        with pytest.raises(ValueError):
            svc.update_status("api", "broken")

    def test_duplicate_component(self):
        svc = StatusPage()
        svc.add_component(Component("api", "API"))
        with pytest.raises(ValueError):
            svc.add_component(Component("api", "API2"))

    def test_isolation(self):
        a, b = StatusPage(), StatusPage()
        a.add_component(Component("api", "API"))
        assert b.get_page()["component_count"] == 0
