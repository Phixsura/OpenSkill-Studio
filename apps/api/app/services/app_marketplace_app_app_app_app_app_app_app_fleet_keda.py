"""Fleet KEDA — track event-driven autoscaling status."""
from __future__ import annotations
def fleet_keda_status(scalers: list[dict]) -> dict:
    active = [s for s in scalers if s.get("active", False)]
    triggered = [s for s in scalers if s.get("triggered", False)]
    return {"total": len(scalers), "active": len(active), "triggered": len(triggered),
            "idle": len(scalers) - len(active), "all_active": len(active) == len(scalers)}
