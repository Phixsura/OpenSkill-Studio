"""API Consumer Deprecation Notice — notify consumers of upcoming API deprecations."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class NoticeUrgency(str, Enum):
    INFO = "info"
    WARNING = "warning"
    URGENT = "urgent"
    FINAL = "final"

@dataclass
class DeprecationNotice:
    notice_id: str
    endpoint: str
    method: str
    urgency: NoticeUrgency
    message: str
    sunset_date: str  # "2025-06-01"
    replacement: str = ""
    acknowledged_by: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiDeprecationNotice:
    def __init__(self) -> None:
        self._notices: dict[tuple[str, str], DeprecationNotice] = {}

    def create_notice(self, installation_id: str, notice: DeprecationNotice) -> DeprecationNotice:
        if not installation_id: raise ValueError("installation_id is required")
        if not notice.sunset_date: raise ValueError("sunset_date is required")
        key = (installation_id, notice.notice_id)
        if key in self._notices: raise ValueError(f"Notice {notice.notice_id} exists")
        self._notices[key] = notice
        return notice

    def acknowledge(self, installation_id: str, notice_id: str, consumer_id: str) -> DeprecationNotice:
        n = self._get(installation_id, notice_id)
        if consumer_id not in n.acknowledged_by:
            n.acknowledged_by.append(consumer_id)
        return n

    def unacknowledged_for(self, installation_id: str, consumer_id: str) -> list[DeprecationNotice]:
        return [n for (inst, _), n in self._notices.items()
                if inst == installation_id and consumer_id not in n.acknowledged_by]

    def urgent_notices(self, installation_id: str) -> list[DeprecationNotice]:
        return [n for (inst, _), n in self._notices.items()
                if inst == installation_id and n.urgency in (NoticeUrgency.URGENT, NoticeUrgency.FINAL)]

    def list_notices(self, installation_id: str) -> list[DeprecationNotice]:
        return [n for (inst, _), n in self._notices.items() if inst == installation_id]

    def _get(self, installation_id: str, notice_id: str) -> DeprecationNotice:
        n = self._notices.get((installation_id, notice_id))
        if n is None: raise KeyError(f"Notice {notice_id} not found")
        return n
