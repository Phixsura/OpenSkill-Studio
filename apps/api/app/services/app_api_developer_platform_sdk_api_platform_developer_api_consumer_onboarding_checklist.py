"""API Consumer Onboarding Checklist — guided onboarding steps for new consumers."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ChecklistStep:
    step_id: str
    title: str
    description: str
    required: bool = True
    completed: bool = False
    completed_at: float = 0.0

@dataclass
class Checklist:
    consumer_id: str
    steps: list[ChecklistStep] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    @property
    def progress_pct(self) -> float:
        if not self.steps: return 0.0
        done = sum(1 for s in self.steps if s.completed)
        return round((done / len(self.steps)) * 100, 1)

    @property
    def required_complete(self) -> bool:
        return all(s.completed for s in self.steps if s.required)

    @property
    def pending_steps(self) -> list[ChecklistStep]:
        return [s for s in self.steps if not s.completed]

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerOnboardingChecklist:
    def __init__(self) -> None:
        self._checklists: dict[tuple[str, str], Checklist] = {}

    def create_checklist(self, installation_id: str, consumer_id: str, steps: list[dict]) -> Checklist:
        if not installation_id: raise ValueError("installation_id is required")
        if not steps: raise ValueError("At least one step required")
        key = (installation_id, consumer_id)
        if key in self._checklists: raise ValueError(f"Checklist for {consumer_id} already exists")
        cl = Checklist(
            consumer_id=consumer_id,
            steps=[ChecklistStep(step_id=s["step_id"], title=s["title"], description=s.get("description", ""), required=s.get("required", True)) for s in steps],
        )
        self._checklists[key] = cl
        return cl

    def complete_step(self, installation_id: str, consumer_id: str, step_id: str) -> ChecklistStep:
        cl = self._get(installation_id, consumer_id)
        for s in cl.steps:
            if s.step_id == step_id:
                s.completed = True
                s.completed_at = time.time()
                return s
        raise KeyError(f"Step {step_id} not found")

    def get_checklist(self, installation_id: str, consumer_id: str) -> Checklist:
        return self._get(installation_id, consumer_id)

    def is_onboarded(self, installation_id: str, consumer_id: str) -> bool:
        cl = self._get(installation_id, consumer_id)
        return cl.required_complete

    def list_checklists(self, installation_id: str) -> list[Checklist]:
        return [cl for (inst, _), cl in self._checklists.items() if inst == installation_id]

    def _get(self, installation_id: str, consumer_id: str) -> Checklist:
        cl = self._checklists.get((installation_id, consumer_id))
        if cl is None: raise KeyError(f"No checklist for {consumer_id}")
        return cl
