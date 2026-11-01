"""App API Developer Satisfaction — comprehensive developer satisfaction tracking."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class SatisfactionMetrics:
    nps_score: float = 0.0  # -100 to 100
    csat_score: float = 0.0  # 0-5
    total_responses: int = 0
    promoters: int = 0
    passives: int = 0
    detractors: int = 0
    top_praise: str = ""
    top_complaint: str = ""

    @property
    def sentiment(self) -> str:
        if self.nps_score >= 50: return "excellent"
        if self.nps_score >= 0: return "good"
        if self.nps_score >= -50: return "needs_improvement"
        return "critical"

class AppAPIDeveloperSatisfaction:
    def __init__(self) -> None:
        self._metrics: dict[str, SatisfactionMetrics] = {}

    def update(self, installation_id: str, **kwargs) -> SatisfactionMetrics:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._metrics:
            self._metrics[installation_id] = SatisfactionMetrics()
        m = self._metrics[installation_id]
        for k, v in kwargs.items():
            if hasattr(m, k): setattr(m, k, v)
        return m

    def get(self, installation_id: str) -> SatisfactionMetrics:
        return self._metrics.get(installation_id, SatisfactionMetrics())
