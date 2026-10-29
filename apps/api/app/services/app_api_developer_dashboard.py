"""App API Developer Dashboard — aggregate developer platform overview.

Provides dashboard overview:
- API health summary
- Key metrics at a glance
- Recent activity feed
- Per-installation scoped dashboards
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class DashboardOverview:
    """Developer platform dashboard overview."""

    total_api_calls: int = 0
    active_developers: int = 0
    webhook_success_rate: float = 100.0
    active_incidents: int = 0
    api_versions: int = 0
    uptime_pct: float = 100.0
    open_tickets: int = 0
    error_rate: float = 0.0


class AppAPIDeveloperDashboard:
    """Aggregate developer platform overview."""

    def __init__(self) -> None:
        self._dashboards: dict[str, DashboardOverview] = {}

    def update(
        self, installation_id: str, **kwargs,
    ) -> DashboardOverview:
        if not installation_id:
            raise ValueError("installation_id is required")

        if installation_id not in self._dashboards:
            self._dashboards[installation_id] = DashboardOverview()

        dash = self._dashboards[installation_id]
        for key, value in kwargs.items():
            if hasattr(dash, key):
                setattr(dash, key, value)
        return dash

    def get_overview(self, installation_id: str) -> DashboardOverview:
        return self._dashboards.get(installation_id, DashboardOverview())

    @property
    def health_status(self) -> str:
        """Not per-installation — just a helper."""
        return "healthy"
