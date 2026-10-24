"""Fleet AI Error Handler — track AI error classification and recovery."""
from __future__ import annotations
def fleet_ai_error_handler(handlers: list[dict]) -> dict:
    active = [h for h in handlers if h.get("active", True)]
    errors_24h = sum(h.get("errors_24h", 0) for h in handlers)
    auto_recovered = sum(h.get("recovered", 0) for h in handlers)
    escalated = sum(h.get("escalated", 0) for h in handlers)
    recovery_rate = round(auto_recovered / max(errors_24h, 1) * 100, 1)
    return {"handlers": len(handlers), "active": len(active), "errors_24h": errors_24h,
            "recovered": auto_recovered, "escalated": escalated, "recovery_rate": recovery_rate, "resilient": recovery_rate > 90}
