"""Backup manager — create, restore, and schedule app backups."""

import secrets
from datetime import datetime, timedelta


def create_backup(*, app_id: str, backup_type: str = "full",
                    include: list[str] | None = None) -> dict:
    valid_types = {"full", "incremental", "config_only"}
    if backup_type not in valid_types:
        return {"error": f"Invalid type. Valid: {', '.join(sorted(valid_types))}"}
    components = include or ["data", "config", "assets", "secrets"]
    size_mb = len(components) * 128
    return {
        "backup_id": f"bak_{secrets.token_urlsafe(8)}",
        "app_id": app_id,
        "type": backup_type,
        "components": components,
        "size_mb": size_mb,
        "status": "completed",
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "restore_cmd": f"openskill restore --backup bak_{secrets.token_urlsafe(4)}",
    }


def list_backups(*, app_id: str) -> dict:
    return {
        "app_id": app_id,
        "backups": [
            {"backup_id": "bak_1", "type": "full", "size_mb": 512, "status": "completed",
             "created_at": "2026-10-23T03:00:00"},
            {"backup_id": "bak_2", "type": "incremental", "size_mb": 64, "status": "completed",
             "created_at": "2026-10-22T03:00:00"},
        ],
        "total": 2,
        "total_size_mb": 576,
    }
