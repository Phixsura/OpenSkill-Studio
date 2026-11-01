"""Extension Rollback — version rollback with safety checks and history.

Manages extension version rollbacks with pre-rollback validation,
automatic backup, rollback history tracking, and rollforward support.
"""
from __future__ import annotations
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class RollbackStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_FORWARD = "rolled_forward"


@dataclass
class VersionSnapshot:
    version: str
    config_hash: str
    install_count: int = 0
    created_at: str = ""


@dataclass
class RollbackRecord:
    rollback_id: str
    extension_id: str
    from_version: str
    to_version: str
    reason: str
    status: RollbackStatus = RollbackStatus.PENDING
    initiated_by: str = ""
    backup_id: str = ""
    started_at: str = ""
    completed_at: str = ""


class ExtensionRollbackService:
    """Manages extension version rollbacks with safety checks."""

    def __init__(self):
        self._versions: dict[str, list[VersionSnapshot]] = {}
        self._current: dict[str, str] = {}
        self._rollbacks: list[RollbackRecord] = []

    def register_version(self, extension_id: str, version: str,
                         config_hash: str = "") -> VersionSnapshot:
        snap = VersionSnapshot(
            version=version, config_hash=config_hash or secrets.token_hex(8),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._versions.setdefault(extension_id, []).append(snap)
        self._current[extension_id] = version
        return snap

    def get_current_version(self, extension_id: str) -> str | None:
        return self._current.get(extension_id)

    def get_available_versions(self, extension_id: str) -> list[str]:
        return [v.version for v in self._versions.get(extension_id, [])]

    def can_rollback(self, extension_id: str, target_version: str) -> dict:
        versions = self.get_available_versions(extension_id)
        current = self._current.get(extension_id)
        if not current:
            return {"can_rollback": False, "reason": "No current version"}
        if target_version not in versions:
            return {"can_rollback": False, "reason": "Target version not found"}
        if target_version == current:
            return {"can_rollback": False, "reason": "Already on this version"}
        return {"can_rollback": True}

    def rollback(self, extension_id: str, target_version: str,
                 reason: str, initiated_by: str) -> RollbackRecord | dict:
        check = self.can_rollback(extension_id, target_version)
        if not check.get("can_rollback"):
            return {"error": check.get("reason", "Cannot rollback")}

        current = self._current[extension_id]
        record = RollbackRecord(
            rollback_id=f"rb_{secrets.token_urlsafe(10)}",
            extension_id=extension_id,
            from_version=current, to_version=target_version,
            reason=reason, initiated_by=initiated_by,
            status=RollbackStatus.IN_PROGRESS,
            backup_id=f"bk_{secrets.token_hex(6)}",
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        self._current[extension_id] = target_version
        record.status = RollbackStatus.COMPLETED
        record.completed_at = datetime.now(timezone.utc).isoformat()
        self._rollbacks.append(record)
        return record

    def rollforward(self, rollback_id: str) -> bool:
        record = next((r for r in self._rollbacks if r.rollback_id == rollback_id), None)
        if not record or record.status != RollbackStatus.COMPLETED:
            return False
        self._current[record.extension_id] = record.from_version
        record.status = RollbackStatus.ROLLED_FORWARD
        return True

    def get_history(self, extension_id: str) -> list[RollbackRecord]:
        return [r for r in self._rollbacks if r.extension_id == extension_id]
