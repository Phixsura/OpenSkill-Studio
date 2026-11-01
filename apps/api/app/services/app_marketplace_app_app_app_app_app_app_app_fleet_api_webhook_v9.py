"""Fleet API Webhook v9 — track outbound webhook delivery and retry."""
from __future__ import annotations
def fleet_api_webhook_v9(webhooks: list[dict]) -> dict:
    active = [w for w in webhooks if w.get("active")]
    delivered = sum(w.get("delivered_today", 0) for w in webhooks)
    failed = sum(w.get("failed_today", 0) for w in webhooks)
    return {"webhooks": len(webhooks), "active": len(active), "delivered_today": delivered,
            "failed_today": failed, "healthy": failed == 0}
