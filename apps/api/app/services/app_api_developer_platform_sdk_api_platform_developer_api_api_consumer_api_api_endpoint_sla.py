"""API Consumer Endpoint SLA — define and track SLA targets per endpoint."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class EndpointSla:
    endpoint: str
    method: str
    target_uptime_pct: float = 99.9
    target_latency_p99_ms: float = 500.0
    target_error_rate_pct: float = 1.0
    actual_uptime_pct: float = 100.0
    actual_latency_p99_ms: float = 0.0
    actual_error_rate_pct: float = 0.0

    @property
    def meeting_sla(self) -> bool:
        return (self.actual_uptime_pct >= self.target_uptime_pct and
                self.actual_latency_p99_ms <= self.target_latency_p99_ms and
                self.actual_error_rate_pct <= self.target_error_rate_pct)

    @property
    def violations(self) -> list[str]:
        v: list[str] = []
        if self.actual_uptime_pct < self.target_uptime_pct: v.append(f"uptime: {self.actual_uptime_pct}% < {self.target_uptime_pct}%")
        if self.actual_latency_p99_ms > self.target_latency_p99_ms: v.append(f"p99: {self.actual_latency_p99_ms}ms > {self.target_latency_p99_ms}ms")
        if self.actual_error_rate_pct > self.target_error_rate_pct: v.append(f"errors: {self.actual_error_rate_pct}% > {self.target_error_rate_pct}%")
        return v

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointSla:
    def __init__(self) -> None:
        self._slas: dict[tuple[str, str, str], EndpointSla] = {}

    def set_sla(self, installation_id: str, sla: EndpointSla) -> EndpointSla:
        if not installation_id: raise ValueError("installation_id is required")
        if not 90 <= sla.target_uptime_pct <= 100: raise ValueError("uptime target must be 90-100%")
        self._slas[(installation_id, sla.method.upper(), sla.endpoint)] = sla
        return sla

    def update_actuals(self, installation_id: str, endpoint: str, method: str, uptime: float, latency_p99: float, error_rate: float) -> EndpointSla:
        key = (installation_id, method.upper(), endpoint)
        sla = self._slas.get(key)
        if sla is None: raise KeyError(f"No SLA for {method} {endpoint}")
        sla.actual_uptime_pct = uptime
        sla.actual_latency_p99_ms = latency_p99
        sla.actual_error_rate_pct = error_rate
        return sla

    def violations(self, installation_id: str) -> list[EndpointSla]:
        return [s for (inst, _, _), s in self._slas.items() if inst == installation_id and not s.meeting_sla]

    def list_slas(self, installation_id: str) -> list[EndpointSla]:
        return [s for (inst, _, _), s in self._slas.items() if inst == installation_id]
