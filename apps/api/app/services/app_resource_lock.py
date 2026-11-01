"""App Resource Lock — distributed-style locking for app resources.

Provides exclusive locking for installed app resources:
- Acquire/release named locks
- Lock expiry (TTL) to prevent deadlocks
- Owner tracking for safe release
- Lock status checking
- Per-installation scoped locks
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Lock:
    """A resource lock."""

    lock_id: str
    installation_id: str
    resource: str
    owner: str
    acquired_at: float = field(default_factory=time.time)
    expires_at: float = 0.0


@dataclass
class LockResult:
    """Result of a lock operation."""

    acquired: bool
    lock_id: str = ""
    owner: str = ""
    reason: str = ""  # "acquired", "already_locked", "expired_reclaimed"


class AppResourceLock:
    """Distributed-style locking for app resources."""

    def __init__(self, default_ttl_seconds: float = 30.0) -> None:
        if default_ttl_seconds <= 0:
            raise ValueError("default_ttl_seconds must be > 0")
        self._ttl = default_ttl_seconds
        # (installation_id, resource) → Lock
        self._locks: dict[tuple[str, str], Lock] = {}

    def acquire(
        self,
        installation_id: str,
        resource: str,
        owner: str,
        lock_id: str = "",
        ttl_seconds: float | None = None,
        now: float | None = None,
    ) -> LockResult:
        """Try to acquire a lock on a resource."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not resource:
            raise ValueError("resource is required")
        if not owner:
            raise ValueError("owner is required")

        now = now or time.time()
        ttl = ttl_seconds if ttl_seconds is not None else self._ttl
        key = (installation_id, resource)
        existing = self._locks.get(key)

        # Check if existing lock is expired
        if existing and now >= existing.expires_at:
            del self._locks[key]
            existing = None
            reason = "expired_reclaimed"
        else:
            reason = "acquired"

        if existing:
            if existing.owner == owner:
                # Re-entrant: extend
                existing.expires_at = now + ttl
                return LockResult(acquired=True, lock_id=existing.lock_id,
                                  owner=owner, reason="acquired")
            return LockResult(acquired=False, lock_id=existing.lock_id,
                              owner=existing.owner, reason="already_locked")

        lock = Lock(
            lock_id=lock_id or f"{resource}:{owner}",
            installation_id=installation_id,
            resource=resource,
            owner=owner,
            acquired_at=now,
            expires_at=now + ttl,
        )
        self._locks[key] = lock
        return LockResult(acquired=True, lock_id=lock.lock_id,
                          owner=owner, reason=reason)

    def release(
        self,
        installation_id: str,
        resource: str,
        owner: str,
    ) -> bool:
        """Release a lock. Only the owner can release. Returns True if released."""
        key = (installation_id, resource)
        lock = self._locks.get(key)
        if lock is None:
            return False
        if lock.owner != owner:
            raise ValueError("Only the lock owner can release")
        del self._locks[key]
        return True

    def is_locked(self, installation_id: str, resource: str,
                  now: float | None = None) -> bool:
        """Check if a resource is currently locked."""
        now = now or time.time()
        key = (installation_id, resource)
        lock = self._locks.get(key)
        if lock is None:
            return False
        if now >= lock.expires_at:
            del self._locks[key]
            return False
        return True

    def get_lock(self, installation_id: str, resource: str) -> Lock | None:
        key = (installation_id, resource)
        return self._locks.get(key)

    def list_locks(self, installation_id: str) -> list[Lock]:
        return [
            lock for (inst, _), lock in self._locks.items()
            if inst == installation_id
        ]
