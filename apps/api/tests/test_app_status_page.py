"""Tests for App Status Page — components, incidents, overall status."""

import pytest

from app.services.app_status_page import AppStatusPage, ComponentStatus


class TestComponent:
    def test_add(self):
        s = AppStatusPage()
        c = s.add_component("inst-1", "api", "API Service")
        assert c.status == ComponentStatus.OPERATIONAL

    def test_update_status(self):
        s = AppStatusPage()
        s.add_component("inst-1", "api", "API")
        c = s.update_status("inst-1", "api", ComponentStatus.DEGRADED)
        assert c.status == ComponentStatus.DEGRADED


class TestOverall:
    def test_all_operational(self):
        s = AppStatusPage()
        s.add_component("inst-1", "api", "API")
        s.add_component("inst-1", "db", "Database")
        assert s.overall_status("inst-1") == ComponentStatus.OPERATIONAL

    def test_worst_wins(self):
        s = AppStatusPage()
        s.add_component("inst-1", "api", "API")
        s.add_component("inst-1", "db", "Database")
        s.update_status("inst-1", "db", ComponentStatus.MAJOR_OUTAGE)
        assert s.overall_status("inst-1") == ComponentStatus.MAJOR_OUTAGE


class TestIncident:
    def test_add_incident(self):
        s = AppStatusPage()
        i = s.add_incident("inst-1", "inc-1", "API Down", ["api"])
        assert i.status == "investigating"

    def test_resolve(self):
        s = AppStatusPage()
        s.add_incident("inst-1", "inc-1", "API Down")
        i = s.resolve_incident("inst-1", "inc-1")
        assert i.status == "resolved"
        assert s.active_incidents("inst-1") == []


class TestIsolation:
    def test_cross(self):
        s = AppStatusPage()
        s.add_component("inst-1", "api", "API")
        assert s.list_components("inst-2") == []
