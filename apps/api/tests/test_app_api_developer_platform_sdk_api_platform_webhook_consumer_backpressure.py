from app.services.app_api_developer_platform_sdk_api_platform_webhook_consumer_backpressure import AppAPIDeveloperPlatformSDKApiPlatformWebhookConsumerBackpressure

class TestConsumerBackpressure:
    def test_normal(self):
        b = AppAPIDeveloperPlatformSDKApiPlatformWebhookConsumerBackpressure()
        s = b.update("inst-1", "https://a.com", 50, 100)
        assert s.pressure_level == "normal"

    def test_critical(self):
        b = AppAPIDeveloperPlatformSDKApiPlatformWebhookConsumerBackpressure()
        s = b.update("inst-1", "https://a.com", 15000, 10, 200)
        assert s.pressure_level == "critical"
        assert s.backpressure_active is True

    def test_drain_estimate(self):
        b = AppAPIDeveloperPlatformSDKApiPlatformWebhookConsumerBackpressure()
        s = b.update("inst-1", "https://a.com", 1000, 100)
        assert s.estimated_drain_seconds == 10.0

    def test_under_pressure(self):
        b = AppAPIDeveloperPlatformSDKApiPlatformWebhookConsumerBackpressure()
        b.update("inst-1", "https://a.com", 50, 100)
        b.update("inst-1", "https://b.com", 5000, 10)
        assert len(b.under_pressure("inst-1")) == 1

    def test_isolation(self):
        b = AppAPIDeveloperPlatformSDKApiPlatformWebhookConsumerBackpressure()
        b.update("inst-1", "https://a.com", 5000, 10)
        assert len(b.all_states("inst-2")) == 0
