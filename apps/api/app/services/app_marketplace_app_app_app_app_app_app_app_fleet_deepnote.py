"""Fleet Deepnote — track collaborative data science."""
from __future__ import annotations
def fleet_deepnote_status(workspaces: list[dict]) -> dict:
    active = [w for w in workspaces if w.get("active", True)]
    projects = sum(w.get("projects", 0) for w in workspaces)
    integrations = sum(w.get("integrations", 0) for w in workspaces)
    return {"workspaces": len(workspaces), "active": len(active), "projects": projects,
            "integrations": integrations, "all_active": len(active) == len(workspaces)}
