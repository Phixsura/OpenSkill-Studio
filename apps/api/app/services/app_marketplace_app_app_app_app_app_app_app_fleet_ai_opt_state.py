"""Fleet AI Optimizer State — track training optimizer state management."""
from __future__ import annotations
def fleet_ai_optimizer_state(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    states_saved = sum(m.get("states", 0) for m in managers)
    storage_gb = round(sum(m.get("storage_gb", 0) for m in managers), 1)
    restorations = sum(m.get("restorations", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "states": states_saved,
            "storage_gb": storage_gb, "restorations": restorations, "persistent": states_saved > 0}
