"""Badge System — award achievement badges to extensions and developers.

Tracks milestones and automatically awards badges based on metrics
like downloads, ratings, contribution streak, and community impact.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Badge:
    badge_id: str
    name: str
    description: str
    icon: str
    tier: str = "bronze"  # bronze, silver, gold, platinum


@dataclass
class AwardedBadge:
    badge: Badge
    awarded_to: str
    awarded_at: str = ""

    def __post_init__(self):
        if not self.awarded_at:
            self.awarded_at = datetime.now(timezone.utc).isoformat()


BADGE_DEFINITIONS: dict[str, Badge] = {
    "first_extension": Badge("first_extension", "First Extension", "Published your first extension", "🎉"),
    "popular_10k": Badge("popular_10k", "Popular", "10,000+ total downloads", "🔥", "silver"),
    "popular_100k": Badge("popular_100k", "Viral", "100,000+ total downloads", "💥", "gold"),
    "top_rated": Badge("top_rated", "Top Rated", "Average rating above 4.5", "⭐", "gold"),
    "prolific": Badge("prolific", "Prolific", "Published 10+ extensions", "📦", "silver"),
    "security_clean": Badge("security_clean", "Security Champion", "Zero security incidents", "🛡️"),
    "fast_responder": Badge("fast_responder", "Fast Responder", "Average support response under 4 hours", "⚡", "silver"),
    "community_hero": Badge("community_hero", "Community Hero", "50+ community contributions", "🦸", "gold"),
    "veteran": Badge("veteran", "Veteran", "Active for over 1 year", "🏅", "silver"),
    "platinum_dev": Badge("platinum_dev", "Platinum Developer", "Platinum reputation tier", "💎", "platinum"),
}


class BadgeSystem:
    """Awards and tracks achievement badges."""

    def __init__(self):
        self._awards: dict[str, list[AwardedBadge]] = {}  # entity_id -> badges

    def check_and_award(self, entity_id: str, metrics: dict) -> list[AwardedBadge]:
        """Check metrics and award any earned badges."""
        existing = {ab.badge.badge_id for ab in self._awards.get(entity_id, [])}
        newly_awarded = []

        checks = [
            ("first_extension", metrics.get("extension_count", 0) >= 1),
            ("popular_10k", metrics.get("total_downloads", 0) >= 10000),
            ("popular_100k", metrics.get("total_downloads", 0) >= 100000),
            ("top_rated", metrics.get("avg_rating", 0) >= 4.5 and metrics.get("review_count", 0) >= 5),
            ("prolific", metrics.get("extension_count", 0) >= 10),
            ("security_clean", metrics.get("security_incidents", 0) == 0 and metrics.get("extension_count", 0) >= 1),
            ("fast_responder", metrics.get("avg_response_hours", 999) < 4),
            ("community_hero", metrics.get("contributions", 0) >= 50),
            ("veteran", metrics.get("account_age_days", 0) >= 365),
            ("platinum_dev", metrics.get("reputation_tier") == "platinum"),
        ]

        for badge_id, earned in checks:
            if earned and badge_id not in existing:
                badge = BADGE_DEFINITIONS[badge_id]
                award = AwardedBadge(badge=badge, awarded_to=entity_id)
                self._awards.setdefault(entity_id, []).append(award)
                newly_awarded.append(award)

        return newly_awarded

    def get_badges(self, entity_id: str) -> list[AwardedBadge]:
        return list(self._awards.get(entity_id, []))

    def has_badge(self, entity_id: str, badge_id: str) -> bool:
        return any(ab.badge.badge_id == badge_id for ab in self._awards.get(entity_id, []))

    def get_available_badges(self) -> list[Badge]:
        return list(BADGE_DEFINITIONS.values())

    def get_badge_holders(self, badge_id: str) -> list[str]:
        return [eid for eid, awards in self._awards.items()
                if any(ab.badge.badge_id == badge_id for ab in awards)]
