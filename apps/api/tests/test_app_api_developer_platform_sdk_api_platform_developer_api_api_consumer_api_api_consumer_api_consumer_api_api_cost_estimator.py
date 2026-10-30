import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_cost_estimator import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiCostEstimator, PricingTier,
)

class TestConsumerApiCostEstimator:
    def test_within_included(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiCostEstimator()
        svc.add_tier("inst-1", PricingTier(tier_name="basic", price_per_request_cents=0.01, included_requests=10000))
        svc.assign_tier("inst-1", "c1", "basic")
        est = svc.estimate("inst-1", "c1", "2026-06", 5000)
        assert est.overage_cost_cents == 0 and est.total_cost_cents == 100

    def test_overage(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiCostEstimator()
        svc.add_tier("inst-1", PricingTier(tier_name="basic", price_per_request_cents=0.01, included_requests=1000, overage_price_cents=0.02))
        svc.assign_tier("inst-1", "c1", "basic")
        est = svc.estimate("inst-1", "c1", "2026-06", 1500)
        assert est.overage_cost_cents == 10  # 500 * 0.02

    def test_no_tier_assigned(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiCostEstimator()
        with pytest.raises(ValueError, match="No tier"):
            svc.estimate("inst-1", "c1", "2026-06", 1000)

    def test_list_tiers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiCostEstimator()
        svc.add_tier("inst-1", PricingTier(tier_name="pro", price_per_request_cents=0.005, included_requests=100000))
        svc.add_tier("inst-1", PricingTier(tier_name="basic", price_per_request_cents=0.01, included_requests=10000))
        tiers = svc.list_tiers("inst-1")
        assert tiers[0].tier_name == "basic" and tiers[1].tier_name == "pro"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiCostEstimator()
        svc.add_tier("inst-1", PricingTier(tier_name="basic", price_per_request_cents=0.01, included_requests=1000))
        assert len(svc.list_tiers("inst-2")) == 0
