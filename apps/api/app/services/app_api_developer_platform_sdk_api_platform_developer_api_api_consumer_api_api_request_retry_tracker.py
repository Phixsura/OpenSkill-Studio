"""API Consumer Request Retry Tracker — track retry patterns across consumers."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class RetryRecord:
    consumer_id: str
    endpoint: str
    total_attempts: int = 0
    successful_retries: int = 0
    failed_retries: int = 0
    max_attempts_reached: int = 0

    @property
    def retry_success_rate(self) -> float:
        total = self.successful_retries + self.failed_retries
        if total == 0: return 0.0
        return round((self.successful_retries / total) * 100, 1)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestRetryTracker:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str, str], RetryRecord] = {}

    def record_retry(self, installation_id: str, consumer_id: str, endpoint: str, success: bool, max_reached: bool = False) -> RetryRecord:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id, endpoint)
        r = self._records.get(key)
        if r is None:
            r = RetryRecord(consumer_id=consumer_id, endpoint=endpoint)
            self._records[key] = r
        r.total_attempts += 1
        if success: r.successful_retries += 1
        else: r.failed_retries += 1
        if max_reached: r.max_attempts_reached += 1
        return r

    def get_record(self, installation_id: str, consumer_id: str, endpoint: str) -> RetryRecord | None:
        return self._records.get((installation_id, consumer_id, endpoint))

    def high_retry_endpoints(self, installation_id: str, min_retries: int = 10) -> list[RetryRecord]:
        return [r for (inst, _, _), r in self._records.items() if inst == installation_id and r.total_attempts >= min_retries]

    def total_retries(self, installation_id: str) -> int:
        return sum(r.total_attempts for (inst, _, _), r in self._records.items() if inst == installation_id)

    def list_records(self, installation_id: str) -> list[RetryRecord]:
        return [r for (inst, _, _), r in self._records.items() if inst == installation_id]
