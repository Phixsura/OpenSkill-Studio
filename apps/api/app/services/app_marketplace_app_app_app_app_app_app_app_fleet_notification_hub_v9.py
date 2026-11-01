"""Fleet Notification Hub v9 — track multi-channel notification delivery."""
from __future__ import annotations
def fleet_notification_hub_v9(channels: list[dict]) -> dict:
    sent = sum(c.get("sent", 0) for c in channels)
    failed = sum(c.get("failed", 0) for c in channels)
    types = len({c.get("type") for c in channels if c.get("type")})
    return {"channels": len(channels), "sent": sent, "failed": failed,
            "channel_types": types, "healthy": failed == 0}
