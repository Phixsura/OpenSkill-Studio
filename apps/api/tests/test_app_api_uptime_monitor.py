"""Tests for App API Uptime Monitor — register, check, uptime %."""

import pytest

from app.services.app_api_uptime_monitor import AppAPIUptimeMonitor


class TestRegister:
    def test_register(self):
        u = AppAPIUptimeMonitor()
        m = u.register("inst-1", "m1", "API")
        assert m.uptime_pct == 100.0


class TestCheck:
    def test_uptime(self):
        u = AppAPIUptimeMonitor()
        u.register("inst-1", "m1", "API")
        for _ in range(9):
            u.record_check("inst-1", "m1", True)
        u.record_check("inst-1", "m1", False)
        m = u.get_monitor("inst-1", "m1")
        assert m.uptime_pct == 90.0

    def test_consecutive_down(self):
        u = AppAPIUptimeMonitor()
        u.register("inst-1", "m1", "API")
        u.record_check("inst-1", "m1", False)
        u.record_check("inst-1", "m1", False)
        assert u.get_monitor("inst-1", "m1").consecutive_down == 2
        u.record_check("inst-1", "m1", True)
        assert u.get_monitor("inst-1", "m1").consecutive_down == 0

    def test_down_monitors(self):
        u = AppAPIUptimeMonitor()
        u.register("inst-1", "m1", "API")
        u.register("inst-1", "m2", "DB")
        u.record_check("inst-1", "m1", False)
        u.record_check("inst-1", "m2", True)
        assert len(u.down_monitors("inst-1")) == 1


class TestIsolation:
    def test_cross(self):
        u = AppAPIUptimeMonitor()
        u.register("inst-1", "m1", "API")
        assert u.list_monitors("inst-2") == []
