"""App Feature Flag Audit — audit trail for feature flag changes.

Tracks all feature flag modifications:
- Record flag creation, toggle, and deletion events
- Query audit log by flag or actor
- Retention-based cleanup
- Per-installation scoped logs
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class FlagAuditEntry:
    """An audit log entry for a feature flag change."""

    entry_id: str
    flag_key: str
    action: str  # "created", "enabled", "disabled", "deleted", "updated"
    actor: str
    old_value: str | None = None
    new_value: str | None = None
    reason: str = ""
    timestamp: float = field(default_factory=time.time)


class AppFeatureFlagAudit:
    """Audit trail for feature flag changes."""

    def __init__(self, max_entries: int = 1000) -> None:
        self._max = max(1, max_entries)
        self._entries: dict[str, list[FlagAuditEntry]] = {}

    def record(
        self, installation_id: str, entry_id: str, flag_key: str,
        action: str, actor: str, old_value: str | None = None,
        new_value: str | None = None, reason: str = "",
    ) -> FlagAuditEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not flag_key:
            raise ValueError("flag_key is required")
        if action not in ("created", "enabled", "disabled", "deleted", "updated"):
            raise ValueError(f"Invalid action: {action}")
        if not actor:
            raise ValueError("actor is required")

        entry = FlagAuditEntry(
            entry_id=entry_id, flag_key=flag_key, action=action,
            actor=actor, old_value=old_value, new_value=new_value, reason=reason,
        )
        entries = self._entries.setdefault(installation_id, [])
        entries.append(entry)
        if len(entries) > self._max:
            self._entries[installation_id] = entries[-self._max:]
        return entry

    def by_flag(self, installation_id: str, flag_key: str) -> list[FlagAuditEntry]:
        entries = self._entries.get(installation_id, [])
        return [e for e in entries if e.flag_key == flag_key]

    def by_actor(self, installation_id: str, actor: str) -> list[FlagAuditEntry]:
        entries = self._entries.get(installation_id, [])
        return [e for e in entries if e.actor == actor]

    def recent(self, installation_id: str, limit: int = 20) -> list[FlagAuditEntry]:
        entries = self._entries.get(installation_id, [])
        return list(reversed(entries[-limit:]))

    def count(self, installation_id: str) -> int:
        return len(self._entries.get(installation_id, []))
