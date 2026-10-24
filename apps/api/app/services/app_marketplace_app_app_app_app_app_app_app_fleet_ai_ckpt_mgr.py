"""Fleet AI Checkpoint Manager — track model training checkpoint storage."""
from __future__ import annotations
def fleet_ai_checkpoint_manager(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    checkpoints = sum(m.get("checkpoints", 0) for m in managers)
    storage_tb = round(sum(m.get("storage_tb", 0) for m in managers), 1)
    auto_cleanup = all(m.get("auto_cleanup", False) for m in managers)
    return {"managers": len(managers), "active": len(active), "checkpoints": checkpoints,
            "storage_tb": storage_tb, "auto_cleanup": auto_cleanup, "organized": auto_cleanup}
