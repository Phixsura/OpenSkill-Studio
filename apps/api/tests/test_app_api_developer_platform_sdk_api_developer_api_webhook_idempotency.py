import pytest
from app.services.app_api_developer_platform_sdk_api_developer_api_webhook_idempotency import AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookIdempotency

class TestWebhookIdempotency:
    def test_first_delivery(self):
        i = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookIdempotency()
        is_dup, r = i.check_and_store("inst-1", "https://a.com", "key-1", '{"event": "push"}')
        assert is_dup is False

    def test_duplicate(self):
        i = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookIdempotency()
        i.check_and_store("inst-1", "https://a.com", "key-1", '{"event": "push"}')
        is_dup, _ = i.check_and_store("inst-1", "https://a.com", "key-1", '{"event": "push"}')
        assert is_dup is True

    def test_payload_mismatch(self):
        i = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookIdempotency()
        i.check_and_store("inst-1", "https://a.com", "key-1", '{"a": 1}')
        with pytest.raises(ValueError, match="mismatch"):
            i.check_and_store("inst-1", "https://a.com", "key-1", '{"a": 2}')

    def test_expired(self):
        i = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookIdempotency(default_ttl=0)
        i.check_and_store("inst-1", "https://a.com", "key-1", "{}")
        import time; time.sleep(0.01)
        is_dup, _ = i.check_and_store("inst-1", "https://a.com", "key-1", "{}")
        assert is_dup is False

    def test_active_count(self):
        i = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookIdempotency()
        i.check_and_store("inst-1", "https://a.com", "k1", "a")
        i.check_and_store("inst-1", "https://a.com", "k2", "b")
        assert i.active_count("inst-1") == 2

    def test_isolation(self):
        i = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookIdempotency()
        i.check_and_store("inst-1", "https://a.com", "k1", "a")
        assert i.active_count("inst-2") == 0
