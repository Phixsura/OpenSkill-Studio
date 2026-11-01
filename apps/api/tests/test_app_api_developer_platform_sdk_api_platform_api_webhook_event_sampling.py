from app.services.app_api_developer_platform_sdk_api_platform_api_webhook_event_sampling import AppAPIDeveloperPlatformSDKApiPlatformApiWebhookEventSampling

class TestWebhookEventSampling:
    def test_store(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiWebhookEventSampling(sample_rate=1.0)
        e = s.store("inst-1", "e1", "push", "https://a.com", '{"data": "test"}', 200, 50)
        assert e.event_type == "push"

    def test_deterministic_sampling(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiWebhookEventSampling(sample_rate=0.5)
        r1 = s.should_sample("event-123")
        r2 = s.should_sample("event-123")
        assert r1 == r2

    def test_by_status(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiWebhookEventSampling()
        s.store("inst-1", "e1", "push", "https://a.com", "{}", 200, 50)
        s.store("inst-1", "e2", "push", "https://a.com", "{}", 500, 100)
        assert len(s.by_status("inst-1", 400)) == 1

    def test_max_samples(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiWebhookEventSampling(max_samples=5)
        for i in range(10): s.store("inst-1", f"e{i}", "push", "https://a.com", "{}", 200, 50)
        assert s.count("inst-1") == 5

    def test_isolation(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiWebhookEventSampling()
        s.store("inst-1", "e1", "push", "https://a.com", "{}", 200, 50)
        assert s.count("inst-2") == 0
