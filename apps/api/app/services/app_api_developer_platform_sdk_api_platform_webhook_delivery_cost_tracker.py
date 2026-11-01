"""App API Developer Webhook Delivery Cost Tracker — track per-delivery costs."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryCost:
    destination: str
    total_deliveries: int = 0
    total_cost_cents: int = 0
    cost_per_delivery_cents: float = 0.0
    retries_cost_cents: int = 0

    @property
    def avg_cost_cents(self) -> float:
        return round(self.total_cost_cents / self.total_deliveries, 3) if self.total_deliveries > 0 else 0.0

    @property
    def retry_cost_pct(self) -> float:
        return round(self.retries_cost_cents / self.total_cost_cents * 100, 1) if self.total_cost_cents > 0 else 0.0

class AppAPIDeveloperPlatformSDKApiPlatformWebhookDeliveryCostTracker:
    def __init__(self) -> None:
        self._costs: dict[tuple[str, str], DeliveryCost] = {}

    def record(self, installation_id: str, destination: str, deliveries: int, cost_cents: int, retries_cost_cents: int = 0) -> DeliveryCost:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, destination)
        if key not in self._costs:
            self._costs[key] = DeliveryCost(destination=destination)
        c = self._costs[key]
        c.total_deliveries += deliveries
        c.total_cost_cents += cost_cents
        c.retries_cost_cents += retries_cost_cents
        return c

    def most_expensive(self, installation_id: str, limit: int = 5) -> list[DeliveryCost]:
        costs = [c for (inst, _), c in self._costs.items() if inst == installation_id]
        return sorted(costs, key=lambda c: c.total_cost_cents, reverse=True)[:limit]

    def total_cost(self, installation_id: str) -> int:
        return sum(c.total_cost_cents for (inst, _), c in self._costs.items() if inst == installation_id)

    def all_costs(self, installation_id: str) -> list[DeliveryCost]:
        return [c for (inst, _), c in self._costs.items() if inst == installation_id]
