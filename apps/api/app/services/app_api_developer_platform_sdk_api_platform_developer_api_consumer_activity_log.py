"""API Consumer Activity Log — audit trail of consumer API activity."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ActivityEntry:
    entry_id: str
    consumer_id: str
    action: str  # "api_call", "key_created", "key_revoked", "scope_changed", "webhook_subscribed"
    resource: str  # endpoint or resource affected
    ip_address: str = ""
    user_agent: str = ""
    status_code: int = 0
    timestamp: float = field(default_factory=time.time)

VALID_ACTIONS = {"api_call", "key_created", "key_revoked", "scope_changed", "webhook_subscribed", "webhook_unsubscribed", "settings_updated"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerActivityLog:
    def __init__(self, max_entries: int = 10000) -> None:
        self._logs: dict[str, list[ActivityEntry]] = {}
        self._max = max(100, max_entries)

    def record(self, installation_id: str, entry: ActivityEntry) -> ActivityEntry:
        if not installation_id: raise ValueError("installation_id is required")
        if entry.action not in VALID_ACTIONS: raise ValueError(f"Invalid action: {entry.action}")
        entries = self._logs.setdefault(installation_id, [])
        entries.append(entry)
        if len(entries) > self._max:
            self._logs[installation_id] = entries[-self._max:]
        return entry

    def query(self, installation_id: str, consumer_id: str | None = None, action: str | None = None, since: float = 0, limit: int = 50) -> list[ActivityEntry]:
        entries = self._logs.get(installation_id, [])
        if consumer_id: entries = [e for e in entries if e.consumer_id == consumer_id]
        if action: entries = [e for e in entries if e.action == action]
        if since > 0: entries = [e for e in entries if e.timestamp >= since]
        return list(reversed(entries[-limit:]))

    def count_by_action(self, installation_id: str) -> dict[str, int]:
        entries = self._logs.get(installation_id, [])
        counts: dict[str, int] = {}
        for e in entries: counts[e.action] = counts.get(e.action, 0) + 1
        return counts

    def unique_consumers(self, installation_id: str, since: float = 0) -> int:
        entries = self._logs.get(installation_id, [])
        if since > 0: entries = [e for e in entries if e.timestamp >= since]
        return len({e.consumer_id for e in entries})

    def total_entries(self, installation_id: str) -> int:
        return len(self._logs.get(installation_id, []))
