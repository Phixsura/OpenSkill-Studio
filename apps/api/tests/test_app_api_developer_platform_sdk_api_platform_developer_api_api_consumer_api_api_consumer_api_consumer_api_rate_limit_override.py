import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_rate_limit_override import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRateLimitOverride, RateLimitOverride,
)

class TestConsumerApiRateLimitOverride:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_create_and_effective(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRateLimitOverride()
        svc.create("inst-1", RateLimitOverride(override_id="o1", consumer_id="c1", multiplier=2.0, starts_at=self._now(), expires_at=self._now() + timedelta(hours=1)))
        assert svc.get_effective("inst-1", "c1", "/api", self._now()) == 2.0

    def test_expired(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRateLimitOverride()
        svc.create("inst-1", RateLimitOverride(override_id="o1", consumer_id="c1", multiplier=2.0, starts_at=self._now(), expires_at=self._now() + timedelta(hours=1)))
        assert svc.get_effective("inst-1", "c1", "/api", self._now() + timedelta(hours=2)) == 1.0

    def test_endpoint_specific(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRateLimitOverride()
        svc.create("inst-1", RateLimitOverride(override_id="o1", consumer_id="c1", endpoint_path="/api/heavy", multiplier=3.0, starts_at=self._now(), expires_at=self._now() + timedelta(hours=1)))
        assert svc.get_effective("inst-1", "c1", "/api/heavy", self._now()) == 3.0
        assert svc.get_effective("inst-1", "c1", "/api/other", self._now()) == 1.0

    def test_revoke(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRateLimitOverride()
        svc.create("inst-1", RateLimitOverride(override_id="o1", consumer_id="c1", multiplier=2.0, starts_at=self._now(), expires_at=self._now() + timedelta(hours=1)))
        svc.revoke("inst-1", "o1")
        assert svc.get_effective("inst-1", "c1", "/api", self._now()) == 1.0

    def test_max_multiplier(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRateLimitOverride()
        with pytest.raises(ValueError, match="cannot exceed 10x"):
            svc.create("inst-1", RateLimitOverride(override_id="o1", consumer_id="c1", multiplier=15.0))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRateLimitOverride()
        svc.create("inst-1", RateLimitOverride(override_id="o1", consumer_id="c1", multiplier=2.0, starts_at=self._now(), expires_at=self._now() + timedelta(hours=1)))
        assert svc.get_effective("inst-2", "c1", "/api", self._now()) == 1.0
