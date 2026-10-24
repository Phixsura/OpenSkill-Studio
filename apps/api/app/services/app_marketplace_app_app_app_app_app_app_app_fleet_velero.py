"""Fleet Velero — track cluster backup and restore status."""
from __future__ import annotations
def fleet_velero_status(backups: list[dict]) -> dict:
    completed = [b for b in backups if b.get("phase") == "Completed"]
    failed = [b for b in backups if b.get("phase") == "Failed"]
    latest_age_h = min((b.get("age_hours", 999) for b in completed), default=999)
    return {"total": len(backups), "completed": len(completed), "failed": len(failed),
            "latest_age_hours": latest_age_h, "fresh": latest_age_h <= 24}
