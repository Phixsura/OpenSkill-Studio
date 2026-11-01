"""App API Developer Consumer Engagement Score — composite engagement scoring."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class EngagementScore:
    consumer_id: str
    api_call_frequency: float  # calls per day
    endpoint_diversity: int  # unique endpoints used
    error_rate_pct: float
    days_since_last_call: int
    uses_webhooks: bool = False
    uses_sdk: bool = False

    @property
    def score(self) -> int:
        s = 0
        if self.api_call_frequency >= 100: s += 30
        elif self.api_call_frequency >= 10: s += 20
        elif self.api_call_frequency >= 1: s += 10
        if self.endpoint_diversity >= 10: s += 20
        elif self.endpoint_diversity >= 5: s += 15
        elif self.endpoint_diversity >= 2: s += 10
        if self.error_rate_pct < 1: s += 20
        elif self.error_rate_pct < 5: s += 10
        if self.days_since_last_call == 0: s += 15
        elif self.days_since_last_call <= 7: s += 10
        if self.uses_webhooks: s += 10
        if self.uses_sdk: s += 5
        return min(s, 100)

    @property
    def tier(self) -> str:
        s = self.score
        if s >= 80: return "champion"
        if s >= 60: return "active"
        if s >= 40: return "moderate"
        if s >= 20: return "casual"
        return "dormant"

class AppAPIDeveloperAPIApiConsumerEngagementScore:
    def __init__(self) -> None:
        self._scores: dict[tuple[str, str], EngagementScore] = {}

    def calculate(self, installation_id: str, consumer_id: str, api_call_frequency: float, endpoint_diversity: int, error_rate_pct: float, days_since_last_call: int, uses_webhooks: bool = False, uses_sdk: bool = False) -> EngagementScore:
        if not installation_id: raise ValueError("installation_id is required")
        e = EngagementScore(consumer_id=consumer_id, api_call_frequency=api_call_frequency, endpoint_diversity=endpoint_diversity, error_rate_pct=error_rate_pct, days_since_last_call=days_since_last_call, uses_webhooks=uses_webhooks, uses_sdk=uses_sdk)
        self._scores[(installation_id, consumer_id)] = e
        return e

    def ranked(self, installation_id: str) -> list[EngagementScore]:
        scores = [e for (inst, _), e in self._scores.items() if inst == installation_id]
        return sorted(scores, key=lambda e: e.score, reverse=True)

    def by_tier(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), e in self._scores.items():
            if inst == installation_id:
                counts[e.tier] = counts.get(e.tier, 0) + 1
        return counts
