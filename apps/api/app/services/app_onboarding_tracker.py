"""App Onboarding Tracker — track user onboarding progress.

Manages onboarding step completion for installed apps:
- Define onboarding steps
- Track per-user progress
- Compute completion percentage
- Per-installation scoped onboarding
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class OnboardingStep:
    """An onboarding step definition."""

    step_id: str
    name: str
    order: int
    required: bool = True


@dataclass
class UserProgress:
    """A user's onboarding progress."""

    user_id: str
    completed_steps: set[str] = field(default_factory=set)
    started_at: float = field(default_factory=time.time)
    completed_at: float | None = None


class AppOnboardingTracker:
    """Track user onboarding progress."""

    def __init__(self) -> None:
        # installation_id → list[OnboardingStep]
        self._steps: dict[str, list[OnboardingStep]] = {}
        # (installation_id, user_id) → UserProgress
        self._progress: dict[tuple[str, str], UserProgress] = {}

    def define_steps(
        self, installation_id: str, steps: list[dict]
    ) -> list[OnboardingStep]:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not steps:
            raise ValueError("at least one step required")

        step_objs = [
            OnboardingStep(
                step_id=s["step_id"], name=s["name"],
                order=i, required=s.get("required", True),
            )
            for i, s in enumerate(steps)
        ]
        self._steps[installation_id] = step_objs
        return step_objs

    def complete_step(
        self,
        installation_id: str,
        user_id: str,
        step_id: str,
        now: float | None = None,
    ) -> UserProgress:
        if not user_id:
            raise ValueError("user_id is required")

        steps = self._steps.get(installation_id, [])
        valid_ids = {s.step_id for s in steps}
        if step_id not in valid_ids:
            raise KeyError(f"Step {step_id} not found")

        key = (installation_id, user_id)
        if key not in self._progress:
            self._progress[key] = UserProgress(user_id=user_id, started_at=now or time.time())

        progress = self._progress[key]
        progress.completed_steps.add(step_id)

        # Check if all required steps done
        required = {s.step_id for s in steps if s.required}
        if required <= progress.completed_steps and progress.completed_at is None:
            progress.completed_at = now or time.time()

        return progress

    def get_progress(self, installation_id: str, user_id: str) -> dict:
        steps = self._steps.get(installation_id, [])
        key = (installation_id, user_id)
        progress = self._progress.get(key)
        completed = progress.completed_steps if progress else set()
        total = len(steps)
        done = len(completed)

        return {
            "total_steps": total,
            "completed_steps": done,
            "completion_pct": round(done / total * 100, 1) if total > 0 else 0,
            "is_complete": progress.completed_at is not None if progress else False,
            "steps": [
                {"step_id": s.step_id, "name": s.name, "completed": s.step_id in completed, "required": s.required}
                for s in sorted(steps, key=lambda s: s.order)
            ],
        }

    def get_completion_rate(self, installation_id: str) -> float:
        """% of users who completed onboarding."""
        users = [p for (inst, _), p in self._progress.items() if inst == installation_id]
        if not users:
            return 0.0
        completed = sum(1 for p in users if p.completed_at is not None)
        return round(completed / len(users) * 100, 1)
