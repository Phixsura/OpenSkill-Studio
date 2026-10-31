"""API Batch Request Processor — process multiple API requests in a single call."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class BatchItem:
    item_id: str
    method: str
    path: str
    body: str = ""

@dataclass
class BatchResult:
    item_id: str
    status_code: int
    body: str = ""
    duration_ms: float = 0.0
    error: str = ""

@dataclass
class BatchResponse:
    batch_id: str
    results: list[BatchResult] = field(default_factory=list)
    total_duration_ms: float = 0.0
    success_count: int = 0
    error_count: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiBatchRequestProcessor:
    def __init__(self, max_batch_size: int = 50, max_body_size: int = 4096) -> None:
        self._max_batch = max(1, max_batch_size)
        self._max_body = max(256, max_body_size)
        self._history: dict[tuple[str, str], BatchResponse] = {}

    def process(self, installation_id: str, batch_id: str, items: list[BatchItem], handler: callable | None = None) -> BatchResponse:
        if not installation_id: raise ValueError("installation_id is required")
        if not items: raise ValueError("Batch must contain at least one item")
        if len(items) > self._max_batch: raise ValueError(f"Batch size {len(items)} exceeds max {self._max_batch}")
        for item in items:
            if len(item.body) > self._max_body:
                item.body = item.body[:self._max_body] + "...[TRUNCATED]"
        results: list[BatchResult] = []
        start = time.time()
        for item in items:
            if handler:
                try:
                    r = handler(item)
                    results.append(r)
                except Exception as e:
                    results.append(BatchResult(item_id=item.item_id, status_code=500, error=str(e)))
            else:
                results.append(BatchResult(item_id=item.item_id, status_code=200, body='{"ok":true}'))
        total_ms = round((time.time() - start) * 1000, 2)
        success = sum(1 for r in results if 200 <= r.status_code < 400)
        resp = BatchResponse(batch_id=batch_id, results=results, total_duration_ms=total_ms, success_count=success, error_count=len(results) - success)
        self._history[(installation_id, batch_id)] = resp
        return resp

    def get_batch(self, installation_id: str, batch_id: str) -> BatchResponse:
        r = self._history.get((installation_id, batch_id))
        if r is None: raise KeyError(f"Batch {batch_id} not found")
        return r

    def batch_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._history if inst == installation_id)
