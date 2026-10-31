"""Fleet AI Model Rollback v2 — track instant model version rollback."""
from __future__ import annotations
def fleet_ai_model_rollback_v2(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    rollbacks_24h = sum(m.get("rollbacks", 0) for m in managers)
    avg_time_s = round(sum(m.get("avg_time_s", 0) for m in managers) / max(len(managers), 1), 1)
    success_rate = round(sum(m.get("success_pct", 0) for m in managers) / max(len(managers), 1), 1)
    return {"managers": len(managers), "active": len(active), "rollbacks": rollbacks_24h,
            "avg_time_s": avg_time_s, "success_rate": success_rate, "instant": avg_time_s < 30}
