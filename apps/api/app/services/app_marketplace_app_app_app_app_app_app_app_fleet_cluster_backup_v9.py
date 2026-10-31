"""Fleet Cluster Backup v9 — track etcd and cluster state backups."""
from __future__ import annotations
def fleet_cluster_backup_v9(backups: list[dict]) -> dict:
    successful = [b for b in backups if b.get("status") == "success"]
    size_gb = sum(b.get("size_gb", 0) for b in backups)
    age_hours = min((b.get("age_hours", 999) for b in backups), default=999)
    return {"backups": len(backups), "successful": len(successful), "size_gb": round(size_gb, 1),
            "newest_age_hours": age_hours, "healthy": age_hours < 24}
