"""App Integration Health — monitor health of third-party integrations.

Tracks health status of external integrations:
- Record ping/check results per integration
- Compute availability and latency
- Degraded/down detection
- Per-installation scoped integrations
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class IntegrationCheck:
    """Result of an integration health check."""

    healthy: bool
    latency_ms: float
    timestamp: float = field(default_factory=time.time)
    error: str = ""


@dataclass
class IntegrationStatus:
    """Current status of an integration."""

    integration_id: str
    name: str
    healthy: bool
    availability_pct: float
    avg_latency_ms: float
    check_count: int
    last_error: str


class AppIntegrationHealth:
    """Monitor health of third-party integrations."""

    def __init__(self, max_checks: int = 100) -> None:
        # (installation_id, integration_id) → (name, list[IntegrationCheck])
        self._integrations: dict[tuple[str, str], tuple[str, list[IntegrationCheck]]] = {}
        self._max = max(10, max_checks)

    def register(
        self, installation_id: str, integration_id: str, name: str
    ) -> None:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not integration_id:
            raise ValueError("integration_id is required")
        key = (installation_id, integration_id)
        if key not in self._integrations:
            self._integrations[key] = (name, [])

    def record_check(
        self,
        installation_id: str,
        integration_id: str,
        healthy: bool,
        latency_ms: float = 0.0,
        error: str = "",
        now: float | None = None,
    ) -> IntegrationCheck:
        key = (installation_id, integration_id)
        if key not in self._integrations:
            raise KeyError(f"Integration {integration_id} not registered")

        check = IntegrationCheck(
            healthy=healthy, latency_ms=max(0, latency_ms),
            timestamp=now or time.time(), error=error,
        )
        name, checks = self._integrations[key]
        checks.append(check)
        if len(checks) > self._max:
            self._integrations[key] = (name, checks[-self._max:])
        return check

    def get_status(self, installation_id: str, integration_id: str) -> IntegrationStatus:
        key = (installation_id, integration_id)
        if key not in self._integrations:
            raise KeyError(f"Integration {integration_id} not found")

        name, checks = self._integrations[key]
        total = len(checks)
        healthy_count = sum(1 for c in checks if c.healthy)
        avail = (healthy_count / total * 100) if total > 0 else 100.0
        avg_lat = sum(c.latency_ms for c in checks if c.healthy) / max(1, healthy_count)
        last_err = ""
        for c in reversed(checks):
            if c.error:
                last_err = c.error
                break

        return IntegrationStatus(
            integration_id=integration_id, name=name,
            healthy=checks[-1].healthy if checks else True,
            availability_pct=round(avail, 2),
            avg_latency_ms=round(avg_lat, 2),
            check_count=total, last_error=last_err,
        )

    def list_integrations(self, installation_id: str) -> list[IntegrationStatus]:
        return [
            self.get_status(installation_id, iid)
            for (inst, iid) in self._integrations if inst == installation_id
        ]
