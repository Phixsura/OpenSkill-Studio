from app.services.app_api_developer_platform_sdk_api_platform_webhook_delivery_cost_tracker import AppAPIDeveloperPlatformSDKApiPlatformWebhookDeliveryCostTracker

class TestDeliveryCostTracker:
    def test_record(self):
        t = AppAPIDeveloperPlatformSDKApiPlatformWebhookDeliveryCostTracker()
        c = t.record("inst-1", "https://a.com", 1000, 500, 50)
        assert c.avg_cost_cents == 0.5
        assert c.retry_cost_pct == 10.0

    def test_most_expensive(self):
        t = AppAPIDeveloperPlatformSDKApiPlatformWebhookDeliveryCostTracker()
        t.record("inst-1", "https://a.com", 1000, 500)
        t.record("inst-1", "https://b.com", 100, 5000)
        assert t.most_expensive("inst-1", 1)[0].destination == "https://b.com"

    def test_total_cost(self):
        t = AppAPIDeveloperPlatformSDKApiPlatformWebhookDeliveryCostTracker()
        t.record("inst-1", "https://a.com", 100, 500)
        t.record("inst-1", "https://b.com", 100, 300)
        assert t.total_cost("inst-1") == 800

    def test_isolation(self):
        t = AppAPIDeveloperPlatformSDKApiPlatformWebhookDeliveryCostTracker()
        t.record("inst-1", "https://a.com", 100, 500)
        assert t.total_cost("inst-2") == 0
