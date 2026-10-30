"""API Consumer Quota Reset Scheduler — schedule periodic quota resets."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class QuotaResetSchedule:
    consumer_id: str
    reset_interval: str  # "hourly", "daily", "weekly", "monthly"
    last_reset: float = field(default_factory=time.time)
    next_reset: float = 0.0
    total_resets: int = 0

INTERVALS = {"hourly": 3600, "daily": 86400, "weekly": 604800, "monthly": 2592000}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiQuotaResetScheduler:
    def __init__(self) -> None:
        self._schedules: dict[tuple[str, str], QuotaResetSchedule] = {}

    def schedule(self, installation_id: str, consumer_id: str, interval: str) -> QuotaResetSchedule:
        if not installation_id: raise ValueError("installation_id is required")
        if interval not in INTERVALS: raise ValueError(f"Invalid interval: {interval}")
        now = time.time()
        sched = QuotaResetSchedule(consumer_id=consumer_id, reset_interval=interval, last_reset=now, next_reset=now + INTERVALS[interval])
        self._schedules[(installation_id, consumer_id)] = sched
        return sched

    def check_and_reset(self, installation_id: str, consumer_id: str) -> bool:
        sched = self._schedules.get((installation_id, consumer_id))
        if sched is None: return False
        now = time.time()
        if now >= sched.next_reset:
            sched.last_reset = now
            sched.next_reset = now + INTERVALS[sched.reset_interval]
            sched.total_resets += 1
            return True
        return False

    def time_until_reset(self, installation_id: str, consumer_id: str) -> float:
        sched = self._schedules.get((installation_id, consumer_id))
        if sched is None: return 0.0
        return max(0, sched.next_reset - time.time())

    def due_for_reset(self, installation_id: str) -> list[QuotaResetSchedule]:
        now = time.time()
        return [s for (inst, _), s in self._schedules.items() if inst == installation_id and now >= s.next_reset]

    def list_schedules(self, installation_id: str) -> list[QuotaResetSchedule]:
        return [s for (inst, _), s in self._schedules.items() if inst == installation_id]
