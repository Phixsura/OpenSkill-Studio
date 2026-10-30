import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_endpoint_rate_limit_tier import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointRateLimitTier, RateLimitTier, TierAssignment,
)

class TestEndpointRateLimitTier:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_within_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointRateLimitTier()
        svc.define_tier("inst-1", RateLimitTier(tier_id="basic", name="Basic", requests_per_second=10, requests_per_minute=100, requests_per_hour=1000))
        svc.assign_tier("inst-1", TierAssignment(consumer_id="c1", endpoint_path="/api", tier_id="basic"))
        result = svc.check_and_consume("inst-1", "c1", "/api", self._now())
        assert result.allowed and result.tier_name == "Basic"

    def test_exceeds_rps(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointRateLimitTier()
        svc.define_tier("inst-1", RateLimitTier(tier_id="basic", name="Basic", requests_per_second=2, requests_per_minute=100, requests_per_hour=1000))
        svc.assign_tier("inst-1", TierAssignment(consumer_id="c1", endpoint_path="/api", tier_id="basic"))
        svc.check_and_consume("inst-1", "c1", "/api", self._now())
        svc.check_and_consume("inst-1", "c1", "/api", self._now())
        result = svc.check_and_consume("inst-1", "c1", "/api", self._now())
        assert not result.allowed and result.retry_after_ms == 1000

    def test_burst(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointRateLimitTier()
        svc.define_tier("inst-1", RateLimitTier(tier_id="burst", name="Burst", requests_per_second=2, requests_per_minute=100, requests_per_hour=1000, burst_size=3))
        svc.assign_tier("inst-1", TierAssignment(consumer_id="c1", endpoint_path="/api", tier_id="burst"))
        for _ in range(5):
            svc.check_and_consume("inst-1", "c1", "/api", self._now())
        result = svc.check_and_consume("inst-1", "c1", "/api", self._now())
        assert not result.allowed  # 2+3=5 allowed, 6th blocked

    def test_no_assignment(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointRateLimitTier()
        result = svc.check_and_consume("inst-1", "c1", "/api", self._now())
        assert result.allowed and result.tier_name == "none"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointRateLimitTier()
        svc.define_tier("inst-1", RateLimitTier(tier_id="t", name="T", requests_per_second=5, requests_per_minute=50, requests_per_hour=500))
        assert len(svc.list_tiers("inst-2")) == 0
