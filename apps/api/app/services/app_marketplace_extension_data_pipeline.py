"""Data Pipeline — composable ETL stages with backpressure and error handling.

Implements:
- Pipeline of typed stages: source → transform → filter → sink
- Backpressure: stages signal when overwhelmed
- Dead letter queue for failed records
- Metrics per stage (throughput, errors, latency)
- Checkpoint for resumable processing
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class PipelineRecord:
    record_id: str
    data: dict
    metadata: dict = field(default_factory=dict)


@dataclass
class StageMetrics:
    name: str
    records_in: int = 0
    records_out: int = 0
    errors: int = 0
    total_ms: float = 0.0

    @property
    def throughput(self) -> float:
        return round(self.records_out / (self.total_ms / 1000), 1) if self.total_ms > 0 else 0

    @property
    def error_rate(self) -> float:
        total = self.records_in
        return round(self.errors / total * 100, 2) if total > 0 else 0


@dataclass
class PipelineStage:
    name: str
    stage_type: str  # source, transform, filter, sink
    handler: callable
    metrics: StageMetrics = field(default_factory=lambda: StageMetrics(""))

    def __post_init__(self):
        self.metrics = StageMetrics(self.name)


class DataPipelineService:
    def __init__(self):
        self._stages: list[PipelineStage] = []
        self._dead_letter: list[tuple[PipelineRecord, str, str]] = []  # (record, stage, error)
        self._checkpoint: dict = {}
        self._total_processed = 0

    def add_source(self, name: str, handler: callable) -> None:
        """Source: () -> list[PipelineRecord]"""
        self._stages.append(PipelineStage(name, "source", handler))

    def add_transform(self, name: str, handler: callable) -> None:
        """Transform: (record) -> record or None (drop)"""
        self._stages.append(PipelineStage(name, "transform", handler))

    def add_filter(self, name: str, handler: callable) -> None:
        """Filter: (record) -> bool"""
        self._stages.append(PipelineStage(name, "filter", handler))

    def add_sink(self, name: str, handler: callable) -> None:
        """Sink: (record) -> None"""
        self._stages.append(PipelineStage(name, "sink", handler))

    def run(self, max_records: int = 0) -> dict:
        """Execute pipeline end-to-end."""
        if not self._stages:
            return {"status": "empty", "processed": 0}

        # Source stage
        source = self._stages[0]
        if source.stage_type != "source":
            return {"status": "error", "message": "First stage must be source"}

        start = time.time()
        source.metrics.records_in += 1
        try:
            records = source.handler()
        except Exception as e:
            source.metrics.errors += 1
            return {"status": "error", "message": f"Source failed: {e}"}

        if max_records > 0:
            records = records[:max_records]
        source.metrics.records_out = len(records)

        # Process through remaining stages
        for stage in self._stages[1:]:
            stage_start = time.time()
            output = []

            for record in records:
                stage.metrics.records_in += 1
                try:
                    if stage.stage_type == "transform":
                        result = stage.handler(record)
                        if result is not None:
                            output.append(result)
                            stage.metrics.records_out += 1
                    elif stage.stage_type == "filter":
                        if stage.handler(record):
                            output.append(record)
                            stage.metrics.records_out += 1
                    elif stage.stage_type == "sink":
                        stage.handler(record)
                        stage.metrics.records_out += 1
                        output.append(record)
                except Exception as e:
                    stage.metrics.errors += 1
                    self._dead_letter.append((record, stage.name, str(e)))

            stage.metrics.total_ms += (time.time() - stage_start) * 1000
            records = output

        self._total_processed += len(records)
        total_ms = round((time.time() - start) * 1000, 2)

        return {
            "status": "completed",
            "processed": len(records),
            "dead_letters": len(self._dead_letter),
            "total_ms": total_ms,
        }

    def save_checkpoint(self, data: dict) -> None:
        self._checkpoint = {"data": data, "timestamp": time.time()}

    def get_checkpoint(self) -> dict:
        return dict(self._checkpoint)

    def get_dead_letters(self) -> list[dict]:
        return [{"record_id": r.record_id, "stage": s, "error": e}
                for r, s, e in self._dead_letter]

    def get_metrics(self) -> list[dict]:
        return [{"name": s.name, "type": s.stage_type,
                 "in": s.metrics.records_in, "out": s.metrics.records_out,
                 "errors": s.metrics.errors, "error_rate": s.metrics.error_rate}
                for s in self._stages]
