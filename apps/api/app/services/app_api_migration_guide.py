"""App API Migration Guide — manage version migration documentation.

Manages migration guides:
- Create guides between version pairs
- Step-by-step migration instructions
- Track migration completion per consumer
- Per-installation scoped guides
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class MigrationStep:
    """A step in a migration guide."""

    step_id: str
    title: str
    description: str
    breaking: bool = False


@dataclass
class MigrationGuide:
    """A migration guide between versions."""

    guide_id: str
    from_version: str
    to_version: str
    steps: list[MigrationStep] = field(default_factory=list)
    completed_by: set[str] = field(default_factory=set)

    @property
    def breaking_count(self) -> int:
        return sum(1 for s in self.steps if s.breaking)


class AppAPIMigrationGuide:
    """Manage version migration documentation."""

    def __init__(self) -> None:
        self._guides: dict[tuple[str, str], MigrationGuide] = {}

    def create_guide(
        self, installation_id: str, guide_id: str,
        from_version: str, to_version: str, steps: list[dict],
    ) -> MigrationGuide:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not steps:
            raise ValueError("at least one step required")

        step_objs = [
            MigrationStep(
                step_id=s["step_id"], title=s["title"],
                description=s.get("description", ""),
                breaking=s.get("breaking", False),
            )
            for s in steps
        ]
        guide = MigrationGuide(
            guide_id=guide_id, from_version=from_version,
            to_version=to_version, steps=step_objs,
        )
        self._guides[(installation_id, guide_id)] = guide
        return guide

    def mark_completed(self, installation_id: str, guide_id: str, consumer_id: str) -> MigrationGuide:
        g = self._get(installation_id, guide_id)
        g.completed_by.add(consumer_id)
        return g

    def completion_count(self, installation_id: str, guide_id: str) -> int:
        return len(self._get(installation_id, guide_id).completed_by)

    def list_guides(self, installation_id: str) -> list[MigrationGuide]:
        return [g for (inst, _), g in self._guides.items() if inst == installation_id]

    def _get(self, installation_id: str, guide_id: str) -> MigrationGuide:
        key = (installation_id, guide_id)
        g = self._guides.get(key)
        if g is None:
            raise KeyError(f"Guide {guide_id} not found")
        return g
