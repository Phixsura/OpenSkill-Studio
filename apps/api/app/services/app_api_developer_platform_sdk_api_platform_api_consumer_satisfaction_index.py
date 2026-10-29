"""App API Developer Consumer Satisfaction Index — composite consumer satisfaction."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class SatisfactionIndex:
    consumer_id: str
    api_reliability_score: float = 0.0  # 0-100
    latency_score: float = 0.0
    documentation_score: float = 0.0
    support_score: float = 0.0
    overall_nps: float = 0.0

    @property
    def csi(self) -> float:
        """Consumer Satisfaction Index (0-100)."""
        return round((self.api_reliability_score * 0.30 + self.latency_score * 0.20 + self.documentation_score * 0.15 + self.support_score * 0.15 + (self.overall_nps + 100) / 2 * 0.20), 1)

    @property
    def satisfaction_tier(self) -> str:
        s = self.csi
        if s >= 85: return "delighted"
        if s >= 70: return "satisfied"
        if s >= 50: return "neutral"
        return "dissatisfied"

class AppAPIDeveloperPlatformSDKApiPlatformApiConsumerSatisfactionIndex:
    def __init__(self) -> None:
        self._indices: dict[tuple[str, str], SatisfactionIndex] = {}

    def update(self, installation_id: str, consumer_id: str, **kwargs) -> SatisfactionIndex:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        s = SatisfactionIndex(consumer_id=consumer_id)
        for k, v in kwargs.items():
            if hasattr(s, k): setattr(s, k, v)
        self._indices[key] = s
        return s

    def dissatisfied(self, installation_id: str) -> list[SatisfactionIndex]:
        return [s for (inst, _), s in self._indices.items() if inst == installation_id and s.satisfaction_tier == "dissatisfied"]

    def avg_csi(self, installation_id: str) -> float:
        indices = [s for (inst, _), s in self._indices.items() if inst == installation_id]
        if not indices: return 0.0
        return round(sum(s.csi for s in indices) / len(indices), 1)

    def all_indices(self, installation_id: str) -> list[SatisfactionIndex]:
        return sorted([s for (inst, _), s in self._indices.items() if inst == installation_id], key=lambda s: s.csi, reverse=True)
