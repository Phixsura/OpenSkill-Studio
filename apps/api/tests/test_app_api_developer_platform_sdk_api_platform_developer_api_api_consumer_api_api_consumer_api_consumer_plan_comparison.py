import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_plan_comparison import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerPlanComparison, PlanDetails,
)

class TestConsumerPlanComparison:
    def test_add_and_list(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerPlanComparison()
        svc.add_plan("inst-1", PlanDetails(plan_id="free", name="Free", monthly_price_cents=0, requests_per_month=1000, rate_limit_rps=10))
        svc.add_plan("inst-1", PlanDetails(plan_id="pro", name="Pro", monthly_price_cents=4999, requests_per_month=100000, rate_limit_rps=100))
        plans = svc.list_plans("inst-1")
        assert len(plans) == 2 and plans[0].name == "Free"

    def test_recommend(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerPlanComparison()
        svc.add_plan("inst-1", PlanDetails(plan_id="free", name="Free", monthly_price_cents=0, requests_per_month=1000, rate_limit_rps=10))
        svc.add_plan("inst-1", PlanDetails(plan_id="pro", name="Pro", monthly_price_cents=4999, requests_per_month=100000, rate_limit_rps=100))
        rec = svc.recommend("inst-1", 5000)
        assert rec.plan_id == "pro"

    def test_compare(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerPlanComparison()
        svc.add_plan("inst-1", PlanDetails(plan_id="a", name="A", monthly_price_cents=0, requests_per_month=100, rate_limit_rps=5))
        svc.add_plan("inst-1", PlanDetails(plan_id="b", name="B", monthly_price_cents=999, requests_per_month=10000, rate_limit_rps=50))
        compared = svc.compare("inst-1", ["a", "b"])
        assert len(compared) == 2

    def test_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerPlanComparison()
        svc.add_plan("inst-1", PlanDetails(plan_id="x", name="X", monthly_price_cents=0, requests_per_month=100, rate_limit_rps=5))
        with pytest.raises(ValueError, match="already exists"):
            svc.add_plan("inst-1", PlanDetails(plan_id="x", name="X2", monthly_price_cents=0, requests_per_month=100, rate_limit_rps=5))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerPlanComparison()
        svc.add_plan("inst-1", PlanDetails(plan_id="x", name="X", monthly_price_cents=0, requests_per_month=100, rate_limit_rps=5))
        assert len(svc.list_plans("inst-2")) == 0
