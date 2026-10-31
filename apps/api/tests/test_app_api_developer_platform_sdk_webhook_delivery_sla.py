from app.services.app_api_developer_platform_sdk_webhook_delivery_sla import AppAPIDeveloperPlatformSDKWebhookDeliverySLA

class TestDeliverySLA:
    def test_meeting_sla(self):
        s = AppAPIDeveloperPlatformSDKWebhookDeliverySLA()
        s.set_sla("inst-1", "https://a.com", 500, 99.0)
        r = s.update("inst-1", "https://a.com", 200, 99.5, 1000)
        assert r.meeting_all_sla is True
        assert r.sla_breaches == 0

    def test_breaching_latency(self):
        s = AppAPIDeveloperPlatformSDKWebhookDeliverySLA()
        s.set_sla("inst-1", "https://a.com", 200, 99.0)
        r = s.update("inst-1", "https://a.com", 500, 99.5, 1000)
        assert r.meeting_latency_sla is False
        assert r.sla_breaches == 1

    def test_breaching_success(self):
        s = AppAPIDeveloperPlatformSDKWebhookDeliverySLA()
        s.set_sla("inst-1", "https://a.com", 500, 99.0)
        s.update("inst-1", "https://a.com", 100, 95.0, 1000)
        assert len(s.breaching("inst-1")) == 1

    def test_isolation(self):
        s = AppAPIDeveloperPlatformSDKWebhookDeliverySLA()
        s.set_sla("inst-1", "https://a.com", 500, 99.0)
        assert len(s.all_slas("inst-2")) == 0
