"""Consumer API Endpoint Error Distribution — analyze error distribution by type."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ErrorBucket:
    status_code: int
    error_code: str
    count: int
    percentage: float

@dataclass
class ErrorDistribution:
    endpoint_path: str
    total_errors: int
    total_requests: int
    error_rate_pct: float
    buckets: list[ErrorBucket]
    most_common_error: str

class AppAPIDeveloperPlatformSDKConsumerApiEndpointErrorDistribution:
    def __init__(self) -> None:
        self._errors: dict[tuple[str, str], list[tuple[int, str]]] = {}
        self._request_counts: dict[tuple[str, str], int] = {}

    def record_error(self, installation_id: str, endpoint: str, status_code: int, error_code: str) -> None:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, endpoint)
        if key not in self._errors:
            self._errors[key] = []
        self._errors[key].append((status_code, error_code))

    def record_request(self, installation_id: str, endpoint: str) -> None:
        key = (installation_id, endpoint)
        self._request_counts[key] = self._request_counts.get(key, 0) + 1

    def get_distribution(self, installation_id: str, endpoint: str) -> ErrorDistribution:
        errors = self._errors.get((installation_id, endpoint), [])
        total_req = self._request_counts.get((installation_id, endpoint), 0)
        if not errors:
            return ErrorDistribution(endpoint_path=endpoint, total_errors=0, total_requests=total_req, error_rate_pct=0, buckets=[], most_common_error="")
        counts: dict[tuple[int, str], int] = {}
        for sc, ec in errors:
            counts[(sc, ec)] = counts.get((sc, ec), 0) + 1
        total = len(errors)
        buckets = sorted([ErrorBucket(status_code=sc, error_code=ec, count=c, percentage=round(c / total * 100, 1)) for (sc, ec), c in counts.items()], key=lambda b: -b.count)
        most_common = buckets[0].error_code if buckets else ""
        error_rate = round(total / max(total_req, 1) * 100, 2)
        return ErrorDistribution(endpoint_path=endpoint, total_errors=total, total_requests=total_req, error_rate_pct=error_rate, buckets=buckets, most_common_error=most_common)
