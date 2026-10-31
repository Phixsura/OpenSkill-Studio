"""Developer badge — award and display achievement badges."""


BADGE_DEFINITIONS = {
    "first_app": {"label": "First App", "icon": "🚀", "description": "Published your first app", "tier": "bronze"},
    "popular": {"label": "Popular", "icon": "🔥", "description": "1,000+ total installs", "tier": "silver"},
    "top_rated": {"label": "Top Rated", "icon": "⭐", "description": "Average rating 4.5+", "tier": "gold"},
    "prolific": {"label": "Prolific", "icon": "📚", "description": "Published 10+ apps", "tier": "silver"},
    "contributor": {"label": "Contributor", "icon": "🤝", "description": "50+ helpful reviews", "tier": "bronze"},
    "veteran": {"label": "Veteran", "icon": "🏅", "description": "Active for 2+ years", "tier": "gold"},
    "revenue_100k": {"label": "Revenue Master", "icon": "💰", "description": "$100K+ lifetime revenue", "tier": "platinum"},
}

TIER_ORDER = {"bronze": 0, "silver": 1, "gold": 2, "platinum": 3}


def evaluate_badges(*, developer: dict) -> dict:
    earned = []
    if developer.get("app_count", 0) >= 1:
        earned.append("first_app")
    if developer.get("total_installs", 0) >= 1000:
        earned.append("popular")
    if developer.get("avg_rating", 0) >= 4.5 and developer.get("app_count", 0) >= 1:
        earned.append("top_rated")
    if developer.get("app_count", 0) >= 10:
        earned.append("prolific")
    if developer.get("review_count", 0) >= 50:
        earned.append("contributor")
    if developer.get("years_active", 0) >= 2:
        earned.append("veteran")
    if developer.get("lifetime_revenue", 0) >= 100000:
        earned.append("revenue_100k")

    badges = [{"id": b, **BADGE_DEFINITIONS[b]} for b in earned]
    badges.sort(key=lambda x: TIER_ORDER.get(x["tier"], 0), reverse=True)
    return {"badges": badges, "total_earned": len(badges),
            "total_available": len(BADGE_DEFINITIONS),
            "highest_tier": badges[0]["tier"] if badges else None}
