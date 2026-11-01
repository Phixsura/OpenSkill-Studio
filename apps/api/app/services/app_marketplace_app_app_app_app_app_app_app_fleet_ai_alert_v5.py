"""Fleet AI Alerting v5 — track intelligent alert management."""
from __future__ import annotations
def fleet_ai_alerting_v5(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    alerts_24h = sum(s.get("alerts_24h", 0) for s in systems)
    acknowledged = sum(s.get("acked", 0) for s in systems)
    auto_resolved = sum(s.get("auto_resolved", 0) for s in systems)
    noise_reduction = round(sum(s.get("noise_reduction_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "alerts_24h": alerts_24h,
            "acked": acknowledged, "auto_resolved": auto_resolved, "noise_reduction": noise_reduction, "smart": noise_reduction > 50}
