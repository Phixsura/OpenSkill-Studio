"""App API Developer API Error Classification — categorize and analyze API errors."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ErrorBucket:
    error_code: str
    category: str  # "client", "server", "auth", "rate_limit", "validation", "timeout"
    count: int = 0
    sample_message: str = ""
    endpoints_affected: set[str] = field(default_factory=set)

class AppAPIDeveloperAPIApiErrorClassification:
    def __init__(self) -> None:
        self._buckets: dict[tuple[str, str], ErrorBucket] = {}

    def classify(self, installation_id: str, status_code: int, error_code: str, endpoint: str, message: str = "") -> ErrorBucket:
        if not installation_id: raise ValueError("installation_id is required")
        if status_code == 401 or status_code == 403: category = "auth"
        elif status_code == 429: category = "rate_limit"
        elif status_code == 422 or status_code == 400: category = "validation"
        elif status_code == 408 or status_code == 504: category = "timeout"
        elif 400 <= status_code < 500: category = "client"
        elif status_code >= 500: category = "server"
        else: category = "client"
        key = (installation_id, error_code)
        if key not in self._buckets:
            self._buckets[key] = ErrorBucket(error_code=error_code, category=category, sample_message=message)
        b = self._buckets[key]
        b.count += 1
        b.endpoints_affected.add(endpoint)
        return b

    def top_errors(self, installation_id: str, limit: int = 10) -> list[ErrorBucket]:
        buckets = [b for (inst, _), b in self._buckets.items() if inst == installation_id]
        return sorted(buckets, key=lambda b: b.count, reverse=True)[:limit]

    def by_category(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), b in self._buckets.items():
            if inst == installation_id:
                counts[b.category] = counts.get(b.category, 0) + b.count
        return counts

    def total_errors(self, installation_id: str) -> int:
        return sum(b.count for (inst, _), b in self._buckets.items() if inst == installation_id)
