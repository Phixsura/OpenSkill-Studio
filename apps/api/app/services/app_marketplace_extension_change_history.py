"""Change History — unified history of all changes to an extension.

Tracks config changes, deployments, permission changes, setting updates
with actor, timestamp, diff, and rollback references.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class ChangeRecord:
    change_id: str
    extension_id: str
    change_type: str  # config, deploy, permission, setting, code
    description: str
    actor: str
    diff: dict = field(default_factory=dict)
    rollback_ref: str = ""
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


class ExtensionChangeHistoryService:
    """Tracks all changes to extensions with diffs and actors."""

    MAX_HISTORY = 5000

    def __init__(self):
        self._history: dict[str, list[ChangeRecord]] = defaultdict(list)

    def record(self, extension_id: str, change_type: str, description: str,
               actor: str, diff: dict | None = None,
               rollback_ref: str = "") -> ChangeRecord:
        record = ChangeRecord(
            change_id=f"ch_{secrets.token_urlsafe(8)}",
            extension_id=extension_id, change_type=change_type,
            description=description, actor=actor,
            diff=diff or {}, rollback_ref=rollback_ref,
        )
        h = self._history[extension_id]
        h.append(record)
        if len(h) > self.MAX_HISTORY:
            self._history[extension_id] = h[-self.MAX_HISTORY:]
        return record

    def get_history(self, extension_id: str, change_type: str | None = None,
                    actor: str | None = None, limit: int = 50) -> list[ChangeRecord]:
        records = self._history.get(extension_id, [])
        if change_type:
            records = [r for r in records if r.change_type == change_type]
        if actor:
            records = [r for r in records if r.actor == actor]
        return records[-limit:]

    def get_types(self, extension_id: str) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for r in self._history.get(extension_id, []):
            counts[r.change_type] += 1
        return dict(counts)

    def get_actors(self, extension_id: str) -> list[str]:
        return sorted({r.actor for r in self._history.get(extension_id, [])})

    def get_recent(self, extension_id: str, hours: float = 24) -> list[ChangeRecord]:
        cutoff = time.time() - hours * 3600
        return [r for r in self._history.get(extension_id, []) if r.timestamp >= cutoff]
