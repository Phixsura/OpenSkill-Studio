"""Fleet JupyterHub — track multi-user notebook server."""
from __future__ import annotations
def fleet_jupyterhub_status(hubs: list[dict]) -> dict:
    running = [h for h in hubs if h.get("running", True)]
    active_users = sum(h.get("active_users", 0) for h in hubs)
    servers = sum(h.get("servers", 0) for h in hubs)
    return {"hubs": len(hubs), "running": len(running), "active_users": active_users,
            "servers": servers, "all_running": len(running) == len(hubs)}
