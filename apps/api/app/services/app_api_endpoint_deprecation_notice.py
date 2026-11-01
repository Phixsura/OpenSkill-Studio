"""App API Endpoint Deprecation Notice — manage deprecation notices."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class DeprecationNotice:
    notice_id: str
    method: str
    path: str
    message: str
    sunset_date: str
    replacement: str = ""
    acknowledged_by: set[str] = None

    def __post_init__(self):
        if self.acknowledged_by is None:
            self.acknowledged_by = set()

class AppAPIEndpointDeprecationNotice:
    def __init__(self) -> None:
        self._notices: dict[tuple[str, str], DeprecationNotice] = {}

    def create(self, installation_id: str, notice_id: str, method: str, path: str, message: str, sunset_date: str, replacement: str = "") -> DeprecationNotice:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, notice_id)
        if key in self._notices: raise ValueError(f"Notice {notice_id} already exists")
        n = DeprecationNotice(notice_id=notice_id, method=method.upper(), path=path, message=message, sunset_date=sunset_date, replacement=replacement)
        self._notices[key] = n
        return n

    def acknowledge(self, installation_id: str, notice_id: str, consumer_id: str) -> DeprecationNotice:
        n = self._get(installation_id, notice_id)
        n.acknowledged_by.add(consumer_id)
        return n

    def unacknowledged_count(self, installation_id: str, notice_id: str, total_consumers: int) -> int:
        n = self._get(installation_id, notice_id)
        return max(0, total_consumers - len(n.acknowledged_by))

    def list_notices(self, installation_id: str) -> list[DeprecationNotice]:
        return [n for (inst, _), n in self._notices.items() if inst == installation_id]

    def _get(self, installation_id: str, notice_id: str) -> DeprecationNotice:
        n = self._notices.get((installation_id, notice_id))
        if n is None: raise KeyError(f"Notice {notice_id} not found")
        return n
