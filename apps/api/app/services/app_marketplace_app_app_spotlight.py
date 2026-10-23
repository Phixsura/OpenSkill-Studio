"""App spotlight — weekly featured app highlight."""


def create_spotlight(*, app: dict, curator_note: str, week: str) -> dict:
    return {
        "week": week,
        "app_id": app.get("id"),
        "app_name": app.get("name"),
        "category": app.get("category"),
        "rating": app.get("avg_rating", 0),
        "install_count": app.get("install_count", 0),
        "curator_note": curator_note,
        "highlights": [
            f"⭐ {app.get('avg_rating', 0)} rating from {app.get('review_count', 0)} reviews",
            f"📥 {app.get('install_count', 0):,} installs",
            f"🏷️ {app.get('category', 'General')}",
        ],
    }


def get_past_spotlights(*, spotlights: list[dict], limit: int = 4) -> dict:
    sorted_s = sorted(spotlights, key=lambda s: s.get("week", ""), reverse=True)
    return {"spotlights": sorted_s[:limit], "total": len(spotlights)}
