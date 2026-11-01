"""Telemetry Pipeline — collect, process, and export extension telemetry.

Ingests metrics, traces, and logs into a unified pipeline with
sampling, aggregation windows, export targets, and data retention.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class TelemetryType(str, Enum):
    METRIC = "metric"
    TRACE = "trace"
    LOG = "log"
    EVENT = "event"


class ExportTarget(str, Enum):
    PROMETHEUS = "prometheus"
    DATADOG = "datadog"
    CUSTOM_WEBHOOK = "custom_webhook"
    STDOUT = "stdout"


@dataclass
class TelemetryRecord:
    record_id: str
    extension_id: str
    telemetry_type: TelemetryType
    name: str
    value: float = 0.0
    tags: dict[str, str] = field(default_factory=dict)
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class PipelineConfig:
    extension_id: str
    sampling_rate: float = 1.0  # 0.0-1.0
    export_targets: list[ExportTarget] = field(default_factory=list)
    retention_hours: int = 72
    aggregation_window_seconds: int = 60


class TelemetryPipelineService:
    """Manages telemetry ingestion with sampling and export."""

    def __init__(self):
        self._configs: dict[str, PipelineConfig] = {}
        self._records: list[TelemetryRecord] = []
        self._exported: dict[str, int] = defaultdict(int)  # target -> count
        self._dropped: int = 0

    def configure(self, extension_id: str, sampling_rate: float = 1.0,
                  export_targets: list[ExportTarget] | None = None,
                  retention_hours: int = 72) -> PipelineConfig:
        if not 0.0 <= sampling_rate <= 1.0:
            raise ValueError("Sampling rate must be 0.0-1.0")
        config = PipelineConfig(
            extension_id=extension_id, sampling_rate=sampling_rate,
            export_targets=export_targets or [ExportTarget.STDOUT],
            retention_hours=retention_hours,
        )
        self._configs[extension_id] = config
        return config

    def ingest(self, extension_id: str, telemetry_type: TelemetryType,
               name: str, value: float = 0.0,
               tags: dict[str, str] | None = None) -> TelemetryRecord | None:
        config = self._configs.get(extension_id)
        if not config:
            return None

        # Sampling
        import random
        if random.random() > config.sampling_rate:
            self._dropped += 1
            return None

        record = TelemetryRecord(
            record_id=f"tel_{secrets.token_urlsafe(8)}",
            extension_id=extension_id, telemetry_type=telemetry_type,
            name=name, value=value, tags=tags or {},
        )
        self._records.append(record)

        # Export
        for target in config.export_targets:
            self._exported[target.value] += 1

        return record

    def query(self, extension_id: str, telemetry_type: TelemetryType | None = None,
              name: str | None = None, limit: int = 100) -> list[TelemetryRecord]:
        results = [r for r in self._records if r.extension_id == extension_id]
        if telemetry_type:
            results = [r for r in results if r.telemetry_type == telemetry_type]
        if name:
            results = [r for r in results if r.name == name]
        return results[-limit:]

    def aggregate(self, extension_id: str, name: str) -> dict:
        records = [r for r in self._records
                   if r.extension_id == extension_id and r.name == name]
        if not records:
            return {"count": 0, "sum": 0, "avg": 0, "min": 0, "max": 0}
        values = [r.value for r in records]
        return {
            "count": len(values),
            "sum": round(sum(values), 3),
            "avg": round(sum(values) / len(values), 3),
            "min": min(values),
            "max": max(values),
        }

    def get_stats(self) -> dict:
        return {
            "total_records": len(self._records),
            "dropped_by_sampling": self._dropped,
            "exported": dict(self._exported),
            "configured_extensions": len(self._configs),
        }

    def flush(self, extension_id: str) -> int:
        before = len(self._records)
        self._records = [r for r in self._records if r.extension_id != extension_id]
        return before - len(self._records)
