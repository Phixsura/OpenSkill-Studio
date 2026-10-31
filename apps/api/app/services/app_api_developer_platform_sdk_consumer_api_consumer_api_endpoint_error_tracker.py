"""Consumer API Endpoint Error Tracker — track and categorize endpoint errors."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class EndpointError:
    error_id: str
    endpoint_path: str
    method: str
    status_code: int
    error_code: str
    message: str
    timestamp: datetime
    consumer_id: str = ""

@dataclass
class ErrorSummary:
    endpoint_path: str
    total_errors: int
    by_status: dict[int, int]
    by_error_code: dict[str, int]
    most_common_error: str
    error_rate_pct: float

class AppAPIDeveloperPlatformSDKConsumerApiConsumerApiEndpointErrorTracker:
    def __init__(self) -> None:
        self._errors: dict[tuple[str, str], list[EndpointError]] = {}  # (inst, endpoint)
        self._request_counts: dict[tuple[str, str], int] = {}

    def record_error(self, installation_id: str, error: EndpointError) -> EndpointError:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, error.endpoint_path)
        if key not in self._errors:
            self._errors[key] = []
        self._errors[key].append(error)
        if len(self._errors[key]) > 10000:
            self._errors[key] = self._errors[key][-10000:]
        return error

    def record_request(self, installation_id: str, endpoint_path: str) -> None:
        key = (installation_id, endpoint_path)
        self._request_counts[key] = self._request_counts.get(key, 0) + 1

    def get_summary(self, installation_id: str, endpoint_path: str) -> ErrorSummary:
        errors = self._errors.get((installation_id, endpoint_path), [])
        total_requests = self._request_counts.get((installation_id, endpoint_path), 0)
        if not errors:
            return ErrorSummary(endpoint_path=endpoint_path, total_errors=0, by_status={}, by_error_code={}, most_common_error="", error_rate_pct=0)
        by_status: dict[int, int] = {}
        by_code: dict[str, int] = {}
        for e in errors:
            by_status[e.status_code] = by_status.get(e.status_code, 0) + 1
            by_code[e.error_code] = by_code.get(e.error_code, 0) + 1
        most_common = max(by_code, key=by_code.get) if by_code else ""
        rate = (len(errors) / max(total_requests, 1)) * 100
        return ErrorSummary(endpoint_path=endpoint_path, total_errors=len(errors), by_status=by_status, by_error_code=by_code, most_common_error=most_common, error_rate_pct=round(rate, 2))

    def get_recent(self, installation_id: str, endpoint_path: str, limit: int = 20) -> list[EndpointError]:
        return list(reversed(self._errors.get((installation_id, endpoint_path), [])[-limit:]))

    def list_erroring_endpoints(self, installation_id: str) -> list[str]:
        return sorted({ep for (inst, ep) in self._errors if inst == installation_id and self._errors[(inst, ep)]})
