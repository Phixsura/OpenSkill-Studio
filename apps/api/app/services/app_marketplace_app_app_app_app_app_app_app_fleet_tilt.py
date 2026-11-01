"""Fleet Tilt — track Tilt development environment health."""
from __future__ import annotations
def fleet_tilt_status(environments: list[dict]) -> dict:
    running = [e for e in environments if e.get("status") == "running"]
    resources = sum(e.get("resources", 0) for e in running)
    avg_update_ms = round(sum(e.get("avg_update_ms", 0) for e in running) / max(len(running), 1), 1)
    return {"total": len(environments), "running": len(running), "resources": resources,
            "avg_update_ms": avg_update_ms, "fast": avg_update_ms < 3000}
