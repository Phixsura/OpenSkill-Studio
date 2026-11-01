from app.services.app_api_webhook_analytics import AppAPIWebhookAnalytics

class TestAnalytics:
    def test_update(self):
        a = AppAPIWebhookAnalytics()
        wa = a.update("inst-1", total_sent=1000, total_failed=50, avg_latency_ms=120.5)
        assert wa.success_rate == 95.2

    def test_default(self):
        a = AppAPIWebhookAnalytics()
        assert a.get("inst-1").total_sent == 0

    def test_isolation(self):
        a = AppAPIWebhookAnalytics()
        a.update("inst-1", total_sent=100)
        assert a.get("inst-2").total_sent == 0
