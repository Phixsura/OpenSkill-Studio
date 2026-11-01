"""Fleet Workspace Manager v9 — track developer workspace provisioning."""
from __future__ import annotations
def fleet_workspace_mgr_v9(workspaces: list[dict]) -> dict:
    running = [w for w in workspaces if w.get("status") == "running"]
    idle = [w for w in workspaces if w.get("status") == "idle"]
    cpu_total = sum(w.get("cpu_cores", 0) for w in workspaces)
    return {"total": len(workspaces), "running": len(running), "idle": len(idle),
            "total_cpu_cores": cpu_total, "healthy": len(running) + len(idle) == len(workspaces)}
