"""App API Developer Activity — track developer engagement metrics.

Manages developer activity:
- Record API calls per developer
- Track active days
- Engagement scoring
- Per-installation scoped activity
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class DeveloperActivity:
    """Activity metrics for a developer."""

    developer_id: str
    api_calls: int = 0
    active_days: set[str] = field(default_factory=set)
    endpoints_used: set[str] = field(default_factory=set)

    @property
    def engagement_score(self) -> float:
        """Score based on calls, days, and endpoint diversity."""
        day_score = min(len(self.active_days) * 10, 100)
        endpoint_score = min(len(self.endpoints_used) * 5, 100)
        call_score = min(self.api_calls, 100)
        return round((day_score + endpoint_score + call_score) / 3, 1)


class AppAPIDeveloperActivity:
    """Track developer engagement metrics."""

    def __init__(self) -> None:
        self._activity: dict[tuple[str, str], DeveloperActivity] = {}

    def record(
        self, installation_id: str, developer_id: str,
        endpoint: str, day: str,
    ) -> DeveloperActivity:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, developer_id)
        if key not in self._activity:
            self._activity[key] = DeveloperActivity(developer_id=developer_id)
        a = self._activity[key]
        a.api_calls += 1
        a.active_days.add(day)
        a.endpoints_used.add(endpoint)
        return a

    def top_developers(self, installation_id: str, limit: int = 10) -> list[DeveloperActivity]:
        devs = [a for (inst, _), a in self._activity.items() if inst == installation_id]
        return sorted(devs, key=lambda a: a.engagement_score, reverse=True)[:limit]

    def get_activity(self, installation_id: str, developer_id: str) -> DeveloperActivity | None:
        return self._activity.get((installation_id, developer_id))

    def active_developer_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._activity if inst == installation_id)
