"""API Consumer Onboarding Progress — track multi-phase onboarding completion."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class OnboardingPhase:
    phase_id: str
    name: str
    order: int
    completed: bool = False
    required: bool = True

@dataclass
class OnboardingProgress:
    consumer_id: str
    phases: list[OnboardingPhase] = field(default_factory=list)

    @property
    def completion_pct(self) -> float:
        if not self.phases: return 0.0
        return round(sum(1 for p in self.phases if p.completed) / len(self.phases) * 100, 1)

    @property
    def current_phase(self) -> str:
        for p in sorted(self.phases, key=lambda x: x.order):
            if not p.completed: return p.name
        return "complete"

    @property
    def ready(self) -> bool:
        return all(p.completed for p in self.phases if p.required)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerOnboardingProgress:
    def __init__(self) -> None:
        self._progress: dict[tuple[str, str], OnboardingProgress] = {}

    def create(self, installation_id: str, consumer_id: str, phases: list[OnboardingPhase]) -> OnboardingProgress:
        if not installation_id: raise ValueError("installation_id is required")
        if not phases: raise ValueError("At least one phase required")
        progress = OnboardingProgress(consumer_id=consumer_id, phases=sorted(phases, key=lambda p: p.order))
        self._progress[(installation_id, consumer_id)] = progress
        return progress

    def complete_phase(self, installation_id: str, consumer_id: str, phase_id: str) -> OnboardingProgress:
        progress = self._get(installation_id, consumer_id)
        for p in progress.phases:
            if p.phase_id == phase_id: p.completed = True; break
        return progress

    def get_progress(self, installation_id: str, consumer_id: str) -> OnboardingProgress:
        return self._get(installation_id, consumer_id)

    def incomplete(self, installation_id: str) -> list[OnboardingProgress]:
        return [p for (inst, _), p in self._progress.items() if inst == installation_id and not p.ready]

    def list_progress(self, installation_id: str) -> list[OnboardingProgress]:
        return [p for (inst, _), p in self._progress.items() if inst == installation_id]

    def _get(self, installation_id: str, consumer_id: str) -> OnboardingProgress:
        p = self._progress.get((installation_id, consumer_id))
        if p is None: raise KeyError(f"No progress for {consumer_id}")
        return p
