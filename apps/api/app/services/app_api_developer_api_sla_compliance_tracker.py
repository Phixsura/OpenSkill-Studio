"""App API Developer SLA Compliance Tracker — track SLA adherence per endpoint."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class SLATarget:
    endpoint: str
    uptime_target_pct: float
    latency_p99_target_ms: float
    actual_uptime_pct: float = 100.0
    actual_latency_p99_ms: float = 0.0
    total_checks: int = 0
    violations: int = 0

    @property
    def compliant(self) -> bool:
        return self.actual_uptime_pct >= self.uptime_target_pct and self.actual_latency_p99_ms <= self.latency_p99_target_ms

    @property
    def violation_rate_pct(self) -> float:
        return round(self.violations / self.total_checks * 100, 1) if self.total_checks > 0 else 0.0

class AppAPIDeveloperAPISLAComplianceTracker:
    def __init__(self) -> None:
        self._targets: dict[tuple[str, str], SLATarget] = {}

    def set_target(self, installation_id: str, endpoint: str, uptime_target_pct: float, latency_p99_target_ms: float) -> SLATarget:
        if not installation_id: raise ValueError("installation_id is required")
        if not 0 < uptime_target_pct <= 100: raise ValueError("invalid uptime target")
        key = (installation_id, endpoint)
        t = SLATarget(endpoint=endpoint, uptime_target_pct=uptime_target_pct, latency_p99_target_ms=latency_p99_target_ms)
        self._targets[key] = t
        return t

    def check(self, installation_id: str, endpoint: str, uptime_pct: float, latency_p99_ms: float) -> SLATarget:
        key = (installation_id, endpoint)
        t = self._targets.get(key)
        if t is None: raise KeyError(f"No SLA for {endpoint}")
        t.actual_uptime_pct = uptime_pct
        t.actual_latency_p99_ms = latency_p99_ms
        t.total_checks += 1
        if not t.compliant: t.violations += 1
        return t

    def non_compliant(self, installation_id: str) -> list[SLATarget]:
        return [t for (inst, _), t in self._targets.items() if inst == installation_id and not t.compliant]

    def all_targets(self, installation_id: str) -> list[SLATarget]:
        return [t for (inst, _), t in self._targets.items() if inst == installation_id]
