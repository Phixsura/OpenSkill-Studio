"""Fleet Databricks — track data lakehouse platform."""
from __future__ import annotations
def fleet_databricks_status(workspaces: list[dict]) -> dict:
    active = [w for w in workspaces if w.get("status") == "RUNNING"]
    clusters = sum(w.get("clusters", 0) for w in workspaces)
    dbu_24h = sum(w.get("dbu_24h", 0) for w in workspaces)
    return {"workspaces": len(workspaces), "active": len(active), "clusters": clusters,
            "dbu_24h": round(dbu_24h, 1), "all_running": len(active) == len(workspaces)}
