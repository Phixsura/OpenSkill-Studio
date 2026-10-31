"""API Consumer Request Circuit Monitor — monitor circuit breaker states across endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class CircuitSnapshot:
    endpoint: str
    state: str  # "closed", "open", "half_open"
    failure_count: int = 0
    last_failure_reason: str = ""
    open_since_seconds: float = 0.0

@dataclass
class CircuitMonitorSummary:
    total_circuits: int = 0
    closed_count: int = 0
    open_count: int = 0
    half_open_count: int = 0
    most_failures_endpoint: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCircuitMonitor:
    def __init__(self) -> None:
        self._circuits: dict[tuple[str, str], CircuitSnapshot] = {}

    def update(self, installation_id: str, snapshot: CircuitSnapshot) -> CircuitSnapshot:
        if not installation_id: raise ValueError("installation_id is required")
        self._circuits[(installation_id, snapshot.endpoint)] = snapshot
        return snapshot

    def summary(self, installation_id: str) -> CircuitMonitorSummary:
        circuits = [c for (inst, _), c in self._circuits.items() if inst == installation_id]
        if not circuits: return CircuitMonitorSummary()
        closed = sum(1 for c in circuits if c.state == "closed")
        opened = sum(1 for c in circuits if c.state == "open")
        half = sum(1 for c in circuits if c.state == "half_open")
        most = max(circuits, key=lambda c: c.failure_count).endpoint if circuits else ""
        return CircuitMonitorSummary(total_circuits=len(circuits), closed_count=closed, open_count=opened, half_open_count=half, most_failures_endpoint=most)

    def open_circuits(self, installation_id: str) -> list[CircuitSnapshot]:
        return [c for (inst, _), c in self._circuits.items() if inst == installation_id and c.state == "open"]

    def list_circuits(self, installation_id: str) -> list[CircuitSnapshot]:
        return [c for (inst, _), c in self._circuits.items() if inst == installation_id]
