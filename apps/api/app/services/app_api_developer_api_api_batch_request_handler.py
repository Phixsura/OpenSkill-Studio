"""App API Developer API Batch Request Handler — process multiple API calls in one request."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class BatchItem:
    request_id: str
    method: str
    path: str
    status_code: int = 0
    success: bool = False

@dataclass
class BatchResult:
    batch_id: str
    items: list[BatchItem] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.items)

    @property
    def succeeded(self) -> int:
        return sum(1 for i in self.items if i.success)

    @property
    def failed(self) -> int:
        return self.total - self.succeeded

class AppAPIDeveloperAPIApiBatchRequestHandler:
    def __init__(self, max_batch_size: int = 50) -> None:
        self._max = max(1, max_batch_size)
        self._results: dict[tuple[str, str], BatchResult] = {}

    def execute(self, installation_id: str, batch_id: str, requests: list[dict]) -> BatchResult:
        if not installation_id: raise ValueError("installation_id is required")
        if len(requests) > self._max: raise ValueError(f"Batch exceeds max size {self._max}")
        if not requests: raise ValueError("Batch must have at least one request")
        items = []
        for r in requests:
            success = 200 <= r.get("status_code", 200) < 400
            items.append(BatchItem(request_id=r["request_id"], method=r.get("method", "GET").upper(), path=r.get("path", "/"), status_code=r.get("status_code", 200), success=success))
        result = BatchResult(batch_id=batch_id, items=items)
        self._results[(installation_id, batch_id)] = result
        return result

    def get_result(self, installation_id: str, batch_id: str) -> BatchResult:
        key = (installation_id, batch_id)
        r = self._results.get(key)
        if r is None: raise KeyError(f"Batch {batch_id} not found")
        return r

    def recent_batches(self, installation_id: str, limit: int = 10) -> list[BatchResult]:
        batches = [r for (inst, _), r in self._results.items() if inst == installation_id]
        return batches[-limit:]

    def avg_batch_size(self, installation_id: str) -> float:
        batches = [r for (inst, _), r in self._results.items() if inst == installation_id]
        return round(sum(r.total for r in batches) / len(batches), 1) if batches else 0.0
