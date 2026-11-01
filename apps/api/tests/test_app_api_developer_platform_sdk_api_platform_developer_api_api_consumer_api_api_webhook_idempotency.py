from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_webhook_idempotency import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookIdempotency

class TestWebhookIdempotency:
    def test_first_delivery_is_new(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookIdempotency()
        is_new, rec = svc.check_and_record("inst-1", "c1", "ev1", "hash1")
        assert is_new is True

    def test_duplicate_detected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookIdempotency()
        svc.check_and_record("inst-1", "c1", "ev1", "hash1")
        is_new, rec = svc.check_and_record("inst-1", "c1", "ev1", "hash1")
        assert is_new is False
        assert rec.delivery_count == 2

    def test_different_events_not_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookIdempotency()
        svc.check_and_record("inst-1", "c1", "ev1", "hash1")
        is_new, _ = svc.check_and_record("inst-1", "c1", "ev2", "hash2")
        assert is_new is True

    def test_duplicate_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookIdempotency()
        svc.check_and_record("inst-1", "c1", "ev1", "h1")
        svc.check_and_record("inst-1", "c1", "ev1", "h1")  # dup
        assert svc.duplicate_rate("inst-1") == 50.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookIdempotency()
        svc.check_and_record("inst-1", "c1", "ev1", "h1")
        assert svc.record_count("inst-2") == 0
