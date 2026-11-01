"""API Consumer Request Payload Size Tracker — track request/response payload sizes."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class PayloadSizeStats:
    endpoint: str
    method: str
    total_request_bytes: int = 0
    total_response_bytes: int = 0
    request_count: int = 0
    max_request_bytes: int = 0
    max_response_bytes: int = 0

    @property
    def avg_request_bytes(self) -> int:
        return self.total_request_bytes // max(1, self.request_count)

    @property
    def avg_response_bytes(self) -> int:
        return self.total_response_bytes // max(1, self.request_count)

    @property
    def total_transfer_mb(self) -> float:
        return round((self.total_request_bytes + self.total_response_bytes) / 1048576, 2)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestPayloadSizeTracker:
    def __init__(self) -> None:
        self._stats: dict[tuple[str, str, str], PayloadSizeStats] = {}

    def record(self, installation_id: str, endpoint: str, method: str, request_bytes: int, response_bytes: int) -> PayloadSizeStats:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, method.upper(), endpoint)
        s = self._stats.get(key)
        if s is None:
            s = PayloadSizeStats(endpoint=endpoint, method=method.upper())
            self._stats[key] = s
        s.total_request_bytes += request_bytes
        s.total_response_bytes += response_bytes
        s.request_count += 1
        s.max_request_bytes = max(s.max_request_bytes, request_bytes)
        s.max_response_bytes = max(s.max_response_bytes, response_bytes)
        return s

    def largest_payloads(self, installation_id: str, limit: int = 5) -> list[PayloadSizeStats]:
        stats = [s for (inst, _, _), s in self._stats.items() if inst == installation_id]
        return sorted(stats, key=lambda s: -(s.avg_request_bytes + s.avg_response_bytes))[:limit]

    def total_transfer(self, installation_id: str) -> float:
        total = sum((s.total_request_bytes + s.total_response_bytes) for (inst, _, _), s in self._stats.items() if inst == installation_id)
        return round(total / 1048576, 2)

    def list_stats(self, installation_id: str) -> list[PayloadSizeStats]:
        return [s for (inst, _, _), s in self._stats.items() if inst == installation_id]
