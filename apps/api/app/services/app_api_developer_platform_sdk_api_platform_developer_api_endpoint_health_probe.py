"""API Endpoint Health Probe — monitor endpoint health with probe checks."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class ProbeStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class ProbeResult:
    endpoint: str
    status: ProbeStatus
    response_time_ms: float
    status_code: int
    checked_at: float = field(default_factory=time.time)
    error: str = ""

@dataclass
class HealthProbe:
    probe_id: str
    endpoint: str
    method: str = "GET"
    interval_s: int = 30
    timeout_ms: int = 5000
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    consecutive_healthy: int = 0
    consecutive_unhealthy: int = 0
    current_status: ProbeStatus = ProbeStatus.UNKNOWN
    last_check: float = 0.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointHealthProbe:
    def __init__(self) -> None:
        self._probes: dict[tuple[str, str], HealthProbe] = {}
        self._history: dict[tuple[str, str], list[ProbeResult]] = {}

    def create_probe(self, installation_id: str, probe: HealthProbe) -> HealthProbe:
        if not installation_id: raise ValueError("installation_id is required")
        if probe.interval_s < 5: raise ValueError("interval must be >= 5s")
        if probe.timeout_ms < 100: raise ValueError("timeout must be >= 100ms")
        key = (installation_id, probe.probe_id)
        self._probes[key] = probe
        return probe

    def record_check(self, installation_id: str, probe_id: str, status_code: int, response_time_ms: float, error: str = "") -> ProbeResult:
        key = (installation_id, probe_id)
        probe = self._probes.get(key)
        if probe is None: raise KeyError(f"Probe {probe_id} not found")
        is_healthy = 200 <= status_code < 400 and response_time_ms <= probe.timeout_ms and not error
        if is_healthy:
            probe.consecutive_healthy += 1
            probe.consecutive_unhealthy = 0
            if probe.consecutive_healthy >= probe.healthy_threshold:
                probe.current_status = ProbeStatus.HEALTHY
        else:
            probe.consecutive_unhealthy += 1
            probe.consecutive_healthy = 0
            if probe.consecutive_unhealthy >= probe.unhealthy_threshold:
                probe.current_status = ProbeStatus.UNHEALTHY
            elif probe.consecutive_unhealthy >= 1:
                probe.current_status = ProbeStatus.DEGRADED

        probe.last_check = time.time()
        status = ProbeStatus.HEALTHY if is_healthy else ProbeStatus.UNHEALTHY
        result = ProbeResult(endpoint=probe.endpoint, status=status, response_time_ms=response_time_ms, status_code=status_code, error=error)
        self._history.setdefault(key, []).append(result)
        if len(self._history[key]) > 100:
            self._history[key] = self._history[key][-100:]
        return result

    def get_status(self, installation_id: str, probe_id: str) -> ProbeStatus:
        probe = self._probes.get((installation_id, probe_id))
        return probe.current_status if probe else ProbeStatus.UNKNOWN

    def unhealthy_probes(self, installation_id: str) -> list[HealthProbe]:
        return [p for (inst, _), p in self._probes.items() if inst == installation_id and p.current_status in (ProbeStatus.UNHEALTHY, ProbeStatus.DEGRADED)]

    def list_probes(self, installation_id: str) -> list[HealthProbe]:
        return [p for (inst, _), p in self._probes.items() if inst == installation_id]
