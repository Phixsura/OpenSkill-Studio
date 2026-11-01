"""Data Export Manager — export platform data in multiple formats."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import time


@dataclass
class ExportJob:
    job_id: str
    user_id: str
    format: str  # json, csv, yaml
    resource: str  # extensions, analytics, reviews, users
    status: str = "pending"  # pending, processing, completed, failed
    result: str = ""
    created_at: float = 0.0
    completed_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class DataExportMgrService:
    VALID_FORMATS = {"json", "csv", "yaml"}
    VALID_RESOURCES = {"extensions", "analytics", "reviews", "users", "connectors"}

    def __init__(self):
        self._jobs: dict[str, ExportJob] = {}
        self._counter = 0

    def create_export(self, user_id: str, resource: str, fmt: str = "json") -> ExportJob:
        if fmt not in self.VALID_FORMATS:
            raise ValueError(f"Invalid format: {fmt}")
        if resource not in self.VALID_RESOURCES:
            raise ValueError(f"Invalid resource: {resource}")
        self._counter += 1
        job = ExportJob(job_id=f"exp-{self._counter}", user_id=user_id,
                        format=fmt, resource=resource)
        self._jobs[job.job_id] = job
        return job

    def process(self, job_id: str, data: list[dict]) -> bool:
        job = self._jobs.get(job_id)
        if not job or job.status != "pending":
            return False
        job.status = "processing"
        if job.format == "json":
            job.result = json.dumps(data, indent=2)
        elif job.format == "csv":
            if data:
                headers = list(data[0].keys())
                lines = [",".join(headers)]
                for row in data:
                    lines.append(",".join(str(row.get(h, "")) for h in headers))
                job.result = "\n".join(lines)
            else:
                job.result = ""
        job.status = "completed"
        job.completed_at = time.time()
        return True

    def get_job(self, job_id: str) -> ExportJob | None:
        return self._jobs.get(job_id)

    def get_user_exports(self, user_id: str) -> list[ExportJob]:
        return [j for j in self._jobs.values() if j.user_id == user_id]
