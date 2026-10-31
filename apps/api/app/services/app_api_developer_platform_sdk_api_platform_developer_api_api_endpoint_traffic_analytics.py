"""API Endpoint Traffic Analytics — real-time traffic analysis per endpoint."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class TrafficWindow:
    endpoint: str
    method: str
    window_minutes: int = 5
    request_count: int = 0
    error_count: int = 0
    unique_consumers: set[str] = field(default_factory=set)
    total_bytes: int = 0

    @property
    def rps(self) -> float:
        if self.window_minutes <= 0: return 0.0
        return round(self.request_count / (self.window_minutes * 60), 2)

    @property
    def error_rate(self) -> float:
        if self.request_count == 0: return 0.0
        return round((self.error_count / self.request_count) * 100, 2)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointTrafficAnalytics:
    def __init__(self) -> None:
        self._windows: dict[tuple[str, str, str], TrafficWindow] = {}

    def record(self, installation_id: str, endpoint: str, method: str, consumer_id: str, status_code: int, bytes_transferred: int = 0) -> TrafficWindow:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, method.upper(), endpoint)
        w = self._windows.get(key)
        if w is None:
            w = TrafficWindow(endpoint=endpoint, method=method.upper())
            self._windows[key] = w
        w.request_count += 1
        w.total_bytes += bytes_transferred
        w.unique_consumers.add(consumer_id)
        if status_code >= 400: w.error_count += 1
        return w

    def get_traffic(self, installation_id: str, endpoint: str, method: str) -> TrafficWindow | None:
        return self._windows.get((installation_id, method.upper(), endpoint))

    def hottest_endpoints(self, installation_id: str, limit: int = 5) -> list[TrafficWindow]:
        windows = [w for (inst, _, _), w in self._windows.items() if inst == installation_id]
        return sorted(windows, key=lambda w: -w.request_count)[:limit]

    def total_rps(self, installation_id: str) -> float:
        return sum(w.rps for (inst, _, _), w in self._windows.items() if inst == installation_id)

    def list_endpoints(self, installation_id: str) -> list[TrafficWindow]:
        return [w for (inst, _, _), w in self._windows.items() if inst == installation_id]
