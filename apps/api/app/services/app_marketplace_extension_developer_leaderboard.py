"""Developer Leaderboard — rank developers by contributions and impact.

Ranks by installs, ratings, extensions published, revenue, and
generates weekly/monthly leaderboards with position tracking.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class LeaderboardMetric(str, Enum):
    INSTALLS = "installs"
    RATING = "rating"
    EXTENSIONS = "extensions"
    REVENUE = "revenue"
    CONTRIBUTIONS = "contributions"


@dataclass
class DeveloperScore:
    developer_id: str
    name: str
    installs: int = 0
    avg_rating: float = 0.0
    extensions: int = 0
    revenue_cents: int = 0
    contributions: int = 0

    @property
    def composite_score(self) -> float:
        return round(self.installs * 0.3 + self.avg_rating * 1000 + self.extensions * 500
                     + self.revenue_cents * 0.01 + self.contributions * 200, 1)


class DeveloperLeaderboardService:
    """Ranks developers across multiple metrics."""

    def __init__(self):
        self._scores: dict[str, DeveloperScore] = {}

    def update(self, developer_id: str, name: str, **metrics: int | float) -> DeveloperScore:
        if developer_id not in self._scores:
            self._scores[developer_id] = DeveloperScore(developer_id=developer_id, name=name)
        score = self._scores[developer_id]
        score.name = name
        for key, val in metrics.items():
            if hasattr(score, key):
                setattr(score, key, val)
        return score

    def get_leaderboard(self, metric: LeaderboardMetric = LeaderboardMetric.INSTALLS,
                        limit: int = 10) -> list[dict]:
        scores = list(self._scores.values())
        if metric == LeaderboardMetric.INSTALLS:
            scores.sort(key=lambda s: s.installs, reverse=True)
        elif metric == LeaderboardMetric.RATING:
            scores.sort(key=lambda s: s.avg_rating, reverse=True)
        elif metric == LeaderboardMetric.EXTENSIONS:
            scores.sort(key=lambda s: s.extensions, reverse=True)
        elif metric == LeaderboardMetric.REVENUE:
            scores.sort(key=lambda s: s.revenue_cents, reverse=True)
        else:
            scores.sort(key=lambda s: s.composite_score, reverse=True)

        return [{"rank": i + 1, "developer_id": s.developer_id, "name": s.name,
                 "value": getattr(s, metric.value, s.composite_score),
                 "composite_score": s.composite_score}
                for i, s in enumerate(scores[:limit])]

    def get_rank(self, developer_id: str) -> dict:
        scores = sorted(self._scores.values(), key=lambda s: s.composite_score, reverse=True)
        for i, s in enumerate(scores):
            if s.developer_id == developer_id:
                return {"rank": i + 1, "total": len(scores),
                        "percentile": round((1 - i / max(len(scores), 1)) * 100, 1),
                        "score": s.composite_score}
        return {"rank": 0, "total": len(scores)}
