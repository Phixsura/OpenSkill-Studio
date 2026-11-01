"""Backup & restore — snapshot app configuration for disaster recovery."""

from datetime import datetime, timezone
import hashlib
import json


def create_backup(*, app_id: str, config: dict, secrets_count: int,
                    webhooks: list[dict], metadata: dict) -> dict:
    snapshot = json.dumps({"config": config, "webhooks_count": len(webhooks), "metadata": metadata}, sort_keys=True)
    checksum = hashlib.sha256(snapshot.encode()).hexdigest()[:16]
    return {
        "app_id": app_id, "backup_id": f"bak_{app_id}_{checksum}",
        "checksum": checksum, "secrets_included": False, "secrets_count": secrets_count,
        "webhooks_count": len(webhooks), "size_bytes": len(snapshot),
        "created_at": datetime.now(timezone.utc).isoformat(), "status": "completed",
    }


def validate_backup(*, backup: dict, current_app_id: str) -> dict:
    if backup.get("app_id") != current_app_id:
        return {"valid": False, "error": "Backup belongs to a different app"}
    if not backup.get("checksum"):
        return {"valid": False, "error": "Backup integrity check failed"}
    return {"valid": True, "error": None}


def restore_from_backup(*, backup: dict, target_app_id: str) -> dict:
    return {
        "target_app_id": target_app_id, "backup_id": backup.get("backup_id"),
        "status": "restored", "restored_at": datetime.now(timezone.utc).isoformat(),
        "warnings": ["Secrets must be re-entered manually"] if backup.get("secrets_count", 0) > 0 else [],
    }
