"""Dependency Lock — lock file management for reproducible builds.

Creates lock files from dependency specs, detects drift between lock
and manifest, and supports integrity hash verification.
"""
from __future__ import annotations
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class LockedDep:
    name: str
    version: str
    integrity: str  # sha256 hash
    resolved_url: str = ""


class ExtensionDepLockService:
    """Manages dependency lock files for reproducible extension builds."""

    def __init__(self):
        self._locks: dict[str, list[LockedDep]] = {}

    def lock(self, extension_id: str, deps: list[dict]) -> list[LockedDep]:
        locked = []
        for d in deps:
            integrity = hashlib.sha256(
                f"{d['name']}@{d['version']}".encode()
            ).hexdigest()[:16]
            locked.append(LockedDep(
                name=d["name"], version=d["version"],
                integrity=f"sha256-{integrity}",
                resolved_url=d.get("url", f"https://registry.example.com/{d['name']}/{d['version']}"),
            ))
        self._locks[extension_id] = locked
        return locked

    def verify(self, extension_id: str) -> dict:
        locked = self._locks.get(extension_id, [])
        if not locked:
            return {"verified": False, "reason": "No lock file"}
        invalid = []
        for dep in locked:
            expected = hashlib.sha256(
                f"{dep.name}@{dep.version}".encode()
            ).hexdigest()[:16]
            if dep.integrity != f"sha256-{expected}":
                invalid.append(dep.name)
        return {"verified": len(invalid) == 0, "invalid": invalid,
                "total": len(locked)}

    def check_drift(self, extension_id: str, manifest_deps: list[dict]) -> dict:
        locked = self._locks.get(extension_id, [])
        lock_map = {d.name: d.version for d in locked}
        manifest_map = {d["name"]: d["version"] for d in manifest_deps}

        added = [n for n in manifest_map if n not in lock_map]
        removed = [n for n in lock_map if n not in manifest_map]
        changed = [n for n in manifest_map
                    if n in lock_map and manifest_map[n] != lock_map[n]]

        return {
            "in_sync": not (added or removed or changed),
            "added": added, "removed": removed, "changed": changed,
        }

    def get_lock(self, extension_id: str) -> list[LockedDep]:
        return list(self._locks.get(extension_id, []))

    def get_lockfile_hash(self, extension_id: str) -> str:
        locked = self._locks.get(extension_id, [])
        content = "|".join(f"{d.name}@{d.version}" for d in sorted(locked, key=lambda d: d.name))
        return hashlib.sha256(content.encode()).hexdigest()[:20]
