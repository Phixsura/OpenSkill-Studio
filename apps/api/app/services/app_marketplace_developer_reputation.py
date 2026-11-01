"""Developer Reputation — calculate and track developer trust scores.

Computes reputation scores based on extension quality, review ratings,
response times, security track record, and community contributions.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class ReputationTier(str, Enum):
    NEW = "new"            # 0-199
    BRONZE = "bronze"      # 200-499
    SILVER = "silver"      # 500-799
    GOLD = "gold"          # 800-1199
    PLATINUM = "platinum"  # 1200+


@dataclass
class ReputationFactors:
    extension_count: int = 0
    avg_rating: float = 0.0
    total_downloads: int = 0
    security_incidents: int = 0
    support_response_hours: float = 24.0
    review_response_rate: float = 0.0  # 0-1
    policy_violations: int = 0
    community_contributions: int = 0
    account_age_days: int = 0


class DeveloperReputationService:
    """Calculates and manages developer reputation scores."""

    WEIGHTS = {
        "extensions": 50,
        "ratings": 200,
        "downloads": 100,
        "security": -150,
        "support": 100,
        "reviews": 50,
        "violations": -200,
        "community": 30,
        "tenure": 20,
    }

    def __init__(self):
        self._scores: dict[str, int] = {}
        self._factors: dict[str, ReputationFactors] = {}
        self._history: dict[str, list[dict]] = {}

    def calculate_score(self, factors: ReputationFactors) -> int:
        """Calculate reputation score from factors."""
        score = 0
        # Extensions published (capped at 10)
        score += min(factors.extension_count, 10) * self.WEIGHTS["extensions"] // 10
        # Average rating (0-5 scale)
        score += int(factors.avg_rating / 5 * self.WEIGHTS["ratings"])
        # Downloads (log scale, capped)
        import math
        if factors.total_downloads > 0:
            score += int(min(math.log10(factors.total_downloads) / 6, 1.0) * self.WEIGHTS["downloads"])
        # Security incidents (penalty)
        score += factors.security_incidents * self.WEIGHTS["security"]
        # Support response time (faster = better, under 4h = max)
        if factors.support_response_hours <= 4:
            score += self.WEIGHTS["support"]
        elif factors.support_response_hours <= 24:
            score += int((1 - factors.support_response_hours / 24) * self.WEIGHTS["support"])
        # Review response rate
        score += int(factors.review_response_rate * self.WEIGHTS["reviews"])
        # Policy violations (penalty)
        score += factors.policy_violations * self.WEIGHTS["violations"]
        # Community contributions
        score += min(factors.community_contributions, 20) * self.WEIGHTS["community"] // 20
        # Account age
        score += min(factors.account_age_days, 365) * self.WEIGHTS["tenure"] // 365

        return max(0, score)

    def get_tier(self, score: int) -> ReputationTier:
        if score >= 1200:
            return ReputationTier.PLATINUM
        elif score >= 800:
            return ReputationTier.GOLD
        elif score >= 500:
            return ReputationTier.SILVER
        elif score >= 200:
            return ReputationTier.BRONZE
        return ReputationTier.NEW

    def update(self, developer_id: str, factors: ReputationFactors) -> dict:
        """Update a developer's reputation."""
        score = self.calculate_score(factors)
        tier = self.get_tier(score)
        self._scores[developer_id] = score
        self._factors[developer_id] = factors
        self._history.setdefault(developer_id, []).append({"score": score, "tier": tier.value})
        return {"developer_id": developer_id, "score": score, "tier": tier.value}

    def get_reputation(self, developer_id: str) -> dict | None:
        score = self._scores.get(developer_id)
        if score is None:
            return None
        return {
            "developer_id": developer_id,
            "score": score,
            "tier": self.get_tier(score).value,
            "factors": self._factors.get(developer_id),
        }

    def get_leaderboard(self, limit: int = 10) -> list[dict]:
        return sorted(
            [{"developer_id": did, "score": s, "tier": self.get_tier(s).value}
             for did, s in self._scores.items()],
            key=lambda x: x["score"], reverse=True,
        )[:limit]
