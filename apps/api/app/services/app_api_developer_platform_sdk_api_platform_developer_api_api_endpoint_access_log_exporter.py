"""API Endpoint Access Log Exporter — export access logs in structured formats."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import time
import structlog

log = structlog.get_logger()

@dataclass
class AccessLogEntry:
    timestamp: float
    method: str
    path: str
    status_code: int
    duration_ms: float
    consumer_id: str = ""
    ip_address: str = ""
    bytes_sent: int = 0

@dataclass
class ExportConfig:
    format: str = "json"  # "json", "csv"
    include_ip: bool = False  # PII consideration
    max_entries: int = 10000

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointAccessLogExporter:
    def __init__(self) -> None:
        self._logs: dict[str, list[AccessLogEntry]] = {}

    def record(self, installation_id: str, entry: AccessLogEntry) -> None:
        if not installation_id: raise ValueError("installation_id is required")
        self._logs.setdefault(installation_id, []).append(entry)

    def export_json(self, installation_id: str, config: ExportConfig | None = None) -> str:
        cfg = config or ExportConfig()
        entries = self._logs.get(installation_id, [])[-cfg.max_entries:]
        data = []
        for e in entries:
            row: dict[str, object] = {"timestamp": e.timestamp, "method": e.method, "path": e.path, "status": e.status_code, "duration_ms": e.duration_ms, "consumer_id": e.consumer_id, "bytes": e.bytes_sent}
            if cfg.include_ip: row["ip"] = e.ip_address
            data.append(row)
        return json.dumps(data)

    def export_csv_header(self, config: ExportConfig | None = None) -> str:
        cfg = config or ExportConfig()
        cols = ["timestamp", "method", "path", "status", "duration_ms", "consumer_id", "bytes"]
        if cfg.include_ip: cols.append("ip")
        return ",".join(cols)

    def entry_count(self, installation_id: str) -> int:
        return len(self._logs.get(installation_id, []))

    def by_status_range(self, installation_id: str) -> dict[str, int]:
        entries = self._logs.get(installation_id, [])
        ranges = {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0}
        for e in entries:
            if 200 <= e.status_code < 300: ranges["2xx"] += 1
            elif 300 <= e.status_code < 400: ranges["3xx"] += 1
            elif 400 <= e.status_code < 500: ranges["4xx"] += 1
            elif e.status_code >= 500: ranges["5xx"] += 1
        return ranges
