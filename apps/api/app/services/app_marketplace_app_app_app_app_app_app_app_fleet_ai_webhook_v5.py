"""Fleet AI Webhook v5 — track enterprise webhook delivery at scale."""
from __future__ import annotations
def fleet_ai_webhook_v5(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    endpoints = sum(s.get("endpoints", 0) for s in systems)
    delivered_24h = sum(s.get("delivered", 0) for s in systems)
    failed = sum(s.get("failed", 0) for s in systems)
    delivery_rate = round(delivered_24h / max(delivered_24h + failed, 1) * 100, 2)
    return {"systems": len(systems), "active": len(active), "endpoints": endpoints,
            "delivered": delivered_24h, "failed": failed, "delivery_rate": delivery_rate, "reliable": delivery_rate > 99.9}
