"""App API Developer Onboarding — guide developers through API setup.

Manages developer onboarding:
- Define setup steps
- Track progress per developer
- Completion analytics
- Per-installation scoped onboarding
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class OnboardingProgress:
    """A developer's onboarding progress."""

    developer_id: str
    completed_steps: set[str] = field(default_factory=set)
    total_steps: int = 0

    @property
    def completion_pct(self) -> float:
        if self.total_steps == 0:
            return 100.0
        return round(len(self.completed_steps) / self.total_steps * 100, 1)

    @property
    def is_complete(self) -> bool:
        return len(self.completed_steps) >= self.total_steps


class AppAPIDeveloperOnboarding:
    """Guide developers through API setup."""

    def __init__(self) -> None:
        self._steps: dict[str, list[str]] = {}  # installation → step_ids
        self._progress: dict[tuple[str, str], OnboardingProgress] = {}

    def define_steps(self, installation_id: str, steps: list[str]) -> list[str]:
        if not installation_id:
            raise ValueError("installation_id is required")
        self._steps[installation_id] = list(steps)
        return steps

    def complete_step(self, installation_id: str, developer_id: str, step_id: str) -> OnboardingProgress:
        steps = self._steps.get(installation_id, [])
        if step_id not in steps:
            raise KeyError(f"Step {step_id} not defined")

        key = (installation_id, developer_id)
        if key not in self._progress:
            self._progress[key] = OnboardingProgress(developer_id=developer_id, total_steps=len(steps))
        p = self._progress[key]
        p.completed_steps.add(step_id)
        return p

    def get_progress(self, installation_id: str, developer_id: str) -> OnboardingProgress:
        key = (installation_id, developer_id)
        steps = self._steps.get(installation_id, [])
        return self._progress.get(key, OnboardingProgress(developer_id=developer_id, total_steps=len(steps)))

    def completion_rate(self, installation_id: str) -> float:
        progs = [p for (inst, _), p in self._progress.items() if inst == installation_id]
        if not progs:
            return 0.0
        completed = sum(1 for p in progs if p.is_complete)
        return round(completed / len(progs) * 100, 1)
