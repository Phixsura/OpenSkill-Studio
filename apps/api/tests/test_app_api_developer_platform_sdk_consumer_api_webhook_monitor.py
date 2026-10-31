"""Tests for Consumer API Webhook Monitoring service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_webhook_monitor import (
    WebhookMonitor, WebhookPing,
)


class TestWebhookMonitor:
    def test_ping_success(self):
        svc = WebhookMonitor()
        result = svc.ping(WebhookPing("wh1", 100.0, True, 45.0))
        assert result["success"] is True
        assert "alert" not in result

    def test_consecutive_failure_alert(self):
        svc = WebhookMonitor()
        svc.configure(alert_threshold=3)
        svc.ping(WebhookPing("wh1", 1.0, False, 0, 500))
        svc.ping(WebhookPing("wh1", 2.0, False, 0, 500))
        result = svc.ping(WebhookPing("wh1", 3.0, False, 0, 500))
        assert result["alert"] is True

    def test_no_alert_with_success(self):
        svc = WebhookMonitor()
        svc.configure(alert_threshold=3)
        svc.ping(WebhookPing("wh1", 1.0, False, 0))
        svc.ping(WebhookPing("wh1", 2.0, True, 50.0))
        result = svc.ping(WebhookPing("wh1", 3.0, False, 0))
        assert "alert" not in result

    def test_health_healthy(self):
        svc = WebhookMonitor()
        for i in range(20):
            svc.ping(WebhookPing("wh1", float(i), True, 50.0))
        health = svc.get_health("wh1")
        assert health["status"] == "healthy"
        assert health["success_rate"] == 100.0

    def test_health_degraded(self):
        svc = WebhookMonitor()
        for i in range(18):
            svc.ping(WebhookPing("wh1", float(i), True, 50.0))
        svc.ping(WebhookPing("wh1", 18.0, False, 0))
        svc.ping(WebhookPing("wh1", 19.0, False, 0))
        health = svc.get_health("wh1")
        assert health["status"] == "degraded"

    def test_health_unknown(self):
        svc = WebhookMonitor()
        assert svc.get_health("missing")["status"] == "unknown"

    def test_get_all_health(self):
        svc = WebhookMonitor()
        svc.ping(WebhookPing("wh1", 1.0, True, 50.0))
        svc.ping(WebhookPing("wh2", 1.0, False, 0))
        results = svc.get_all_health()
        assert len(results) == 2
        # Sorted by success rate ascending
        assert results[0]["webhook_id"] == "wh2"

    def test_timeline(self):
        svc = WebhookMonitor()
        for i in range(5):
            svc.ping(WebhookPing("wh1", float(i), True, 50.0))
        timeline = svc.get_timeline("wh1", limit=3)
        assert len(timeline) == 3

    def test_stats(self):
        svc = WebhookMonitor()
        svc.ping(WebhookPing("wh1", 1.0, True, 50.0))
        svc.ping(WebhookPing("wh1", 2.0, False, 0))
        stats = svc.get_stats()
        assert stats["webhooks_monitored"] == 1
        assert stats["total_pings"] == 2
        assert stats["overall_success_rate"] == 50.0

    def test_invalid_threshold(self):
        svc = WebhookMonitor()
        with pytest.raises(ValueError):
            svc.configure(alert_threshold=0)

    def test_isolation(self):
        a, b = WebhookMonitor(), WebhookMonitor()
        a.ping(WebhookPing("wh1", 1.0, True, 50.0))
        assert b.get_stats()["webhooks_monitored"] == 0
