"""Fleet Skaffold — track inner-loop development metrics."""
from __future__ import annotations
def fleet_skaffold_status(devs: list[dict]) -> dict:
    active = [d for d in devs if d.get("dev_loop_active", False)]
    avg_sync_ms = round(sum(d.get("sync_ms", 0) for d in active) / max(len(active), 1), 1)
    return {"total_devs": len(devs), "active_loops": len(active),
            "avg_sync_ms": avg_sync_ms, "fast": avg_sync_ms < 5000}
