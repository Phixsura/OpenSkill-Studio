import pytest, time
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_rate_limit_override import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRateLimitOverride, RateLimitOverride,
)

class TestRateLimitOverride:
    def test_create_and_effective(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRateLimitOverride()
        svc.create_override("inst-1", RateLimitOverride(override_id="o1", consumer_id="c1", endpoint="/api", original_rpm=60, override_rpm=120, reason="Launch event"))
        assert svc.get_effective_rpm("inst-1", "c1", "/api", 60) == 120

    def test_no_override_returns_default(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRateLimitOverride()
        assert svc.get_effective_rpm("inst-1", "c1", "/api", 60) == 60

    def test_revoke(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRateLimitOverride()
        svc.create_override("inst-1", RateLimitOverride(override_id="o1", consumer_id="c1", endpoint="/api", original_rpm=60, override_rpm=200))
        svc.revoke("inst-1", "o1")
        assert svc.get_effective_rpm("inst-1", "c1", "/api", 60) == 60

    def test_active_overrides(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRateLimitOverride()
        svc.create_override("inst-1", RateLimitOverride(override_id="o1", consumer_id="c1", endpoint="/api", original_rpm=60, override_rpm=120))
        assert len(svc.active_overrides("inst-1")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRateLimitOverride()
        svc.create_override("inst-1", RateLimitOverride(override_id="o1", consumer_id="c1", endpoint="/api", original_rpm=60, override_rpm=120))
        assert svc.override_count("inst-2") == 0
