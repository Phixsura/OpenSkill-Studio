"""Tests for App Maintenance Window — schedule, lifecycle, upcoming."""

import pytest

from app.services.app_maintenance_window import AppMaintenanceWindow, WindowStatus


class TestSchedule:
    def test_schedule(self):
        m = AppMaintenanceWindow()
        w = m.schedule("inst-1", "w1", "DB Migration", "Upgrading schema",
                       start_at=2000.0, end_at=2100.0, affected_services=["db", "api"])
        assert w.status == WindowStatus.SCHEDULED
        assert w.affected_services == ["db", "api"]

    def test_invalid_range(self):
        m = AppMaintenanceWindow()
        with pytest.raises(ValueError, match="end_at"):
            m.schedule("inst-1", "w1", "X", "Y", start_at=2000, end_at=1000)

    def test_duplicate(self):
        m = AppMaintenanceWindow()
        m.schedule("inst-1", "w1", "X", "Y", start_at=1000, end_at=2000)
        with pytest.raises(ValueError, match="already exists"):
            m.schedule("inst-1", "w1", "Z", "W", start_at=3000, end_at=4000)


class TestLifecycle:
    def test_activate(self):
        m = AppMaintenanceWindow()
        m.schedule("inst-1", "w1", "X", "Y", start_at=1000, end_at=2000)
        w = m.activate("inst-1", "w1")
        assert w.status == WindowStatus.ACTIVE

    def test_complete(self):
        m = AppMaintenanceWindow()
        m.schedule("inst-1", "w1", "X", "Y", start_at=1000, end_at=2000)
        m.activate("inst-1", "w1")
        w = m.complete("inst-1", "w1")
        assert w.status == WindowStatus.COMPLETED

    def test_cancel_scheduled(self):
        m = AppMaintenanceWindow()
        m.schedule("inst-1", "w1", "X", "Y", start_at=1000, end_at=2000)
        w = m.cancel("inst-1", "w1")
        assert w.status == WindowStatus.CANCELLED

    def test_cannot_complete_scheduled(self):
        m = AppMaintenanceWindow()
        m.schedule("inst-1", "w1", "X", "Y", start_at=1000, end_at=2000)
        with pytest.raises(ValueError):
            m.complete("inst-1", "w1")

    def test_cannot_cancel_completed(self):
        m = AppMaintenanceWindow()
        m.schedule("inst-1", "w1", "X", "Y", start_at=1000, end_at=2000)
        m.activate("inst-1", "w1")
        m.complete("inst-1", "w1")
        with pytest.raises(ValueError):
            m.cancel("inst-1", "w1")


class TestMaintenance:
    def test_in_maintenance(self):
        m = AppMaintenanceWindow()
        m.schedule("inst-1", "w1", "X", "Y", start_at=1000, end_at=2000)
        m.activate("inst-1", "w1")
        assert m.is_in_maintenance("inst-1") is True

    def test_not_in_maintenance(self):
        m = AppMaintenanceWindow()
        m.schedule("inst-1", "w1", "X", "Y", start_at=1000, end_at=2000)
        assert m.is_in_maintenance("inst-1") is False


class TestUpcoming:
    def test_sorted_by_start(self):
        m = AppMaintenanceWindow()
        m.schedule("inst-1", "w2", "Later", "Y", start_at=3000, end_at=4000)
        m.schedule("inst-1", "w1", "Sooner", "Y", start_at=1000, end_at=2000)
        upcoming = m.get_upcoming("inst-1")
        assert upcoming[0].title == "Sooner"

    def test_excludes_completed(self):
        m = AppMaintenanceWindow()
        m.schedule("inst-1", "w1", "X", "Y", start_at=1000, end_at=2000)
        m.activate("inst-1", "w1")
        m.complete("inst-1", "w1")
        assert m.get_upcoming("inst-1") == []


class TestIsolation:
    def test_cross_installation(self):
        m = AppMaintenanceWindow()
        m.schedule("inst-1", "w1", "X", "Y", start_at=1000, end_at=2000)
        with pytest.raises(KeyError):
            m._get("inst-2", "w1")
