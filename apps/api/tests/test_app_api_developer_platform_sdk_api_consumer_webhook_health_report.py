from app.services.app_api_developer_platform_sdk_api_consumer_webhook_health_report import AppAPIDeveloperPlatformSDKApiConsumerWebhookHealthReport

class TestConsumerWebhookHealth:
    def test_update(self):
        r = AppAPIDeveloperPlatformSDKApiConsumerWebhookHealthReport()
        h = r.update("inst-1", "c1", total_deliveries=1000, successful_deliveries=990, failed_deliveries=10)
        assert h.success_rate == 99.0
        assert h.health_grade == "A"

    def test_unhealthy(self):
        r = AppAPIDeveloperPlatformSDKApiConsumerWebhookHealthReport()
        r.update("inst-1", "c1", total_deliveries=100, successful_deliveries=99, failed_deliveries=1)
        r.update("inst-1", "c2", total_deliveries=100, successful_deliveries=80, failed_deliveries=20)
        assert len(r.unhealthy("inst-1")) == 1

    def test_ranked(self):
        r = AppAPIDeveloperPlatformSDKApiConsumerWebhookHealthReport()
        r.update("inst-1", "c1", total_deliveries=100, successful_deliveries=99)
        r.update("inst-1", "c2", total_deliveries=100, successful_deliveries=80)
        ranked = r.ranked("inst-1")
        assert ranked[0].consumer_id == "c2"  # worst first

    def test_isolation(self):
        r = AppAPIDeveloperPlatformSDKApiConsumerWebhookHealthReport()
        r.update("inst-1", "c1", total_deliveries=100, successful_deliveries=100)
        assert len(r.ranked("inst-2")) == 0
