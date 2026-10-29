from app.services.app_api_webhook_health_dashboard import AppAPIWebhookHealthDashboard

class TestDashboard:
    def test_healthy(self):
        d = AppAPIWebhookHealthDashboard()
        dash = d.update("inst-1", total_destinations=10, healthy_count=10, success_rate=99.9)
        assert dash.overall_status == "healthy"

    def test_degraded(self):
        d = AppAPIWebhookHealthDashboard()
        dash = d.update("inst-1", degraded_count=2, success_rate=92.0)
        assert dash.overall_status == "degraded"

    def test_critical(self):
        d = AppAPIWebhookHealthDashboard()
        dash = d.update("inst-1", down_count=1)
        assert dash.overall_status == "critical"

    def test_isolation(self):
        d = AppAPIWebhookHealthDashboard()
        d.update("inst-1", total_destinations=5)
        assert d.get("inst-2").total_destinations == 0
