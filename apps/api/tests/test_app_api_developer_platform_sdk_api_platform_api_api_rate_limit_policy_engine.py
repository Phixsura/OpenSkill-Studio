import pytest
from app.services.app_api_developer_platform_sdk_api_platform_api_api_rate_limit_policy_engine import AppAPIDeveloperPlatformSDKApiPlatformApiApiRateLimitPolicyEngine

class TestRateLimitPolicyEngine:
    def test_create(self):
        e = AppAPIDeveloperPlatformSDKApiPlatformApiApiRateLimitPolicyEngine()
        p = e.create("inst-1", "p1", "Standard", [{"endpoint": "/api/*", "limit": 1000, "window_seconds": 60}])
        assert p.enforcement == "enforce"

    def test_no_rules_rejected(self):
        e = AppAPIDeveloperPlatformSDKApiPlatformApiApiRateLimitPolicyEngine()
        with pytest.raises(ValueError):
            e.create("inst-1", "p1", "Empty", [])

    def test_apply_to(self):
        e = AppAPIDeveloperPlatformSDKApiPlatformApiApiRateLimitPolicyEngine()
        e.create("inst-1", "p1", "Standard", [{"limit": 1000}])
        e.apply_to("inst-1", "p1", ["c1", "c2"])
        assert len(e.policy_for_consumer("inst-1", "c1")) == 1

    def test_active(self):
        e = AppAPIDeveloperPlatformSDKApiPlatformApiApiRateLimitPolicyEngine()
        e.create("inst-1", "p1", "Active", [{"limit": 1000}], "enforce")
        e.create("inst-1", "p2", "Off", [{"limit": 500}], "disabled")
        assert len(e.active_policies("inst-1")) == 1

    def test_isolation(self):
        e = AppAPIDeveloperPlatformSDKApiPlatformApiApiRateLimitPolicyEngine()
        e.create("inst-1", "p1", "X", [{"limit": 100}])
        assert len(e.all_policies("inst-2")) == 0
