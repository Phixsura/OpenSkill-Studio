"""Fleet Hex — track collaborative data workspace."""
from __future__ import annotations
def fleet_hex_status(workspaces: list[dict]) -> dict:
    active = [w for w in workspaces if w.get("active", True)]
    projects = sum(w.get("projects", 0) for w in workspaces)
    runs_24h = sum(w.get("runs_24h", 0) for w in workspaces)
    return {"workspaces": len(workspaces), "active": len(active), "projects": projects,
            "runs_24h": runs_24h, "all_active": len(active) == len(workspaces)}
