"""Tests for App Usage Alert — thresholds, levels, acknowledgment."""

import pytest

from app.services.app_usage_alert import AlertLevel, AppUsageAlert


class TestSetThreshold:
    def test_set(self):
        a = AppUsageAlert()
        t = a.set_threshold("inst-1", "api_calls", limit=1000, warning_pct=80, critical_pct=95)
        assert t.limit == 1000

    def test_invalid_limit(self):
        a = AppUsageAlert()
        with pytest.raises(ValueError, match="positive"):
            a.set_threshold("inst-1", "x", limit=0)

    def test_invalid_thresholds(self):
        a = AppUsageAlert()
        with pytest.raises(ValueError, match="thresholds"):
            a.set_threshold("inst-1", "x", limit=100, warning_pct=95, critical_pct=80)


class TestCheck:
    def test_ok(self):
        a = AppUsageAlert()
        a.set_threshold("inst-1", "api_calls", limit=1000)
        s = a.check("inst-1", "api_calls", 500)
        assert s.level == AlertLevel.OK
        assert s.usage_pct == 50.0

    def test_warning(self):
        a = AppUsageAlert()
        a.set_threshold("inst-1", "api_calls", limit=1000, warning_pct=80, critical_pct=95)
        s = a.check("inst-1", "api_calls", 850)
        assert s.level == AlertLevel.WARNING

    def test_critical(self):
        a = AppUsageAlert()
        a.set_threshold("inst-1", "api_calls", limit=1000, warning_pct=80, critical_pct=95)
        s = a.check("inst-1", "api_calls", 960)
        assert s.level == AlertLevel.CRITICAL

    def test_unknown_metric(self):
        a = AppUsageAlert()
        with pytest.raises(KeyError):
            a.check("inst-1", "nope", 100)


class TestAcknowledge:
    def test_ack(self):
        a = AppUsageAlert()
        a.set_threshold("inst-1", "api_calls", limit=1000)
        a.acknowledge("inst-1", "api_calls")
        s = a.check("inst-1", "api_calls", 900)
        assert s.acknowledged is True

    def test_reset_ack(self):
        a = AppUsageAlert()
        a.set_threshold("inst-1", "api_calls", limit=1000)
        a.acknowledge("inst-1", "api_calls")
        a.reset_ack("inst-1", "api_calls")
        s = a.check("inst-1", "api_calls", 900)
        assert s.acknowledged is False


class TestCheckAll:
    def test_multiple_metrics(self):
        a = AppUsageAlert()
        a.set_threshold("inst-1", "api_calls", limit=1000)
        a.set_threshold("inst-1", "storage_mb", limit=500)
        results = a.check_all("inst-1", {"api_calls": 900, "storage_mb": 100})
        assert len(results) == 2


class TestIsolation:
    def test_cross_installation(self):
        a = AppUsageAlert()
        a.set_threshold("inst-1", "api_calls", limit=1000)
        with pytest.raises(KeyError):
            a.check("inst-2", "api_calls", 500)
