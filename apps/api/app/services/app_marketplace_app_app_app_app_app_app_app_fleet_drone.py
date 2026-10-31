"""Fleet Drone CI — track container-native CI metrics."""
from __future__ import annotations
def fleet_drone_status(builds: list[dict]) -> dict:
    success = [b for b in builds if b.get("status") == "success"]
    failure = [b for b in builds if b.get("status") == "failure"]
    avg_steps = round(sum(b.get("steps", 0) for b in builds) / max(len(builds), 1), 1)
    return {"total": len(builds), "success": len(success), "failure": len(failure),
            "avg_steps": avg_steps, "success_rate": round(len(success) / max(len(builds), 1) * 100, 1)}
