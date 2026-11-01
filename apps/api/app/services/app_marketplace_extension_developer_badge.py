"""Developer Badge — achievement badges for extension developers.

Awards badges based on milestones (first extension, 100 installs,
5-star rating), tracks progress, and displays developer achievements.
"""
from __future__ import annotations
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Badge:
    badge_id: str
    name: str
    description: str
    icon: str
    tier: str  # bronze, silver, gold, platinum
    requirement: str
    threshold: int


@dataclass
class DeveloperBadge:
    badge_id: str
    developer_id: str
    earned_at: float = 0.0


BADGE_CATALOG = [
    Badge("first_ext", "First Extension", "Published your first extension", "🎯", "bronze", "extensions_published", 1),
    Badge("popular_10", "Getting Popular", "10+ installs on an extension", "📈", "bronze", "max_installs", 10),
    Badge("popular_100", "Rising Star", "100+ installs", "⭐", "silver", "max_installs", 100),
    Badge("popular_1000", "Marketplace Hit", "1,000+ installs", "🌟", "gold", "max_installs", 1000),
    Badge("five_star", "Perfect Score", "5-star average rating", "💎", "gold", "avg_rating_x10", 50),
    Badge("prolific_5", "Prolific Creator", "Published 5+ extensions", "🏗️", "silver", "extensions_published", 5),
    Badge("prolific_10", "Extension Factory", "Published 10+ extensions", "🏭", "gold", "extensions_published", 10),
    Badge("revenue_100", "First Revenue", "$100+ earned", "💰", "bronze", "revenue_cents", 10000),
    Badge("revenue_1000", "Profitable", "$1,000+ earned", "💵", "silver", "revenue_cents", 100000),
    Badge("contributor", "Open Source Hero", "Contributed to 3+ extensions", "🤝", "silver", "contributions", 3),
]


class DeveloperBadgeService:
    """Awards and tracks developer achievement badges."""

    def __init__(self):
        self._earned: dict[str, dict[str, DeveloperBadge]] = defaultdict(dict)
        self._metrics: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def update_metric(self, developer_id: str, metric: str, value: int) -> list[Badge]:
        self._metrics[developer_id][metric] = max(self._metrics[developer_id][metric], value)
        return self._check_badges(developer_id)

    def increment_metric(self, developer_id: str, metric: str, amount: int = 1) -> list[Badge]:
        self._metrics[developer_id][metric] += amount
        return self._check_badges(developer_id)

    def _check_badges(self, developer_id: str) -> list[Badge]:
        newly_earned: list[Badge] = []
        metrics = self._metrics[developer_id]
        earned = self._earned[developer_id]

        for badge in BADGE_CATALOG:
            if badge.badge_id in earned:
                continue
            if metrics.get(badge.requirement, 0) >= badge.threshold:
                earned[badge.badge_id] = DeveloperBadge(
                    badge_id=badge.badge_id, developer_id=developer_id,
                    earned_at=time.time(),
                )
                newly_earned.append(badge)

        return newly_earned

    def get_badges(self, developer_id: str) -> list[Badge]:
        earned_ids = set(self._earned.get(developer_id, {}).keys())
        return [b for b in BADGE_CATALOG if b.badge_id in earned_ids]

    def get_progress(self, developer_id: str) -> list[dict]:
        metrics = self._metrics.get(developer_id, {})
        earned_ids = set(self._earned.get(developer_id, {}).keys())
        return [{
            "badge": b.name, "icon": b.icon, "tier": b.tier,
            "earned": b.badge_id in earned_ids,
            "progress": min(metrics.get(b.requirement, 0), b.threshold),
            "threshold": b.threshold,
            "percent": min(100, round(metrics.get(b.requirement, 0) / b.threshold * 100)),
        } for b in BADGE_CATALOG]
