"""Fleet AI Model Snapshot — track point-in-time model state capture."""
from __future__ import annotations
def fleet_ai_model_snapshot(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    snapshots = sum(m.get("snapshots", 0) for m in managers)
    storage_tb = round(sum(m.get("storage_tb", 0) for m in managers), 1)
    restorations_24h = sum(m.get("restorations", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "snapshots": snapshots,
            "storage_tb": storage_tb, "restorations": restorations_24h, "backed_up": snapshots > 0}
