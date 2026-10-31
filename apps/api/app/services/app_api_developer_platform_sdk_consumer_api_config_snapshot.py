"""Consumer API Config Snapshot — configuration snapshots with rollback."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()


@dataclass
class ConfigSnapshot:
    snapshot_id: str
    consumer_id: str
    config: dict
    label: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ConfigSnapshotManager:
    """Manage configuration snapshots with diff and rollback."""

    _snapshots: dict[str, list[ConfigSnapshot]] = field(default_factory=dict)  # consumer -> snapshots
    _current: dict[str, dict] = field(default_factory=dict)  # consumer -> current config

    def set_config(self, consumer_id: str, config: dict) -> dict:
        self._current[consumer_id] = dict(config)
        return {"consumer_id": consumer_id, "keys": len(config)}

    def take_snapshot(self, consumer_id: str, snapshot_id: str, label: str = "") -> dict:
        config = self._current.get(consumer_id)
        if not config:
            raise ValueError(f"No config for {consumer_id}")
        if any(s.snapshot_id == snapshot_id for s in self._snapshots.get(consumer_id, [])):
            raise ValueError(f"Snapshot {snapshot_id} already exists")
        snapshot = ConfigSnapshot(
            snapshot_id=snapshot_id, consumer_id=consumer_id,
            config=dict(config), label=label,
        )
        self._snapshots.setdefault(consumer_id, []).append(snapshot)
        logger.info("snapshot_taken", snapshot_id=snapshot_id)
        return {"snapshot_id": snapshot_id, "keys": len(config)}

    def rollback(self, consumer_id: str, snapshot_id: str) -> dict:
        snapshots = self._snapshots.get(consumer_id, [])
        target = None
        for s in snapshots:
            if s.snapshot_id == snapshot_id:
                target = s
                break
        if not target:
            raise ValueError(f"Snapshot {snapshot_id} not found")
        self._current[consumer_id] = dict(target.config)
        logger.info("config_rolled_back", snapshot_id=snapshot_id)
        return {"snapshot_id": snapshot_id, "rolled_back": True, "keys": len(target.config)}

    def diff(self, consumer_id: str, snapshot_id_a: str, snapshot_id_b: str) -> dict:
        snapshots = {s.snapshot_id: s for s in self._snapshots.get(consumer_id, [])}
        a = snapshots.get(snapshot_id_a)
        b = snapshots.get(snapshot_id_b)
        if not a or not b:
            raise ValueError("Both snapshots must exist")
        added = sorted(set(b.config) - set(a.config))
        removed = sorted(set(a.config) - set(b.config))
        changed = [k for k in sorted(set(a.config) & set(b.config))
                   if a.config[k] != b.config[k]]
        return {"from": snapshot_id_a, "to": snapshot_id_b,
                "added": added, "removed": removed, "changed": changed,
                "total_changes": len(added) + len(removed) + len(changed)}

    def get_current(self, consumer_id: str) -> dict:
        config = self._current.get(consumer_id)
        if not config:
            return {"consumer_id": consumer_id, "config": {}}
        return {"consumer_id": consumer_id, "config": config, "keys": len(config)}

    def list_snapshots(self, consumer_id: str) -> list[dict]:
        return [
            {"snapshot_id": s.snapshot_id, "label": s.label,
             "keys": len(s.config), "created_at": s.created_at}
            for s in self._snapshots.get(consumer_id, [])
        ]

    def delete_snapshot(self, consumer_id: str, snapshot_id: str) -> dict:
        snapshots = self._snapshots.get(consumer_id, [])
        before = len(snapshots)
        self._snapshots[consumer_id] = [s for s in snapshots if s.snapshot_id != snapshot_id]
        return {"deleted": before > len(self._snapshots[consumer_id])}

    def get_stats(self) -> dict:
        total_snapshots = sum(len(v) for v in self._snapshots.values())
        return {
            "consumers_with_config": len(self._current),
            "total_snapshots": total_snapshots,
        }
