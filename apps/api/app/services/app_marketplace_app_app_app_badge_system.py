"""App badge system — achievement badges for apps and developers."""

import html

BADGES = {
    "verified": {"label": "Verified", "icon": "✅", "description": "Verified by OpenSkill team"},
    "top_rated": {"label": "Top Rated", "icon": "⭐", "description": "Rating above 4.5"},
    "popular": {"label": "Popular", "icon": "🔥", "description": "Over 10,000 installs"},
    "trending": {"label": "Trending", "icon": "📈", "description": "Fastest growing this week"},
    "staff_pick": {"label": "Staff Pick", "icon": "💎", "description": "Recommended by the team"},
    "open_source": {"label": "Open Source", "icon": "🐙", "description": "Source code is public"},
    "new": {"label": "New", "icon": "🆕", "description": "Published in the last 30 days"},
}


def evaluate_badges(*, app: dict) -> dict:
    earned = []
    if app.get("verified"):
        earned.append("verified")
    if app.get("rating", 0) >= 4.5:
        earned.append("top_rated")
    if app.get("installs", 0) >= 10000:
        earned.append("popular")
    if app.get("open_source"):
        earned.append("open_source")
    if app.get("staff_pick"):
        earned.append("staff_pick")
    badges = [{"id": b, **BADGES[b]} for b in earned if b in BADGES]
    return {"badges": badges, "count": len(badges),
            "badge_ids": earned}
