"""API Consumer Data Export — export consumer data in various formats."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import structlog

log = structlog.get_logger()

class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"

class ExportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ExportJob:
    job_id: str
    consumer_id: str
    format: ExportFormat
    status: ExportStatus = ExportStatus.PENDING
    data_types: list[str] = field(default_factory=list)  # "usage", "billing", "webhooks", "logs"
    record_count: int = 0
    file_size_bytes: int = 0
    created_at: float = field(default_factory=time.time)
    completed_at: float = 0.0

VALID_DATA_TYPES = {"usage", "billing", "webhooks", "logs", "settings", "keys"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerDataExport:
    def __init__(self) -> None:
        self._jobs: dict[tuple[str, str], ExportJob] = {}

    def create_export(self, installation_id: str, job: ExportJob) -> ExportJob:
        if not installation_id: raise ValueError("installation_id is required")
        invalid = set(job.data_types) - VALID_DATA_TYPES
        if invalid: raise ValueError(f"Invalid data types: {invalid}")
        if not job.data_types: raise ValueError("At least one data type required")
        key = (installation_id, job.job_id)
        if key in self._jobs: raise ValueError(f"Job {job.job_id} exists")
        self._jobs[key] = job
        return job

    def complete_export(self, installation_id: str, job_id: str, record_count: int, file_size_bytes: int) -> ExportJob:
        job = self._get(installation_id, job_id)
        if job.status != ExportStatus.PENDING and job.status != ExportStatus.PROCESSING:
            raise ValueError(f"Job is {job.status.value}")
        job.status = ExportStatus.COMPLETED
        job.record_count = record_count
        job.file_size_bytes = file_size_bytes
        job.completed_at = time.time()
        return job

    def fail_export(self, installation_id: str, job_id: str) -> ExportJob:
        job = self._get(installation_id, job_id)
        job.status = ExportStatus.FAILED
        return job

    def list_exports(self, installation_id: str, consumer_id: str | None = None) -> list[ExportJob]:
        jobs = [j for (inst, _), j in self._jobs.items() if inst == installation_id]
        if consumer_id: jobs = [j for j in jobs if j.consumer_id == consumer_id]
        return jobs

    def _get(self, installation_id: str, job_id: str) -> ExportJob:
        j = self._jobs.get((installation_id, job_id))
        if j is None: raise KeyError(f"Job {job_id} not found")
        return j
