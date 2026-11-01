"""App API Developer API Resource Usage Limiter — enforce resource consumption limits."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ResourceLimit:
    resource_type: str  # "compute", "storage", "bandwidth", "connections"
    limit: float
    used: float = 0.0
    unit: str = ""

    @property
    def remaining(self) -> float:
        return max(0.0, round(self.limit - self.used, 2))

    @property
    def usage_pct(self) -> float:
        return round(self.used / self.limit * 100, 1) if self.limit > 0 else 0.0

    @property
    def exceeded(self) -> bool:
        return self.used >= self.limit

class AppAPIDeveloperAPIApiResourceUsageLimiter:
    def __init__(self) -> None:
        self._limits: dict[tuple[str, str, str], ResourceLimit] = {}

    def set_limit(self, installation_id: str, consumer_id: str, resource_type: str, limit: float, unit: str = "") -> ResourceLimit:
        if not installation_id: raise ValueError("installation_id is required")
        if resource_type not in ("compute", "storage", "bandwidth", "connections"): raise ValueError("invalid resource_type")
        if limit <= 0: raise ValueError("limit must be positive")
        key = (installation_id, consumer_id, resource_type)
        r = ResourceLimit(resource_type=resource_type, limit=limit, unit=unit)
        self._limits[key] = r
        return r

    def consume(self, installation_id: str, consumer_id: str, resource_type: str, amount: float) -> ResourceLimit:
        key = (installation_id, consumer_id, resource_type)
        r = self._limits.get(key)
        if r is None: raise KeyError(f"No limit for {consumer_id}/{resource_type}")
        if r.exceeded: raise ValueError("Resource limit exceeded")
        r.used = round(r.used + amount, 2)
        return r

    def check(self, installation_id: str, consumer_id: str, resource_type: str) -> ResourceLimit | None:
        return self._limits.get((installation_id, consumer_id, resource_type))

    def exceeded_limits(self, installation_id: str) -> list[ResourceLimit]:
        return [r for (inst, _, _), r in self._limits.items() if inst == installation_id and r.exceeded]

    def consumer_limits(self, installation_id: str, consumer_id: str) -> list[ResourceLimit]:
        return [r for (inst, cid, _), r in self._limits.items() if inst == installation_id and cid == consumer_id]
