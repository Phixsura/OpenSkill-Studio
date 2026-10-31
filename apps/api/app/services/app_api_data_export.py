"""App API Data Export — export data in various formats.

Manages data exports:
- Create export jobs with format selection
- Track export status and file size
- Per-installation scoped exports
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class ExportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DataExport:
    """A data export job."""

    export_id: str
    format: str  # "json", "csv", "parquet"
    resource: str
    status: ExportStatus = ExportStatus.PENDING
    file_size_bytes: int = 0
    record_count: int = 0
    created_at: float = field(default_factory=time.time)


VALID_FORMATS = {"json", "csv", "parquet"}


class AppAPIDataExport:
    """Export data in various formats."""

    def __init__(self) -> None:
        self._exports: dict[tuple[str, str], DataExport] = {}

    def create(
        self, installation_id: str, export_id: str, format: str, resource: str,
    ) -> DataExport:
        if not installation_id:
            raise ValueError("installation_id is required")
        if format not in VALID_FORMATS:
            raise ValueError(f"format must be one of {VALID_FORMATS}")

        export = DataExport(export_id=export_id, format=format, resource=resource)
        self._exports[(installation_id, export_id)] = export
        return export

    def complete(
        self, installation_id: str, export_id: str,
        file_size_bytes: int, record_count: int,
    ) -> DataExport:
        e = self._get(installation_id, export_id)
        e.status = ExportStatus.COMPLETED
        e.file_size_bytes = file_size_bytes
        e.record_count = record_count
        return e

    def fail(self, installation_id: str, export_id: str) -> DataExport:
        e = self._get(installation_id, export_id)
        e.status = ExportStatus.FAILED
        return e

    def list_exports(self, installation_id: str) -> list[DataExport]:
        return [e for (inst, _), e in self._exports.items() if inst == installation_id]

    def _get(self, installation_id: str, export_id: str) -> DataExport:
        key = (installation_id, export_id)
        e = self._exports.get(key)
        if e is None:
            raise KeyError(f"Export {export_id} not found")
        return e
