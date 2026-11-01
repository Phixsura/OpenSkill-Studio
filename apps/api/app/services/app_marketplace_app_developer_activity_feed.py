"""Developer activity feed — unified activity stream across all developer actions."""

from datetime import datetime, timezone

ACTIVITY_ICONS = {
    "app_created": "📦", "version_published": "🚀", "review_received": "⭐",
    "install_milestone": "📈", "webhook_configured": "🔗", "api_key_created": "🔑",
    "team_member_added": "👥", "config_updated": "⚙️", "badge_earned": "🏆",
}


def create_activity(*, type: str, actor_id: str, app_id: str | None = None,
                      message: str = "") -> dict:
    return {"type": type, "actor_id": actor_id, "app_id": app_id,
            "message": message, "icon": ACTIVITY_ICONS.get(type, "📌"),
            "timestamp": datetime.now(timezone.utc).isoformat()}


def build_activity_feed(*, activities: list[dict], limit: int = 20) -> dict:
    sorted_acts = sorted(activities, key=lambda a: a.get("timestamp", ""), reverse=True)[:limit]
    return {"activities": sorted_acts, "total": len(activities), "showing": len(sorted_acts)}


def group_activities_by_day(*, activities: list[dict]) -> list[dict]:
    groups: dict[str, list] = {}
    for a in activities:
        day = a.get("timestamp", "")[:10]
        groups.setdefault(day, []).append(a)
    return [{"date": d, "activities": acts, "count": len(acts)} for d, acts in sorted(groups.items(), reverse=True)]
