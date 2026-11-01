"""Dependency Lock — freeze and verify extension dependency versions.

Creates lockfiles that pin exact dependency versions for reproducible
builds, with integrity checking via content hashes.
"""
from __future__ import annotations
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class LockedDependency:
    name: str
    version: str
    integrity: str  # SHA-256 hash
    resolved_url: str = ""


@dataclass
class LockFile:
    extension_id: str
    lock_version: int
    dependencies: list[LockedDependency]
    created_at: str = ""
    checksum: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.checksum:
            self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        content = "|".join(f"{d.name}@{d.version}:{d.integrity}" for d in sorted(self.dependencies, key=lambda d: d.name))
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class DependencyLockService:
    """Manages dependency lockfiles for reproducible extension builds."""

    def __init__(self):
        self._locks: dict[str, LockFile] = {}
        self._lock_history: dict[str, list[LockFile]] = {}

    def create_lock(self, extension_id: str, dependencies: list[dict]) -> LockFile:
        """Create a lockfile from resolved dependencies."""
        locked = [
            LockedDependency(
                name=d["name"], version=d["version"],
                integrity=d.get("integrity", hashlib.sha256(f"{d['name']}@{d['version']}".encode()).hexdigest()),
                resolved_url=d.get("url", ""),
            )
            for d in dependencies
        ]
        version = len(self._lock_history.get(extension_id, [])) + 1
        lock = LockFile(extension_id, version, locked)
        self._locks[extension_id] = lock
        self._lock_history.setdefault(extension_id, []).append(lock)
        return lock

    def get_lock(self, extension_id: str) -> LockFile | None:
        return self._locks.get(extension_id)

    def verify(self, extension_id: str, current_deps: list[dict]) -> tuple[bool, list[str]]:
        """Verify current dependencies match the lockfile."""
        lock = self._locks.get(extension_id)
        if not lock:
            return False, ["No lockfile found"]

        locked_map = {d.name: d for d in lock.dependencies}
        errors = []

        for dep in current_deps:
            locked = locked_map.get(dep["name"])
            if not locked:
                errors.append(f"New dependency not in lockfile: {dep['name']}")
            elif locked.version != dep["version"]:
                errors.append(f"{dep['name']}: version mismatch (locked={locked.version}, current={dep['version']})")
            elif dep.get("integrity") and locked.integrity != dep["integrity"]:
                errors.append(f"{dep['name']}: integrity check failed")

        for name in locked_map:
            if not any(d["name"] == name for d in current_deps):
                errors.append(f"Missing locked dependency: {name}")

        return len(errors) == 0, errors

    def diff(self, extension_id: str, new_deps: list[dict]) -> dict:
        """Show differences between lockfile and new dependencies."""
        lock = self._locks.get(extension_id)
        if not lock:
            return {"added": [d["name"] for d in new_deps], "removed": [], "changed": []}
        locked_map = {d.name: d for d in lock.dependencies}
        new_map = {d["name"]: d for d in new_deps}

        return {
            "added": sorted(set(new_map) - set(locked_map)),
            "removed": sorted(set(locked_map) - set(new_map)),
            "changed": sorted(n for n in set(locked_map) & set(new_map) if locked_map[n].version != new_map[n]["version"]),
        }

    def get_history(self, extension_id: str) -> list[LockFile]:
        return list(self._lock_history.get(extension_id, []))
