"""API Consumer Migration Guide — generate migration guides between API versions."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class MigrationStep:
    step_id: str
    title: str
    description: str
    breaking: bool = False
    code_example: str = ""
    difficulty: str = "easy"  # "easy", "medium", "hard"

@dataclass
class MigrationGuide:
    guide_id: str
    from_version: str
    to_version: str
    steps: list[MigrationStep] = field(default_factory=list)
    estimated_hours: float = 0.0

VALID_DIFFICULTIES = {"easy", "medium", "hard"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiMigrationGuide:
    def __init__(self) -> None:
        self._guides: dict[tuple[str, str], MigrationGuide] = {}

    def create_guide(self, installation_id: str, guide: MigrationGuide) -> MigrationGuide:
        if not installation_id: raise ValueError("installation_id is required")
        if not guide.steps: raise ValueError("Guide must have at least one step")
        for s in guide.steps:
            if s.difficulty not in VALID_DIFFICULTIES: raise ValueError(f"Invalid difficulty: {s.difficulty}")
        key = (installation_id, guide.guide_id)
        if key in self._guides: raise ValueError(f"Guide {guide.guide_id} exists")
        # Auto-calculate estimated hours
        diff_hours = {"easy": 0.5, "medium": 2.0, "hard": 4.0}
        guide.estimated_hours = sum(diff_hours.get(s.difficulty, 1.0) for s in guide.steps)
        self._guides[key] = guide
        return guide

    def get_guide(self, installation_id: str, from_ver: str, to_ver: str) -> MigrationGuide | None:
        for (inst, _), g in self._guides.items():
            if inst == installation_id and g.from_version == from_ver and g.to_version == to_ver:
                return g
        return None

    def breaking_steps(self, installation_id: str, guide_id: str) -> list[MigrationStep]:
        g = self._get(installation_id, guide_id)
        return [s for s in g.steps if s.breaking]

    def list_guides(self, installation_id: str) -> list[MigrationGuide]:
        return [g for (inst, _), g in self._guides.items() if inst == installation_id]

    def _get(self, installation_id: str, guide_id: str) -> MigrationGuide:
        g = self._guides.get((installation_id, guide_id))
        if g is None: raise KeyError(f"Guide {guide_id} not found")
        return g
