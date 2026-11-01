"""Fleet Backup Vault v9 — track backup storage and retention compliance."""
from __future__ import annotations
def fleet_backup_vault_v9(backups: list[dict]) -> dict:
    valid = [b for b in backups if b.get("valid", True)]
    size_gb = sum(b.get("size_gb", 0) for b in backups)
    return {"total": len(backups), "valid": len(valid), "size_gb": round(size_gb, 1),
            "retention_compliant": all(b.get("retention_days", 0) >= 30 for b in backups),
            "healthy": len(valid) == len(backups)}
