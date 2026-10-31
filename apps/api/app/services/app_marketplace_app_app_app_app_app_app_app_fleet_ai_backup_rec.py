"""Fleet AI Backup & Recovery — track AI model and data backup systems."""
from __future__ import annotations
def fleet_ai_backup_recovery(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    backups_24h = sum(s.get("backups_24h", 0) for s in systems)
    total_size_tb = round(sum(s.get("size_tb", 0) for s in systems), 1)
    rpo_min = min((s.get("rpo_min", 9999) for s in systems), default=9999)
    rto_min = min((s.get("rto_min", 9999) for s in systems), default=9999)
    return {"systems": len(systems), "active": len(active), "backups_24h": backups_24h,
            "size_tb": total_size_tb, "rpo_min": rpo_min, "rto_min": rto_min, "resilient": rpo_min < 60}
