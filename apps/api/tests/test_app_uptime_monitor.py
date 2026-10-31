"""Tests for App Uptime Monitor — state changes, uptime, downtimes."""

import pytest

from app.services.app_uptime_monitor import AppUptimeMonitor


class TestRecordState:
    def test_record(self):
        m = AppUptimeMonitor()
        s = m.record_state("inst-1", "api", True, now=1000.0)
        assert s.is_up is True

    def test_is_up(self):
        m = AppUptimeMonitor()
        m.record_state("inst-1", "api", True, now=1000.0)
        assert m.is_up("inst-1", "api") is True
        m.record_state("inst-1", "api", False, now=1001.0)
        assert m.is_up("inst-1", "api") is False

    def test_default_is_up(self):
        m = AppUptimeMonitor()
        assert m.is_up("inst-1", "api") is True


class TestUptimePct:
    def test_100_pct(self):
        m = AppUptimeMonitor()
        m.record_state("inst-1", "api", True, now=1000.0)
        assert m.uptime_pct("inst-1", "api", since=1000.0, until=2000.0) == 100.0

    def test_50_pct(self):
        m = AppUptimeMonitor()
        m.record_state("inst-1", "api", True, now=1000.0)
        m.record_state("inst-1", "api", False, now=1500.0)
        pct = m.uptime_pct("inst-1", "api", since=1000.0, until=2000.0)
        assert pct == 50.0

    def test_downtime_then_recovery(self):
        m = AppUptimeMonitor()
        m.record_state("inst-1", "api", True, now=1000.0)
        m.record_state("inst-1", "api", False, now=1200.0)
        m.record_state("inst-1", "api", True, now=1400.0)
        pct = m.uptime_pct("inst-1", "api", since=1000.0, until=2000.0)
        # Up: 200 (1000-1200) + 600 (1400-2000) = 800 / 1000 = 80%
        assert pct == 80.0

    def test_no_data(self):
        m = AppUptimeMonitor()
        assert m.uptime_pct("inst-1", "api") == 100.0


class TestDowntimes:
    def test_downtime_windows(self):
        m = AppUptimeMonitor()
        m.record_state("inst-1", "api", True, now=1000.0)
        m.record_state("inst-1", "api", False, reason="deploy", now=1200.0)
        m.record_state("inst-1", "api", True, now=1400.0)
        windows = m.get_downtimes("inst-1", "api")
        assert len(windows) == 1
        assert windows[0].duration_seconds == 200.0
        assert windows[0].reason == "deploy"

    def test_ongoing_downtime(self):
        m = AppUptimeMonitor()
        m.record_state("inst-1", "api", False, now=1000.0)
        windows = m.get_downtimes("inst-1", "api")
        assert len(windows) == 1
        assert windows[0].ended_at is None


class TestListServices:
    def test_list(self):
        m = AppUptimeMonitor()
        m.record_state("inst-1", "api", True)
        m.record_state("inst-1", "db", True)
        assert m.list_services("inst-1") == ["api", "db"]


class TestIsolation:
    def test_cross_installation(self):
        m = AppUptimeMonitor()
        m.record_state("inst-1", "api", False)
        assert m.is_up("inst-2", "api") is True
