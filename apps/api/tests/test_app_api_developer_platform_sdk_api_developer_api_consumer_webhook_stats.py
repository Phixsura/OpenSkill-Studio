from app.services.app_api_developer_platform_sdk_api_developer_api_consumer_webhook_stats import AppAPIDeveloperPlatformSDKApiDeveloperApiConsumerWebhookStats

class TestConsumerWebhookStats:
    def test_update(self):
        s = AppAPIDeveloperPlatformSDKApiDeveloperApiConsumerWebhookStats()
        st = s.update("inst-1", "c1", total_deliveries=1000, successful=990, failed=10)
        assert st.success_rate == 99.0
        assert st.health_status == "excellent"

    def test_poor_health(self):
        s = AppAPIDeveloperPlatformSDKApiDeveloperApiConsumerWebhookStats()
        st = s.update("inst-1", "c1", total_deliveries=100, successful=80, failed=20)
        assert st.health_status == "poor"

    def test_poorest(self):
        s = AppAPIDeveloperPlatformSDKApiDeveloperApiConsumerWebhookStats()
        s.update("inst-1", "c1", total_deliveries=100, successful=99)
        s.update("inst-1", "c2", total_deliveries=100, successful=80)
        assert s.poorest("inst-1", 1)[0].consumer_id == "c2"

    def test_by_health(self):
        s = AppAPIDeveloperPlatformSDKApiDeveloperApiConsumerWebhookStats()
        s.update("inst-1", "c1", total_deliveries=100, successful=100)
        s.update("inst-1", "c2", total_deliveries=100, successful=80)
        h = s.by_health("inst-1")
        assert "excellent" in h
        assert "poor" in h

    def test_isolation(self):
        s = AppAPIDeveloperPlatformSDKApiDeveloperApiConsumerWebhookStats()
        s.update("inst-1", "c1", total_deliveries=100, successful=100)
        assert len(s.all_stats("inst-2")) == 0
