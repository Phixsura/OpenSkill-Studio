"""Tests for Consumer API Usage Alert service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_usage_alert import (
    UsageAlertManager, AlertThreshold,
)


class TestUsageAlertManager:
    def test_fire_alert(self):
        svc = UsageAlertManager()
        svc.add_threshold(AlertThreshold("t1", "error_rate", "gt", 5.0, "warning"))
        alerts = svc.evaluate("error_rate", 8.0)
        assert len(alerts) == 1
        assert alerts[0]["level"] == "warning"

    def test_no_fire_below(self):
        svc = UsageAlertManager()
        svc.add_threshold(AlertThreshold("t1", "error_rate", "gt", 5.0))
        alerts = svc.evaluate("error_rate", 3.0)
        assert len(alerts) == 0

    def test_cooldown(self):
        svc = UsageAlertManager()
        svc.add_threshold(AlertThreshold("t1", "cpu", "gt", 90, cooldown_seconds=60))
        svc.evaluate("cpu", 95, current_time=100)
        alerts = svc.evaluate("cpu", 95, current_time=120)  # within cooldown
        assert len(alerts) == 0
        alerts = svc.evaluate("cpu", 95, current_time=200)  # after cooldown
        assert len(alerts) == 1

    def test_lt_operator(self):
        svc = UsageAlertManager()
        svc.add_threshold(AlertThreshold("t1", "available", "lt", 10.0, "critical"))
        alerts = svc.evaluate("available", 5.0)
        assert len(alerts) == 1
        assert alerts[0]["level"] == "critical"

    def test_gte_operator(self):
        svc = UsageAlertManager()
        svc.add_threshold(AlertThreshold("t1", "latency", "gte", 100.0))
        assert len(svc.evaluate("latency", 100.0)) == 1
        assert len(svc.evaluate("latency", 99.0, current_time=1000)) == 0

    def test_disabled_threshold(self):
        svc = UsageAlertManager()
        svc.add_threshold(AlertThreshold("t1", "cpu", "gt", 90, enabled=False))
        alerts = svc.evaluate("cpu", 95)
        assert len(alerts) == 0

    def test_toggle(self):
        svc = UsageAlertManager()
        svc.add_threshold(AlertThreshold("t1", "cpu", "gt", 90))
        svc.toggle("t1", False)
        assert len(svc.evaluate("cpu", 95)) == 0

    def test_get_fired_alerts(self):
        svc = UsageAlertManager()
        svc.add_threshold(AlertThreshold("t1", "cpu", "gt", 90, "warning"))
        svc.add_threshold(AlertThreshold("t2", "cpu", "gt", 95, "critical"))
        svc.evaluate("cpu", 98)
        alerts = svc.get_fired_alerts(level="critical")
        assert len(alerts) == 1

    def test_stats(self):
        svc = UsageAlertManager()
        svc.add_threshold(AlertThreshold("t1", "cpu", "gt", 90))
        svc.evaluate("cpu", 95)
        stats = svc.get_stats()
        assert stats["total_fired"] == 1
        assert stats["total_thresholds"] == 1

    def test_duplicate_threshold(self):
        svc = UsageAlertManager()
        svc.add_threshold(AlertThreshold("t1", "cpu", "gt", 90))
        with pytest.raises(ValueError):
            svc.add_threshold(AlertThreshold("t1", "mem", "gt", 80))

    def test_invalid_level(self):
        svc = UsageAlertManager()
        with pytest.raises(ValueError):
            svc.add_threshold(AlertThreshold("t1", "cpu", "gt", 90, "emergency"))

    def test_isolation(self):
        a, b = UsageAlertManager(), UsageAlertManager()
        a.add_threshold(AlertThreshold("t1", "cpu", "gt", 90))
        a.evaluate("cpu", 95)
        assert b.get_stats()["total_fired"] == 0
