"""Extension Audit Trail — immutable audit log for extension lifecycle events."""
from __future__ import annotations
from dataclasses import dataclass
import time


@dataclass(frozen=True)
class AuditEntry:
    entry_id: str
    extension_id: str
    actor_id: str
    action: str
    details: str = ""
    timestamp: float = 0.0


class ExtAuditTrailService:
    VALID_ACTIONS = frozenset([
        "created", "published", "updated", "unpublished", "deleted",
        "reviewed", "approved", "rejected", "installed", "uninstalled",
        "permission_granted", "permission_revoked", "transferred",
    ])

    def __init__(self):
        self._log: list[AuditEntry] = []
        self._counter = 0

    def record(self, extension_id: str, actor_id: str, action: str,
               details: str = "") -> AuditEntry:
        if action not in self.VALID_ACTIONS:
            raise ValueError(f"Invalid action: {action}")
        self._counter += 1
        entry = AuditEntry(entry_id=f"aud-{self._counter}",
                           extension_id=extension_id, actor_id=actor_id,
                           action=action, details=details,
                           timestamp=time.time())
        self._log.append(entry)
        return entry

    def get_by_extension(self, extension_id: str, limit: int = 100) -> list[AuditEntry]:
        return [e for e in reversed(self._log)
                if e.extension_id == extension_id][:limit]

    def get_by_actor(self, actor_id: str, limit: int = 100) -> list[AuditEntry]:
        return [e for e in reversed(self._log)
                if e.actor_id == actor_id][:limit]

    def get_by_action(self, action: str) -> list[AuditEntry]:
        return [e for e in self._log if e.action == action]

    def count_actions(self, extension_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for e in self._log:
            if e.extension_id == extension_id:
                counts[e.action] = counts.get(e.action, 0) + 1
        return counts
