"""User activity tracker — track user actions for analytics."""

from datetime import datetime, timedelta


def track_activity(*, user_id: str, action: str, resource: str,
                     metadata: dict | None = None) -> dict:
    return {
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow().isoformat(),
    }


def get_activity_summary(*, activities: list[dict], period_days: int = 7) -> dict:
    by_action: dict[str, int] = {}
    by_user: dict[str, int] = {}
    daily: dict[str, int] = {}
    for a in activities:
        action = a.get("action", "unknown")
        by_action[action] = by_action.get(action, 0) + 1
        uid = a.get("user_id", "")
        by_user[uid] = by_user.get(uid, 0) + 1
        day = a.get("timestamp", "")[:10]
        if day:
            daily[day] = daily.get(day, 0) + 1
    top_actions = sorted(by_action.items(), key=lambda x: x[1], reverse=True)[:5]
    return {
        "total_activities": len(activities),
        "unique_users": len(by_user),
        "top_actions": [{"action": a, "count": c} for a, c in top_actions],
        "daily_counts": dict(sorted(daily.items())),
        "avg_daily": round(len(activities) / max(period_days, 1), 1),
    }
