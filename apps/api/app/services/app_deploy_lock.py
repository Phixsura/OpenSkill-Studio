"""App Deploy Lock — prevent concurrent deployments.

Manages deploy locks:
- Acquire/release exclusive deploy locks
- Lock timeout for stale locks
- Lock history tracking
- Per-installation scoped locks
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class DeployLock:
    """A deploy lock."""

    lock_id: str
    owner: str
    reason: str = ""
    acquired_at: float = field(default_factory=time.time)
    timeout_seconds: float = 600.0  # 10 min default
    released_at: float | None = None

    @property
    def is_active(self) -> bool:
        if self.released_at is not None:
            return False
        return (time.time() - self.acquired_at) < self.timeout_seconds

    @property
    def is_expired(self) -> bool:
        if self.released_at is not None:
            return False
        return (time.time() - self.acquired_at) >= self.timeout_seconds


class AppDeployLock:
    """Prevent concurrent deployments."""

    def __init__(self) -> None:
        self._locks: dict[str, list[DeployLock]] = {}

    def acquire(
        self, installation_id: str, lock_id: str, owner: str,
        reason: str = "", timeout_seconds: float = 600.0,
    ) -> DeployLock:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not owner:
            raise ValueError("owner is required")

        # Check for existing active lock
        current = self.current_lock(installation_id)
        if current is not None:
            raise ValueError(f"Deploy locked by {current.owner}")

        lock = DeployLock(
            lock_id=lock_id, owner=owner, reason=reason,
            timeout_seconds=timeout_seconds,
        )
        self._locks.setdefault(installation_id, []).append(lock)
        return lock

    def release(self, installation_id: str, owner: str) -> DeployLock:
        current = self.current_lock(installation_id)
        if current is None:
            raise ValueError("No active lock")
        if current.owner != owner:
            raise ValueError(f"Lock owned by {current.owner}, not {owner}")
        current.released_at = time.time()
        return current

    def force_release(self, installation_id: str) -> DeployLock | None:
        """Force release regardless of owner (admin action)."""
        current = self.current_lock(installation_id)
        if current is None:
            return None
        current.released_at = time.time()
        return current

    def current_lock(self, installation_id: str) -> DeployLock | None:
        locks = self._locks.get(installation_id, [])
        for lock in reversed(locks):
            if lock.is_active:
                return lock
        return None

    def is_locked(self, installation_id: str) -> bool:
        return self.current_lock(installation_id) is not None

    def history(self, installation_id: str, limit: int = 20) -> list[DeployLock]:
        locks = self._locks.get(installation_id, [])
        return list(reversed(locks[-limit:]))
