"""App Onboarding Checklist — guide new users through setup.

Manages onboarding checklists:
- Define steps with completion criteria
- Track progress per user
- Calculate completion percentage
- Per-installation scoped checklists
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class OnboardingStep:
    """An onboarding checklist step."""

    step_id: str
    title: str
    description: str
    required: bool = True
    sort_order: int = 0


@dataclass
class UserProgress:
    """A user's onboarding progress."""

    user_id: str
    completed_steps: set[str] = field(default_factory=set)


class AppOnboardingChecklist:
    """Guide new users through setup."""

    def __init__(self) -> None:
        self._steps: dict[tuple[str, str], OnboardingStep] = {}
        self._progress: dict[tuple[str, str], UserProgress] = {}

    def add_step(
        self, installation_id: str, step_id: str, title: str,
        description: str, required: bool = True, sort_order: int = 0,
    ) -> OnboardingStep:
        if not installation_id:
            raise ValueError("installation_id is required")
        step = OnboardingStep(
            step_id=step_id, title=title, description=description,
            required=required, sort_order=sort_order,
        )
        self._steps[(installation_id, step_id)] = step
        return step

    def complete_step(self, installation_id: str, user_id: str, step_id: str) -> UserProgress:
        if (installation_id, step_id) not in self._steps:
            raise KeyError(f"Step {step_id} not found")
        key = (installation_id, user_id)
        progress = self._progress.setdefault(key, UserProgress(user_id=user_id))
        progress.completed_steps.add(step_id)
        return progress

    def completion_pct(self, installation_id: str, user_id: str) -> float:
        steps = self._get_steps(installation_id)
        required = [s for s in steps if s.required]
        if not required:
            return 100.0
        progress = self._progress.get((installation_id, user_id))
        if progress is None:
            return 0.0
        completed = sum(1 for s in required if s.step_id in progress.completed_steps)
        return round(completed / len(required) * 100, 1)

    def is_complete(self, installation_id: str, user_id: str) -> bool:
        return self.completion_pct(installation_id, user_id) >= 100.0

    def remaining_steps(self, installation_id: str, user_id: str) -> list[OnboardingStep]:
        steps = self._get_steps(installation_id)
        progress = self._progress.get((installation_id, user_id))
        completed = progress.completed_steps if progress else set()
        return [s for s in steps if s.step_id not in completed and s.required]

    def _get_steps(self, installation_id: str) -> list[OnboardingStep]:
        steps = [s for (inst, _), s in self._steps.items() if inst == installation_id]
        return sorted(steps, key=lambda s: s.sort_order)
