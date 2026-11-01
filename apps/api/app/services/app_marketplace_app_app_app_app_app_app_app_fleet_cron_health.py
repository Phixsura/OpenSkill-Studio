"""Fleet cron job health — track scheduled job reliability."""
from __future__ import annotations
def fleet_cron_health(jobs: list[dict]) -> dict:
    on_time = [j for j in jobs if j.get("on_schedule", True)]
    failed = [j for j in jobs if j.get("last_status") == "failed"]
    return {"total": len(jobs), "on_time": len(on_time), "delayed": len(jobs) - len(on_time),
            "failed": len(failed), "healthy": len(failed) == 0 and len(on_time) == len(jobs)}
