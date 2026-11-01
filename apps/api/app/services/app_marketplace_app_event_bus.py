"""Event bus — publish-subscribe event system for app communication."""

import secrets
from datetime import datetime


def publish_event(*, topic: str, payload: dict, source: str) -> dict:
    return {
        "event_id": f"ev_{secrets.token_urlsafe(10)}",
        "topic": topic,
        "payload": payload,
        "source": source,
        "published_at": datetime.utcnow().isoformat(),
        "status": "published",
    }


def subscribe(*, topic: str, subscriber_id: str, endpoint: str,
                filter_expr: str | None = None) -> dict:
    return {
        "subscription_id": f"sub_{secrets.token_urlsafe(8)}",
        "topic": topic,
        "subscriber_id": subscriber_id,
        "endpoint": endpoint,
        "filter": filter_expr,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
    }


def get_topic_stats(*, topics: list[dict]) -> dict:
    return {
        "topics": [{
            "name": t["name"],
            "subscribers": t.get("subscriber_count", 0),
            "events_24h": t.get("events_24h", 0),
            "avg_latency_ms": t.get("avg_latency_ms", 0),
        } for t in topics],
        "total_topics": len(topics),
        "total_events_24h": sum(t.get("events_24h", 0) for t in topics),
    }
