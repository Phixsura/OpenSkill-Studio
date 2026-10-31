"""App Cost Estimator — project monthly costs for installed apps based on usage patterns.

Helps platform operators and app developers forecast costs:
- Per-metric unit cost projection
- Usage trend extrapolation (linear from current rate)
- Tier-based pricing comparison
- Cost breakdown by metric category
- Budget alert thresholds
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class CostCategory(str, Enum):
    API_CALLS = "api_calls"
    BANDWIDTH = "bandwidth"
    STORAGE = "storage"
    COMPUTE = "compute"
    WEBHOOKS = "webhooks"


@dataclass(frozen=True)
class UnitPrice:
    """Price per unit for a metric."""

    category: CostCategory
    included: int        # free units per month
    unit_price: float    # cost per unit above included
    unit_label: str      # e.g. "per 1K calls"


@dataclass
class UsageProjection:
    """Projected usage for a metric."""

    category: CostCategory
    current_usage: float
    projected_monthly: float
    days_elapsed: int
    days_in_month: int


@dataclass
class CostLineItem:
    """A single cost line item."""

    category: CostCategory
    projected_usage: float
    included: int
    overage: float
    unit_price: float
    cost: float


@dataclass
class CostEstimate:
    """Complete monthly cost estimate."""

    app_id: str
    line_items: list[CostLineItem]
    total_cost: float
    budget_limit: float | None
    over_budget: bool
    savings_vs_next_tier: float | None


DEFAULT_PRICING: dict[CostCategory, UnitPrice] = {
    CostCategory.API_CALLS: UnitPrice(CostCategory.API_CALLS, 50_000, 0.001, "per call"),
    CostCategory.BANDWIDTH: UnitPrice(CostCategory.BANDWIDTH, 10, 0.10, "per GB"),
    CostCategory.STORAGE: UnitPrice(CostCategory.STORAGE, 5, 0.05, "per GB"),
    CostCategory.COMPUTE: UnitPrice(CostCategory.COMPUTE, 10, 0.50, "per hour"),
    CostCategory.WEBHOOKS: UnitPrice(CostCategory.WEBHOOKS, 10_000, 0.0005, "per delivery"),
}

TIER_PRICING: dict[str, dict[CostCategory, UnitPrice]] = {
    "starter": DEFAULT_PRICING,
    "growth": {
        CostCategory.API_CALLS: UnitPrice(CostCategory.API_CALLS, 500_000, 0.0005, "per call"),
        CostCategory.BANDWIDTH: UnitPrice(CostCategory.BANDWIDTH, 100, 0.05, "per GB"),
        CostCategory.STORAGE: UnitPrice(CostCategory.STORAGE, 50, 0.03, "per GB"),
        CostCategory.COMPUTE: UnitPrice(CostCategory.COMPUTE, 100, 0.25, "per hour"),
        CostCategory.WEBHOOKS: UnitPrice(CostCategory.WEBHOOKS, 100_000, 0.0002, "per delivery"),
    },
}


def project_monthly(current: float, days_elapsed: int, days_in_month: int = 30) -> float:
    """Linearly extrapolate current usage to a full month."""
    if days_elapsed <= 0:
        return 0.0
    rate = current / days_elapsed
    return round(rate * days_in_month, 2)


def compute_line_item(projection: UsageProjection, price: UnitPrice) -> CostLineItem:
    """Compute cost for a single metric."""
    overage = max(0, projection.projected_monthly - price.included)
    cost = round(overage * price.unit_price, 4)
    return CostLineItem(
        category=projection.category,
        projected_usage=projection.projected_monthly,
        included=price.included,
        overage=overage,
        unit_price=price.unit_price,
        cost=cost,
    )


class AppCostEstimator:
    """Estimate monthly costs from current usage."""

    def __init__(self, pricing: dict[CostCategory, UnitPrice] | None = None):
        self._pricing = pricing or dict(DEFAULT_PRICING)
        self._budgets: dict[str, float] = {}

    def set_budget(self, app_id: str, limit: float) -> None:
        if limit <= 0:
            raise ValueError("Budget limit must be positive")
        self._budgets[app_id] = limit

    def estimate(self, app_id: str, projections: list[UsageProjection]) -> CostEstimate:
        """Compute a cost estimate from usage projections."""
        line_items: list[CostLineItem] = []
        for proj in projections:
            price = self._pricing.get(proj.category)
            if price is None:
                continue
            line_items.append(compute_line_item(proj, price))

        total = round(sum(li.cost for li in line_items), 2)
        budget = self._budgets.get(app_id)
        over_budget = budget is not None and total > budget

        # Compare with growth tier
        savings = None
        if "growth" in TIER_PRICING:
            growth_total = 0.0
            for proj in projections:
                gp = TIER_PRICING["growth"].get(proj.category)
                if gp:
                    growth_total += compute_line_item(proj, gp).cost
            growth_total = round(growth_total, 2)
            if growth_total < total:
                savings = round(total - growth_total, 2)

        return CostEstimate(
            app_id=app_id, line_items=line_items,
            total_cost=total, budget_limit=budget,
            over_budget=over_budget, savings_vs_next_tier=savings,
        )
