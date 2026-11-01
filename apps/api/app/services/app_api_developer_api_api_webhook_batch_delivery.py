"""App API Developer Webhook Batch Delivery — batch multiple events into one delivery."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class BatchConfig:
    destination: str
    max_batch_size: int
    max_wait_ms: int
    current_batch: list[str] = field(default_factory=list)
    batches_sent: int = 0
    events_batched: int = 0

@dataclass
class DeliveredBatch:
    batch_id: str
    destination: str
    event_count: int
    delivered_at: float = field(default_factory=time.time)

class AppAPIDeveloperAPIApiWebhookBatchDelivery:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], BatchConfig] = {}
        self._delivered: dict[str, list[DeliveredBatch]] = {}
        self._counter = 0

    def configure(self, installation_id: str, destination: str, max_batch_size: int, max_wait_ms: int) -> BatchConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if max_batch_size < 1: raise ValueError("max_batch_size must be >= 1")
        if max_wait_ms < 100: raise ValueError("max_wait_ms must be >= 100")
        key = (installation_id, destination)
        c = BatchConfig(destination=destination, max_batch_size=max_batch_size, max_wait_ms=max_wait_ms)
        self._configs[key] = c
        return c

    def add_event(self, installation_id: str, destination: str, event_id: str) -> DeliveredBatch | None:
        key = (installation_id, destination)
        c = self._configs.get(key)
        if c is None: raise KeyError(f"No config for {destination}")
        c.current_batch.append(event_id)
        c.events_batched += 1
        if len(c.current_batch) >= c.max_batch_size:
            return self._flush(installation_id, c)
        return None

    def flush(self, installation_id: str, destination: str) -> DeliveredBatch | None:
        key = (installation_id, destination)
        c = self._configs.get(key)
        if c is None or not c.current_batch: return None
        return self._flush(installation_id, c)

    def _flush(self, installation_id: str, c: BatchConfig) -> DeliveredBatch:
        self._counter += 1
        b = DeliveredBatch(batch_id=f"batch-{self._counter}", destination=c.destination, event_count=len(c.current_batch))
        c.batches_sent += 1
        c.current_batch = []
        self._delivered.setdefault(installation_id, []).append(b)
        return b

    def stats(self, installation_id: str) -> dict[str, int]:
        configs = [c for (inst, _), c in self._configs.items() if inst == installation_id]
        return {"batches_sent": sum(c.batches_sent for c in configs), "events_batched": sum(c.events_batched for c in configs), "pending": sum(len(c.current_batch) for c in configs)}
