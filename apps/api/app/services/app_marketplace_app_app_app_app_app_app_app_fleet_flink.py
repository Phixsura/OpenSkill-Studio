"""Fleet Flink — track stream processing health."""
from __future__ import annotations
def fleet_flink_status(clusters: list[dict]) -> dict:
    running = [c for c in clusters if c.get("status") == "RUNNING"]
    total_slots = sum(c.get("task_slots", 0) for c in clusters)
    checkpoints_ok = all(c.get("checkpoint_ok", True) for c in clusters)
    return {"clusters": len(clusters), "running": len(running), "task_slots": total_slots,
            "checkpoints_ok": checkpoints_ok, "healthy": len(running) == len(clusters) and checkpoints_ok}
