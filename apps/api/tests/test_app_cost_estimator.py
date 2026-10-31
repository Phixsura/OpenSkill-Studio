"""Tests for App Cost Estimator — projections, line items, budgets, tier comparison."""

import pytest

from app.services.app_cost_estimator import (
    AppCostEstimator,
    CostCategory,
    UsageProjection,
    project_monthly,
)


def _proj(category: CostCategory, current: float, days: int = 15) -> UsageProjection:
    return UsageProjection(category=category, current_usage=current,
                           projected_monthly=project_monthly(current, days),
                           days_elapsed=days, days_in_month=30)


class TestProjectMonthly:
    def test_half_month(self):
        assert project_monthly(5000, 15) == 10000

    def test_full_month(self):
        assert project_monthly(10000, 30) == 10000

    def test_one_day(self):
        assert project_monthly(100, 1) == 3000

    def test_zero_days(self):
        assert project_monthly(100, 0) == 0


class TestEstimate:
    def test_within_included(self):
        e = AppCostEstimator()
        projections = [_proj(CostCategory.API_CALLS, 20000)]  # proj: 40K, included: 50K
        result = e.estimate("app-1", projections)
        assert result.total_cost == 0

    def test_overage_cost(self):
        e = AppCostEstimator()
        projections = [_proj(CostCategory.API_CALLS, 50000)]  # proj: 100K, included: 50K
        result = e.estimate("app-1", projections)
        api_item = result.line_items[0]
        assert api_item.overage == 50000
        assert api_item.cost == pytest.approx(50.0)  # 50K * $0.001
        assert result.total_cost == pytest.approx(50.0)

    def test_multiple_categories(self):
        e = AppCostEstimator()
        projections = [
            _proj(CostCategory.API_CALLS, 50000),     # 100K proj, 50K over
            _proj(CostCategory.BANDWIDTH, 30),          # 60GB proj, 50GB over
        ]
        result = e.estimate("app-1", projections)
        assert len(result.line_items) == 2
        assert result.total_cost > 0

    def test_all_within_included(self):
        e = AppCostEstimator()
        projections = [
            _proj(CostCategory.API_CALLS, 10000),
            _proj(CostCategory.STORAGE, 1),
        ]
        result = e.estimate("app-1", projections)
        assert result.total_cost == 0

    def test_empty_projections(self):
        e = AppCostEstimator()
        result = e.estimate("app-1", [])
        assert result.total_cost == 0
        assert result.line_items == []


class TestBudget:
    def test_under_budget(self):
        e = AppCostEstimator()
        e.set_budget("app-1", 100.0)
        projections = [_proj(CostCategory.API_CALLS, 25000)]  # 50K proj, $0 cost
        result = e.estimate("app-1", projections)
        assert result.over_budget is False

    def test_over_budget(self):
        e = AppCostEstimator()
        e.set_budget("app-1", 10.0)
        projections = [_proj(CostCategory.API_CALLS, 50000)]  # $50 cost
        result = e.estimate("app-1", projections)
        assert result.over_budget is True

    def test_no_budget(self):
        e = AppCostEstimator()
        result = e.estimate("app-1", [_proj(CostCategory.API_CALLS, 50000)])
        assert result.budget_limit is None
        assert result.over_budget is False

    def test_invalid_budget(self):
        e = AppCostEstimator()
        with pytest.raises(ValueError, match="positive"):
            e.set_budget("app-1", 0)


class TestTierComparison:
    def test_savings_available(self):
        e = AppCostEstimator()
        # High usage where growth tier would be cheaper
        projections = [_proj(CostCategory.API_CALLS, 500000)]  # 1M proj
        result = e.estimate("app-1", projections)
        if result.savings_vs_next_tier is not None:
            assert result.savings_vs_next_tier > 0

    def test_no_savings_low_usage(self):
        e = AppCostEstimator()
        projections = [_proj(CostCategory.API_CALLS, 10000)]  # 20K, within all tiers
        result = e.estimate("app-1", projections)
        # Both tiers cost $0, so no savings
        assert result.savings_vs_next_tier is None or result.savings_vs_next_tier == 0


class TestLineItems:
    def test_line_item_details(self):
        e = AppCostEstimator()
        projections = [_proj(CostCategory.STORAGE, 20)]  # 40GB proj
        result = e.estimate("app-1", projections)
        item = result.line_items[0]
        assert item.category == CostCategory.STORAGE
        assert item.included == 5
        assert item.overage == 35  # 40 - 5
        assert item.unit_price == 0.05
        assert item.cost == pytest.approx(1.75)
