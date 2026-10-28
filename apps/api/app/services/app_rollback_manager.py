"""App Rollback Manager — manage version rollbacks.

Manages rollback operations:
- Track deployment versions
- Initiate rollbacks to previous versions
- Rollback history with reasons
- Per-installation scoped versions
"""

from __future__ import annotations

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


@dataclass
class DeployVersion:
    """A deployed version."""

    version: str
    deployed_at: float = field(default_factory=time.time)
    is_current: bool = True


@dataclass
class RollbackRecord:
    """A rollback operation record."""

    rollback_id: str
    from_version: str
    to_version: str
    reason: str
    status: RollbackStatus = RollbackStatus.PENDING
    initiated_by: str = ""
    created_at: float = field(default_factory=time.time)


class AppRollbackManager:
    """Manage version rollbacks."""

    def __init__(self) -> None:
        self._versions: dict[str, list[DeployVersion]] = {}
        self._rollbacks: dict[str, list[RollbackRecord]] = {}

    def record_deploy(self, installation_id: str, version: str) -> DeployVersion:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not version:
            raise ValueError("version is required")

        versions = self._versions.setdefault(installation_id, [])
        # Mark previous as not current
        for v in versions:
            v.is_current = False

        dv = DeployVersion(version=version)
        versions.append(dv)
        return dv

    def rollback(
        self, installation_id: str, rollback_id: str,
        reason: str = "", initiated_by: str = "",
    ) -> RollbackRecord:
        versions = self._versions.get(installation_id, [])
        if len(versions) < 2:
            raise ValueError("No previous version to rollback to")

        current = versions[-1]
        previous = versions[-2]

        record = RollbackRecord(
            rollback_id=rollback_id, from_version=current.version,
            to_version=previous.version, reason=reason,
            initiated_by=initiated_by, status=RollbackStatus.IN_PROGRESS,
        )
        self._rollbacks.setdefault(installation_id, []).append(record)

        # Update version state
        current.is_current = False
        previous.is_current = True

        return record

    def complete_rollback(self, installation_id: str, rollback_id: str) -> RollbackRecord:
        r = self._find_rollback(installation_id, rollback_id)
        if r.status != RollbackStatus.IN_PROGRESS:
            raise ValueError("Rollback not in progress")
        r.status = RollbackStatus.COMPLETED
        return r

    def fail_rollback(self, installation_id: str, rollback_id: str, error: str = "") -> RollbackRecord:
        r = self._find_rollback(installation_id, rollback_id)
        if r.status != RollbackStatus.IN_PROGRESS:
            raise ValueError("Rollback not in progress")
        r.status = RollbackStatus.FAILED
        return r

    def current_version(self, installation_id: str) -> str | None:
        versions = self._versions.get(installation_id, [])
        for v in reversed(versions):
            if v.is_current:
                return v.version
        return None

    def rollback_history(self, installation_id: str) -> list[RollbackRecord]:
        return list(reversed(self._rollbacks.get(installation_id, [])))

    def _find_rollback(self, installation_id: str, rollback_id: str) -> RollbackRecord:
        for r in self._rollbacks.get(installation_id, []):
            if r.rollback_id == rollback_id:
                return r
        raise KeyError(f"Rollback {rollback_id} not found")
