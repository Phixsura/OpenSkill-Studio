"""Fleet DevSpace — track cloud development environments."""
from __future__ import annotations
def fleet_devspace_status(spaces: list[dict]) -> dict:
    active = [s for s in spaces if s.get("active", False)]
    sleeping = [s for s in spaces if s.get("sleeping", False)]
    return {"total": len(spaces), "active": len(active), "sleeping": len(sleeping),
            "cost_saving": len(sleeping) > 0}
