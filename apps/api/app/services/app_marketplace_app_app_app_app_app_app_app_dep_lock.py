"""Service dependency lock — lock service versions for stable deployments."""
from __future__ import annotations


class DependencyLockManager:
    def __init__(self):
        self._locks: dict[str, dict] = {}

    def lock(self, service: str, version: str, locked_by: str) -> dict:
        self._locks[service] = {"service": service, "version": version,
                                 "locked_by": locked_by, "locked": True}
        return self._locks[service]

    def unlock(self, service: str) -> dict:
        if service in self._locks:
            del self._locks[service]
            return {"service": service, "unlocked": True}
        return {"service": service, "unlocked": False}

    def is_locked(self, service: str) -> bool:
        return service in self._locks

    def check_upgrade(self, service: str, new_version: str) -> dict:
        if service in self._locks:
            locked = self._locks[service]
            return {"allowed": False, "reason": f"locked at {locked['version']} by {locked['locked_by']}"}
        return {"allowed": True, "service": service, "new_version": new_version}

    def list_locks(self) -> list[dict]:
        return list(self._locks.values())
