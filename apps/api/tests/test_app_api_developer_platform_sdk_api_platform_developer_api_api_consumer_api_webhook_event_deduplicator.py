from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_webhook_event_deduplicator import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventDeduplicator

class TestWebhookEventDeduplicator:
    def test_first_is_not_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventDeduplicator()
        r = svc.check("inst-1", "c1", "e1", '{"data":"test"}')
        assert r.is_duplicate is False

    def test_same_payload_is_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventDeduplicator()
        svc.check("inst-1", "c1", "e1", '{"data":"test"}')
        r = svc.check("inst-1", "c1", "e2", '{"data":"test"}')
        assert r.is_duplicate is True

    def test_different_payload_not_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventDeduplicator()
        svc.check("inst-1", "c1", "e1", '{"a":1}')
        r = svc.check("inst-1", "c1", "e2", '{"b":2}')
        assert r.is_duplicate is False

    def test_duplicate_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventDeduplicator()
        svc.check("inst-1", "c1", "e1", "payload1")
        svc.check("inst-1", "c1", "e2", "payload1")  # dupe
        assert svc.duplicate_rate("inst-1") == 50.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventDeduplicator()
        svc.check("inst-1", "c1", "e1", "x")
        assert svc.stats("inst-2")["checked"] == 0
