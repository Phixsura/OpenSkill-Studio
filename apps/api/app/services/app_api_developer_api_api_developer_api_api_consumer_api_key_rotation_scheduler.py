"""App API Developer Consumer API Key Rotation Scheduler — automated per-consumer key rotation."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class KeyRotationSchedule:
    consumer_id: str
    key_id: str
    rotation_interval_days: int
    last_rotated_at: float = field(default_factory=time.time)
    rotation_count: int = 0
    auto_rotate: bool = True

    @property
    def next_rotation_at(self) -> float:
        return self.last_rotated_at + self.rotation_interval_days * 86400

    @property
    def overdue(self) -> bool:
        return time.time() > self.next_rotation_at

    @property
    def days_until_rotation(self) -> float:
        return max(0.0, round((self.next_rotation_at - time.time()) / 86400, 1))

class AppAPIDeveloperAPIApiDeveloperApiApiConsumerApiKeyRotationScheduler:
    def __init__(self) -> None:
        self._schedules: dict[tuple[str, str, str], KeyRotationSchedule] = {}

    def schedule(self, installation_id: str, consumer_id: str, key_id: str, rotation_interval_days: int, auto_rotate: bool = True) -> KeyRotationSchedule:
        if not installation_id: raise ValueError("installation_id is required")
        if rotation_interval_days < 1: raise ValueError("interval must be >= 1 day")
        key = (installation_id, consumer_id, key_id)
        s = KeyRotationSchedule(consumer_id=consumer_id, key_id=key_id, rotation_interval_days=rotation_interval_days, auto_rotate=auto_rotate)
        self._schedules[key] = s
        return s

    def rotate(self, installation_id: str, consumer_id: str, key_id: str) -> KeyRotationSchedule:
        key = (installation_id, consumer_id, key_id)
        s = self._schedules.get(key)
        if s is None: raise KeyError(f"No schedule for {consumer_id}/{key_id}")
        s.last_rotated_at = time.time()
        s.rotation_count += 1
        return s

    def overdue_keys(self, installation_id: str) -> list[KeyRotationSchedule]:
        return [s for (inst, _, _), s in self._schedules.items() if inst == installation_id and s.overdue]

    def by_consumer(self, installation_id: str, consumer_id: str) -> list[KeyRotationSchedule]:
        return [s for (inst, cid, _), s in self._schedules.items() if inst == installation_id and cid == consumer_id]

    def all_schedules(self, installation_id: str) -> list[KeyRotationSchedule]:
        return [s for (inst, _, _), s in self._schedules.items() if inst == installation_id]
