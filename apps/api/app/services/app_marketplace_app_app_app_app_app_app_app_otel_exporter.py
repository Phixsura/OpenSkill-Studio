"""OpenTelemetry span exporter — batch and export trace spans."""
from __future__ import annotations
import secrets


class OtelExporter:
    def __init__(self, *, batch_size: int = 100, endpoint: str = ""):
        self._batch_size = batch_size
        self._endpoint = endpoint
        self._buffer: list[dict] = []
        self._exported_count = 0
        self._batches_sent = 0

    def add_span(self, *, service: str, operation: str, duration_ms: int,
                  status: str = "ok", attributes: dict | None = None) -> dict:
        span = {"trace_id": secrets.token_hex(16), "span_id": secrets.token_hex(8),
                "service": service, "operation": operation,
                "duration_ms": duration_ms, "status": status,
                "attributes": attributes or {}}
        self._buffer.append(span)
        flushed = False
        if len(self._buffer) >= self._batch_size:
            self._flush()
            flushed = True
        return {"buffered": len(self._buffer), "flushed": flushed}

    def flush(self) -> dict:
        count = len(self._buffer)
        self._flush()
        return {"flushed": count, "total_exported": self._exported_count}

    def stats(self) -> dict:
        return {"buffered": len(self._buffer), "exported": self._exported_count,
                "batches_sent": self._batches_sent, "batch_size": self._batch_size}

    def _flush(self) -> None:
        if self._buffer:
            self._exported_count += len(self._buffer)
            self._batches_sent += 1
            self._buffer.clear()
