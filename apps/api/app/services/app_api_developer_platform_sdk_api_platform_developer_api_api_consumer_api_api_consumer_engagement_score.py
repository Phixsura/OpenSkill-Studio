"""API Consumer Engagement Score — measure consumer API engagement levels."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class EngagementMetrics:
    consumer_id: str
    requests_per_day: float = 0.0
    unique_endpoints_used: int = 0
    days_since_last_request: int = 0
    webhook_success_rate: float = 100.0
    docs_pages_viewed: int = 0

@dataclass
class EngagementScore:
    consumer_id: str
    score: float  # 0-100
    level: str  # "power_user", "active", "moderate", "low", "dormant"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerEngagementScore:
    def __init__(self) -> None:
        self._metrics: dict[tuple[str, str], EngagementMetrics] = {}

    def update_metrics(self, installation_id: str, metrics: EngagementMetrics) -> EngagementMetrics:
        if not installation_id: raise ValueError("installation_id is required")
        self._metrics[(installation_id, metrics.consumer_id)] = metrics
        return metrics

    def compute(self, installation_id: str, consumer_id: str) -> EngagementScore:
        m = self._metrics.get((installation_id, consumer_id))
        if m is None: return EngagementScore(consumer_id=consumer_id, score=0, level="dormant")
        score = 0.0
        # Request volume (30%)
        score += min(30, m.requests_per_day / 10 * 30)
        # Endpoint diversity (20%)
        score += min(20, m.unique_endpoints_used * 2)
        # Recency (20%)
        recency = max(0, 20 - m.days_since_last_request * 2)
        score += recency
        # Webhook health (15%)
        score += m.webhook_success_rate / 100 * 15
        # Docs engagement (15%)
        score += min(15, m.docs_pages_viewed * 1.5)
        score = round(min(100, score), 1)
        if score >= 80: level = "power_user"
        elif score >= 60: level = "active"
        elif score >= 40: level = "moderate"
        elif score >= 20: level = "low"
        else: level = "dormant"
        return EngagementScore(consumer_id=consumer_id, score=score, level=level)

    def list_scores(self, installation_id: str) -> list[EngagementScore]:
        return [self.compute(installation_id, cid) for (inst, cid) in self._metrics if inst == installation_id]

    def dormant_consumers(self, installation_id: str) -> list[EngagementScore]:
        return [s for s in self.list_scores(installation_id) if s.level == "dormant"]
