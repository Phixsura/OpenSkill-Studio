"""App Rollback Manager — manage version rollbacks with safety checks.

Handles rollback operations for installed apps:
- Track rollback history
- Safety checks (min version, cooldown)
- Rollback reason recording
- Per-installation scoped rollbacks
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class RollbackStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class RollbackRecord:
    """A rollback operation record."""

    rollback_id: str
    installation_id: str
    from_version: str
    to_version: str
    reason: str
    status: RollbackStatus = RollbackStatus.PENDING
    initiated_by: str = ""
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    error: str | None = None


_SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)")


def _parse_version(v: str) -> tuple[int, int, int]:
    """Parse a version string into a comparable tuple."""
    m = _SEMVER_RE.match(v)
    if not m:
        raise ValueError(f"Invalid version string: {v}")
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


class AppRollbackManager:
    """Manage version rollbacks with safety checks."""

    def __init__(
        self,
        min_version: str = "0.0.0",
        cooldown_seconds: float = 300,
    ) -> None:
        _parse_version(min_version)  # validate
        self._min_version = min_version
        self._cooldown = cooldown_seconds
        self._rollbacks: dict[tuple[str, str], RollbackRecord] = {}
        self._history: dict[str, list[RollbackRecord]] = {}

    def initiate_rollback(
        self,
        installation_id: str,
        rollback_id: str,
        from_version: str,
        to_version: str,
        reason: str,
        initiated_by: str = "",
        now: float | None = None,
    ) -> RollbackRecord:
        """Initiate a rollback with safety checks."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not rollback_id:
            raise ValueError("rollback_id is required")
        if not reason:
            raise ValueError("reason is required")
        to_parsed = _parse_version(to_version)
        from_parsed = _parse_version(from_version)

        if to_parsed == from_parsed:
            raise ValueError("Cannot rollback to the same version")

        # Check min version
        if to_parsed < _parse_version(self._min_version):
            raise ValueError(f"Cannot rollback below minimum version {self._min_version}")

        now = now or time.time()

        # Check cooldown
        history = self._history.get(installation_id, [])
        if history:
            last = history[-1]
            if now - last.created_at < self._cooldown:
                raise ValueError(
                    f"Rollback cooldown: wait {self._cooldown}s between rollbacks"
                )

        key = (installation_id, rollback_id)
        if key in self._rollbacks:
            raise ValueError(f"Rollback {rollback_id} already exists")

        record = RollbackRecord(
            rollback_id=rollback_id,
            installation_id=installation_id,
            from_version=from_version,
            to_version=to_version,
            reason=reason,
            initiated_by=initiated_by,
            created_at=now,
        )
        self._rollbacks[key] = record
        self._history.setdefault(installation_id, []).append(record)
        log.warning("rollback.initiated", rollback_id=rollback_id,
                     from_version=from_version, to_version=to_version)
        return record

    def start_rollback(self, installation_id: str, rollback_id: str) -> RollbackRecord:
        r = self._get(installation_id, rollback_id)
        if r.status != RollbackStatus.PENDING:
            raise ValueError(f"Cannot start rollback in {r.status} state")
        r.status = RollbackStatus.IN_PROGRESS
        return r

    def complete_rollback(self, installation_id: str, rollback_id: str) -> RollbackRecord:
        r = self._get(installation_id, rollback_id)
        if r.status != RollbackStatus.IN_PROGRESS:
            raise ValueError(f"Cannot complete rollback in {r.status} state")
        r.status = RollbackStatus.COMPLETED
        r.completed_at = time.time()
        return r

    def fail_rollback(self, installation_id: str, rollback_id: str, error: str = "") -> RollbackRecord:
        r = self._get(installation_id, rollback_id)
        if r.status != RollbackStatus.IN_PROGRESS:
            raise ValueError(f"Cannot fail rollback in {r.status} state")
        r.status = RollbackStatus.FAILED
        r.error = error
        return r

    def get_rollback(self, installation_id: str, rollback_id: str) -> RollbackRecord:
        return self._get(installation_id, rollback_id)

    def get_history(self, installation_id: str, limit: int = 20) -> list[RollbackRecord]:
        history = self._history.get(installation_id, [])
        return list(reversed(history[-limit:]))

    def _get(self, installation_id: str, rollback_id: str) -> RollbackRecord:
        key = (installation_id, rollback_id)
        r = self._rollbacks.get(key)
        if r is None:
            raise KeyError(f"Rollback {rollback_id} not found")
        return r
