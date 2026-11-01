"""App Health Check — monitor service health endpoints.

Manages health check configurations:
- Register health endpoints with intervals
- Record check results (up/down/degraded)
- Calculate uptime percentage
- Per-installation scoped checks
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class HealthStatus(str, Enum):
    UP = "up"
    DOWN = "down"
    DEGRADED = "degraded"


@dataclass
class HealthResult:
    """Result of a health check."""

    status: HealthStatus
    latency_ms: float
    message: str = ""
    checked_at: float = field(default_factory=time.time)


@dataclass
class HealthEndpoint:
    """A registered health check endpoint."""

    endpoint_id: str
    url: str
    interval_seconds: int = 30
    timeout_ms: int = 5000
    results: list[HealthResult] = field(default_factory=list)

    @property
    def current_status(self) -> HealthStatus | None:
        if not self.results:
            return None
        return self.results[-1].status

    @property
    def uptime_pct(self) -> float:
        if not self.results:
            return 100.0
        up = sum(1 for r in self.results if r.status == HealthStatus.UP)
        return round(up / len(self.results) * 100, 1)


class AppHealthCheck:
    """Monitor service health endpoints."""

    def __init__(self, max_results: int = 100) -> None:
        self._max = max(1, max_results)
        self._endpoints: dict[tuple[str, str], HealthEndpoint] = {}

    def register(
        self, installation_id: str, endpoint_id: str, url: str,
        interval_seconds: int = 30, timeout_ms: int = 5000,
    ) -> HealthEndpoint:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not endpoint_id:
            raise ValueError("endpoint_id is required")
        if not url:
            raise ValueError("url is required")

        ep = HealthEndpoint(
            endpoint_id=endpoint_id, url=url,
            interval_seconds=interval_seconds, timeout_ms=timeout_ms,
        )
        self._endpoints[(installation_id, endpoint_id)] = ep
        return ep

    def record(
        self, installation_id: str, endpoint_id: str,
        status: HealthStatus, latency_ms: float, message: str = "",
    ) -> HealthResult:
        ep = self._get(installation_id, endpoint_id)
        result = HealthResult(status=status, latency_ms=latency_ms, message=message)
        ep.results.append(result)
        if len(ep.results) > self._max:
            ep.results = ep.results[-self._max:]
        return result

    def get_status(self, installation_id: str, endpoint_id: str) -> HealthStatus | None:
        return self._get(installation_id, endpoint_id).current_status

    def get_uptime(self, installation_id: str, endpoint_id: str) -> float:
        return self._get(installation_id, endpoint_id).uptime_pct

    def avg_latency(self, installation_id: str, endpoint_id: str) -> float:
        ep = self._get(installation_id, endpoint_id)
        if not ep.results:
            return 0.0
        return round(sum(r.latency_ms for r in ep.results) / len(ep.results), 1)

    def list_endpoints(self, installation_id: str) -> list[HealthEndpoint]:
        return [ep for (inst, _), ep in self._endpoints.items() if inst == installation_id]

    def down_endpoints(self, installation_id: str) -> list[HealthEndpoint]:
        return [
            ep for (inst, _), ep in self._endpoints.items()
            if inst == installation_id and ep.current_status == HealthStatus.DOWN
        ]

    def _get(self, installation_id: str, endpoint_id: str) -> HealthEndpoint:
        key = (installation_id, endpoint_id)
        ep = self._endpoints.get(key)
        if ep is None:
            raise KeyError(f"Endpoint {endpoint_id} not found")
        return ep
