"""API Consumer Cost Estimator — estimate API costs based on usage patterns."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class CostEstimate:
    consumer_id: str
    period: str
    estimated_requests: int
    cost_per_request_cents: float
    base_cost_cents: int
    estimated_total_cents: float
    currency: str = "USD"

    @property
    def estimated_total_dollars(self) -> str:
        return f"${self.estimated_total_cents / 100:.2f}"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCostEstimator:
    def __init__(self) -> None:
        self._pricing: dict[tuple[str, str], dict[str, float]] = {}  # (inst, tier) → pricing

    def set_pricing(self, installation_id: str, tier: str, base_cents: int, per_request_cents: float) -> None:
        if not installation_id: raise ValueError("installation_id is required")
        if base_cents < 0 or per_request_cents < 0: raise ValueError("Costs must be non-negative")
        self._pricing[(installation_id, tier)] = {"base": base_cents, "per_request": per_request_cents}

    def estimate(self, installation_id: str, consumer_id: str, tier: str, period: str, estimated_requests: int) -> CostEstimate:
        pricing = self._pricing.get((installation_id, tier))
        if pricing is None: raise KeyError(f"No pricing for tier {tier}")
        if estimated_requests < 0: raise ValueError("Requests must be non-negative")
        base = int(pricing["base"])
        per_req = pricing["per_request"]
        total = base + estimated_requests * per_req
        return CostEstimate(consumer_id=consumer_id, period=period, estimated_requests=estimated_requests, cost_per_request_cents=per_req, base_cost_cents=base, estimated_total_cents=round(total, 2))

    def compare_tiers(self, installation_id: str, estimated_requests: int) -> list[dict[str, object]]:
        results = []
        for (inst, tier), pricing in self._pricing.items():
            if inst != installation_id: continue
            total = pricing["base"] + estimated_requests * pricing["per_request"]
            results.append({"tier": tier, "total_cents": round(total, 2), "total_dollars": f"${total / 100:.2f}"})
        return sorted(results, key=lambda x: x["total_cents"])

    def list_tiers(self, installation_id: str) -> list[str]:
        return [tier for (inst, tier) in self._pricing if inst == installation_id]
