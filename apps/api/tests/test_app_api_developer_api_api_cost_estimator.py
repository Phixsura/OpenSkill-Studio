import pytest
from app.services.app_api_developer_api_api_cost_estimator import AppAPIDeveloperAPIApiCostEstimator

class TestCostEstimator:
    def test_estimate_free(self):
        e = AppAPIDeveloperAPIApiCostEstimator()
        r = e.estimate("inst-1", "free", 5000, 500, 1.0)
        assert r.total_cost == 0

    def test_estimate_pro(self):
        e = AppAPIDeveloperAPIApiCostEstimator()
        r = e.estimate("inst-1", "pro", 100000, 50000, 10)
        assert r.api_cost == 30.0
        assert r.webhook_cost == 25.0
        assert r.storage_cost == 0.5

    def test_compare_tiers(self):
        e = AppAPIDeveloperAPIApiCostEstimator()
        tiers = e.compare_tiers("inst-1", 50000, 5000, 5)
        assert len(tiers) == 4

    def test_cheapest(self):
        e = AppAPIDeveloperAPIApiCostEstimator()
        r = e.cheapest_tier("inst-1", 5000, 500, 0.5)
        assert r.tier == "free"

    def test_invalid_tier(self):
        e = AppAPIDeveloperAPIApiCostEstimator()
        with pytest.raises(ValueError):
            e.estimate("inst-1", "unknown", 1000, 100, 1)
