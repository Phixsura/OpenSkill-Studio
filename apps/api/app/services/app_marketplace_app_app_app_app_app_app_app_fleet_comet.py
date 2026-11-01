"""Fleet Comet — track ML experiment management."""
from __future__ import annotations
def fleet_comet_status(workspaces: list[dict]) -> dict:
    active = [w for w in workspaces if w.get("active", True)]
    experiments = sum(w.get("experiments", 0) for w in workspaces)
    panels = sum(w.get("panels", 0) for w in workspaces)
    return {"workspaces": len(workspaces), "active": len(active), "experiments": experiments,
            "panels": panels, "all_active": len(active) == len(workspaces)}
