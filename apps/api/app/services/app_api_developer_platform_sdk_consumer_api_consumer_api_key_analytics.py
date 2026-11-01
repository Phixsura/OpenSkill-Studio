"""Consumer API Key Analytics — per-key usage analytics and insights."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class KeyUsageRecord:
    key_id: str
    endpoint: str
    method: str
    status_code: int
    latency_ms: float
    timestamp: datetime

@dataclass
class KeyAnalytics:
    key_id: str
    total_requests: int
    error_count: int
    error_rate_pct: float
    avg_latency_ms: float
    unique_endpoints: int
    last_used: datetime | None
    top_endpoints: list[tuple[str, int]]
    status_distribution: dict[int, int]

class AppAPIDeveloperPlatformSDKConsumerApiConsumerApiKeyAnalytics:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str, str], list[KeyUsageRecord]] = {}

    def record(self, installation_id: str, consumer_id: str, record: KeyUsageRecord) -> KeyUsageRecord:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, consumer_id, record.key_id)
        if key not in self._records:
            self._records[key] = []
        self._records[key].append(record)
        if len(self._records[key]) > 50000:
            self._records[key] = self._records[key][-50000:]
        return record

    def get_analytics(self, installation_id: str, consumer_id: str, key_id: str) -> KeyAnalytics:
        records = self._records.get((installation_id, consumer_id, key_id), [])
        if not records:
            return KeyAnalytics(key_id=key_id, total_requests=0, error_count=0, error_rate_pct=0, avg_latency_ms=0, unique_endpoints=0, last_used=None, top_endpoints=[], status_distribution={})
        errors = sum(1 for r in records if r.status_code >= 400)
        avg_lat = sum(r.latency_ms for r in records) / len(records)
        endpoints: dict[str, int] = {}
        status_dist: dict[int, int] = {}
        for r in records:
            ep = f"{r.method} {r.endpoint}"
            endpoints[ep] = endpoints.get(ep, 0) + 1
            status_dist[r.status_code] = status_dist.get(r.status_code, 0) + 1
        top = sorted(endpoints.items(), key=lambda x: -x[1])[:5]
        return KeyAnalytics(key_id=key_id, total_requests=len(records), error_count=errors, error_rate_pct=round(errors / len(records) * 100, 1), avg_latency_ms=round(avg_lat, 1), unique_endpoints=len(endpoints), last_used=records[-1].timestamp, top_endpoints=top, status_distribution=status_dist)

    def compare_keys(self, installation_id: str, consumer_id: str) -> list[KeyAnalytics]:
        keys = {kid for (inst, cid, kid) in self._records if inst == installation_id and cid == consumer_id}
        return sorted([self.get_analytics(installation_id, consumer_id, kid) for kid in keys], key=lambda a: -a.total_requests)
