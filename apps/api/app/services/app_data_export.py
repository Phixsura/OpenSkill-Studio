"""App Data Export Manager — manage data export requests for installed apps.

Handles data export lifecycle:
- Request exports by type (json, csv, parquet)
- Track export status: pending → processing → completed → expired / failed
- Record file metadata (size, row count, download URL)
- Per-installation scoped exports
- Expiry-based cleanup
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"


class ExportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class ExportRequest:
    """A data export request."""

    export_id: str
    installation_id: str
    resource_type: str  # e.g. "users", "events", "analytics"
    format: ExportFormat
    status: ExportStatus = ExportStatus.PENDING
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    expires_at: float | None = None
    file_url: str | None = None
    file_size_bytes: int = 0
    row_count: int = 0
    error_message: str | None = None
    filters: dict = field(default_factory=dict)


class AppDataExportManager:
    """Manage data export requests for installed apps."""

    def __init__(self, expiry_hours: int = 24) -> None:
        self._exports: dict[tuple[str, str], ExportRequest] = {}
        self._expiry_seconds = expiry_hours * 3600

    def request_export(
        self,
        installation_id: str,
        export_id: str,
        resource_type: str,
        fmt: ExportFormat = ExportFormat.JSON,
        filters: dict | None = None,
    ) -> ExportRequest:
        """Create a new export request."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not export_id:
            raise ValueError("export_id is required")
        if not resource_type:
            raise ValueError("resource_type is required")

        key = (installation_id, export_id)
        if key in self._exports:
            raise ValueError(f"Export {export_id} already exists")

        export = ExportRequest(
            export_id=export_id,
            installation_id=installation_id,
            resource_type=resource_type,
            format=fmt,
            filters=filters or {},
        )
        self._exports[key] = export
        log.info("export.requested", export_id=export_id, resource_type=resource_type)
        return export

    def start_processing(self, installation_id: str, export_id: str) -> ExportRequest:
        """Mark export as processing."""
        export = self._get(installation_id, export_id)
        if export.status != ExportStatus.PENDING:
            raise ValueError(f"Cannot start export in {export.status} state")
        export.status = ExportStatus.PROCESSING
        return export

    def complete_export(
        self,
        installation_id: str,
        export_id: str,
        file_url: str,
        file_size_bytes: int = 0,
        row_count: int = 0,
    ) -> ExportRequest:
        """Mark export as completed with file metadata."""
        export = self._get(installation_id, export_id)
        if export.status != ExportStatus.PROCESSING:
            raise ValueError(f"Cannot complete export in {export.status} state")
        if not file_url:
            raise ValueError("file_url is required")

        export.status = ExportStatus.COMPLETED
        export.completed_at = time.time()
        export.expires_at = export.completed_at + self._expiry_seconds
        export.file_url = file_url
        export.file_size_bytes = max(0, file_size_bytes)
        export.row_count = max(0, row_count)
        log.info("export.completed", export_id=export_id, rows=row_count)
        return export

    def fail_export(
        self, installation_id: str, export_id: str, error: str = ""
    ) -> ExportRequest:
        """Mark export as failed."""
        export = self._get(installation_id, export_id)
        if export.status in (ExportStatus.COMPLETED, ExportStatus.EXPIRED):
            raise ValueError(f"Cannot fail export in {export.status} state")
        export.status = ExportStatus.FAILED
        export.error_message = error
        return export

    def get_export(self, installation_id: str, export_id: str) -> ExportRequest:
        return self._get(installation_id, export_id)

    def list_exports(
        self, installation_id: str, limit: int = 20
    ) -> list[ExportRequest]:
        """List exports for an installation, newest first."""
        exports = [
            e for (inst, _), e in self._exports.items()
            if inst == installation_id
        ]
        exports.sort(key=lambda e: e.created_at, reverse=True)
        return exports[:limit]

    def cleanup_expired(self, now: float | None = None) -> int:
        """Mark completed exports past expiry as expired. Returns count."""
        now = now or time.time()
        count = 0
        for export in self._exports.values():
            if (
                export.status == ExportStatus.COMPLETED
                and export.expires_at
                and now >= export.expires_at
            ):
                export.status = ExportStatus.EXPIRED
                export.file_url = None  # revoke download
                count += 1
        return count

    def _get(self, installation_id: str, export_id: str) -> ExportRequest:
        key = (installation_id, export_id)
        export = self._exports.get(key)
        if export is None:
            raise KeyError(f"Export {export_id} not found")
        return export
