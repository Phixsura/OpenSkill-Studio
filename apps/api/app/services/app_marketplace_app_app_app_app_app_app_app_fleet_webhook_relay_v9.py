"""Fleet Webhook Relay v9 — track webhook delivery and retry queues."""
from __future__ import annotations
def fleet_webhook_relay_v9(endpoints: list[dict]) -> dict:
    delivered = sum(e.get("delivered", 0) for e in endpoints)
    failed = sum(e.get("failed", 0) for e in endpoints)
    retries = sum(e.get("retries", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "delivered": delivered, "failed": failed,
            "retries": retries, "healthy": failed == 0}
