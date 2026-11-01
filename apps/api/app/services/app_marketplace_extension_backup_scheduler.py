"""Backup Scheduler — schedule and manage automatic config backups.

Provides cron-like scheduling for automatic extension config snapshots
with retention policies, restore points, and backup health monitoring.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class BackupSchedule:
    schedule_id: str
    extension_id: str
    org_id: str
    frequency: str  # hourly, daily, weekly
    retention_count: int = 30
    enabled: bool = True
    last_run: str = ""
    next_run: str = ""
    total_backups: int = 0
    failed_backups: int = 0


@dataclass
class BackupRecord:
    backup_id: str
    schedule_id: str
    extension_id: str
    org_id: str
    status: str  # success, failed, expired
    size_bytes: int = 0
    created_at: str = ""
    expires_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class BackupScheduler:
    """Manages automatic backup schedules for extension configs."""

    def __init__(self):
        self._schedules: dict[str, BackupSchedule] = {}
        self._backups: dict[str, list[BackupRecord]] = {}  # schedule_id -> records
        self._counter = 0

    def create_schedule(self, extension_id: str, org_id: str,
                        frequency: str = "daily", retention: int = 30) -> BackupSchedule:
        self._counter += 1
        schedule = BackupSchedule(
            schedule_id=f"sched-{self._counter}",
            extension_id=extension_id, org_id=org_id,
            frequency=frequency, retention_count=retention,
        )
        self._schedules[schedule.schedule_id] = schedule
        return schedule

    def disable_schedule(self, schedule_id: str) -> bool:
        s = self._schedules.get(schedule_id)
        if s:
            s.enabled = False
            return True
        return False

    def enable_schedule(self, schedule_id: str) -> bool:
        s = self._schedules.get(schedule_id)
        if s:
            s.enabled = True
            return True
        return False

    def run_backup(self, schedule_id: str, data_size: int = 0) -> BackupRecord:
        """Execute a backup for a schedule."""
        schedule = self._schedules.get(schedule_id)
        if not schedule:
            return BackupRecord("", schedule_id, "", "", "failed")

        self._counter += 1
        record = BackupRecord(
            backup_id=f"bak-{self._counter}", schedule_id=schedule_id,
            extension_id=schedule.extension_id, org_id=schedule.org_id,
            status="success", size_bytes=data_size,
        )
        schedule.total_backups += 1
        schedule.last_run = record.created_at

        records = self._backups.setdefault(schedule_id, [])
        records.append(record)

        # Enforce retention
        while len(records) > schedule.retention_count:
            expired = records.pop(0)
            expired.status = "expired"

        return record

    def record_failure(self, schedule_id: str, error: str = "") -> None:
        schedule = self._schedules.get(schedule_id)
        if schedule:
            schedule.failed_backups += 1

    def get_schedule(self, schedule_id: str) -> BackupSchedule | None:
        return self._schedules.get(schedule_id)

    def list_schedules(self, extension_id: str | None = None) -> list[BackupSchedule]:
        schedules = list(self._schedules.values())
        if extension_id:
            schedules = [s for s in schedules if s.extension_id == extension_id]
        return schedules

    def get_backups(self, schedule_id: str) -> list[BackupRecord]:
        return list(self._backups.get(schedule_id, []))

    def get_health(self, schedule_id: str) -> dict:
        schedule = self._schedules.get(schedule_id)
        if not schedule:
            return {"error": "Not found"}
        backups = self._backups.get(schedule_id, [])
        return {
            "schedule_id": schedule_id, "enabled": schedule.enabled,
            "total_backups": schedule.total_backups,
            "failed_backups": schedule.failed_backups,
            "success_rate": round((schedule.total_backups - schedule.failed_backups) / max(1, schedule.total_backups) * 100, 1),
            "stored_backups": len(backups),
            "retention_count": schedule.retention_count,
            "last_run": schedule.last_run,
        }
