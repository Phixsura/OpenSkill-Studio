"""App API Developer Endpoint Health Probe — active health probing per endpoint."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ProbeResult:
    endpoint: str
    status_code: int
    response_time_ms: float
    healthy: bool
    checked_at: float = field(default_factory=time.time)

@dataclass
class ProbeConfig:
    endpoint: str
    interval_seconds: int
    timeout_ms: int = 5000
    expected_status: int = 200
    results: list[ProbeResult] = field(default_factory=list)
    consecutive_failures: int = 0

    @property
    def last_result(self) -> ProbeResult | None:
        return self.results[-1] if self.results else None

    @property
    def success_rate(self) -> float:
        if not self.results: return 100.0
        return round(sum(1 for r in self.results if r.healthy) / len(self.results) * 100, 1)

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiEndpointHealthProbe:
    def __init__(self) -> None:
        self._probes: dict[tuple[str, str], ProbeConfig] = {}

    def configure(self, installation_id: str, endpoint: str, interval_seconds: int, timeout_ms: int = 5000, expected_status: int = 200) -> ProbeConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if interval_seconds < 5: raise ValueError("interval must be >= 5 seconds")
        key = (installation_id, endpoint)
        p = ProbeConfig(endpoint=endpoint, interval_seconds=interval_seconds, timeout_ms=timeout_ms, expected_status=expected_status)
        self._probes[key] = p
        return p

    def record_result(self, installation_id: str, endpoint: str, status_code: int, response_time_ms: float) -> ProbeConfig:
        key = (installation_id, endpoint)
        p = self._probes.get(key)
        if p is None: raise KeyError(f"No probe for {endpoint}")
        healthy = status_code == p.expected_status and response_time_ms <= p.timeout_ms
        r = ProbeResult(endpoint=endpoint, status_code=status_code, response_time_ms=response_time_ms, healthy=healthy)
        p.results.append(r)
        if healthy: p.consecutive_failures = 0
        else: p.consecutive_failures += 1
        if len(p.results) > 100: p.results = p.results[-100:]
        return p

    def unhealthy_probes(self, installation_id: str) -> list[ProbeConfig]:
        return [p for (inst, _), p in self._probes.items() if inst == installation_id and p.consecutive_failures > 0]

    def all_probes(self, installation_id: str) -> list[ProbeConfig]:
        return [p for (inst, _), p in self._probes.items() if inst == installation_id]
