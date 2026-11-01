"""Fleet AI Alert Manager — track AI system alerting and notification."""
from __future__ import annotations
def fleet_ai_alert_manager(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    alerts_24h = sum(m.get("alerts_24h", 0) for m in managers)
    acknowledged = sum(m.get("acked", 0) for m in managers)
    silenced = sum(m.get("silenced", 0) for m in managers)
    channels = sum(m.get("channels", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "alerts_24h": alerts_24h,
            "acked": acknowledged, "silenced": silenced, "channels": channels, "responsive": acknowledged > 0}
