"""API Consumer Access Audit — audit all access attempts for compliance."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class AccessAttempt:
    attempt_id: str
    consumer_id: str
    endpoint: str
    method: str
    granted: bool
    reason: str = ""  # "authorized", "rate_limited", "scope_denied", "ip_blocked", "key_expired"
    timestamp: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiAccessAudit:
    def __init__(self, max_entries: int = 50000) -> None:
        self._entries: dict[str, list[AccessAttempt]] = {}
        self._max = max(1000, max_entries)

    def record(self, installation_id: str, attempt: AccessAttempt) -> AccessAttempt:
        if not installation_id: raise ValueError("installation_id is required")
        entries = self._entries.setdefault(installation_id, [])
        entries.append(attempt)
        if len(entries) > self._max: self._entries[installation_id] = entries[-self._max:]
        return attempt

    def denied_attempts(self, installation_id: str, limit: int = 50) -> list[AccessAttempt]:
        return [a for a in self._entries.get(installation_id, []) if not a.granted][-limit:]

    def denial_rate(self, installation_id: str) -> float:
        entries = self._entries.get(installation_id, [])
        if not entries: return 0.0
        denied = sum(1 for a in entries if not a.granted)
        return round((denied / len(entries)) * 100, 1)

    def by_reason(self, installation_id: str) -> dict[str, int]:
        result: dict[str, int] = {}
        for a in self._entries.get(installation_id, []):
            if not a.granted:
                result[a.reason] = result.get(a.reason, 0) + 1
        return result

    def total_entries(self, installation_id: str) -> int:
        return len(self._entries.get(installation_id, []))
