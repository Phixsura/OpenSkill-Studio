"""Badge system — earn and display badges on app listings."""

APP_BADGES = {
    "verified": {"label": "Verified", "icon": "✅", "color": "blue", "description": "Verified developer"},
    "popular": {"label": "Popular", "icon": "🔥", "color": "orange", "description": "1000+ installs"},
    "top_rated": {"label": "Top Rated", "icon": "⭐", "color": "yellow", "description": "4.5+ average rating"},
    "new": {"label": "New", "icon": "🆕", "color": "green", "description": "Published in last 30 days"},
    "trending": {"label": "Trending", "icon": "📈", "color": "purple", "description": "Fast-growing installs"},
    "security_certified": {"label": "Security Certified", "icon": "🔒", "color": "indigo", "description": "Passed security audit"},
    "open_source": {"label": "Open Source", "icon": "📖", "color": "gray", "description": "Source code available"},
}


def compute_badges(*, app: dict) -> list[dict]:
    badges = []
    if app.get("developer_verified"):
        badges.append(APP_BADGES["verified"])
    if app.get("install_count", 0) >= 1000:
        badges.append(APP_BADGES["popular"])
    if app.get("avg_rating", 0) >= 4.5 and app.get("review_count", 0) >= 10:
        badges.append(APP_BADGES["top_rated"])
    if app.get("is_new"):
        badges.append(APP_BADGES["new"])
    if app.get("trending"):
        badges.append(APP_BADGES["trending"])
    if app.get("security_certified"):
        badges.append(APP_BADGES["security_certified"])
    if app.get("open_source"):
        badges.append(APP_BADGES["open_source"])
    return badges


def get_badge_info(*, badge_id: str) -> dict | None:
    return APP_BADGES.get(badge_id)
