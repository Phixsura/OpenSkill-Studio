"""Consumer API Batch Request — process multiple API requests in a single call."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class BatchItem:
    item_id: str
    method: str
    path: str
    body: dict | None = None
    headers: dict[str, str] = field(default_factory=dict)

@dataclass
class BatchItemResult:
    item_id: str
    status_code: int
    body: dict = field(default_factory=dict)
    error: str | None = None

@dataclass
class BatchResult:
    total: int
    succeeded: int
    failed: int
    results: list[BatchItemResult] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiBatchRequest:
    def __init__(self, max_batch_size: int = 50) -> None:
        self._max = max_batch_size
        self._stats: dict[tuple[str, str], dict[str, int]] = {}

    def execute(self, installation_id: str, consumer_id: str, items: list[BatchItem]) -> BatchResult:
        if not installation_id:
            raise ValueError("installation_id is required")
        if len(items) == 0:
            raise ValueError("Batch must contain at least one item")
        if len(items) > self._max:
            raise ValueError(f"Batch size {len(items)} exceeds max {self._max}")
        # Check for duplicate IDs
        ids = [i.item_id for i in items]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate item_id in batch")
        results: list[BatchItemResult] = []
        succeeded = 0
        failed = 0
        for item in items:
            if item.method.upper() not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                results.append(BatchItemResult(item_id=item.item_id, status_code=400, error=f"Invalid method: {item.method}"))
                failed += 1
            elif not item.path.startswith("/"):
                results.append(BatchItemResult(item_id=item.item_id, status_code=400, error="Path must start with /"))
                failed += 1
            else:
                results.append(BatchItemResult(item_id=item.item_id, status_code=200, body={"message": "ok", "method": item.method, "path": item.path}))
                succeeded += 1
        # Track stats
        key = (installation_id, consumer_id)
        if key not in self._stats:
            self._stats[key] = {"batches": 0, "items": 0}
        self._stats[key]["batches"] += 1
        self._stats[key]["items"] += len(items)
        log.info("batch_executed", installation_id=installation_id, consumer=consumer_id, items=len(items), succeeded=succeeded)
        return BatchResult(total=len(items), succeeded=succeeded, failed=failed, results=results)

    def get_stats(self, installation_id: str, consumer_id: str) -> dict[str, int]:
        return self._stats.get((installation_id, consumer_id), {"batches": 0, "items": 0})
