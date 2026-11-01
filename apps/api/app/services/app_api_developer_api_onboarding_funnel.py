"""App API Developer API Onboarding Funnel — track onboarding conversion rates."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class FunnelStage:
    stage_name: str
    entered: int = 0
    completed: int = 0

    @property
    def conversion_rate(self) -> float:
        if self.entered == 0: return 0.0
        return round(self.completed / self.entered * 100, 1)

@dataclass
class OnboardingFunnel:
    stages: list[FunnelStage]

    @property
    def overall_conversion(self) -> float:
        if not self.stages or self.stages[0].entered == 0: return 0.0
        return round(self.stages[-1].completed / self.stages[0].entered * 100, 1)

class AppAPIDeveloperAPIOnboardingFunnel:
    def __init__(self) -> None:
        self._funnels: dict[str, OnboardingFunnel] = {}

    def set_funnel(self, installation_id: str, stages: list[dict]) -> OnboardingFunnel:
        if not installation_id: raise ValueError("installation_id is required")
        if not stages: raise ValueError("at least one stage required")
        stage_objs = [FunnelStage(stage_name=s["name"], entered=s.get("entered", 0), completed=s.get("completed", 0)) for s in stages]
        f = OnboardingFunnel(stages=stage_objs)
        self._funnels[installation_id] = f
        return f

    def get(self, installation_id: str) -> OnboardingFunnel | None:
        return self._funnels.get(installation_id)
