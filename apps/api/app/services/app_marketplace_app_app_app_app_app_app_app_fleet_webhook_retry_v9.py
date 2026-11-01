"""Fleet Webhook Retry v9 — track webhook delivery retry queues."""
from __future__ import annotations
def fleet_webhook_retry_v9(queues: list[dict]) -> dict:
    pending = sum(q.get("pending", 0) for q in queues)
    retrying = sum(q.get("retrying", 0) for q in queues)
    dead_letter = sum(q.get("dead_letter", 0) for q in queues)
    return {"queues": len(queues), "pending": pending, "retrying": retrying,
            "dead_letter": dead_letter, "healthy": dead_letter == 0}
