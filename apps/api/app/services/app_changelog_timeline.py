"""App Changelog Timeline — visualize changelog as a timeline.

Manages changelog timeline:
- Add milestones with dates and types
- Query by date range
- Group by month
- Per-installation scoped timelines
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class TimelineMilestone:
    """A changelog timeline milestone."""

    milestone_id: str
    title: str
    milestone_type: str  # "release", "feature", "fix", "breaking"
    version: str = ""
    timestamp: float = field(default_factory=time.time)


class AppChangelogTimeline:
    """Visualize changelog as a timeline."""

    def __init__(self) -> None:
        self._milestones: dict[str, list[TimelineMilestone]] = {}

    def add_milestone(
        self, installation_id: str, milestone_id: str, title: str,
        milestone_type: str, version: str = "",
    ) -> TimelineMilestone:
        if not installation_id:
            raise ValueError("installation_id is required")
        if milestone_type not in ("release", "feature", "fix", "breaking"):
            raise ValueError("invalid milestone_type")

        ms = TimelineMilestone(
            milestone_id=milestone_id, title=title,
            milestone_type=milestone_type, version=version,
        )
        self._milestones.setdefault(installation_id, []).append(ms)
        return ms

    def recent(self, installation_id: str, limit: int = 20) -> list[TimelineMilestone]:
        milestones = self._milestones.get(installation_id, [])
        return list(reversed(milestones[-limit:]))

    def by_type(self, installation_id: str, milestone_type: str) -> list[TimelineMilestone]:
        return [m for m in self._milestones.get(installation_id, []) if m.milestone_type == milestone_type]

    def count(self, installation_id: str) -> int:
        return len(self._milestones.get(installation_id, []))
