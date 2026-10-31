"""Consumer API Usage Comparison — compare usage across consumers or time periods."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerUsage:
    consumer_id: str
    requests: int
    errors: int
    avg_latency_ms: float
    active_keys: int
    active_webhooks: int

@dataclass
class ComparisonResult:
    consumers: list[ConsumerUsage]
    highest_usage: str
    lowest_usage: str
    avg_requests: float
    total_requests: int

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiUsageComparison:
    def __init__(self) -> None:
        self._usage: dict[tuple[str, str], ConsumerUsage] = {}

    def set_usage(self, installation_id: str, usage: ConsumerUsage) -> ConsumerUsage:
        if not installation_id:
            raise ValueError("installation_id is required")
        if usage.requests < 0:
            raise ValueError("requests must be non-negative")
        self._usage[(installation_id, usage.consumer_id)] = usage
        return usage

    def compare(self, installation_id: str, consumer_ids: list[str] | None = None) -> ComparisonResult:
        all_usage = [u for (inst, _), u in self._usage.items() if inst == installation_id]
        if consumer_ids:
            all_usage = [u for u in all_usage if u.consumer_id in consumer_ids]
        if not all_usage:
            return ComparisonResult(consumers=[], highest_usage="", lowest_usage="", avg_requests=0, total_requests=0)
        sorted_by_req = sorted(all_usage, key=lambda u: -u.requests)
        total = sum(u.requests for u in all_usage)
        avg = total / len(all_usage)
        return ComparisonResult(consumers=sorted_by_req, highest_usage=sorted_by_req[0].consumer_id, lowest_usage=sorted_by_req[-1].consumer_id, avg_requests=round(avg, 1), total_requests=total)

    def rank_by_metric(self, installation_id: str, metric: str, limit: int = 10) -> list[ConsumerUsage]:
        all_usage = [u for (inst, _), u in self._usage.items() if inst == installation_id]
        key_map = {"requests": lambda u: u.requests, "errors": lambda u: u.errors, "latency": lambda u: u.avg_latency_ms}
        sort_fn = key_map.get(metric, lambda u: u.requests)
        return sorted(all_usage, key=sort_fn, reverse=True)[:limit]
