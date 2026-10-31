"""API Consumer Health Score — composite health score for each consumer."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class HealthFactors:
    success_rate: float = 100.0  # 0-100
    avg_latency_ms: float = 0.0
    error_spike: bool = False
    quota_usage_pct: float = 0.0  # 0-100
    last_active_hours_ago: float = 0.0

@dataclass
class HealthScore:
    consumer_id: str
    score: float  # 0-100
    grade: str  # "A", "B", "C", "D", "F"
    factors: HealthFactors
    risk_level: str  # "low", "medium", "high", "critical"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerHealthScore:
    def __init__(self) -> None:
        self._factors: dict[tuple[str, str], HealthFactors] = {}

    def update_factors(self, installation_id: str, consumer_id: str, factors: HealthFactors) -> HealthFactors:
        if not installation_id: raise ValueError("installation_id is required")
        self._factors[(installation_id, consumer_id)] = factors
        return factors

    def compute(self, installation_id: str, consumer_id: str) -> HealthScore:
        f = self._factors.get((installation_id, consumer_id))
        if f is None: raise KeyError(f"No factors for {consumer_id}")
        # Weighted score
        score = 0.0
        score += min(f.success_rate, 100) * 0.4  # 40% weight
        latency_score = max(0, 100 - (f.avg_latency_ms / 10))  # 1000ms = 0 score
        score += latency_score * 0.2  # 20% weight
        score += (100 - min(f.quota_usage_pct, 100)) * 0.2  # 20% weight
        activity_score = max(0, 100 - f.last_active_hours_ago * 2)  # 50h = 0
        score += activity_score * 0.1  # 10% weight
        if not f.error_spike: score += 10  # 10% bonus
        score = round(min(100, max(0, score)), 1)
        grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F"
        risk = "low" if score >= 80 else "medium" if score >= 60 else "high" if score >= 30 else "critical"
        return HealthScore(consumer_id=consumer_id, score=score, grade=grade, factors=f, risk_level=risk)

    def list_scores(self, installation_id: str) -> list[HealthScore]:
        return [self.compute(installation_id, cid) for (inst, cid) in self._factors if inst == installation_id]

    def at_risk(self, installation_id: str, threshold: float = 60.0) -> list[HealthScore]:
        return [s for s in self.list_scores(installation_id) if s.score < threshold]
