"""API Consumer Satisfaction — measure consumer satisfaction from multiple signals."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class SatisfactionSignals:
    consumer_id: str
    api_reliability_pct: float = 100.0
    avg_latency_ms: float = 0.0
    support_resolution_hours: float = 0.0
    documentation_rating: float = 5.0  # 1-5
    nps_score: int = 0  # -100 to 100

@dataclass
class SatisfactionScore:
    consumer_id: str
    score: float  # 0-100
    sentiment: str  # "delighted", "satisfied", "neutral", "dissatisfied"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerSatisfaction:
    def __init__(self) -> None:
        self._signals: dict[tuple[str, str], SatisfactionSignals] = {}

    def update_signals(self, installation_id: str, signals: SatisfactionSignals) -> SatisfactionSignals:
        if not installation_id: raise ValueError("installation_id is required")
        self._signals[(installation_id, signals.consumer_id)] = signals
        return signals

    def compute(self, installation_id: str, consumer_id: str) -> SatisfactionScore:
        s = self._signals.get((installation_id, consumer_id))
        if s is None: return SatisfactionScore(consumer_id=consumer_id, score=50, sentiment="neutral")
        score = 0.0
        score += min(30, s.api_reliability_pct * 0.3)  # 30% weight
        latency_score = max(0, 20 - s.avg_latency_ms / 50)
        score += latency_score  # 20% weight
        support_score = max(0, 15 - s.support_resolution_hours * 0.3)
        score += support_score  # 15% weight
        score += (s.documentation_rating / 5) * 15  # 15% weight
        nps_norm = (s.nps_score + 100) / 200 * 20
        score += nps_norm  # 20% weight
        score = round(min(100, max(0, score)), 1)
        if score >= 80: sentiment = "delighted"
        elif score >= 60: sentiment = "satisfied"
        elif score >= 40: sentiment = "neutral"
        else: sentiment = "dissatisfied"
        return SatisfactionScore(consumer_id=consumer_id, score=score, sentiment=sentiment)

    def average_satisfaction(self, installation_id: str) -> float:
        scores = [self.compute(installation_id, cid) for (inst, cid) in self._signals if inst == installation_id]
        if not scores: return 0.0
        return round(sum(s.score for s in scores) / len(scores), 1)

    def list_scores(self, installation_id: str) -> list[SatisfactionScore]:
        return [self.compute(installation_id, cid) for (inst, cid) in self._signals if inst == installation_id]
