"""App Analytics Funnel — track user conversion funnels for installed apps.

Manages multi-step conversion funnels:
- Define funnel steps
- Record user progress through steps
- Compute conversion rates between steps
- Drop-off analysis
- Per-installation scoped funnels
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class FunnelStep:
    """A step in a conversion funnel."""

    step_id: str
    name: str
    order: int


@dataclass
class Funnel:
    """A conversion funnel definition."""

    funnel_id: str
    installation_id: str
    name: str
    steps: list[FunnelStep] = field(default_factory=list)


@dataclass
class StepMetrics:
    """Metrics for a single funnel step."""

    step_id: str
    name: str
    entered: int
    conversion_pct: float  # % of step-1 users who reached this step
    drop_off_pct: float    # % lost between previous step and this one


class AppAnalyticsFunnel:
    """Track user conversion funnels."""

    def __init__(self) -> None:
        self._funnels: dict[tuple[str, str], Funnel] = {}
        # (installation_id, funnel_id, step_id) → set of user_ids
        self._progress: dict[tuple[str, str, str], set[str]] = {}

    def create_funnel(
        self,
        installation_id: str,
        funnel_id: str,
        name: str,
        steps: list[dict],
    ) -> Funnel:
        """Create a funnel with ordered steps."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not funnel_id:
            raise ValueError("funnel_id is required")
        if len(steps) < 2:
            raise ValueError("At least 2 steps required")

        key = (installation_id, funnel_id)
        if key in self._funnels:
            raise ValueError(f"Funnel {funnel_id} already exists")

        step_objs = [
            FunnelStep(step_id=s["step_id"], name=s["name"], order=i)
            for i, s in enumerate(steps)
        ]
        funnel = Funnel(
            funnel_id=funnel_id, installation_id=installation_id,
            name=name, steps=step_objs,
        )
        self._funnels[key] = funnel
        return funnel

    def record_step(
        self,
        installation_id: str,
        funnel_id: str,
        step_id: str,
        user_id: str,
    ) -> None:
        """Record a user reaching a funnel step."""
        key = (installation_id, funnel_id)
        if key not in self._funnels:
            raise KeyError(f"Funnel {funnel_id} not found")

        progress_key = (installation_id, funnel_id, step_id)
        self._progress.setdefault(progress_key, set()).add(user_id)

    def get_metrics(
        self, installation_id: str, funnel_id: str
    ) -> list[StepMetrics]:
        """Compute conversion metrics for each step."""
        key = (installation_id, funnel_id)
        funnel = self._funnels.get(key)
        if funnel is None:
            raise KeyError(f"Funnel {funnel_id} not found")

        results: list[StepMetrics] = []
        prev_count = 0

        for step in sorted(funnel.steps, key=lambda s: s.order):
            progress_key = (installation_id, funnel_id, step.step_id)
            users = self._progress.get(progress_key, set())
            count = len(users)

            if step.order == 0:
                conversion = 100.0
                drop_off = 0.0
            else:
                conversion = (count / prev_count * 100) if prev_count > 0 else 0.0
                drop_off = 100.0 - conversion

            results.append(StepMetrics(
                step_id=step.step_id, name=step.name,
                entered=count,
                conversion_pct=round(conversion, 1),
                drop_off_pct=round(drop_off, 1),
            ))
            prev_count = count

        return results

    def get_overall_conversion(
        self, installation_id: str, funnel_id: str
    ) -> float:
        """Overall conversion: first step to last step."""
        metrics = self.get_metrics(installation_id, funnel_id)
        if not metrics or metrics[0].entered == 0:
            return 0.0
        return round(metrics[-1].entered / metrics[0].entered * 100, 1)

    def get_funnel(self, installation_id: str, funnel_id: str) -> Funnel:
        key = (installation_id, funnel_id)
        funnel = self._funnels.get(key)
        if funnel is None:
            raise KeyError(f"Funnel {funnel_id} not found")
        return funnel

    def list_funnels(self, installation_id: str) -> list[Funnel]:
        return [f for (inst, _), f in self._funnels.items() if inst == installation_id]
