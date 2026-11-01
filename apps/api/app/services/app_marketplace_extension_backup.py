"""Extension Backup — snapshot and restore extension configurations.

Creates point-in-time backups of extension configs, permissions,
and webhooks for disaster recovery and migration.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from copy import deepcopy


@dataclass
class BackupSnapshot:
    snapshot_id: str
    extension_id: str
    org_id: str
    created_at: str
    created_by: str
    data: dict
    size_bytes: int = 0
    label: str = ""
    restored: bool = False


class ExtensionBackupService:
    """Manages extension configuration backups."""

    def __init__(self, max_snapshots_per_ext: int = 50):
        self._snapshots: dict[str, BackupSnapshot] = {}
        self._max = max_snapshots_per_ext

    def create_snapshot(self, snapshot_id: str, extension_id: str, org_id: str,
                        created_by: str, data: dict, label: str = "") -> BackupSnapshot:
        """Create a backup snapshot of extension state."""
        snapshot = BackupSnapshot(
            snapshot_id=snapshot_id, extension_id=extension_id,
            org_id=org_id, created_by=created_by,
            created_at=datetime.now(timezone.utc).isoformat(),
            data=deepcopy(data),
            size_bytes=len(str(data)),
            label=label or f"Backup {snapshot_id}",
        )
        self._snapshots[snapshot_id] = snapshot
        self._enforce_limit(extension_id, org_id)
        return snapshot

    def restore_snapshot(self, snapshot_id: str) -> dict | None:
        """Restore from a snapshot. Returns the data to apply."""
        snapshot = self._snapshots.get(snapshot_id)
        if not snapshot:
            return None
        snapshot.restored = True
        return deepcopy(snapshot.data)

    def get_snapshot(self, snapshot_id: str) -> BackupSnapshot | None:
        return self._snapshots.get(snapshot_id)

    def list_snapshots(self, extension_id: str, org_id: str = "") -> list[BackupSnapshot]:
        snapshots = [s for s in self._snapshots.values()
                     if s.extension_id == extension_id]
        if org_id:
            snapshots = [s for s in snapshots if s.org_id == org_id]
        return sorted(snapshots, key=lambda s: s.created_at, reverse=True)

    def delete_snapshot(self, snapshot_id: str) -> bool:
        return self._snapshots.pop(snapshot_id, None) is not None

    def compare_snapshots(self, id_a: str, id_b: str) -> dict:
        """Compare two snapshots and show differences."""
        a = self._snapshots.get(id_a)
        b = self._snapshots.get(id_b)
        if not a or not b:
            return {"error": "Snapshot not found"}
        keys_a = set(a.data.keys())
        keys_b = set(b.data.keys())
        return {
            "added": sorted(keys_b - keys_a),
            "removed": sorted(keys_a - keys_b),
            "changed": sorted(k for k in keys_a & keys_b if a.data[k] != b.data[k]),
            "unchanged": sorted(k for k in keys_a & keys_b if a.data[k] == b.data[k]),
        }

    def _enforce_limit(self, extension_id: str, org_id: str) -> None:
        snapshots = self.list_snapshots(extension_id, org_id)
        while len(snapshots) > self._max:
            oldest = snapshots.pop()
            self._snapshots.pop(oldest.snapshot_id, None)
