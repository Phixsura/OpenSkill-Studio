"""Fleet AI Graceful Shutdown — track zero-loss AI service termination."""
from __future__ import annotations
def fleet_ai_graceful_shutdown(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    shutdowns_24h = sum(m.get("shutdowns_24h", 0) for m in managers)
    requests_drained = sum(m.get("drained", 0) for m in managers)
    lost = sum(m.get("lost", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "shutdowns_24h": shutdowns_24h,
            "drained": requests_drained, "lost": lost, "zero_loss": lost == 0}
