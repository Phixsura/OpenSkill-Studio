from app.services.app_api_developer_platform_sdk_webhook_consumer_trust_score import AppAPIDeveloperPlatformSDKWebhookConsumerTrustScore

class TestConsumerTrustScore:
    def test_trusted(self):
        t = AppAPIDeveloperPlatformSDKWebhookConsumerTrustScore()
        s = t.compute("inst-1", "c1", auth_success_rate=99, payload_valid_rate=99, response_time_score=95, days_active=365)
        assert s.trust_tier == "trusted"

    def test_restricted(self):
        t = AppAPIDeveloperPlatformSDKWebhookConsumerTrustScore()
        s = t.compute("inst-1", "c1", auth_success_rate=50, payload_valid_rate=50, response_time_score=30, violations=5)
        assert s.trust_tier == "restricted"

    def test_ranked(self):
        t = AppAPIDeveloperPlatformSDKWebhookConsumerTrustScore()
        t.compute("inst-1", "c1", auth_success_rate=99, days_active=365)
        t.compute("inst-1", "c2", auth_success_rate=50, violations=10)
        ranked = t.ranked("inst-1")
        assert ranked[0].consumer_id == "c1"

    def test_isolation(self):
        t = AppAPIDeveloperPlatformSDKWebhookConsumerTrustScore()
        t.compute("inst-1", "c1", auth_success_rate=99)
        assert len(t.ranked("inst-2")) == 0
