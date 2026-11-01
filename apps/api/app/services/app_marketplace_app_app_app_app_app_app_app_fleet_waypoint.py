"""Fleet Waypoint — track HashiCorp Waypoint deployments."""
from __future__ import annotations
def fleet_waypoint_status(deployments: list[dict]) -> dict:
    successful = [d for d in deployments if d.get("status") == "SUCCESS"]
    released = [d for d in deployments if d.get("released", False)]
    return {"total": len(deployments), "successful": len(successful), "released": len(released),
            "unreleased": len(successful) - len(released), "healthy": len(successful) == len(deployments)}
