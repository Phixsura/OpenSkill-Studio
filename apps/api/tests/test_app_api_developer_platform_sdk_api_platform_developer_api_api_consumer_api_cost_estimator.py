import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_cost_estimator import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCostEstimator

class TestCostEstimator:
    def test_estimate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCostEstimator()
        svc.set_pricing("inst-1", "pro", base_cents=4999, per_request_cents=0.01)
        est = svc.estimate("inst-1", "c1", "pro", "2024-01", 100000)
        assert est.estimated_total_cents == 4999 + 1000  # base + 100k * 0.01
        assert est.estimated_total_dollars == "$59.99"

    def test_compare_tiers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCostEstimator()
        svc.set_pricing("inst-1", "free", base_cents=0, per_request_cents=0.05)
        svc.set_pricing("inst-1", "pro", base_cents=4999, per_request_cents=0.01)
        results = svc.compare_tiers("inst-1", 200000)
        assert results[0]["tier"] in ("free", "pro")  # cheapest first

    def test_unknown_tier(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCostEstimator()
        with pytest.raises(KeyError):
            svc.estimate("inst-1", "c1", "nope", "2024-01", 1000)

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCostEstimator()
        svc.set_pricing("inst-1", "free", 0, 0.01)
        assert len(svc.list_tiers("inst-2")) == 0
