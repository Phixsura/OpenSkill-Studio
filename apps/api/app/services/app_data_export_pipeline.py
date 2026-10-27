"""App Data Export Pipeline — structured data export for installed apps with privacy controls.

Provides GDPR-compliant data export for the developer platform:
- Export job lifecycle: request → processing → ready → downloaded → expired
- Field-level PII redaction (email, name, IP → masked)
- Format support: JSON, CSV
- Row-count and byte-size limits
- Export expiry with auto-cleanup
- Audit trail per export
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

import structlog

log = structlog.get_logger()


class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"


class ExportStatus(str, Enum):
    REQUESTED = "requested"
    PROCESSING = "processing"
    READY = "ready"
    DOWNLOADED = "downloaded"
    EXPIRED = "expired"
    FAILED = "failed"


class PIIField(str, Enum):
    EMAIL = "email"
    NAME = "name"
    IP_ADDRESS = "ip_address"
    PHONE = "phone"


PII_MASKS = {
    PIIField.EMAIL: lambda v: v.split("@")[0][:2] + "***@" + v.split("@")[-1] if "@" in str(v) else "***",
    PIIField.NAME: lambda v: str(v)[:1] + "***" if v else "***",
    PIIField.IP_ADDRESS: lambda _: "xxx.xxx.xxx.xxx",
    PIIField.PHONE: lambda v: "***" + str(v)[-4:] if len(str(v)) >= 4 else "***",
}

MAX_ROWS = 100_000
MAX_BYTES = 50 * 1024 * 1024  # 50MB
DEFAULT_EXPIRY_HOURS = 24


@dataclass
class ExportJob:
    """An export job with lifecycle tracking."""

    job_id: str
    installation_id: str
    requested_by: str
    export_format: ExportFormat
    status: ExportStatus = ExportStatus.REQUESTED
    pii_fields: list[PIIField] = field(default_factory=list)  # fields to redact
    row_count: int = 0
    byte_size: int = 0
    output: str | None = None           # rendered output
    error: str | None = None
    requested_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    expires_at: datetime | None = None
    downloaded_at: datetime | None = None


@dataclass
class ExportResult:
    """Result of creating or fetching an export."""

    success: bool
    job_id: str | None = None
    error: str | None = None


class AppDataExportPipeline:
    """Manage data export jobs with PII redaction."""

    def __init__(self):
        self._jobs: dict[str, ExportJob] = {}
        self._next_id = 0

    def request_export(self, installation_id: str, requested_by: str,
                       export_format: ExportFormat = ExportFormat.JSON,
                       pii_fields: list[PIIField] | None = None) -> ExportResult:
        """Create a new export job."""
        self._next_id += 1
        job_id = f"export-{self._next_id}"
        job = ExportJob(
            job_id=job_id,
            installation_id=installation_id,
            requested_by=requested_by,
            export_format=export_format,
            pii_fields=pii_fields or [],
        )
        self._jobs[job_id] = job
        log.info("export.requested", job_id=job_id, installation_id=installation_id)
        return ExportResult(success=True, job_id=job_id)

    def process_export(self, job_id: str, rows: list[dict]) -> ExportResult:
        """Process an export job with the provided data rows."""
        job = self._jobs.get(job_id)
        if job is None:
            return ExportResult(success=False, error="Job not found")
        if job.status != ExportStatus.REQUESTED:
            return ExportResult(success=False, error=f"Job in wrong status: {job.status.value}")

        job.status = ExportStatus.PROCESSING

        # Row limit
        if len(rows) > MAX_ROWS:
            job.status = ExportStatus.FAILED
            job.error = f"Row count {len(rows)} exceeds limit {MAX_ROWS}"
            return ExportResult(success=False, error=job.error)

        # Redact PII
        redacted = [self._redact_row(row, job.pii_fields) for row in rows]

        # Render output
        try:
            if job.export_format == ExportFormat.JSON:
                output = json.dumps(redacted, indent=2, default=str)
            elif job.export_format == ExportFormat.CSV:
                output = self._render_csv(redacted)
            else:
                output = json.dumps(redacted, default=str)
        except Exception as e:
            job.status = ExportStatus.FAILED
            job.error = f"Render error: {e}"
            return ExportResult(success=False, error=job.error)

        # Size limit
        byte_size = len(output.encode("utf-8"))
        if byte_size > MAX_BYTES:
            job.status = ExportStatus.FAILED
            job.error = f"Output size {byte_size} bytes exceeds limit {MAX_BYTES}"
            return ExportResult(success=False, error=job.error)

        job.output = output
        job.row_count = len(redacted)
        job.byte_size = byte_size
        job.status = ExportStatus.READY
        job.completed_at = datetime.now(UTC)
        job.expires_at = datetime.now(UTC) + timedelta(hours=DEFAULT_EXPIRY_HOURS)

        log.info("export.ready", job_id=job_id, rows=job.row_count, bytes=job.byte_size)
        return ExportResult(success=True, job_id=job_id)

    def download(self, job_id: str, user_id: str) -> tuple[str | None, str | None]:
        """Download an export. Returns (output, error)."""
        job = self._jobs.get(job_id)
        if job is None:
            return None, "Job not found"
        if job.requested_by != user_id:
            return None, "Access denied"
        if job.status == ExportStatus.EXPIRED:
            return None, "Export has expired"
        if job.expires_at and datetime.now(UTC) >= job.expires_at:
            job.status = ExportStatus.EXPIRED
            return None, "Export has expired"
        if job.status != ExportStatus.READY and job.status != ExportStatus.DOWNLOADED:
            return None, f"Export not ready (status: {job.status.value})"

        job.status = ExportStatus.DOWNLOADED
        job.downloaded_at = datetime.now(UTC)
        return job.output, None

    def cleanup_expired(self) -> int:
        """Remove expired export data."""
        now = datetime.now(UTC)
        count = 0
        for job in self._jobs.values():
            if job.expires_at and now >= job.expires_at and job.status != ExportStatus.EXPIRED:
                job.status = ExportStatus.EXPIRED
                job.output = None  # free memory
                count += 1
        return count

    def get_job(self, job_id: str) -> ExportJob | None:
        return self._jobs.get(job_id)

    def list_jobs(self, installation_id: str) -> list[ExportJob]:
        return sorted(
            [j for j in self._jobs.values() if j.installation_id == installation_id],
            key=lambda j: j.requested_at, reverse=True,
        )

    # ── Internal ─────────────────────────────────────────

    @staticmethod
    def _redact_row(row: dict, pii_fields: list[PIIField]) -> dict:
        result = dict(row)
        for pii in pii_fields:
            field_name = pii.value
            if field_name in result and result[field_name]:
                mask_fn = PII_MASKS.get(pii)
                if mask_fn:
                    result[field_name] = mask_fn(result[field_name])
        return result

    @staticmethod
    def _render_csv(rows: list[dict]) -> str:
        if not rows:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()
