"""Fleet AI Platform Notification v3 — track multi-channel alert routing."""
from __future__ import annotations
def fleet_ai_platform_notification_v3(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    sent_24h = sum(s.get("sent_24h", 0) for s in systems)
    channels = sum(s.get("channels", 0) for s in systems)
    delivery_rate = round(sum(s.get("delivery_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "sent_24h": sent_24h,
            "channels": channels, "delivery_rate": delivery_rate, "reliable": delivery_rate > 99}
