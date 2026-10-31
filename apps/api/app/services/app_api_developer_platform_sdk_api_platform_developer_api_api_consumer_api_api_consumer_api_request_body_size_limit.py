"""API Consumer Request Body Size Limit — enforce per-endpoint body size limits."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class BodySizeLimit:
    endpoint: str
    method: str
    max_bytes: int
    rejected_count: int = 0
    total_checked: int = 0

    @property
    def rejection_rate(self) -> float:
        if self.total_checked == 0: return 0.0
        return round((self.rejected_count / self.total_checked) * 100, 1)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestBodySizeLimit:
    def __init__(self, default_max_bytes: int = 1048576) -> None:
        self._limits: dict[tuple[str, str, str], BodySizeLimit] = {}
        self._default = max(1024, default_max_bytes)

    def set_limit(self, installation_id: str, endpoint: str, method: str, max_bytes: int) -> BodySizeLimit:
        if not installation_id: raise ValueError("installation_id is required")
        if max_bytes < 1: raise ValueError("max_bytes must be >= 1")
        limit = BodySizeLimit(endpoint=endpoint, method=method.upper(), max_bytes=max_bytes)
        self._limits[(installation_id, method.upper(), endpoint)] = limit
        return limit

    def check(self, installation_id: str, endpoint: str, method: str, body_bytes: int) -> dict[str, object]:
        key = (installation_id, method.upper(), endpoint)
        limit = self._limits.get(key)
        max_b = limit.max_bytes if limit else self._default
        if limit: limit.total_checked += 1
        if body_bytes > max_b:
            if limit: limit.rejected_count += 1
            return {"allowed": False, "max_bytes": max_b, "actual_bytes": body_bytes}
        return {"allowed": True, "max_bytes": max_b}

    def most_rejected(self, installation_id: str, limit: int = 5) -> list[BodySizeLimit]:
        limits = [l for (inst, _, _), l in self._limits.items() if inst == installation_id]
        return sorted(limits, key=lambda l: -l.rejected_count)[:limit]

    def list_limits(self, installation_id: str) -> list[BodySizeLimit]:
        return [l for (inst, _, _), l in self._limits.items() if inst == installation_id]
