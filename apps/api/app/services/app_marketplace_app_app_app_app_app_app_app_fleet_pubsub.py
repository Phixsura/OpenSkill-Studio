"""Fleet Pub/Sub — track messaging service health."""
from __future__ import annotations
def fleet_pubsub_status(topics: list[dict]) -> dict:
    total_msgs = sum(t.get("messages_24h", 0) for t in topics)
    total_subs = sum(t.get("subscriptions", 0) for t in topics)
    backlog = sum(t.get("backlog_messages", 0) for t in topics)
    return {"topics": len(topics), "messages_24h": total_msgs, "subscriptions": total_subs,
            "backlog": backlog, "healthy": backlog < 10000}
