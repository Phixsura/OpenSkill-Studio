"""App API Developer Endpoint Monitor — real-time endpoint monitoring."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class EndpointMonitorState:
    method: str
    path: str
    status: str = "healthy"  # "healthy", "slow", "erroring", "down"
    avg_response_ms: float = 0.0
    error_rate_pct: float = 0.0
    requests_per_minute: int = 0

class AppAPIDeveloperAPIEndpointMonitor:
    def __init__(self) -> None:
        self._monitors: dict[tuple[str, str, str], EndpointMonitorState] = {}

    def update(self, installation_id: str, method: str, path: str, avg_response_ms: float, error_rate_pct: float, rpm: int) -> EndpointMonitorState:
        if not installation_id: raise ValueError("installation_id is required")
        status = "healthy"
        if error_rate_pct > 10: status = "down"
        elif error_rate_pct > 5: status = "erroring"
        elif avg_response_ms > 1000: status = "slow"
        m = EndpointMonitorState(method=method.upper(), path=path, status=status, avg_response_ms=avg_response_ms, error_rate_pct=error_rate_pct, requests_per_minute=rpm)
        self._monitors[(installation_id, method.upper(), path)] = m
        return m

    def unhealthy(self, installation_id: str) -> list[EndpointMonitorState]:
        return [m for (inst, _, _), m in self._monitors.items() if inst == installation_id and m.status != "healthy"]

    def list_monitors(self, installation_id: str) -> list[EndpointMonitorState]:
        return [m for (inst, _, _), m in self._monitors.items() if inst == installation_id]
