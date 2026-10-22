"""Sandbox snapshot — save and restore sandbox states for debugging."""

import hashlib
from datetime import datetime, timezone


def create_snapshot(*, sandbox_id: str, name: str, filesystem: dict, config: dict) -> dict:
    content = f"{sandbox_id}:{name}:{str(filesystem)}:{str(config)}"
    snapshot_id = hashlib.sha256(content.encode()).hexdigest()[:12]
    return {"snapshot_id": f"snap_{snapshot_id}", "sandbox_id": sandbox_id, "name": name,
            "filesystem_files": filesystem.get("files", 0),
            "config_keys": len(config), "size_bytes": len(content),
            "created_at": datetime.now(timezone.utc).isoformat()}


def list_snapshots(*, snapshots: list[dict], limit: int = 10) -> list[dict]:
    sorted_snaps = sorted(snapshots, key=lambda s: s.get("created_at", ""), reverse=True)
    return sorted_snaps[:limit]


def restore_snapshot(*, snapshot: dict) -> dict:
    return {"snapshot_id": snapshot["snapshot_id"], "status": "restored",
            "restored_at": datetime.now(timezone.utc).isoformat()}
