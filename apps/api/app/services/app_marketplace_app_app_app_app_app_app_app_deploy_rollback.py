"""Deployment rollback manager — track versions and perform safe rollbacks."""
from __future__ import annotations


class RollbackManager:
    def __init__(self):
        self._history: list[dict] = []
        self._current: dict | None = None

    def deploy(self, *, version: str, commit: str, deployer: str) -> dict:
        entry = {"version": version, "commit": commit, "deployer": deployer,
                 "status": "active", "index": len(self._history)}
        if self._current:
            self._current["status"] = "superseded"
        self._history.append(entry)
        self._current = entry
        return {"deployed": version, "index": entry["index"], "status": "active"}

    def rollback(self, *, to_index: int | None = None) -> dict:
        if len(self._history) < 2:
            return {"error": "No previous version to rollback to"}
        target_idx = to_index if to_index is not None else len(self._history) - 2
        if target_idx < 0 or target_idx >= len(self._history):
            return {"error": f"Invalid index: {target_idx}"}
        target = self._history[target_idx]
        if self._current:
            self._current["status"] = "rolled_back"
        new_entry = {**target, "status": "active", "index": len(self._history),
                     "rollback_from": self._current["version"] if self._current else None}
        self._history.append(new_entry)
        self._current = new_entry
        return {"rolled_back_to": target["version"], "from": new_entry.get("rollback_from"),
                "new_index": new_entry["index"]}

    def history(self) -> dict:
        return {"total": len(self._history),
                "current": self._current["version"] if self._current else None,
                "entries": list(reversed(self._history[-10:]))}
