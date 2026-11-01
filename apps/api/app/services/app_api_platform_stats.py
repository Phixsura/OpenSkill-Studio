"""App API Platform Stats — aggregate platform-wide statistics.

The capstone service — aggregates all platform metrics:
- Total services, endpoints, consumers
- Overall health score
- Platform uptime and activity
- Per-installation scoped stats
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class PlatformStats:
    """Aggregate platform statistics."""

    total_services: int = 0
    total_endpoints: int = 0
    total_consumers: int = 0
    total_api_calls: int = 0
    total_webhooks_sent: int = 0
    overall_health: float = 100.0
    uptime_pct: float = 100.0
    active_incidents: int = 0
    open_tickets: int = 0
    sdk_versions_in_use: int = 0


class AppAPIPlatformStats:
    """Aggregate platform-wide statistics."""

    def __init__(self) -> None:
        self._stats: dict[str, PlatformStats] = {}

    def update(self, installation_id: str, **kwargs) -> PlatformStats:
        if not installation_id:
            raise ValueError("installation_id is required")
        if installation_id not in self._stats:
            self._stats[installation_id] = PlatformStats()
        stats = self._stats[installation_id]
        for key, value in kwargs.items():
            if hasattr(stats, key):
                setattr(stats, key, value)
        return stats

    def get_stats(self, installation_id: str) -> PlatformStats:
        return self._stats.get(installation_id, PlatformStats())

    def is_healthy(self, installation_id: str) -> bool:
        stats = self.get_stats(installation_id)
        return stats.overall_health >= 90 and stats.active_incidents == 0
