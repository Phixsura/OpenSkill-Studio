import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_rate_plan import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerRatePlan, RatePlan,
)

class TestConsumerRatePlan:
    def test_create_and_assign(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerRatePlan()
        svc.create_plan("inst-1", RatePlan(plan_id="free", name="Free", requests_per_minute=60, requests_per_day=10000))
        cp = svc.assign("inst-1", "c1", "free")
        assert cp.plan_id == "free"

    def test_minute_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerRatePlan()
        svc.create_plan("inst-1", RatePlan(plan_id="p1", name="Test", requests_per_minute=2, requests_per_day=1000))
        svc.assign("inst-1", "c1", "p1")
        svc.record_request("inst-1", "c1")
        svc.record_request("inst-1", "c1")
        result = svc.check_limit("inst-1", "c1")
        assert result["allowed"] is False and result["reason"] == "minute_limit"

    def test_no_plan_allows(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerRatePlan()
        assert svc.check_limit("inst-1", "c1")["allowed"] is True

    def test_invalid_limits(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerRatePlan()
        with pytest.raises(ValueError, match="daily limit"):
            svc.create_plan("inst-1", RatePlan(plan_id="bad", name="Bad", requests_per_minute=100, requests_per_day=50))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerRatePlan()
        svc.create_plan("inst-1", RatePlan(plan_id="p1", name="T", requests_per_minute=10, requests_per_day=100))
        assert len(svc.list_plans("inst-2")) == 0
