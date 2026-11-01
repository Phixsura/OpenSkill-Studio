"""Tests for App API Webhook Delivery Metric — record, rank, slow."""

from app.services.app_api_webhook_delivery_metric import AppAPIWebhookDeliveryMetric


class TestRecord:
    def test_record(self):
        m = AppAPIWebhookDeliveryMetric()
        dm = m.record("inst-1", "https://a.com", True, 50.0)
        assert dm.deliveries == 1
        assert dm.success_rate == 100.0

    def test_accumulate(self):
        m = AppAPIWebhookDeliveryMetric()
        m.record("inst-1", "https://a.com", True, 50)
        m.record("inst-1", "https://a.com", False, 100)
        dm = m.top_destinations("inst-1")[0]
        assert dm.success_rate == 50.0
        assert dm.avg_latency == 75.0


class TestQuery:
    def test_top(self):
        m = AppAPIWebhookDeliveryMetric()
        for _ in range(10):
            m.record("inst-1", "https://a.com", True, 50)
        for _ in range(3):
            m.record("inst-1", "https://b.com", True, 50)
        top = m.top_destinations("inst-1")
        assert top[0].destination == "https://a.com"

    def test_slow(self):
        m = AppAPIWebhookDeliveryMetric()
        m.record("inst-1", "https://fast.com", True, 50)
        m.record("inst-1", "https://slow.com", True, 2000)
        slow = m.slow_destinations("inst-1", threshold_ms=1000)
        assert len(slow) == 1
        assert slow[0].destination == "https://slow.com"


class TestIsolation:
    def test_cross(self):
        m = AppAPIWebhookDeliveryMetric()
        m.record("inst-1", "https://a.com", True, 50)
        assert m.top_destinations("inst-2") == []
