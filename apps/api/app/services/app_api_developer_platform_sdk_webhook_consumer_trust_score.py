"""App API Developer Webhook Consumer Trust Score — compute trust scores for consumers."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerTrustScore:
    consumer_id: str
    auth_success_rate: float = 100.0
    payload_valid_rate: float = 100.0
    response_time_score: float = 100.0
    days_active: int = 0
    violations: int = 0

    @property
    def trust_score(self) -> int:
        s = int((self.auth_success_rate * 0.25 + self.payload_valid_rate * 0.20 + self.response_time_score * 0.15) + min(self.days_active, 365) / 365 * 20)
        s -= self.violations * 5
        return max(0, min(100, s))

    @property
    def trust_tier(self) -> str:
        t = self.trust_score
        if t >= 90: return "trusted"
        if t >= 70: return "verified"
        if t >= 50: return "standard"
        return "restricted"

class AppAPIDeveloperPlatformSDKWebhookConsumerTrustScore:
    def __init__(self) -> None:
        self._scores: dict[tuple[str, str], ConsumerTrustScore] = {}

    def compute(self, installation_id: str, consumer_id: str, **kwargs) -> ConsumerTrustScore:
        if not installation_id: raise ValueError("installation_id is required")
        s = ConsumerTrustScore(consumer_id=consumer_id)
        for k, v in kwargs.items():
            if hasattr(s, k): setattr(s, k, v)
        self._scores[(installation_id, consumer_id)] = s
        return s

    def restricted(self, installation_id: str) -> list[ConsumerTrustScore]:
        return [s for (inst, _), s in self._scores.items() if inst == installation_id and s.trust_tier == "restricted"]

    def ranked(self, installation_id: str) -> list[ConsumerTrustScore]:
        scores = [s for (inst, _), s in self._scores.items() if inst == installation_id]
        return sorted(scores, key=lambda s: s.trust_score, reverse=True)
