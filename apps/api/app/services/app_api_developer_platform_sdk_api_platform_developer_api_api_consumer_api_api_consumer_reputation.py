"""API Consumer Reputation — track consumer reliability and trust scores."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ReputationScore:
    consumer_id: str
    score: int = 100  # 0-100
    violations: int = 0
    good_standing_days: int = 0
    tier: str = "trusted"  # "trusted", "standard", "restricted", "blocked"

    def apply_penalty(self, points: int) -> None:
        self.score = max(0, self.score - points)
        self.violations += 1
        self._update_tier()

    def apply_reward(self, points: int) -> None:
        self.score = min(100, self.score + points)
        self._update_tier()

    def _update_tier(self) -> None:
        if self.score >= 80: self.tier = "trusted"
        elif self.score >= 50: self.tier = "standard"
        elif self.score >= 20: self.tier = "restricted"
        else: self.tier = "blocked"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerReputation:
    def __init__(self) -> None:
        self._scores: dict[tuple[str, str], ReputationScore] = {}

    def get_or_create(self, installation_id: str, consumer_id: str) -> ReputationScore:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        if key not in self._scores:
            self._scores[key] = ReputationScore(consumer_id=consumer_id)
        return self._scores[key]

    def penalize(self, installation_id: str, consumer_id: str, points: int, reason: str = "") -> ReputationScore:
        if points < 1: raise ValueError("points must be >= 1")
        score = self.get_or_create(installation_id, consumer_id)
        score.apply_penalty(points)
        return score

    def reward(self, installation_id: str, consumer_id: str, points: int) -> ReputationScore:
        if points < 1: raise ValueError("points must be >= 1")
        score = self.get_or_create(installation_id, consumer_id)
        score.apply_reward(points)
        return score

    def blocked_consumers(self, installation_id: str) -> list[ReputationScore]:
        return [s for (inst, _), s in self._scores.items() if inst == installation_id and s.tier == "blocked"]

    def list_scores(self, installation_id: str) -> list[ReputationScore]:
        return [s for (inst, _), s in self._scores.items() if inst == installation_id]
