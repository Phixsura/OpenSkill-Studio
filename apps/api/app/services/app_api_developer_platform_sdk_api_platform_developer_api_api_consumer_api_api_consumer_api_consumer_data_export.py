"""Consumer Data Export — export consumer data in various formats."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import json
import csv
import io
import structlog

log = structlog.get_logger()

@dataclass
class ExportRequest:
    export_id: str
    consumer_id: str
    format: str = "json"  # "json", "csv", "ndjson"
    filters: dict[str, str] = field(default_factory=dict)
    created_at: datetime | None = None
    status: str = "pending"  # "pending", "processing", "completed", "failed"

@dataclass
class ExportResult:
    export_id: str
    format: str
    content: str
    record_count: int
    size_bytes: int

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerDataExport:
    def __init__(self) -> None:
        self._requests: dict[tuple[str, str], ExportRequest] = {}

    def create_export(self, installation_id: str, req: ExportRequest) -> ExportRequest:
        if not installation_id:
            raise ValueError("installation_id is required")
        if req.format not in ("json", "csv", "ndjson"):
            raise ValueError(f"Unsupported format: {req.format}")
        req.created_at = req.created_at or datetime.utcnow()
        req.status = "pending"
        self._requests[(installation_id, req.export_id)] = req
        log.info("export_created", installation_id=installation_id, export_id=req.export_id, fmt=req.format)
        return req

    def execute(self, installation_id: str, export_id: str, records: list[dict]) -> ExportResult:
        key = (installation_id, export_id)
        req = self._requests.get(key)
        if not req:
            raise ValueError("Export not found")
        req.status = "processing"
        # Apply filters
        filtered = records
        for fk, fv in req.filters.items():
            filtered = [r for r in filtered if str(r.get(fk, "")) == fv]
        # Format
        if req.format == "json":
            content = json.dumps(filtered, default=str)
        elif req.format == "ndjson":
            content = "\n".join(json.dumps(r, default=str) for r in filtered)
        elif req.format == "csv":
            if not filtered:
                content = ""
            else:
                buf = io.StringIO()
                writer = csv.DictWriter(buf, fieldnames=filtered[0].keys())
                writer.writeheader()
                writer.writerows(filtered)
                content = buf.getvalue()
        else:
            content = ""
        req.status = "completed"
        return ExportResult(export_id=export_id, format=req.format, content=content, record_count=len(filtered), size_bytes=len(content.encode()))

    def get_status(self, installation_id: str, export_id: str) -> ExportRequest | None:
        return self._requests.get((installation_id, export_id))

    def list_exports(self, installation_id: str, consumer_id: str | None = None) -> list[ExportRequest]:
        return [r for (inst, _), r in self._requests.items() if inst == installation_id and (consumer_id is None or r.consumer_id == consumer_id)]
