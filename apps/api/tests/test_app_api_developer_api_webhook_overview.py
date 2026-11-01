from app.services.app_api_developer_api_webhook_overview import AppAPIDeveloperAPIWebhookOverview

class TestWebhookOverview:
    def test_update(self):
        o = AppAPIDeveloperAPIWebhookOverview()
        wo = o.update("inst-1", total_events_emitted=100000, total_deliveries=95000, success_rate=99.5, dead_letters=50)
        assert wo.total_events_emitted == 100000

    def test_default(self):
        o = AppAPIDeveloperAPIWebhookOverview()
        assert o.get("inst-1").success_rate == 100.0

    def test_isolation(self):
        o = AppAPIDeveloperAPIWebhookOverview()
        o.update("inst-1", total_deliveries=5000)
        assert o.get("inst-2").total_deliveries == 0
