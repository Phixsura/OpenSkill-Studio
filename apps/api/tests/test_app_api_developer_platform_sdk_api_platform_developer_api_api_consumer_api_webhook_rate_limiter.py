import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_webhook_rate_limiter import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookRateLimiter

class TestWebhookRateLimiter:
    def test_allow_within_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookRateLimiter()
        svc.configure("inst-1", "c1", max_per_second=5, max_per_minute=100)
        assert svc.allow("inst-1", "c1") is True

    def test_block_over_second_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookRateLimiter()
        svc.configure("inst-1", "c1", max_per_second=3, max_per_minute=100)
        for _ in range(3): svc.allow("inst-1", "c1")
        assert svc.allow("inst-1", "c1") is False

    def test_no_config_allows(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookRateLimiter()
        assert svc.allow("inst-1", "c1") is True

    def test_total_limited(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookRateLimiter()
        svc.configure("inst-1", "c1", max_per_second=1, max_per_minute=100)
        svc.allow("inst-1", "c1")
        svc.allow("inst-1", "c1")  # blocked
        assert svc.get_limit("inst-1", "c1").total_limited == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookRateLimiter()
        svc.configure("inst-1", "c1", max_per_second=5)
        assert len(svc.list_limits("inst-2")) == 0
