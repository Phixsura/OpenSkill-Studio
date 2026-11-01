"""App API Analytics — track and analyze API usage patterns.

Provides analytics on API usage:
- Request volume by endpoint
- Peak hour detection
- Error hotspots
- Per-installation scoped analytics
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class EndpointAnalytics:
    """Analytics for a single endpoint."""

    method: str
    path: str
    total_requests: int = 0
    total_errors: int = 0
    total_latency_ms: float = 0.0
    hourly_distribution: dict[int, int] = field(default_factory=dict)

    @property
    def avg_latency_ms(self) -> float:
        return round(self.total_latency_ms / self.total_requests, 1) if self.total_requests > 0 else 0

    @property
    def error_rate_pct(self) -> float:
        return round(self.total_errors / self.total_requests * 100, 1) if self.total_requests > 0 else 0

    @property
    def peak_hour(self) -> int | None:
        if not self.hourly_distribution:
            return None
        return max(self.hourly_distribution, key=self.hourly_distribution.get)


class AppAPIAnalytics:
    """Track and analyze API usage patterns."""

    def __init__(self) -> None:
        # (installation_id, method, path) → EndpointAnalytics
        self._endpoints: dict[tuple[str, str, str], EndpointAnalytics] = {}

    def record_request(
        self,
        installation_id: str,
        method: str,
        path: str,
        status_code: int,
        latency_ms: float,
        hour: int | None = None,
    ) -> None:
        if not installation_id:
            raise ValueError("installation_id is required")

        key = (installation_id, method.upper(), path)
        if key not in self._endpoints:
            self._endpoints[key] = EndpointAnalytics(method=method.upper(), path=path)

        ep = self._endpoints[key]
        ep.total_requests += 1
        ep.total_latency_ms += max(0, latency_ms)
        if status_code >= 400:
            ep.total_errors += 1
        if hour is not None:
            ep.hourly_distribution[hour] = ep.hourly_distribution.get(hour, 0) + 1

    def get_top_endpoints(self, installation_id: str, limit: int = 10) -> list[EndpointAnalytics]:
        eps = [e for (inst, _, _), e in self._endpoints.items() if inst == installation_id]
        return sorted(eps, key=lambda e: e.total_requests, reverse=True)[:limit]

    def get_error_hotspots(self, installation_id: str, limit: int = 10) -> list[EndpointAnalytics]:
        eps = [e for (inst, _, _), e in self._endpoints.items()
               if inst == installation_id and e.total_errors > 0]
        return sorted(eps, key=lambda e: e.error_rate_pct, reverse=True)[:limit]

    def get_slowest(self, installation_id: str, limit: int = 10) -> list[EndpointAnalytics]:
        eps = [e for (inst, _, _), e in self._endpoints.items()
               if inst == installation_id and e.total_requests > 0]
        return sorted(eps, key=lambda e: e.avg_latency_ms, reverse=True)[:limit]
