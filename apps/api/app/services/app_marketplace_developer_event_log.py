"""Developer event log — comprehensive log of all developer platform events."""

from datetime import datetime, timezone
from collections import defaultdict

EVENT_CATEGORIES = {
    "app": ["app.created", "app.published", "app.updated", "app.deleted"],
    "install": ["install.created", "install.removed", "install.upgraded"],
    "webhook": ["webhook.delivered", "webhook.failed", "webhook.retried"],
    "auth": ["auth.login", "auth.token_created", "auth.token_revoked"],
    "team": ["team.member_added", "team.member_removed", "team.role_changed"],
}


def log_event(*, category: str, event_type: str, actor_id: str,
                app_id: str | None = None, metadata: dict | None = None) -> dict:
    return {"category": category, "event_type": event_type, "actor_id": actor_id,
            "app_id": app_id, "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()}


def query_events(*, events: list[dict], category: str | None = None,
                    actor_id: str | None = None, limit: int = 50) -> list[dict]:
    result = events
    if category:
        result = [e for e in result if e.get("category") == category]
    if actor_id:
        result = [e for e in result if e.get("actor_id") == actor_id]
    return sorted(result, key=lambda e: e.get("timestamp", ""), reverse=True)[:limit]


def compute_activity_stats(*, events: list[dict]) -> dict:
    by_category = defaultdict(int)
    by_actor = defaultdict(int)
    for e in events:
        by_category[e.get("category", "other")] += 1
        by_actor[e.get("actor_id", "unknown")] += 1
    top_actors = sorted(by_actor.items(), key=lambda x: -x[1])[:5]
    return {"total": len(events), "by_category": dict(by_category),
            "unique_actors": len(by_actor), "top_actors": [{"id": a, "count": c} for a, c in top_actors]}
