"""App API Developer Activity Log — track developer actions on the platform."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ActivityEntry:
    activity_id: str
    developer_id: str
    action: str  # "key_created", "key_revoked", "app_created", "webhook_configured", "settings_changed", "team_joined"
    resource: str
    timestamp: float = field(default_factory=time.time)
    ip_address: str = ""

VALID_ACTIONS = {"key_created", "key_revoked", "app_created", "webhook_configured", "settings_changed", "team_joined", "login", "logout"}

class AppAPIDeveloperAPIApiDeveloperActivityLog:
    def __init__(self, max_entries: int = 5000) -> None:
        self._max = max(1, max_entries)
        self._log: dict[str, list[ActivityEntry]] = {}

    def record(self, installation_id: str, activity_id: str, developer_id: str, action: str, resource: str, ip_address: str = "") -> ActivityEntry:
        if not installation_id: raise ValueError("installation_id is required")
        if action not in VALID_ACTIONS: raise ValueError(f"Invalid action: {action}")
        e = ActivityEntry(activity_id=activity_id, developer_id=developer_id, action=action, resource=resource, ip_address=ip_address)
        entries = self._log.setdefault(installation_id, [])
        entries.append(e)
        if len(entries) > self._max: self._log[installation_id] = entries[-self._max:]
        return e

    def by_developer(self, installation_id: str, developer_id: str, limit: int = 50) -> list[ActivityEntry]:
        entries = [e for e in self._log.get(installation_id, []) if e.developer_id == developer_id]
        return list(reversed(entries[-limit:]))

    def by_action(self, installation_id: str, action: str) -> list[ActivityEntry]:
        return [e for e in self._log.get(installation_id, []) if e.action == action]

    def recent(self, installation_id: str, limit: int = 50) -> list[ActivityEntry]:
        return list(reversed(self._log.get(installation_id, [])[-limit:]))

    def count(self, installation_id: str) -> int:
        return len(self._log.get(installation_id, []))
