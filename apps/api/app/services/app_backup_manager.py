"""App Backup Manager — manage backup snapshots for installed apps.

Manages backup lifecycle:
- Create backup snapshots
- Track backup status and size
- Restore from backups
- Retention policy enforcement
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class BackupStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RESTORED = "restored"


@dataclass
class Backup:
    """A backup snapshot."""

    backup_id: str
    installation_id: str
    status: BackupStatus = BackupStatus.PENDING
    size_mb: float = 0.0
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    error: str = ""
    label: str = ""


class AppBackupManager:
    """Manage backup snapshots."""

    def __init__(self, max_backups: int = 30) -> None:
        self._backups: dict[tuple[str, str], Backup] = {}
        self._history: dict[str, list[str]] = {}
        self._max = max(1, max_backups)

    def create_backup(
        self, installation_id: str, backup_id: str, label: str = "",
        now: float | None = None,
    ) -> Backup:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not backup_id:
            raise ValueError("backup_id is required")

        key = (installation_id, backup_id)
        if key in self._backups:
            raise ValueError(f"Backup {backup_id} already exists")

        backup = Backup(
            backup_id=backup_id, installation_id=installation_id,
            label=label, created_at=now or time.time(),
        )
        self._backups[key] = backup
        self._history.setdefault(installation_id, []).append(backup_id)

        # Enforce retention
        history = self._history[installation_id]
        while len(history) > self._max:
            old_id = history.pop(0)
            self._backups.pop((installation_id, old_id), None)

        return backup

    def complete_backup(
        self, installation_id: str, backup_id: str, size_mb: float
    ) -> Backup:
        b = self._get(installation_id, backup_id)
        b.status = BackupStatus.COMPLETED
        b.size_mb = max(0, size_mb)
        b.completed_at = time.time()
        return b

    def fail_backup(
        self, installation_id: str, backup_id: str, error: str = ""
    ) -> Backup:
        b = self._get(installation_id, backup_id)
        b.status = BackupStatus.FAILED
        b.error = error
        return b

    def restore_backup(self, installation_id: str, backup_id: str) -> Backup:
        b = self._get(installation_id, backup_id)
        if b.status != BackupStatus.COMPLETED:
            raise ValueError("Can only restore completed backups")
        b.status = BackupStatus.RESTORED
        return b

    def list_backups(self, installation_id: str) -> list[Backup]:
        ids = self._history.get(installation_id, [])
        return [self._backups[(installation_id, bid)] for bid in reversed(ids)
                if (installation_id, bid) in self._backups]

    def total_size_mb(self, installation_id: str) -> float:
        return sum(b.size_mb for b in self.list_backups(installation_id))

    def _get(self, installation_id: str, backup_id: str) -> Backup:
        key = (installation_id, backup_id)
        b = self._backups.get(key)
        if b is None:
            raise KeyError(f"Backup {backup_id} not found")
        return b
