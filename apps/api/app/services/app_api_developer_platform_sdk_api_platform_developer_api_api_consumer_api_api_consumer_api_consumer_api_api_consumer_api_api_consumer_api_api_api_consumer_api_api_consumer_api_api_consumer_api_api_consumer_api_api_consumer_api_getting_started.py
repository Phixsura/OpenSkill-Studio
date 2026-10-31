"""Consumer API Getting Started — interactive getting started experience."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class GettingStartedStep:
    step_id: str
    title: str
    description: str
    code_snippet: str = ""
    doc_url: str = ""
    completed: bool = False
    order: int = 0

@dataclass
class GettingStartedGuide:
    consumer_id: str
    steps: list[GettingStartedStep] = field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiGettingStarted:
    def __init__(self) -> None:
        self._guides: dict[tuple[str, str], GettingStartedGuide] = {}

    def initialize(self, installation_id: str, consumer_id: str, steps: list[GettingStartedStep], now: datetime | None = None) -> GettingStartedGuide:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not steps:
            raise ValueError("At least one step required")
        steps.sort(key=lambda s: s.order)
        guide = GettingStartedGuide(consumer_id=consumer_id, steps=steps, started_at=now or datetime.utcnow())
        self._guides[(installation_id, consumer_id)] = guide
        return guide

    def complete_step(self, installation_id: str, consumer_id: str, step_id: str, now: datetime | None = None) -> GettingStartedStep:
        guide = self._guides.get((installation_id, consumer_id))
        if not guide:
            raise ValueError("Guide not found")
        for step in guide.steps:
            if step.step_id == step_id:
                step.completed = True
                # Check if all done
                if all(s.completed for s in guide.steps):
                    guide.completed_at = now or datetime.utcnow()
                return step
        raise ValueError("Step not found")

    def get_progress(self, installation_id: str, consumer_id: str) -> dict:
        guide = self._guides.get((installation_id, consumer_id))
        if not guide:
            return {"total": 0, "completed": 0, "pct": 0, "done": False}
        completed = sum(1 for s in guide.steps if s.completed)
        total = len(guide.steps)
        return {"total": total, "completed": completed, "pct": round(completed / total * 100, 1) if total else 0, "done": guide.completed_at is not None}

    def get_next_step(self, installation_id: str, consumer_id: str) -> GettingStartedStep | None:
        guide = self._guides.get((installation_id, consumer_id))
        if not guide:
            return None
        for step in guide.steps:
            if not step.completed:
                return step
        return None

    def get_guide(self, installation_id: str, consumer_id: str) -> GettingStartedGuide | None:
        return self._guides.get((installation_id, consumer_id))
