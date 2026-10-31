"""Rollback manager — manage deployment rollbacks."""
from __future__ import annotations
import time


def create_snapshot(version: str, config: dict, metadata: dict | None = None) -> dict:
    return {"version": version, "config": config, "metadata": metadata or {},
            "created_at": time.time(), "status": "available"}


def rollback(current: dict, target: dict) -> dict:
    changes = []
    for k in set(current["config"]) | set(target["config"]):
        old_val = current["config"].get(k)
        new_val = target["config"].get(k)
        if old_val != new_val:
            changes.append({"key": k, "from": old_val, "to": new_val})
    return {"from_version": current["version"], "to_version": target["version"],
            "changes": changes, "change_count": len(changes),
            "status": "completed", "rolled_back_at": time.time()}


def list_snapshots(snapshots: list[dict]) -> dict:
    available = [s for s in snapshots if s["status"] == "available"]
    return {"snapshots": snapshots, "total": len(snapshots),
            "available": len(available),
            "latest": snapshots[-1]["version"] if snapshots else None}
