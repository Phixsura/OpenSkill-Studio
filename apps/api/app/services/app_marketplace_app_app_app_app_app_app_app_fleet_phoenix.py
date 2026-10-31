"""Fleet Phoenix — track Elixir web framework health."""
from __future__ import annotations
def fleet_phoenix_status(apps: list[dict]) -> dict:
    running = [a for a in apps if a.get("running", True)]
    total_channels = sum(a.get("channels", 0) for a in apps)
    ws_connections = sum(a.get("ws_connections", 0) for a in apps)
    return {"apps": len(apps), "running": len(running), "channels": total_channels,
            "ws_connections": ws_connections, "all_running": len(running) == len(apps)}
