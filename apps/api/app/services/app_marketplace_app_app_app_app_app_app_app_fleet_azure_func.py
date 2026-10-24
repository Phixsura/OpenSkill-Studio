"""Fleet Azure Functions — track serverless compute health."""
from __future__ import annotations
def fleet_azure_func_status(apps: list[dict]) -> dict:
    running = [a for a in apps if a.get("status") == "Running"]
    total_exec = sum(a.get("executions_24h", 0) for a in apps)
    consumption_units = sum(a.get("gb_seconds", 0) for a in apps)
    return {"apps": len(apps), "running": len(running), "executions_24h": total_exec,
            "gb_seconds": consumption_units, "all_running": len(running) == len(apps)}
