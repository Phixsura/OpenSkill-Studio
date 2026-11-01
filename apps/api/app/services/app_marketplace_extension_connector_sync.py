"""Connector Sync Engine — bidirectional data synchronization between connectors.

Manages sync jobs between source and target connectors with conflict
resolution, incremental sync via cursors, and sync health monitoring.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class SyncDirection(str, Enum):
    SOURCE_TO_TARGET = "source_to_target"
    TARGET_TO_SOURCE = "target_to_source"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(str, Enum):
    IDLE = "idle"
    SYNCING = "syncing"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


class ConflictResolution(str, Enum):
    SOURCE_WINS = "source_wins"
    TARGET_WINS = "target_wins"
    NEWEST_WINS = "newest_wins"
    MANUAL = "manual"


@dataclass
class SyncJob:
    job_id: str
    extension_id: str
    source_connector: str
    target_connector: str
    direction: SyncDirection
    conflict_resolution: ConflictResolution
    status: SyncStatus = SyncStatus.IDLE
    records_synced: int = 0
    records_failed: int = 0
    conflicts: int = 0
    cursor: str = ""
    last_sync_at: str = ""
    error: str = ""


class ConnectorSyncService:
    """Manages bidirectional data sync between connectors."""

    def __init__(self):
        self._jobs: dict[str, SyncJob] = {}

    def create_job(self, extension_id: str, source: str, target: str,
                   direction: SyncDirection = SyncDirection.SOURCE_TO_TARGET,
                   conflict_resolution: ConflictResolution = ConflictResolution.SOURCE_WINS) -> SyncJob:
        job_id = f"sync_{secrets.token_urlsafe(10)}"
        job = SyncJob(
            job_id=job_id, extension_id=extension_id,
            source_connector=source, target_connector=target,
            direction=direction, conflict_resolution=conflict_resolution,
        )
        self._jobs[job_id] = job
        return job

    def start_sync(self, job_id: str) -> dict:
        job = self._jobs.get(job_id)
        if not job:
            return {"ok": False, "error": "Job not found"}
        if job.status == SyncStatus.SYNCING:
            return {"ok": False, "error": "Already syncing"}
        job.status = SyncStatus.SYNCING
        return {"ok": True, "job_id": job_id}

    def record_progress(self, job_id: str, synced: int = 0,
                        failed: int = 0, conflicts: int = 0,
                        cursor: str = "") -> bool:
        job = self._jobs.get(job_id)
        if not job or job.status != SyncStatus.SYNCING:
            return False
        job.records_synced += synced
        job.records_failed += failed
        job.conflicts += conflicts
        if cursor:
            job.cursor = cursor
        return True

    def complete_sync(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if not job or job.status != SyncStatus.SYNCING:
            return False
        job.status = SyncStatus.COMPLETED if job.conflicts == 0 else SyncStatus.CONFLICT
        job.last_sync_at = datetime.now(timezone.utc).isoformat()
        return True

    def fail_sync(self, job_id: str, error: str) -> bool:
        job = self._jobs.get(job_id)
        if not job or job.status != SyncStatus.SYNCING:
            return False
        job.status = SyncStatus.FAILED
        job.error = error
        return True

    def resolve_conflicts(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if not job or job.status != SyncStatus.CONFLICT:
            return False
        job.conflicts = 0
        job.status = SyncStatus.COMPLETED
        return True

    def get_job(self, job_id: str) -> SyncJob | None:
        return self._jobs.get(job_id)

    def list_jobs(self, extension_id: str) -> list[SyncJob]:
        return [j for j in self._jobs.values() if j.extension_id == extension_id]

    def get_sync_health(self, extension_id: str) -> dict:
        jobs = self.list_jobs(extension_id)
        return {
            "total_jobs": len(jobs),
            "active": sum(1 for j in jobs if j.status == SyncStatus.SYNCING),
            "completed": sum(1 for j in jobs if j.status == SyncStatus.COMPLETED),
            "failed": sum(1 for j in jobs if j.status == SyncStatus.FAILED),
            "conflicts": sum(1 for j in jobs if j.status == SyncStatus.CONFLICT),
            "total_synced": sum(j.records_synced for j in jobs),
        }
