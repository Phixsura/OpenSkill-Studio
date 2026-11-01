"""Extension Dependency Lockfile — pin exact dependency versions."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import json
import time


@dataclass
class LockedDep:
    name: str
    version: str
    integrity: str = ""  # sha256 hash


@dataclass
class Lockfile:
    extension_id: str
    deps: list[LockedDep] = field(default_factory=list)
    generated_at: float = 0.0
    checksum: str = ""
    def __post_init__(self):
        if not self.generated_at: self.generated_at = time.time()


class ExtDepLockfileService:
    def __init__(self):
        self._lockfiles: dict[str, Lockfile] = {}

    def generate(self, extension_id: str, deps: list[tuple[str, str]]) -> Lockfile:
        locked = []
        for name, version in deps:
            integrity = hashlib.sha256(f"{name}@{version}".encode()).hexdigest()[:16]
            locked.append(LockedDep(name=name, version=version, integrity=integrity))
        content = json.dumps([(d.name, d.version) for d in locked], sort_keys=True)
        checksum = hashlib.sha256(content.encode()).hexdigest()[:32]
        lf = Lockfile(extension_id=extension_id, deps=locked, checksum=checksum)
        self._lockfiles[extension_id] = lf
        return lf

    def verify(self, extension_id: str, deps: list[tuple[str, str]]) -> tuple[bool, list[str]]:
        lf = self._lockfiles.get(extension_id)
        if not lf:
            return False, ["No lockfile found"]
        locked_map = {d.name: d.version for d in lf.deps}
        mismatches = []
        for name, version in deps:
            if name not in locked_map:
                mismatches.append(f"New dep: {name}@{version}")
            elif locked_map[name] != version:
                mismatches.append(f"Version mismatch: {name} ({locked_map[name]} locked, {version} requested)")
        return len(mismatches) == 0, mismatches

    def get(self, extension_id: str) -> Lockfile | None:
        return self._lockfiles.get(extension_id)

    def diff(self, extension_id: str, new_deps: list[tuple[str, str]]) -> dict:
        lf = self._lockfiles.get(extension_id)
        old = {d.name: d.version for d in lf.deps} if lf else {}
        new = dict(new_deps)
        added = {k: v for k, v in new.items() if k not in old}
        removed = {k: v for k, v in old.items() if k not in new}
        changed = {k: {"from": old[k], "to": new[k]} for k in old if k in new and old[k] != new[k]}
        return {"added": added, "removed": removed, "changed": changed}
