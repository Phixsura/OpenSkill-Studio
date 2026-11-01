import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_key_usage_limit import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiKeyUsageLimit, KeyUsageLimit,
)

class TestConsumerApiKeyUsageLimit:
    def test_set_and_consume(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiKeyUsageLimit()
        svc.set_limit("inst-1", KeyUsageLimit(key_id="k1", consumer_id="c1", daily_limit=100, monthly_limit=3000))
        l = svc.consume("inst-1", "k1", 50)
        assert l.daily_remaining == 50 and l.monthly_remaining == 2950

    def test_daily_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiKeyUsageLimit()
        svc.set_limit("inst-1", KeyUsageLimit(key_id="k1", consumer_id="c1", daily_limit=10, monthly_limit=1000))
        svc.consume("inst-1", "k1", 10)
        with pytest.raises(ValueError, match="Daily"):
            svc.consume("inst-1", "k1", 1)

    def test_reset_daily(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiKeyUsageLimit()
        svc.set_limit("inst-1", KeyUsageLimit(key_id="k1", consumer_id="c1", daily_limit=10, monthly_limit=1000))
        svc.consume("inst-1", "k1", 10)
        svc.reset_daily("inst-1", "k1")
        l = svc._limits[("inst-1", "k1")]
        assert l.daily_used == 0 and l.monthly_used == 10

    def test_near_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiKeyUsageLimit()
        svc.set_limit("inst-1", KeyUsageLimit(key_id="k1", consumer_id="c1", daily_limit=100, monthly_limit=3000))
        svc.consume("inst-1", "k1", 85)
        assert len(svc.near_limit("inst-1", 80)) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiKeyUsageLimit()
        svc.set_limit("inst-1", KeyUsageLimit(key_id="k1", consumer_id="c1", daily_limit=100, monthly_limit=3000))
        assert len(svc.list_limits("inst-2")) == 0
