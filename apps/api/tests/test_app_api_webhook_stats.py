"""Tests for App API Webhook Stats — record, rates, latency."""

from app.services.app_api_webhook_stats import AppAPIWebhookStats


class TestRecord:
    def test_record(self):
        s = AppAPIWebhookStats()
        stats = s.record_delivery("inst-1", True, 45.0)
        assert stats.total_sent == 1

    def test_success_rate(self):
        s = AppAPIWebhookStats()
        for _ in range(8):
            s.record_delivery("inst-1", True, 50)
        for _ in range(2):
            s.record_delivery("inst-1", False, 100)
        assert s.get_stats("inst-1").success_rate == 80.0


class TestLatency:
    def test_avg(self):
        s = AppAPIWebhookStats()
        s.record_delivery("inst-1", True, 100)
        s.record_delivery("inst-1", True, 200)
        assert s.get_stats("inst-1").avg_latency == 150.0

    def test_p95(self):
        s = AppAPIWebhookStats()
        for i in range(100):
            s.record_delivery("inst-1", True, float(i))
        assert s.get_stats("inst-1").p95_latency == 95.0


class TestIsolation:
    def test_cross(self):
        s = AppAPIWebhookStats()
        s.record_delivery("inst-1", True, 50)
        assert s.get_stats("inst-2").total_sent == 0
