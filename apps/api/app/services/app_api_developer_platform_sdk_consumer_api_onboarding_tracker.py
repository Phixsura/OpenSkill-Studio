"""Consumer Onboarding Tracker — step-based onboarding with progress tracking."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()


@dataclass
class OnboardingStep:
    step_id: str
    name: str
    description: str = ""
    required: bool = True
    order: int = 0


@dataclass
class StepCompletion:
    step_id: str
    completed_at: str
    metadata: dict = field(default_factory=dict)


@dataclass
class OnboardingTracker:
    """Track consumer onboarding progress through defined steps."""

    _steps: list[OnboardingStep] = field(default_factory=list)
    _completions: dict[str, dict[str, StepCompletion]] = field(default_factory=dict)  # consumer -> {step_id: completion}

    def define_step(self, step: OnboardingStep) -> dict:
        for existing in self._steps:
            if existing.step_id == step.step_id:
                raise ValueError(f"Step {step.step_id} already defined")
        self._steps.append(step)
        self._steps.sort(key=lambda s: s.order)
        logger.info("onboarding_step_defined", step_id=step.step_id)
        return {"step_id": step.step_id, "total_steps": len(self._steps)}

    def complete_step(self, consumer_id: str, step_id: str, metadata: dict | None = None) -> dict:
        valid_ids = {s.step_id for s in self._steps}
        if step_id not in valid_ids:
            raise ValueError(f"Step {step_id} not defined")
        completions = self._completions.setdefault(consumer_id, {})
        if step_id in completions:
            return {"already_completed": True, "step_id": step_id}
        completions[step_id] = StepCompletion(
            step_id=step_id,
            completed_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )
        logger.info("step_completed", consumer_id=consumer_id, step_id=step_id)
        progress = self._calc_progress(consumer_id)
        return {"step_id": step_id, "completed": True, **progress}

    def _calc_progress(self, consumer_id: str) -> dict:
        completions = self._completions.get(consumer_id, {})
        total = len(self._steps)
        completed = sum(1 for s in self._steps if s.step_id in completions)
        required_total = sum(1 for s in self._steps if s.required)
        required_done = sum(1 for s in self._steps if s.required and s.step_id in completions)
        pct = round(completed / total * 100, 1) if total > 0 else 0
        return {
            "completed_count": completed,
            "total_steps": total,
            "progress_pct": pct,
            "required_done": required_done,
            "required_total": required_total,
            "onboarding_complete": required_done >= required_total and required_total > 0,
        }

    def get_progress(self, consumer_id: str) -> dict:
        progress = self._calc_progress(consumer_id)
        completions = self._completions.get(consumer_id, {})
        steps = []
        for s in self._steps:
            comp = completions.get(s.step_id)
            steps.append({
                "step_id": s.step_id,
                "name": s.name,
                "required": s.required,
                "completed": comp is not None,
                "completed_at": comp.completed_at if comp else None,
            })
        return {"consumer_id": consumer_id, **progress, "steps": steps}

    def get_next_step(self, consumer_id: str) -> dict | None:
        completions = self._completions.get(consumer_id, {})
        for s in self._steps:
            if s.step_id not in completions:
                return {"step_id": s.step_id, "name": s.name, "required": s.required}
        return None

    def get_completion_stats(self) -> dict:
        total_consumers = len(self._completions)
        fully_complete = sum(
            1 for cid in self._completions
            if self._calc_progress(cid)["onboarding_complete"]
        )
        return {
            "total_consumers": total_consumers,
            "fully_complete": fully_complete,
            "completion_rate": round(fully_complete / total_consumers * 100, 1) if total_consumers > 0 else 0,
        }

    def reset_consumer(self, consumer_id: str) -> dict:
        removed = consumer_id in self._completions
        self._completions.pop(consumer_id, None)
        return {"reset": removed}
