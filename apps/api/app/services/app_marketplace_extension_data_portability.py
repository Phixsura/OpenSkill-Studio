"""Data Portability — export and import extension data for migration and backup.

Supports selective export by data type, format conversion (JSON/CSV),
data validation on import, and conflict resolution strategies.
"""
from __future__ import annotations
import json
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"


class ConflictStrategy(str, Enum):
    SKIP = "skip"
    OVERWRITE = "overwrite"
    RENAME = "rename"


class ImportStatus(str, Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    IMPORTING = "importing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ExportJob:
    job_id: str
    extension_id: str
    data_types: list[str]
    format: ExportFormat
    status: str = "completed"
    record_count: int = 0
    data: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class ImportJob:
    job_id: str
    extension_id: str
    status: ImportStatus = ImportStatus.PENDING
    conflict_strategy: ConflictStrategy = ConflictStrategy.SKIP
    total_records: int = 0
    imported: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


ALLOWED_DATA_TYPES = {"settings", "users", "content", "analytics", "webhooks", "workflows"}


class DataPortabilityService:
    """Manages extension data export and import with validation."""

    def __init__(self):
        self._exports: dict[str, ExportJob] = {}
        self._imports: dict[str, ImportJob] = {}
        self._extension_data: dict[str, dict[str, list[dict]]] = {}

    def store_data(self, extension_id: str, data_type: str, records: list[dict]) -> None:
        if data_type not in ALLOWED_DATA_TYPES:
            raise ValueError(f"Invalid data type: {data_type}")
        self._extension_data.setdefault(extension_id, {})
        self._extension_data[extension_id][data_type] = records

    def export_data(self, extension_id: str, data_types: list[str],
                    fmt: ExportFormat = ExportFormat.JSON) -> ExportJob:
        for dt in data_types:
            if dt not in ALLOWED_DATA_TYPES:
                raise ValueError(f"Invalid data type: {dt}")

        ext_data = self._extension_data.get(extension_id, {})
        export_records: dict[str, list[dict]] = {}
        count = 0
        for dt in data_types:
            records = ext_data.get(dt, [])
            export_records[dt] = records
            count += len(records)

        job_id = f"exp_{secrets.token_urlsafe(12)}"
        job = ExportJob(
            job_id=job_id, extension_id=extension_id,
            data_types=data_types, format=fmt,
            record_count=count, data=json.dumps(export_records),
        )
        self._exports[job_id] = job
        return job

    def validate_import(self, data: str) -> tuple[bool, list[str]]:
        errors = []
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            return False, ["Invalid JSON"]
        if not isinstance(parsed, dict):
            return False, ["Root must be an object"]
        for key in parsed:
            if key not in ALLOWED_DATA_TYPES:
                errors.append(f"Unknown data type: {key}")
            elif not isinstance(parsed[key], list):
                errors.append(f"{key} must be an array")
        return len(errors) == 0, errors

    def import_data(self, extension_id: str, data: str,
                    conflict_strategy: ConflictStrategy = ConflictStrategy.SKIP) -> ImportJob:
        job_id = f"imp_{secrets.token_urlsafe(12)}"
        job = ImportJob(
            job_id=job_id, extension_id=extension_id,
            conflict_strategy=conflict_strategy,
        )
        valid, errors = self.validate_import(data)
        if not valid:
            job.status = ImportStatus.FAILED
            job.errors = errors
            self._imports[job_id] = job
            return job

        job.status = ImportStatus.IMPORTING
        parsed = json.loads(data)
        ext_data = self._extension_data.setdefault(extension_id, {})

        for dtype, records in parsed.items():
            if dtype not in ALLOWED_DATA_TYPES:
                continue
            existing = ext_data.get(dtype, [])
            existing_ids = {r.get("id") for r in existing if "id" in r}

            for record in records:
                job.total_records += 1
                rid = record.get("id")
                if rid and rid in existing_ids:
                    if conflict_strategy == ConflictStrategy.SKIP:
                        job.skipped += 1
                        continue
                    elif conflict_strategy == ConflictStrategy.OVERWRITE:
                        existing = [r for r in existing if r.get("id") != rid]
                        existing.append(record)
                        job.imported += 1
                    elif conflict_strategy == ConflictStrategy.RENAME:
                        record = {**record, "id": f"{rid}_imported"}
                        existing.append(record)
                        job.imported += 1
                else:
                    existing.append(record)
                    job.imported += 1
            ext_data[dtype] = existing

        job.status = ImportStatus.COMPLETED
        self._imports[job_id] = job
        return job
