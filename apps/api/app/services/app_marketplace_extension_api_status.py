"""API Status — real-time status of all API endpoints."""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class EndpointStatus:
    endpoint: str
    method: str
    status: str = "operational"  # operational, degraded, down, maintenance
    response_time_ms: float = 0.0
    error_rate: float = 0.0


class PlatformApiStatusService:
    def __init__(self):
        self._statuses: dict[str, EndpointStatus] = {}

    def set_status(self, endpoint: str, method: str, status: str,
                   response_time: float = 0, error_rate: float = 0) -> EndpointStatus:
        key = f"{method}:{endpoint}"
        es = EndpointStatus(endpoint=endpoint, method=method, status=status,
                            response_time_ms=response_time, error_rate=error_rate)
        self._statuses[key] = es
        return es

    def get_all(self) -> list[EndpointStatus]:
        return list(self._statuses.values())

    def get_overall(self) -> str:
        statuses = [s.status for s in self._statuses.values()]
        if any(s == "down" for s in statuses): return "down"
        if any(s == "degraded" for s in statuses): return "degraded"
        if any(s == "maintenance" for s in statuses): return "maintenance"
        return "operational"

    def get_by_status(self, status: str) -> list[EndpointStatus]:
        return [s for s in self._statuses.values() if s.status == status]
