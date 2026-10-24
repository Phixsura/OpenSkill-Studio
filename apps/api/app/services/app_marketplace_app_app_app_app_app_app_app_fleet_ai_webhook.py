"""Fleet AI Webhook — track AI event notification delivery."""
from __future__ import annotations
def fleet_ai_webhook(endpoints: list[dict]) -> dict:
    active = [e for e in endpoints if e.get("active", True)]
    delivered_24h = sum(e.get("delivered_24h", 0) for e in endpoints)
    failed_24h = sum(e.get("failed_24h", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "active": len(active), "delivered_24h": delivered_24h,
            "failed_24h": failed_24h, "reliable": failed_24h == 0}
