"""App API Developer API Data Export Manager — schedule and track data exports."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ExportJob:
    job_id: str
    export_type: str  # "usage", "logs", "analytics", "billing"
    format: str  # "csv", "json", "parquet"
    status: str = "pending"  # "pending", "running", "completed", "failed"
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    row_count: int = 0
    file_size_bytes: int = 0

class AppAPIDeveloperAPIApiDataExportManager:
    def __init__(self) -> None:
        self._jobs: dict[tuple[str, str], ExportJob] = {}

    def create(self, installation_id: str, job_id: str, export_type: str, fmt: str) -> ExportJob:
        if not installation_id: raise ValueError("installation_id is required")
        if export_type not in ("usage", "logs", "analytics", "billing"): raise ValueError("invalid export_type")
        if fmt not in ("csv", "json", "parquet"): raise ValueError("invalid format")
        key = (installation_id, job_id)
        if key in self._jobs: raise ValueError(f"Job {job_id} exists")
        j = ExportJob(job_id=job_id, export_type=export_type, format=fmt)
        self._jobs[key] = j
        return j

    def start(self, installation_id: str, job_id: str) -> ExportJob:
        j = self._get(installation_id, job_id)
        j.status = "running"
        return j

    def complete(self, installation_id: str, job_id: str, row_count: int, file_size_bytes: int) -> ExportJob:
        j = self._get(installation_id, job_id)
        j.status = "completed"
        j.completed_at = time.time()
        j.row_count = row_count
        j.file_size_bytes = file_size_bytes
        return j

    def fail(self, installation_id: str, job_id: str) -> ExportJob:
        j = self._get(installation_id, job_id)
        j.status = "failed"
        return j

    def list_jobs(self, installation_id: str, status: str | None = None) -> list[ExportJob]:
        jobs = [j for (inst, _), j in self._jobs.items() if inst == installation_id]
        if status: jobs = [j for j in jobs if j.status == status]
        return jobs

    def _get(self, installation_id: str, job_id: str) -> ExportJob:
        key = (installation_id, job_id)
        j = self._jobs.get(key)
        if j is None: raise KeyError(f"Job {job_id} not found")
        return j
