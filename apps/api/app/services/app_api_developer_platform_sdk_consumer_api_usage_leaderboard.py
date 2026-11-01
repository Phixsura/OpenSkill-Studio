"""Consumer Usage Leaderboard — ranked consumer usage with gamification."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

TIERS = [
    ("bronze", 0), ("silver", 1000), ("gold", 10000),
    ("platinum", 100000), ("diamond", 1000000),
]


@dataclass
class ConsumerScore:
    consumer_id: str
    total_requests: int = 0
    total_endpoints_used: int = 0
    uptime_days: int = 0
    badges: list[str] = field(default_factory=list)


@dataclass
class UsageLeaderboard:
    """Ranked consumer usage with tiers and badges."""

    _scores: dict[str, ConsumerScore] = field(default_factory=dict)

    def record_usage(self, consumer_id: str, requests: int = 1,
                     endpoints_used: int = 0) -> dict:
        if requests < 0:
            raise ValueError("Requests must be non-negative")
        score = self._scores.setdefault(consumer_id, ConsumerScore(consumer_id=consumer_id))
        score.total_requests += requests
        if endpoints_used > score.total_endpoints_used:
            score.total_endpoints_used = endpoints_used
        return {"consumer_id": consumer_id, "total_requests": score.total_requests}

    def _get_tier(self, total_requests: int) -> str:
        tier = "bronze"
        for name, threshold in TIERS:
            if total_requests >= threshold:
                tier = name
        return tier

    def _calc_points(self, score: ConsumerScore) -> int:
        return (score.total_requests +
                score.total_endpoints_used * 100 +
                score.uptime_days * 50)

    def award_badge(self, consumer_id: str, badge: str) -> dict:
        score = self._scores.get(consumer_id)
        if not score:
            raise ValueError(f"Consumer {consumer_id} not found")
        if badge in score.badges:
            return {"awarded": False, "reason": "already_has_badge"}
        score.badges.append(badge)
        logger.info("badge_awarded", consumer_id=consumer_id, badge=badge)
        return {"awarded": True, "badge": badge, "total_badges": len(score.badges)}

    def set_uptime(self, consumer_id: str, days: int) -> dict:
        score = self._scores.setdefault(consumer_id, ConsumerScore(consumer_id=consumer_id))
        score.uptime_days = days
        return {"consumer_id": consumer_id, "uptime_days": days}

    def get_ranking(self, limit: int = 10) -> list[dict]:
        entries = []
        for score in self._scores.values():
            points = self._calc_points(score)
            tier = self._get_tier(score.total_requests)
            entries.append({
                "consumer_id": score.consumer_id,
                "points": points,
                "tier": tier,
                "total_requests": score.total_requests,
                "endpoints_used": score.total_endpoints_used,
                "badges": len(score.badges),
            })
        entries.sort(key=lambda x: x["points"], reverse=True)
        for i, e in enumerate(entries):
            e["rank"] = i + 1
        return entries[:limit]

    def get_consumer_profile(self, consumer_id: str) -> dict | None:
        score = self._scores.get(consumer_id)
        if not score:
            return None
        points = self._calc_points(score)
        tier = self._get_tier(score.total_requests)
        ranking = self.get_ranking(100)
        rank = next((r["rank"] for r in ranking if r["consumer_id"] == consumer_id), 0)
        next_tier_threshold = 0
        for name, thresh in TIERS:
            if thresh > score.total_requests:
                next_tier_threshold = thresh
                break
        return {
            "consumer_id": consumer_id,
            "points": points,
            "tier": tier,
            "rank": rank,
            "total_requests": score.total_requests,
            "endpoints_used": score.total_endpoints_used,
            "uptime_days": score.uptime_days,
            "badges": score.badges,
            "next_tier_at": next_tier_threshold,
            "progress_to_next": round(score.total_requests / next_tier_threshold * 100, 1) if next_tier_threshold > 0 else 100,
        }

    def get_stats(self) -> dict:
        tiers: dict[str, int] = {}
        for score in self._scores.values():
            t = self._get_tier(score.total_requests)
            tiers[t] = tiers.get(t, 0) + 1
        return {
            "total_consumers": len(self._scores),
            "by_tier": tiers,
            "total_badges_awarded": sum(len(s.badges) for s in self._scores.values()),
        }
