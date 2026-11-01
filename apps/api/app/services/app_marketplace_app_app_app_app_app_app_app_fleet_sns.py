"""Fleet SNS — track notification service health."""
from __future__ import annotations
def fleet_sns_status(topics: list[dict]) -> dict:
    total_msgs = sum(t.get("messages_published_24h", 0) for t in topics)
    total_subs = sum(t.get("subscriptions", 0) for t in topics)
    failed_deliveries = sum(t.get("failed_deliveries", 0) for t in topics)
    return {"topics": len(topics), "messages_24h": total_msgs, "subscriptions": total_subs,
            "failed_deliveries": failed_deliveries, "healthy": failed_deliveries == 0}
