"""Tests for App Status Page Builder — components, system status, incidents, maintenance."""

from datetime import UTC, datetime, timedelta

import pytest

from app.services.app_status_page_builder import (
    ActiveIncident,
    AppStatusPageBuilder,
    ComponentStatus,
    MaintenanceWindow,
    StatusComponent,
    SystemStatus,
)


class TestSystemStatus:
    def test_all_operational(self):
        b = AppStatusPageBuilder()
        b.set_components("app-1", [
            StatusComponent("API", ComponentStatus.OPERATIONAL),
            StatusComponent("Dashboard", ComponentStatus.OPERATIONAL),
        ])
        page = b.build("app-1", "My App")
        assert page.system_status == SystemStatus.ALL_OPERATIONAL

    def test_minor_issues(self):
        b = AppStatusPageBuilder()
        b.set_components("app-1", [
            StatusComponent("API", ComponentStatus.OPERATIONAL),
            StatusComponent("Webhooks", ComponentStatus.DEGRADED),
        ])
        page = b.build("app-1", "My App")
        assert page.system_status == SystemStatus.MINOR_ISSUES

    def test_major_issues(self):
        b = AppStatusPageBuilder()
        b.set_components("app-1", [
            StatusComponent("API", ComponentStatus.PARTIAL_OUTAGE),
            StatusComponent("Dashboard", ComponentStatus.OPERATIONAL),
        ])
        page = b.build("app-1", "My App")
        assert page.system_status == SystemStatus.MAJOR_ISSUES

    def test_outage(self):
        b = AppStatusPageBuilder()
        b.set_components("app-1", [
            StatusComponent("API", ComponentStatus.MAJOR_OUTAGE),
        ])
        page = b.build("app-1", "My App")
        assert page.system_status == SystemStatus.OUTAGE

    def test_no_components(self):
        b = AppStatusPageBuilder()
        page = b.build("app-1", "My App")
        assert page.system_status == SystemStatus.ALL_OPERATIONAL


class TestComponents:
    def test_components_in_page(self):
        b = AppStatusPageBuilder()
        b.set_components("app-1", [
            StatusComponent("API", ComponentStatus.OPERATIONAL, uptime_pct=99.95),
            StatusComponent("Webhooks", ComponentStatus.DEGRADED, uptime_pct=98.5),
        ])
        page = b.build("app-1", "My App")
        assert len(page.components) == 2
        assert page.components[0].name == "API"
        assert page.components[0].uptime_pct == 99.95

    def test_app_name(self):
        b = AppStatusPageBuilder()
        page = b.build("app-1", "Cool App")
        assert page.app_name == "Cool App"


class TestIncidents:
    def test_incidents_embedded(self):
        b = AppStatusPageBuilder()
        b.set_incidents("app-1", [
            ActiveIncident("API Latency", "investigating", "major",
                           datetime.now(UTC), "Looking into it"),
        ])
        page = b.build("app-1", "App")
        assert len(page.active_incidents) == 1
        assert page.active_incidents[0].title == "API Latency"

    def test_no_incidents(self):
        b = AppStatusPageBuilder()
        page = b.build("app-1", "App")
        assert page.active_incidents == []


class TestMaintenance:
    def test_active_maintenance(self):
        b = AppStatusPageBuilder()
        b.set_components("app-1", [StatusComponent("API", ComponentStatus.OPERATIONAL)])
        now = datetime.now(UTC)
        b.add_maintenance("app-1", MaintenanceWindow(
            "DB Migration", now - timedelta(hours=1), now + timedelta(hours=1),
            ["API"], "Upgrading database",
        ))
        page = b.build("app-1", "App")
        assert len(page.maintenance_windows) == 1
        # API should be marked as maintenance
        assert page.components[0].status == ComponentStatus.MAINTENANCE

    def test_upcoming_maintenance(self):
        b = AppStatusPageBuilder()
        b.set_components("app-1", [StatusComponent("API", ComponentStatus.OPERATIONAL)])
        future = datetime.now(UTC) + timedelta(days=1)
        b.add_maintenance("app-1", MaintenanceWindow(
            "Planned Update", future, future + timedelta(hours=2), ["API"],
        ))
        page = b.build("app-1", "App")
        assert len(page.maintenance_windows) == 1
        # API should NOT be marked as maintenance (not yet active)
        assert page.components[0].status == ComponentStatus.OPERATIONAL

    def test_past_maintenance_excluded(self):
        b = AppStatusPageBuilder()
        past = datetime.now(UTC) - timedelta(days=2)
        b.add_maintenance("app-1", MaintenanceWindow(
            "Old", past, past + timedelta(hours=1), ["API"],
        ))
        page = b.build("app-1", "App")
        assert len(page.maintenance_windows) == 0

    def test_maintenance_system_status(self):
        b = AppStatusPageBuilder()
        b.set_components("app-1", [
            StatusComponent("API", ComponentStatus.OPERATIONAL),
            StatusComponent("DB", ComponentStatus.OPERATIONAL),
        ])
        now = datetime.now(UTC)
        b.add_maintenance("app-1", MaintenanceWindow(
            "DB Maintenance", now - timedelta(minutes=30), now + timedelta(hours=1),
            ["DB"],
        ))
        page = b.build("app-1", "App")
        assert page.system_status == SystemStatus.MINOR_ISSUES


class TestGenerated:
    def test_generated_at(self):
        b = AppStatusPageBuilder()
        page = b.build("app-1", "App")
        assert page.generated_at is not None
