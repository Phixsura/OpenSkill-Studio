import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_usage_limit_policy import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageLimitPolicy, UsageLimit,
)

class TestConsumerApiUsageLimitPolicy:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_within_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageLimitPolicy()
        svc.set_limit("inst-1", UsageLimit(limit_id="l1", consumer_id="c1", metric="requests", period="hour", max_value=100))
        result = svc.consume("inst-1", "c1", "requests", 10, self._now())
        assert result.allowed and result.remaining == 90

    def test_exceeded(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageLimitPolicy()
        svc.set_limit("inst-1", UsageLimit(limit_id="l1", consumer_id="c1", metric="requests", period="hour", max_value=5))
        svc.consume("inst-1", "c1", "requests", 5, self._now())
        result = svc.consume("inst-1", "c1", "requests", 1, self._now())
        assert not result.allowed

    def test_auto_reset(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageLimitPolicy()
        svc.set_limit("inst-1", UsageLimit(limit_id="l1", consumer_id="c1", metric="requests", period="hour", max_value=10))
        svc.consume("inst-1", "c1", "requests", 10, self._now())
        result = svc.consume("inst-1", "c1", "requests", 5, self._now() + timedelta(hours=2))
        assert result.allowed and result.current == 5

    def test_no_limit_allows(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageLimitPolicy()
        result = svc.consume("inst-1", "c1", "requests", 999, self._now())
        assert result.allowed

    def test_invalid_period(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageLimitPolicy()
        with pytest.raises(ValueError, match="Invalid period"):
            svc.set_limit("inst-1", UsageLimit(limit_id="l1", consumer_id="c1", metric="x", period="year", max_value=100))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageLimitPolicy()
        svc.set_limit("inst-1", UsageLimit(limit_id="l1", consumer_id="c1", metric="requests", period="hour", max_value=5))
        result = svc.consume("inst-2", "c1", "requests", 100, self._now())
        assert result.allowed
