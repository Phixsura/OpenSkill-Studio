"""App API Developer API Secret Rotation Scheduler — automated credential rotation."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class RotationSchedule:
    secret_id: str
    secret_type: str  # "api_key", "webhook_secret", "jwt_signing_key"
    rotation_interval_days: int
    last_rotated_at: float = 0.0
    next_rotation_at: float = 0.0
    rotation_count: int = 0

    @property
    def overdue(self) -> bool:
        return time.time() > self.next_rotation_at and self.next_rotation_at > 0

    @property
    def days_until_rotation(self) -> float:
        return max(0.0, round((self.next_rotation_at - time.time()) / 86400, 1))

class AppAPIDeveloperAPIApiSecretRotationScheduler:
    def __init__(self) -> None:
        self._schedules: dict[tuple[str, str], RotationSchedule] = {}

    def schedule(self, installation_id: str, secret_id: str, secret_type: str, rotation_interval_days: int) -> RotationSchedule:
        if not installation_id: raise ValueError("installation_id is required")
        if secret_type not in ("api_key", "webhook_secret", "jwt_signing_key"): raise ValueError("invalid secret_type")
        if rotation_interval_days < 1: raise ValueError("interval must be at least 1 day")
        key = (installation_id, secret_id)
        now = time.time()
        s = RotationSchedule(secret_id=secret_id, secret_type=secret_type, rotation_interval_days=rotation_interval_days, last_rotated_at=now, next_rotation_at=now + rotation_interval_days * 86400)
        self._schedules[key] = s
        return s

    def rotate(self, installation_id: str, secret_id: str) -> RotationSchedule:
        s = self._get(installation_id, secret_id)
        now = time.time()
        s.last_rotated_at = now
        s.next_rotation_at = now + s.rotation_interval_days * 86400
        s.rotation_count += 1
        return s

    def overdue(self, installation_id: str) -> list[RotationSchedule]:
        return [s for (inst, _), s in self._schedules.items() if inst == installation_id and s.overdue]

    def all_schedules(self, installation_id: str) -> list[RotationSchedule]:
        return [s for (inst, _), s in self._schedules.items() if inst == installation_id]

    def _get(self, installation_id: str, secret_id: str) -> RotationSchedule:
        key = (installation_id, secret_id)
        s = self._schedules.get(key)
        if s is None: raise KeyError(f"Schedule {secret_id} not found")
        return s
