"""App API Developer Consumer Authentication Tracker — track auth methods and failures."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class AuthRecord:
    consumer_id: str
    auth_method: str  # "api_key", "oauth2", "jwt", "basic"
    successful: int = 0
    failed: int = 0
    last_auth_at: float = 0.0
    last_failure_reason: str = ""

    @property
    def failure_rate(self) -> float:
        total = self.successful + self.failed
        return round(self.failed / total * 100, 1) if total > 0 else 0.0

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiConsumerAuthenticationTracker:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str], AuthRecord] = {}

    def record_auth(self, installation_id: str, consumer_id: str, auth_method: str, success: bool, failure_reason: str = "") -> AuthRecord:
        if not installation_id: raise ValueError("installation_id is required")
        if auth_method not in ("api_key", "oauth2", "jwt", "basic"): raise ValueError("invalid auth_method")
        key = (installation_id, consumer_id)
        if key not in self._records:
            self._records[key] = AuthRecord(consumer_id=consumer_id, auth_method=auth_method)
        r = self._records[key]
        r.last_auth_at = time.time()
        if success: r.successful += 1
        else:
            r.failed += 1
            r.last_failure_reason = failure_reason
        return r

    def high_failure_rate(self, installation_id: str, threshold: float = 10.0) -> list[AuthRecord]:
        return [r for (inst, _), r in self._records.items() if inst == installation_id and r.failure_rate >= threshold]

    def by_method(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), r in self._records.items():
            if inst == installation_id: counts[r.auth_method] = counts.get(r.auth_method, 0) + 1
        return counts

    def all_records(self, installation_id: str) -> list[AuthRecord]:
        return [r for (inst, _), r in self._records.items() if inst == installation_id]
