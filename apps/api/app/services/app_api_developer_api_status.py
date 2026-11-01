"""App API Developer API Status — real-time API status for developers."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class APIStatus:
    service_name: str
    status: str  # "operational", "degraded", "outage"
    response_time_ms: float = 0.0
    last_checked: str = ""

class AppAPIDeveloperAPIStatus:
    def __init__(self) -> None:
        self._statuses: dict[tuple[str, str], APIStatus] = {}

    def update(self, installation_id: str, service_name: str, status: str, response_time_ms: float = 0.0, last_checked: str = "") -> APIStatus:
        if not installation_id: raise ValueError("installation_id is required")
        if status not in ("operational", "degraded", "outage"): raise ValueError("invalid status")
        s = APIStatus(service_name=service_name, status=status, response_time_ms=response_time_ms, last_checked=last_checked)
        self._statuses[(installation_id, service_name)] = s
        return s

    def overall_status(self, installation_id: str) -> str:
        statuses = [s for (inst, _), s in self._statuses.items() if inst == installation_id]
        if not statuses: return "operational"
        if any(s.status == "outage" for s in statuses): return "outage"
        if any(s.status == "degraded" for s in statuses): return "degraded"
        return "operational"

    def list_statuses(self, installation_id: str) -> list[APIStatus]:
        return [s for (inst, _), s in self._statuses.items() if inst == installation_id]
