"""Fleet AI Webhook Delivery — track webhook delivery reliability."""
from __future__ import annotations
def fleet_ai_webhook_delivery(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    sent_24h = sum(s.get("sent_24h", 0) for s in systems)
    delivered = sum(s.get("delivered", 0) for s in systems)
    failed = sum(s.get("failed", 0) for s in systems)
    delivery_rate = round(delivered / max(sent_24h, 1) * 100, 2)
    return {"systems": len(systems), "active": len(active), "sent_24h": sent_24h,
            "delivered": delivered, "failed": failed, "delivery_rate": delivery_rate, "reliable": delivery_rate > 99}
