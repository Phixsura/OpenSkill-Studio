"""App API Developer Engagement Funnel — track developer journey from signup to power user."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

STAGES = ["visited_docs", "created_account", "generated_key", "first_call", "regular_usage", "power_user"]

@dataclass
class FunnelStage:
    stage: str
    count: int = 0

@dataclass
class EngagementFunnel:
    stages: list[FunnelStage]

    @property
    def conversion_rate(self) -> float:
        if not self.stages or self.stages[0].count == 0: return 0.0
        return round(self.stages[-1].count / self.stages[0].count * 100, 1)

    @property
    def biggest_dropoff(self) -> str:
        worst_stage = ""
        worst_drop = 0.0
        for i in range(1, len(self.stages)):
            if self.stages[i - 1].count > 0:
                drop = (self.stages[i - 1].count - self.stages[i].count) / self.stages[i - 1].count * 100
                if drop > worst_drop:
                    worst_drop = drop
                    worst_stage = self.stages[i].stage
        return worst_stage

class AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperEngagementFunnel:
    def __init__(self) -> None:
        self._funnels: dict[str, EngagementFunnel] = {}

    def update(self, installation_id: str, stage_counts: dict[str, int]) -> EngagementFunnel:
        if not installation_id: raise ValueError("installation_id is required")
        stages = [FunnelStage(stage=s, count=stage_counts.get(s, 0)) for s in STAGES]
        f = EngagementFunnel(stages=stages)
        self._funnels[installation_id] = f
        return f

    def get(self, installation_id: str) -> EngagementFunnel | None:
        return self._funnels.get(installation_id)
