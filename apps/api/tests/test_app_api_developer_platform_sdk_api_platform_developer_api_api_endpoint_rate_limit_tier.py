import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_endpoint_rate_limit_tier import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointRateLimitTier, TierLimit,
)

class TestEndpointRateLimitTier:
    def test_configure_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointRateLimitTier()
        tiers = [TierLimit("free", 10, 100), TierLimit("pro", 100, 5000)]
        svc.configure("inst-1", "/api/users", "GET", tiers)
        limit = svc.get_limit("inst-1", "/api/users", "GET", "pro")
        assert limit is not None and limit.requests_per_minute == 100

    def test_unknown_tier(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointRateLimitTier()
        svc.configure("inst-1", "/api", "GET", [TierLimit("free", 10, 100)])
        assert svc.get_limit("inst-1", "/api", "GET", "enterprise") is None

    def test_invalid_limits(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointRateLimitTier()
        with pytest.raises(ValueError, match="rph must be >= rpm"):
            svc.configure("inst-1", "/api", "GET", [TierLimit("free", 100, 50)])

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointRateLimitTier()
        svc.configure("inst-1", "/api", "GET", [TierLimit("free", 10, 100)])
        assert len(svc.list_configs("inst-2")) == 0
