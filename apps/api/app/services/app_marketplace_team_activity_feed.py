"""Team activity feed — aggregate team actions across the platform."""

from datetime import datetime, timedelta


def build_activity_feed(*, team_id: str, limit: int = 20) -> dict:
    base = datetime(2026, 10, 23, 12, 0)
    activities = [
        {"id": "a1", "actor": "Alice", "action": "published", "target": "Analytics SDK v2.1",
         "type": "release", "timestamp": (base - timedelta(hours=1)).isoformat()},
        {"id": "a2", "actor": "Bob", "action": "merged", "target": "PR #42: Fix auth flow",
         "type": "code", "timestamp": (base - timedelta(hours=3)).isoformat()},
        {"id": "a3", "actor": "Carol", "action": "replied to", "target": "Review by user_x",
         "type": "review", "timestamp": (base - timedelta(hours=5)).isoformat()},
        {"id": "a4", "actor": "Alice", "action": "created", "target": "Webhook endpoint /events",
         "type": "config", "timestamp": (base - timedelta(hours=8)).isoformat()},
        {"id": "a5", "actor": "Dave", "action": "resolved", "target": "Incident INC-042",
         "type": "incident", "timestamp": (base - timedelta(days=1)).isoformat()},
    ]
    return {
        "team_id": team_id,
        "activities": activities[:limit],
        "total": len(activities),
        "has_more": len(activities) > limit,
    }


def get_activity_stats(*, team_id: str) -> dict:
    return {
        "team_id": team_id,
        "today": {"commits": 12, "reviews": 5, "deployments": 2, "incidents": 0},
        "this_week": {"commits": 67, "reviews": 23, "deployments": 8, "incidents": 1},
        "active_members": 4,
        "busiest_day": "Monday",
    }
