"""Fleet Dagster — track data orchestration health."""
from __future__ import annotations
def fleet_dagster_status(deployments: list[dict]) -> dict:
    running = [d for d in deployments if d.get("status") == "running"]
    assets = sum(d.get("assets", 0) for d in deployments)
    materializations_24h = sum(d.get("materializations_24h", 0) for d in deployments)
    return {"deployments": len(deployments), "running": len(running), "assets": assets,
            "materializations_24h": materializations_24h, "active": materializations_24h > 0}
