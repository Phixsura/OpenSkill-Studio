"""Consumer API Log Export — export API logs in structured formats."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import csv
import io
import structlog

log = structlog.get_logger()

@dataclass
class LogEntry:
    log_id: str
    consumer_id: str
    method: str
    path: str
    status_code: int
    latency_ms: float
    timestamp: datetime

@dataclass
class ExportJob:
    job_id: str
    consumer_id: str
    format: str  # "json", "csv", "ndjson"
    start_time: datetime
    end_time: datetime
    status: str = "pending"
    record_count: int = 0
    content: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiLogExport:
    def __init__(self) -> None:
        self._logs: dict[tuple[str, str], list[LogEntry]] = {}
        self._jobs: dict[tuple[str, str], ExportJob] = {}

    def append_log(self, installation_id: str, entry: LogEntry) -> LogEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, entry.consumer_id)
        if key not in self._logs:
            self._logs[key] = []
        self._logs[key].append(entry)
        return entry

    def export(self, installation_id: str, job: ExportJob) -> ExportJob:
        if job.format not in ("json", "csv", "ndjson"):
            raise ValueError(f"Unsupported format: {job.format}")
        logs = self._logs.get((installation_id, job.consumer_id), [])
        filtered = [l for l in logs if job.start_time <= l.timestamp <= job.end_time]
        records = [{"log_id": l.log_id, "method": l.method, "path": l.path, "status": l.status_code, "latency_ms": l.latency_ms, "timestamp": l.timestamp.isoformat()} for l in filtered]
        if job.format == "json":
            job.content = json.dumps(records)
        elif job.format == "ndjson":
            job.content = "\n".join(json.dumps(r) for r in records)
        elif job.format == "csv":
            if records:
                buf = io.StringIO()
                writer = csv.DictWriter(buf, fieldnames=records[0].keys())
                writer.writeheader()
                writer.writerows(records)
                job.content = buf.getvalue()
            else:
                job.content = ""
        job.record_count = len(records)
        job.status = "completed"
        self._jobs[(installation_id, job.job_id)] = job
        return job

    def get_job(self, installation_id: str, job_id: str) -> ExportJob | None:
        return self._jobs.get((installation_id, job_id))
