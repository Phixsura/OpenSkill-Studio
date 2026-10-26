"""Sandbox Snapshot — capture and restore sandbox state snapshots.

Creates point-in-time snapshots of sandbox state (files, env vars,
process list) for debugging, rollback, and state sharing.
"""
from __future__ import annotations
import copy
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class SandboxSnapshot:
    snapshot_id: str
    sandbox_id: str
    label: str
    files: dict[str, bytes] = field(default_factory=dict)
    env_vars: dict[str, str] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    size_bytes: int = 0
    created_at: str = ""
    created_by: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.size_bytes:
            self.size_bytes = sum(len(v) for v in self.files.values())


class SandboxSnapshotService:
    """Manages sandbox state snapshots for debugging and rollback."""

    MAX_SNAPSHOTS_PER_SANDBOX = 10
    MAX_SNAPSHOT_SIZE = 50 * 1024 * 1024  # 50MB

    def __init__(self):
        self._snapshots: dict[str, list[SandboxSnapshot]] = {}

    def capture(self, sandbox_id: str, label: str, files: dict[str, bytes],
                env_vars: dict[str, str] | None = None,
                metadata: dict | None = None,
                created_by: str = "") -> SandboxSnapshot | dict:
        total_size = sum(len(v) for v in files.values())
        if total_size > self.MAX_SNAPSHOT_SIZE:
            return {"error": f"Snapshot too large: {total_size} bytes (max {self.MAX_SNAPSHOT_SIZE})"}

        snapshot = SandboxSnapshot(
            snapshot_id=f"snap_{secrets.token_urlsafe(10)}",
            sandbox_id=sandbox_id, label=label,
            files=copy.deepcopy(files),
            env_vars=dict(env_vars or {}),
            metadata=dict(metadata or {}),
            created_by=created_by,
        )

        snapshots = self._snapshots.setdefault(sandbox_id, [])
        if len(snapshots) >= self.MAX_SNAPSHOTS_PER_SANDBOX:
            snapshots.pop(0)  # remove oldest
        snapshots.append(snapshot)
        return snapshot

    def restore(self, sandbox_id: str, snapshot_id: str) -> dict | None:
        for snap in self._snapshots.get(sandbox_id, []):
            if snap.snapshot_id == snapshot_id:
                return {
                    "files": copy.deepcopy(snap.files),
                    "env_vars": dict(snap.env_vars),
                    "metadata": dict(snap.metadata),
                    "restored_from": snapshot_id,
                }
        return None

    def list_snapshots(self, sandbox_id: str) -> list[dict]:
        return [
            {"snapshot_id": s.snapshot_id, "label": s.label,
             "size_bytes": s.size_bytes, "file_count": len(s.files),
             "created_at": s.created_at, "created_by": s.created_by}
            for s in self._snapshots.get(sandbox_id, [])
        ]

    def delete(self, sandbox_id: str, snapshot_id: str) -> bool:
        for i, snap in enumerate(self._snapshots.get(sandbox_id, [])):
            if snap.snapshot_id == snapshot_id:
                self._snapshots[sandbox_id].pop(i)
                return True
        return False

    def compare(self, sandbox_id: str, snap_id_1: str, snap_id_2: str) -> dict | None:
        s1 = s2 = None
        for snap in self._snapshots.get(sandbox_id, []):
            if snap.snapshot_id == snap_id_1:
                s1 = snap
            if snap.snapshot_id == snap_id_2:
                s2 = snap
        if not s1 or not s2:
            return None

        added = [f for f in s2.files if f not in s1.files]
        removed = [f for f in s1.files if f not in s2.files]
        modified = [f for f in s1.files if f in s2.files and s1.files[f] != s2.files[f]]
        return {"added": added, "removed": removed, "modified": modified,
                "has_changes": bool(added or removed or modified)}
