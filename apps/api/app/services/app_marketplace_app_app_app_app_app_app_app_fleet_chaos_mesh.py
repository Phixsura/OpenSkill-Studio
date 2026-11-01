"""Fleet Chaos Mesh — track chaos experiment orchestration."""
from __future__ import annotations
def fleet_chaos_mesh(experiments: list[dict]) -> dict:
    running = [e for e in experiments if e.get("status") == "running"]
    paused = [e for e in experiments if e.get("status") == "paused"]
    completed = [e for e in experiments if e.get("status") == "completed"]
    return {"total": len(experiments), "running": len(running), "paused": len(paused),
            "completed": len(completed), "active": len(running) > 0}
