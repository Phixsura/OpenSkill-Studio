"""API Consumer Endpoint Capacity — track and manage endpoint capacity limits."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class EndpointCapacity:
    endpoint: str
    method: str
    max_rps: int  # requests per second
    current_rps: float = 0.0
    burst_capacity: int = 0
    queue_depth: int = 0

    @property
    def utilization_pct(self) -> float:
        if self.max_rps == 0: return 0.0
        return round(min(100.0, (self.current_rps / self.max_rps) * 100), 1)

    @property
    def status(self) -> str:
        u = self.utilization_pct
        if u >= 95: return "saturated"
        if u >= 80: return "high"
        if u >= 50: return "moderate"
        return "low"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointCapacity:
    def __init__(self) -> None:
        self._capacities: dict[tuple[str, str, str], EndpointCapacity] = {}

    def set_capacity(self, installation_id: str, endpoint: str, method: str, max_rps: int, burst: int = 0) -> EndpointCapacity:
        if not installation_id: raise ValueError("installation_id is required")
        if max_rps < 1: raise ValueError("max_rps must be >= 1")
        cap = EndpointCapacity(endpoint=endpoint, method=method.upper(), max_rps=max_rps, burst_capacity=burst)
        self._capacities[(installation_id, method.upper(), endpoint)] = cap
        return cap

    def update_load(self, installation_id: str, endpoint: str, method: str, current_rps: float, queue_depth: int = 0) -> EndpointCapacity:
        key = (installation_id, method.upper(), endpoint)
        cap = self._capacities.get(key)
        if cap is None: raise KeyError(f"No capacity for {method} {endpoint}")
        cap.current_rps = current_rps
        cap.queue_depth = queue_depth
        return cap

    def saturated_endpoints(self, installation_id: str, threshold_pct: float = 80.0) -> list[EndpointCapacity]:
        return [c for (inst, _, _), c in self._capacities.items() if inst == installation_id and c.utilization_pct >= threshold_pct]

    def list_capacities(self, installation_id: str) -> list[EndpointCapacity]:
        return [c for (inst, _, _), c in self._capacities.items() if inst == installation_id]
