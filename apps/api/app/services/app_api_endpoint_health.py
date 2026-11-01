"""App API Endpoint Health — per-endpoint health tracking.

Manages endpoint health:
- Record success/failure per endpoint
- Calculate per-endpoint error rates
- Identify degraded endpoints
- Per-installation scoped health
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class EndpointHealth:
    """Health tracking for an endpoint."""

    method: str
    path: str
    success_count: int = 0
    error_count: int = 0

    @property
    def total(self) -> int:
        return self.success_count + self.error_count

    @property
    def error_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return round(self.error_count / self.total * 100, 1)

    @property
    def is_degraded(self) -> bool:
        return self.total >= 10 and self.error_rate > 5.0


class AppAPIEndpointHealth:
    """Per-endpoint health tracking."""

    def __init__(self) -> None:
        self._endpoints: dict[tuple[str, str, str], EndpointHealth] = {}

    def record(
        self, installation_id: str, method: str, path: str, success: bool,
    ) -> EndpointHealth:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, method.upper(), path)
        if key not in self._endpoints:
            self._endpoints[key] = EndpointHealth(method=method.upper(), path=path)
        ep = self._endpoints[key]
        if success:
            ep.success_count += 1
        else:
            ep.error_count += 1
        return ep

    def degraded_endpoints(self, installation_id: str) -> list[EndpointHealth]:
        return [
            ep for (inst, _, _), ep in self._endpoints.items()
            if inst == installation_id and ep.is_degraded
        ]

    def top_errors(self, installation_id: str, limit: int = 10) -> list[EndpointHealth]:
        eps = [ep for (inst, _, _), ep in self._endpoints.items() if inst == installation_id and ep.error_count > 0]
        return sorted(eps, key=lambda e: e.error_count, reverse=True)[:limit]

    def list_endpoints(self, installation_id: str) -> list[EndpointHealth]:
        return [ep for (inst, _, _), ep in self._endpoints.items() if inst == installation_id]
