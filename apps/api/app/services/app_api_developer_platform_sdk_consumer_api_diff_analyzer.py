"""Consumer API Diff Analyzer — compare API responses across versions."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class ResponseSnapshot:
    snapshot_id: str
    endpoint_id: str
    version: str
    status_code: int
    body: dict
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class DiffResult:
    added_fields: list[str]
    removed_fields: list[str]
    changed_fields: list[dict]
    type_changes: list[dict]
    breaking: bool = False


@dataclass
class DiffAnalyzer:
    """Compare API responses across versions to detect breaking changes."""

    _snapshots: dict[str, ResponseSnapshot] = field(default_factory=dict)

    def store_snapshot(self, snapshot: ResponseSnapshot) -> dict:
        key = f"{snapshot.endpoint_id}:{snapshot.version}"
        self._snapshots[key] = snapshot
        logger.info("snapshot_stored", endpoint=snapshot.endpoint_id, version=snapshot.version)
        return {"key": key, "stored": True}

    def _flatten(self, obj: dict, prefix: str = "") -> dict[str, type]:
        flat: dict[str, type] = {}
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            flat[path] = type(v)
            if isinstance(v, dict):
                flat.update(self._flatten(v, path))
        return flat

    def diff(self, endpoint_id: str, version_a: str, version_b: str) -> dict:
        key_a = f"{endpoint_id}:{version_a}"
        key_b = f"{endpoint_id}:{version_b}"
        snap_a = self._snapshots.get(key_a)
        snap_b = self._snapshots.get(key_b)
        if not snap_a or not snap_b:
            raise ValueError("Both snapshots must exist")

        fields_a = self._flatten(snap_a.body)
        fields_b = self._flatten(snap_b.body)

        added = sorted(set(fields_b) - set(fields_a))
        removed = sorted(set(fields_a) - set(fields_b))
        common = set(fields_a) & set(fields_b)

        type_changes = []
        changed_values = []
        for field_path in sorted(common):
            if fields_a[field_path] != fields_b[field_path]:
                type_changes.append({
                    "field": field_path,
                    "from": fields_a[field_path].__name__,
                    "to": fields_b[field_path].__name__,
                })

        # Value comparison for leaf values
        def get_value(obj: dict, path: str):
            parts = path.split(".")
            val = obj
            for p in parts:
                if isinstance(val, dict) and p in val:
                    val = val[p]
                else:
                    return None
            return val

        for field_path in sorted(common):
            val_a = get_value(snap_a.body, field_path)
            val_b = get_value(snap_b.body, field_path)
            if val_a != val_b and not isinstance(val_a, dict) and not isinstance(val_b, dict):
                changed_values.append({"field": field_path, "from": val_a, "to": val_b})

        status_changed = snap_a.status_code != snap_b.status_code
        breaking = len(removed) > 0 or len(type_changes) > 0 or status_changed

        return {
            "endpoint_id": endpoint_id,
            "from_version": version_a,
            "to_version": version_b,
            "added_fields": added,
            "removed_fields": removed,
            "type_changes": type_changes,
            "value_changes": changed_values,
            "status_code_changed": status_changed,
            "breaking": breaking,
            "total_changes": len(added) + len(removed) + len(changed_values),
        }

    def list_snapshots(self, endpoint_id: str | None = None) -> list[dict]:
        snaps = list(self._snapshots.values())
        if endpoint_id:
            snaps = [s for s in snaps if s.endpoint_id == endpoint_id]
        return [{"snapshot_id": s.snapshot_id, "endpoint": s.endpoint_id,
                 "version": s.version, "status_code": s.status_code}
                for s in snaps]

    def get_stats(self) -> dict:
        endpoints = set(s.endpoint_id for s in self._snapshots.values())
        return {
            "total_snapshots": len(self._snapshots),
            "unique_endpoints": len(endpoints),
        }
