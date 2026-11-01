"""API Consumer Request Correlation — correlate related API requests with trace IDs."""
from __future__ import annotations
from dataclasses import dataclass, field
import secrets
import time
import structlog

log = structlog.get_logger()

@dataclass
class CorrelatedRequest:
    request_id: str
    trace_id: str
    span_id: str
    parent_span_id: str = ""
    method: str = ""
    path: str = ""
    status_code: int = 0
    duration_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestCorrelation:
    def __init__(self) -> None:
        self._traces: dict[tuple[str, str], list[CorrelatedRequest]] = {}

    def generate_trace_id(self) -> str:
        return secrets.token_hex(16)

    def generate_span_id(self) -> str:
        return secrets.token_hex(8)

    def record(self, installation_id: str, request: CorrelatedRequest) -> CorrelatedRequest:
        if not installation_id: raise ValueError("installation_id is required")
        if not request.trace_id: raise ValueError("trace_id is required")
        key = (installation_id, request.trace_id)
        self._traces.setdefault(key, []).append(request)
        return request

    def get_trace(self, installation_id: str, trace_id: str) -> list[CorrelatedRequest]:
        return self._traces.get((installation_id, trace_id), [])

    def trace_duration(self, installation_id: str, trace_id: str) -> float:
        requests = self.get_trace(installation_id, trace_id)
        if not requests: return 0.0
        return round(sum(r.duration_ms for r in requests), 2)

    def trace_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._traces if inst == installation_id)

    def failed_traces(self, installation_id: str) -> list[str]:
        result = []
        for (inst, tid), requests in self._traces.items():
            if inst == installation_id and any(r.status_code >= 500 for r in requests):
                result.append(tid)
        return result
