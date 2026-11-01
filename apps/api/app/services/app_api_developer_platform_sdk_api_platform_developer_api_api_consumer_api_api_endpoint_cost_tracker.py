"""API Consumer Endpoint Cost Tracker — track per-endpoint API costs."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class EndpointCost:
    endpoint: str
    method: str
    cost_per_request_cents: float
    total_requests: int = 0
    total_cost_cents: float = 0.0

    @property
    def total_dollars(self) -> str:
        return f"${self.total_cost_cents / 100:.2f}"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointCostTracker:
    def __init__(self) -> None:
        self._costs: dict[tuple[str, str, str], EndpointCost] = {}

    def set_cost(self, installation_id: str, endpoint: str, method: str, cost_per_request_cents: float) -> EndpointCost:
        if not installation_id: raise ValueError("installation_id is required")
        if cost_per_request_cents < 0: raise ValueError("cost must be non-negative")
        key = (installation_id, method.upper(), endpoint)
        ec = self._costs.get(key)
        if ec is None:
            ec = EndpointCost(endpoint=endpoint, method=method.upper(), cost_per_request_cents=cost_per_request_cents)
            self._costs[key] = ec
        else:
            ec.cost_per_request_cents = cost_per_request_cents
        return ec

    def record_request(self, installation_id: str, endpoint: str, method: str, count: int = 1) -> EndpointCost:
        key = (installation_id, method.upper(), endpoint)
        ec = self._costs.get(key)
        if ec is None: raise KeyError(f"No cost for {method} {endpoint}")
        ec.total_requests += count
        ec.total_cost_cents = round(ec.total_requests * ec.cost_per_request_cents, 2)
        return ec

    def total_cost(self, installation_id: str) -> float:
        return round(sum(ec.total_cost_cents for (inst, _, _), ec in self._costs.items() if inst == installation_id), 2)

    def most_expensive(self, installation_id: str, limit: int = 5) -> list[EndpointCost]:
        costs = [ec for (inst, _, _), ec in self._costs.items() if inst == installation_id]
        return sorted(costs, key=lambda c: -c.total_cost_cents)[:limit]

    def list_costs(self, installation_id: str) -> list[EndpointCost]:
        return [ec for (inst, _, _), ec in self._costs.items() if inst == installation_id]
