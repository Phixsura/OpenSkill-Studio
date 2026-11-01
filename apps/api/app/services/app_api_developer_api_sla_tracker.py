"""App API Developer API SLA Tracker — track SLA compliance per service."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class SLATarget:
    service_name: str
    uptime_target: float  # e.g., 99.9
    latency_target_ms: float  # p95 target
    current_uptime: float = 100.0
    current_p95_ms: float = 0.0

    @property
    def uptime_met(self) -> bool:
        return self.current_uptime >= self.uptime_target

    @property
    def latency_met(self) -> bool:
        return self.current_p95_ms <= self.latency_target_ms

    @property
    def sla_met(self) -> bool:
        return self.uptime_met and self.latency_met

class AppAPIDeveloperAPISLATracker:
    def __init__(self) -> None:
        self._slas: dict[tuple[str, str], SLATarget] = {}

    def set_target(self, installation_id: str, service_name: str, uptime_target: float, latency_target_ms: float) -> SLATarget:
        if not installation_id: raise ValueError("installation_id is required")
        s = SLATarget(service_name=service_name, uptime_target=uptime_target, latency_target_ms=latency_target_ms)
        self._slas[(installation_id, service_name)] = s
        return s

    def update_actuals(self, installation_id: str, service_name: str, uptime: float, p95_ms: float) -> SLATarget:
        s = self._slas.get((installation_id, service_name))
        if s is None: raise KeyError(f"SLA for {service_name} not found")
        s.current_uptime = uptime
        s.current_p95_ms = p95_ms
        return s

    def violations(self, installation_id: str) -> list[SLATarget]:
        return [s for (inst, _), s in self._slas.items() if inst == installation_id and not s.sla_met]

    def list_slas(self, installation_id: str) -> list[SLATarget]:
        return [s for (inst, _), s in self._slas.items() if inst == installation_id]
