"""Consumer API Migration Guide — guide consumers through API version migrations."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class MigrationStep:
    step_id: str
    title: str
    description: str
    code_example: str = ""
    breaking: bool = False
    completed: bool = False
    completed_at: datetime | None = None
    order: int = 0

@dataclass
class MigrationGuide:
    guide_id: str
    from_version: str
    to_version: str
    title: str
    steps: list[MigrationStep] = field(default_factory=list)
    estimated_hours: float = 1.0

@dataclass
class MigrationProgress:
    guide_id: str
    consumer_id: str
    total_steps: int
    completed_steps: int
    breaking_remaining: int
    progress_pct: float
    complete: bool

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiMigrationGuide:
    def __init__(self) -> None:
        self._guides: dict[tuple[str, str], MigrationGuide] = {}
        self._progress: dict[tuple[str, str, str], list[str]] = {}  # completed step IDs

    def create_guide(self, installation_id: str, guide: MigrationGuide) -> MigrationGuide:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not guide.steps:
            raise ValueError("At least one step required")
        guide.steps.sort(key=lambda s: s.order)
        self._guides[(installation_id, guide.guide_id)] = guide
        return guide

    def complete_step(self, installation_id: str, consumer_id: str, guide_id: str, step_id: str, now: datetime) -> MigrationStep:
        guide = self._guides.get((installation_id, guide_id))
        if not guide:
            raise ValueError("Guide not found")
        step = next((s for s in guide.steps if s.step_id == step_id), None)
        if not step:
            raise ValueError("Step not found")
        key = (installation_id, consumer_id, guide_id)
        if key not in self._progress:
            self._progress[key] = []
        if step_id not in self._progress[key]:
            self._progress[key].append(step_id)
        return step

    def get_progress(self, installation_id: str, consumer_id: str, guide_id: str) -> MigrationProgress:
        guide = self._guides.get((installation_id, guide_id))
        if not guide:
            raise ValueError("Guide not found")
        completed_ids = set(self._progress.get((installation_id, consumer_id, guide_id), []))
        total = len(guide.steps)
        completed = sum(1 for s in guide.steps if s.step_id in completed_ids)
        breaking_remaining = sum(1 for s in guide.steps if s.breaking and s.step_id not in completed_ids)
        pct = (completed / total * 100) if total > 0 else 0
        return MigrationProgress(guide_id=guide_id, consumer_id=consumer_id, total_steps=total, completed_steps=completed, breaking_remaining=breaking_remaining, progress_pct=round(pct, 1), complete=completed >= total)

    def list_guides(self, installation_id: str) -> list[MigrationGuide]:
        return [g for (inst, _), g in self._guides.items() if inst == installation_id]
