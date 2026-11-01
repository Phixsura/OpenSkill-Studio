"""App API Developer API Cost Estimator — estimate costs based on usage patterns."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class CostEstimate:
    tier: str
    api_calls: int
    webhooks: int
    storage_gb: float
    api_cost: float
    webhook_cost: float
    storage_cost: float

    @property
    def total_cost(self) -> float:
        return round(self.api_cost + self.webhook_cost + self.storage_cost, 2)

PRICING = {
    "free": {"api_per_1k": 0, "webhook_per_1k": 0, "storage_per_gb": 0, "api_limit": 10000, "webhook_limit": 1000},
    "starter": {"api_per_1k": 0.50, "webhook_per_1k": 1.00, "storage_per_gb": 0.10, "api_limit": 100000, "webhook_limit": 10000},
    "pro": {"api_per_1k": 0.30, "webhook_per_1k": 0.50, "storage_per_gb": 0.05, "api_limit": 1000000, "webhook_limit": 100000},
    "enterprise": {"api_per_1k": 0.10, "webhook_per_1k": 0.20, "storage_per_gb": 0.02, "api_limit": float("inf"), "webhook_limit": float("inf")},
}

class AppAPIDeveloperAPIApiCostEstimator:
    def __init__(self) -> None:
        self._estimates: dict[tuple[str, str], CostEstimate] = {}

    def estimate(self, installation_id: str, tier: str, api_calls: int, webhooks: int, storage_gb: float) -> CostEstimate:
        if not installation_id: raise ValueError("installation_id is required")
        if tier not in PRICING: raise ValueError(f"Unknown tier: {tier}")
        p = PRICING[tier]
        api_cost = round(api_calls / 1000 * p["api_per_1k"], 2)
        webhook_cost = round(webhooks / 1000 * p["webhook_per_1k"], 2)
        storage_cost = round(storage_gb * p["storage_per_gb"], 2)
        e = CostEstimate(tier=tier, api_calls=api_calls, webhooks=webhooks, storage_gb=storage_gb, api_cost=api_cost, webhook_cost=webhook_cost, storage_cost=storage_cost)
        self._estimates[(installation_id, tier)] = e
        return e

    def compare_tiers(self, installation_id: str, api_calls: int, webhooks: int, storage_gb: float) -> list[CostEstimate]:
        return [self.estimate(installation_id, tier, api_calls, webhooks, storage_gb) for tier in PRICING]

    def cheapest_tier(self, installation_id: str, api_calls: int, webhooks: int, storage_gb: float) -> CostEstimate:
        estimates = self.compare_tiers(installation_id, api_calls, webhooks, storage_gb)
        viable = [e for e in estimates if api_calls <= PRICING[e.tier]["api_limit"] and webhooks <= PRICING[e.tier]["webhook_limit"]]
        return min(viable, key=lambda e: e.total_cost) if viable else estimates[-1]
