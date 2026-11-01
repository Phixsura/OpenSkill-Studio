"""Tests for App Maintenance Window — schedule, lifecycle, service check."""

import pytest
import time

from app.services.app_maintenance_window import AppMaintenanceWindow, WindowStatus


class TestSchedule:
    def test_schedule(self):
        m = AppMaintenanceWindow()
        now = time.time()
        w = m.schedule("inst-1", "w1", "DB Upgrade", now + 3600, now + 7200, ["db"])
        assert w.status == WindowStatus.SCHEDULED
        assert w.duration_minutes == 60.0

    def test_invalid_times(self):
        m = AppMaintenanceWindow()
        with pytest.raises(ValueError, match="after"):
            m.schedule("inst-1", "w1", "Bad", 100, 50)


class TestLifecycle:
    def test_activate_complete(self):
        m = AppMaintenanceWindow()
        now = time.time()
        m.schedule("inst-1", "w1", "Upgrade", now, now + 3600)
        m.activate("inst-1", "w1")
        w = m.complete("inst-1", "w1")
        assert w.status == WindowStatus.COMPLETED

    def test_cancel(self):
        m = AppMaintenanceWindow()
        now = time.time()
        m.schedule("inst-1", "w1", "Upgrade", now, now + 3600)
        w = m.cancel("inst-1", "w1")
        assert w.status == WindowStatus.CANCELLED


class TestMaintenanceCheck:
    def test_in_maintenance(self):
        m = AppMaintenanceWindow()
        now = time.time()
        m.schedule("inst-1", "w1", "Upgrade", now, now + 3600, ["db", "api"])
        m.activate("inst-1", "w1")
        assert m.is_in_maintenance("inst-1", "db") is True
        assert m.is_in_maintenance("inst-1", "cache") is False

    def test_not_in_maintenance(self):
        m = AppMaintenanceWindow()
        assert m.is_in_maintenance("inst-1") is False


class TestIsolation:
    def test_cross(self):
        m = AppMaintenanceWindow()
        now = time.time()
        m.schedule("inst-1", "w1", "Upgrade", now, now + 3600)
        assert m.list_windows("inst-2") == []
