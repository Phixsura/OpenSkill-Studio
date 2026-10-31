"""Tests for Consumer Webhook Dashboard service."""
from app.services.app_api_developer_platform_sdk_consumer_api_webhook_dashboard import (
    WebhookDashboard, DeliveryEvent,
)


class TestWebhookDashboard:
    def test_record_and_health(self):
        svc = WebhookDashboard()
        for i in range(10):
            svc.record(DeliveryEvent("wh1", f"t{i}", 200, 50.0))
        health = svc.get_webhook_health("wh1")
        assert health["health"] == "healthy"
        assert health["success_rate"] == 100.0

    def test_degraded_health(self):
        svc = WebhookDashboard()
        for i in range(9):
            svc.record(DeliveryEvent("wh1", f"t{i}", 200, 50.0))
        svc.record(DeliveryEvent("wh1", "t9", 500, 100.0))
        health = svc.get_webhook_health("wh1")
        assert health["health"] == "degraded"

    def test_critical_health(self):
        svc = WebhookDashboard()
        for i in range(5):
            svc.record(DeliveryEvent("wh1", f"t{i}", 200, 50.0))
        for i in range(5):
            svc.record(DeliveryEvent("wh1", f"f{i}", 500, 100.0))
        health = svc.get_webhook_health("wh1")
        assert health["health"] == "critical"

    def test_overview(self):
        svc = WebhookDashboard()
        for i in range(10):
            svc.record(DeliveryEvent("wh1", f"t{i}", 200, 30.0))
        for i in range(5):
            svc.record(DeliveryEvent("wh2", f"t{i}", 500, 100.0))
        overview = svc.get_overview()
        assert overview["total_webhooks"] == 2
        assert overview["healthy"] == 1
        assert overview["total_deliveries"] == 15

    def test_empty_overview(self):
        svc = WebhookDashboard()
        assert svc.get_overview()["total_webhooks"] == 0

    def test_top_failures(self):
        svc = WebhookDashboard()
        for i in range(3):
            svc.record(DeliveryEvent("wh1", f"t{i}", 500, 50.0))
        svc.record(DeliveryEvent("wh2", "t0", 500, 50.0))
        top = svc.get_top_failures()
        assert top[0]["webhook_id"] == "wh1"

    def test_latency_ranking(self):
        svc = WebhookDashboard()
        svc.record(DeliveryEvent("fast", "t0", 200, 10.0))
        svc.record(DeliveryEvent("slow", "t0", 200, 500.0))
        ranking = svc.get_latency_ranking()
        assert ranking[0]["webhook_id"] == "slow"

    def test_retry_tracking(self):
        svc = WebhookDashboard()
        svc.record(DeliveryEvent("wh1", "t0", 200, 50.0, retry_count=2))
        svc.record(DeliveryEvent("wh1", "t1", 200, 50.0, retry_count=1))
        health = svc.get_webhook_health("wh1")
        assert health["total_retries"] == 3

    def test_no_data(self):
        svc = WebhookDashboard()
        assert svc.get_webhook_health("missing")["status"] == "no_data"

    def test_isolation(self):
        a, b = WebhookDashboard(), WebhookDashboard()
        a.record(DeliveryEvent("wh1", "t0", 200, 50.0))
        assert b.get_overview()["total_webhooks"] == 0
