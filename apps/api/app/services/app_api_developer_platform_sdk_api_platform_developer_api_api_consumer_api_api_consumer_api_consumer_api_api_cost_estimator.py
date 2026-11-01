"""Consumer API Cost Estimator — estimate API costs based on usage projections."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class PricingTier:
    tier_name: str
    price_per_request_cents: float
    included_requests: int = 0
    overage_price_cents: float = 0.0

@dataclass
class UsageProjection:
    metric: str
    projected_count: int
    current_count: int = 0

@dataclass
class CostEstimate:
    consumer_id: str
    period: str
    projections: list[UsageProjection]
    base_cost_cents: int
    overage_cost_cents: int
    total_cost_cents: int
    savings_vs_next_tier_cents: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiCostEstimator:
    def __init__(self) -> None:
        self._tiers: dict[tuple[str, str], PricingTier] = {}  # (inst, tier_name)
        self._assignments: dict[tuple[str, str], str] = {}  # (inst, consumer) -> tier_name

    def add_tier(self, installation_id: str, tier: PricingTier) -> PricingTier:
        if not installation_id:
            raise ValueError("installation_id is required")
        if tier.price_per_request_cents < 0:
            raise ValueError("Price must be non-negative")
        self._tiers[(installation_id, tier.tier_name)] = tier
        return tier

    def assign_tier(self, installation_id: str, consumer_id: str, tier_name: str) -> None:
        if (installation_id, tier_name) not in self._tiers:
            raise ValueError(f"Tier {tier_name} not found")
        self._assignments[(installation_id, consumer_id)] = tier_name

    def estimate(self, installation_id: str, consumer_id: str, period: str, projected_requests: int) -> CostEstimate:
        tier_name = self._assignments.get((installation_id, consumer_id))
        if not tier_name:
            raise ValueError("No tier assigned")
        tier = self._tiers[(installation_id, tier_name)]
        if projected_requests <= tier.included_requests:
            base_cost = int(tier.included_requests * tier.price_per_request_cents)
            overage = 0
        else:
            base_cost = int(tier.included_requests * tier.price_per_request_cents)
            overage = int((projected_requests - tier.included_requests) * tier.overage_price_cents)
        total = base_cost + overage
        # Check savings vs next tier
        savings = 0
        all_tiers = sorted([t for (inst, _), t in self._tiers.items() if inst == installation_id], key=lambda t: t.included_requests)
        for t in all_tiers:
            if t.included_requests > tier.included_requests and projected_requests <= t.included_requests:
                alt_cost = int(t.included_requests * t.price_per_request_cents)
                if alt_cost < total:
                    savings = total - alt_cost
                    break
        return CostEstimate(consumer_id=consumer_id, period=period, projections=[UsageProjection(metric="requests", projected_count=projected_requests)], base_cost_cents=base_cost, overage_cost_cents=overage, total_cost_cents=total, savings_vs_next_tier_cents=savings)

    def list_tiers(self, installation_id: str) -> list[PricingTier]:
        return sorted([t for (inst, _), t in self._tiers.items() if inst == installation_id], key=lambda t: t.included_requests)
