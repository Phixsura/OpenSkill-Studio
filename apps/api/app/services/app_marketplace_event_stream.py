"""Event stream — publish and subscribe to platform events."""

from datetime import datetime
import secrets


EVENT_TYPES = {
    "app.installed", "app.uninstalled", "app.updated", "app.published",
    "review.created", "review.replied", "webhook.delivered", "webhook.failed",
    "user.signup", "user.upgraded", "payment.completed", "payment.failed",
}


def create_event(*, event_type: str, source: str, payload: dict) -> dict:
    if event_type not in EVENT_TYPES:
        return {"error": f"Unknown event type: {event_type}"}
    return {
        "event_id": f"evt_{secrets.token_urlsafe(12)}",
        "type": event_type,
        "source": source,
        "payload": payload,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0",
    }


def filter_events(*, events: list[dict], event_types: list[str] | None = None,
                     source: str | None = None, limit: int = 50) -> dict:
    filtered = events
    if event_types:
        type_set = set(event_types)
        filtered = [e for e in filtered if e.get("type") in type_set]
    if source:
        filtered = [e for e in filtered if e.get("source") == source]
    return {"events": filtered[:limit], "total": len(filtered),
            "has_more": len(filtered) > limit}


def get_event_type_stats(*, events: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for e in events:
        t = e.get("type", "unknown")
        counts[t] = counts.get(t, 0) + 1
    sorted_types = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return {"types": [{"type": k, "count": v} for k, v in sorted_types],
            "total_events": len(events), "unique_types": len(counts)}
