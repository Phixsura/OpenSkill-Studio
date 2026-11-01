"""API Consumer Request Log Aggregator — aggregate request logs into time buckets."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class TimeBucket:
    bucket_key: str  # "2024-01-15T14:00" (hourly)
    request_count: int = 0
    error_count: int = 0
    total_latency_ms: float = 0.0
    unique_consumers: set[str] = field(default_factory=set)
    bytes_transferred: int = 0

    @property
    def avg_latency(self) -> float:
        if self.request_count == 0: return 0.0
        return round(self.total_latency_ms / self.request_count, 2)

    @property
    def error_rate(self) -> float:
        if self.request_count == 0: return 0.0
        return round((self.error_count / self.request_count) * 100, 2)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestLogAggregator:
    def __init__(self) -> None:
        self._buckets: dict[tuple[str, str], TimeBucket] = {}

    def record(self, installation_id: str, bucket_key: str, consumer_id: str, latency_ms: float, error: bool = False, bytes_transferred: int = 0) -> TimeBucket:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, bucket_key)
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = TimeBucket(bucket_key=bucket_key)
            self._buckets[key] = bucket
        bucket.request_count += 1
        bucket.total_latency_ms += latency_ms
        bucket.bytes_transferred += bytes_transferred
        bucket.unique_consumers.add(consumer_id)
        if error: bucket.error_count += 1
        return bucket

    def get_bucket(self, installation_id: str, bucket_key: str) -> TimeBucket | None:
        return self._buckets.get((installation_id, bucket_key))

    def recent_buckets(self, installation_id: str, limit: int = 24) -> list[TimeBucket]:
        buckets = [b for (inst, _), b in self._buckets.items() if inst == installation_id]
        return sorted(buckets, key=lambda b: b.bucket_key)[-limit:]

    def peak_bucket(self, installation_id: str) -> TimeBucket | None:
        buckets = [b for (inst, _), b in self._buckets.items() if inst == installation_id]
        return max(buckets, key=lambda b: b.request_count) if buckets else None

    def total_requests(self, installation_id: str) -> int:
        return sum(b.request_count for (inst, _), b in self._buckets.items() if inst == installation_id)
