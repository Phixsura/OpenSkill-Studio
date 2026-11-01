"""App API Changelog Milestone — mark significant changelog milestones."""

from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class Milestone:
    milestone_id: str
    title: str
    version: str
    description: str = ""
    pinned: bool = False

class AppAPIChangelogMilestone:
    def __init__(self) -> None:
        self._milestones: dict[tuple[str, str], Milestone] = {}

    def create(self, installation_id: str, milestone_id: str, title: str, version: str, description: str = "") -> Milestone:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, milestone_id)
        if key in self._milestones: raise ValueError(f"Milestone {milestone_id} already exists")
        m = Milestone(milestone_id=milestone_id, title=title, version=version, description=description)
        self._milestones[key] = m
        return m

    def pin(self, installation_id: str, milestone_id: str) -> Milestone:
        m = self._get(installation_id, milestone_id)
        m.pinned = True
        return m

    def pinned(self, installation_id: str) -> list[Milestone]:
        return [m for (inst, _), m in self._milestones.items() if inst == installation_id and m.pinned]

    def list_milestones(self, installation_id: str) -> list[Milestone]:
        return [m for (inst, _), m in self._milestones.items() if inst == installation_id]

    def _get(self, installation_id: str, milestone_id: str) -> Milestone:
        m = self._milestones.get((installation_id, milestone_id))
        if m is None: raise KeyError(f"Milestone {milestone_id} not found")
        return m
