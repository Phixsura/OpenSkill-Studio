"""Consumer API Endpoint Usage Analytics V2 — advanced per-endpoint analytics."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class EndpointUsageRecord:
    endpoint_path: str
    method: str
    status_code: int
    latency_ms: float
    consumer_id: str
    timestamp: datetime

@dataclass
class EndpointAnalytics:
    endpoint_path: str
    total_requests: int
    unique_consumers: int
    avg_latency_ms: float
    p95_latency_ms: float
    error_rate_pct: float
    requests_per_minute: float
    top_consumers: list[tuple[str, int]]
    status_distribution: dict[int, int]

class AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerEndpointUsageAnalyticsV2:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str], list[EndpointUsageRecord]] = {}

    def record(self, installation_id: str, record: EndpointUsageRecord) -> EndpointUsageRecord:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, record.endpoint_path)
        if key not in self._records:
            self._records[key] = []
        self._records[key].append(record)
        if len(self._records[key]) > 50000:
            self._records[key] = self._records[key][-50000:]
        return record

    def analyze(self, installation_id: str, endpoint_path: str) -> EndpointAnalytics:
        records = self._records.get((installation_id, endpoint_path), [])
        if not records:
            return EndpointAnalytics(endpoint_path=endpoint_path, total_requests=0, unique_consumers=0, avg_latency_ms=0, p95_latency_ms=0, error_rate_pct=0, requests_per_minute=0, top_consumers=[], status_distribution={})
        latencies = sorted(r.latency_ms for r in records)
        n = len(latencies)
        p95 = latencies[min(int(n * 0.95), n - 1)]
        avg = sum(latencies) / n
        errors = sum(1 for r in records if r.status_code >= 400)
        consumers: dict[str, int] = {}
        status_dist: dict[int, int] = {}
        for r in records:
            consumers[r.consumer_id] = consumers.get(r.consumer_id, 0) + 1
            status_dist[r.status_code] = status_dist.get(r.status_code, 0) + 1
        top = sorted(consumers.items(), key=lambda x: -x[1])[:5]
        # RPM estimate
        if len(records) >= 2:
            time_span = (records[-1].timestamp - records[0].timestamp).total_seconds()
            rpm = (n / max(time_span, 1)) * 60 if time_span > 0 else 0
        else:
            rpm = 0
        return EndpointAnalytics(endpoint_path=endpoint_path, total_requests=n, unique_consumers=len(consumers), avg_latency_ms=round(avg, 1), p95_latency_ms=round(p95, 1), error_rate_pct=round(errors / n * 100, 2), requests_per_minute=round(rpm, 1), top_consumers=top, status_distribution=status_dist)

    def list_endpoints(self, installation_id: str) -> list[str]:
        return sorted({ep for (inst, ep) in self._records if inst == installation_id})
