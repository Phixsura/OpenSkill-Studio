"""API Consumer Webhook Event Aggregator — aggregate events before delivery."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class AggregatedBatch:
    batch_id: str
    consumer_id: str
    events: list[dict] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    flushed: bool = False

@dataclass
class AggregationConfig:
    consumer_id: str
    max_batch_size: int = 50
    max_wait_s: int = 30
    enabled: bool = True

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventAggregator:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], AggregationConfig] = {}
        self._batches: dict[tuple[str, str], AggregatedBatch] = {}
        self._counter: dict[str, int] = {}

    def configure(self, installation_id: str, config: AggregationConfig) -> AggregationConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if config.max_batch_size < 1: raise ValueError("max_batch_size must be >= 1")
        if config.max_wait_s < 1: raise ValueError("max_wait_s must be >= 1")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def add_event(self, installation_id: str, consumer_id: str, event: dict) -> AggregatedBatch | None:
        """Add event. Returns batch if ready to flush, None otherwise."""
        config = self._configs.get((installation_id, consumer_id))
        if config is None or not config.enabled: return None
        key = (installation_id, consumer_id)
        batch = self._batches.get(key)
        if batch is None or batch.flushed:
            self._counter[installation_id] = self._counter.get(installation_id, 0) + 1
            batch = AggregatedBatch(batch_id=f"batch-{self._counter[installation_id]}", consumer_id=consumer_id)
            self._batches[key] = batch
        batch.events.append(event)
        if len(batch.events) >= config.max_batch_size:
            batch.flushed = True
            return batch
        return None

    def flush(self, installation_id: str, consumer_id: str) -> AggregatedBatch | None:
        key = (installation_id, consumer_id)
        batch = self._batches.get(key)
        if batch and not batch.flushed and batch.events:
            batch.flushed = True
            return batch
        return None

    def pending_count(self, installation_id: str, consumer_id: str) -> int:
        batch = self._batches.get((installation_id, consumer_id))
        if batch and not batch.flushed: return len(batch.events)
        return 0

    def list_configs(self, installation_id: str) -> list[AggregationConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
