"""Fleet AI Timeout Manager — track AI request timeout configuration."""
from __future__ import annotations
def fleet_ai_timeout_manager(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    timeouts_24h = sum(m.get("timeouts_24h", 0) for m in managers)
    default_ms = round(sum(m.get("default_ms", 0) for m in managers) / max(len(managers), 1))
    adaptive = sum(1 for m in managers if m.get("adaptive", False))
    return {"managers": len(managers), "active": len(active), "timeouts_24h": timeouts_24h,
            "default_ms": default_ms, "adaptive": adaptive, "smart": adaptive > 0}
