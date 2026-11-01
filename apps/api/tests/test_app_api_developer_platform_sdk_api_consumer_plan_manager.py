import pytest
from app.services.app_api_developer_platform_sdk_api_consumer_plan_manager import AppAPIDeveloperPlatformSDKApiConsumerPlanManager

class TestConsumerPlanManager:
    def test_assign(self):
        m = AppAPIDeveloperPlatformSDKApiConsumerPlanManager()
        c = m.assign("inst-1", "c1", "pro")
        assert c.plan == "pro"
        assert c.limits["api_calls"] == 1000000

    def test_upgrade_tracks_previous(self):
        m = AppAPIDeveloperPlatformSDKApiConsumerPlanManager()
        m.assign("inst-1", "c1", "free")
        c = m.assign("inst-1", "c1", "pro")
        assert c.previous_plan == "free"

    def test_invalid_plan(self):
        m = AppAPIDeveloperPlatformSDKApiConsumerPlanManager()
        with pytest.raises(ValueError):
            m.assign("inst-1", "c1", "ultra")

    def test_check_limit(self):
        m = AppAPIDeveloperPlatformSDKApiConsumerPlanManager()
        m.assign("inst-1", "c1", "starter")
        assert m.check_limit("inst-1", "c1", "api_calls") == 100000

    def test_by_plan(self):
        m = AppAPIDeveloperPlatformSDKApiConsumerPlanManager()
        m.assign("inst-1", "c1", "free")
        m.assign("inst-1", "c2", "pro")
        m.assign("inst-1", "c3", "pro")
        assert m.by_plan("inst-1") == {"free": 1, "pro": 2}

    def test_isolation(self):
        m = AppAPIDeveloperPlatformSDKApiConsumerPlanManager()
        m.assign("inst-1", "c1", "free")
        assert len(m.all_consumers("inst-2")) == 0
