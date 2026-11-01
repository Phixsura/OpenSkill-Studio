"""Fleet Tecton — track real-time feature platform."""
from __future__ import annotations
def fleet_tecton_status(workspaces: list[dict]) -> dict:
    active = [w for w in workspaces if w.get("active", True)]
    features = sum(w.get("features", 0) for w in workspaces)
    serves_per_sec = sum(w.get("serves_per_sec", 0) for w in workspaces)
    return {"workspaces": len(workspaces), "active": len(active), "features": features,
            "serves_per_sec": serves_per_sec, "all_active": len(active) == len(workspaces)}
