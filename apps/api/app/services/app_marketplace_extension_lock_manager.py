"""Lock Manager — distributed locking for extension operations.

Provides advisory locks to prevent concurrent modifications to
extension configs, deployments, and state during critical sections.
"""
from __future__ import annotations
import time
from dataclasses import dataclass


@dataclass
class Lock:
    lock_id: str
    resource: str
    holder: str
    acquired_at: float
    ttl_seconds: float
    released: bool = False

    @property
    def expired(self) -> bool:
        return time.monotonic() - self.acquired_at > self.ttl_seconds


class LockManager:
    """Advisory lock manager for critical extension operations."""

    def __init__(self, default_ttl: float = 30.0):
        self._locks: dict[str, Lock] = {}
        self._default_ttl = default_ttl
        self._counter = 0

    def acquire(self, resource: str, holder: str,
                ttl: float | None = None) -> tuple[Lock | None, str]:
        """Try to acquire a lock on a resource."""
        existing = self._locks.get(resource)
        if existing and not existing.released and not existing.expired:
            if existing.holder == holder:
                # Re-entrant: extend TTL
                existing.acquired_at = time.monotonic()
                return existing, "Extended"
            return None, f"Resource locked by {existing.holder}"

        self._counter += 1
        lock = Lock(
            lock_id=f"lock-{self._counter}",
            resource=resource, holder=holder,
            acquired_at=time.monotonic(),
            ttl_seconds=ttl or self._default_ttl,
        )
        self._locks[resource] = lock
        return lock, "Acquired"

    def release(self, resource: str, holder: str) -> bool:
        """Release a lock. Only the holder can release."""
        lock = self._locks.get(resource)
        if not lock or lock.holder != holder:
            return False
        lock.released = True
        return True

    def is_locked(self, resource: str) -> bool:
        lock = self._locks.get(resource)
        return lock is not None and not lock.released and not lock.expired

    def get_lock_info(self, resource: str) -> dict | None:
        lock = self._locks.get(resource)
        if not lock:
            return None
        return {
            "resource": resource, "holder": lock.holder,
            "locked": not lock.released and not lock.expired,
            "expired": lock.expired, "released": lock.released,
            "ttl_remaining": max(0, lock.ttl_seconds - (time.monotonic() - lock.acquired_at)),
        }

    def force_release(self, resource: str) -> bool:
        """Admin force-release a lock regardless of holder."""
        lock = self._locks.get(resource)
        if lock:
            lock.released = True
            return True
        return False

    def list_active_locks(self) -> list[dict]:
        return [
            {"resource": r, "holder": l.holder, "lock_id": l.lock_id}
            for r, l in self._locks.items()
            if not l.released and not l.expired
        ]

    def cleanup_expired(self) -> int:
        expired = [r for r, l in self._locks.items() if l.expired or l.released]
        for r in expired:
            del self._locks[r]
        return len(expired)
