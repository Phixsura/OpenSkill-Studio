"""Audit Trail Logger — immutable event log with tamper detection."""
from __future__ import annotations

import hashlib
import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()


@dataclass
class AuditEvent:
    event_id: str
    actor_id: str
    action: str
    resource_type: str
    resource_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: dict = field(default_factory=dict)
    ip_address: str = ""


@dataclass
class AuditEntry:
    event: AuditEvent
    sequence: int
    hash: str
    prev_hash: str


@dataclass
class AuditTrailLogger:
    """Immutable append-only audit log with hash chain for tamper detection."""

    _entries: list[AuditEntry] = field(default_factory=list)
    _prev_hash: str = "0" * 64

    def _compute_hash(self, event: AuditEvent, sequence: int, prev_hash: str) -> str:
        data = f"{sequence}:{prev_hash}:{event.event_id}:{event.actor_id}:{event.action}:{event.resource_type}:{event.resource_id}:{event.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

    def log(self, event: AuditEvent) -> dict:
        if not event.action:
            raise ValueError("Action is required")
        sequence = len(self._entries) + 1
        entry_hash = self._compute_hash(event, sequence, self._prev_hash)
        entry = AuditEntry(
            event=event, sequence=sequence,
            hash=entry_hash, prev_hash=self._prev_hash,
        )
        self._entries.append(entry)
        self._prev_hash = entry_hash
        logger.info("audit_event_logged", event_id=event.event_id, action=event.action)
        return {"event_id": event.event_id, "sequence": sequence, "hash": entry_hash}

    def verify_integrity(self) -> dict:
        if not self._entries:
            return {"valid": True, "checked": 0}
        prev = "0" * 64
        for entry in self._entries:
            if entry.prev_hash != prev:
                return {"valid": False, "broken_at": entry.sequence, "reason": "prev_hash_mismatch"}
            expected = self._compute_hash(entry.event, entry.sequence, prev)
            if entry.hash != expected:
                return {"valid": False, "broken_at": entry.sequence, "reason": "hash_mismatch"}
            prev = entry.hash
        return {"valid": True, "checked": len(self._entries)}

    def query(self, actor_id: str | None = None, action: str | None = None,
              resource_type: str | None = None, limit: int = 50) -> list[dict]:
        results = []
        for entry in reversed(self._entries):
            if actor_id and entry.event.actor_id != actor_id:
                continue
            if action and entry.event.action != action:
                continue
            if resource_type and entry.event.resource_type != resource_type:
                continue
            results.append({
                "event_id": entry.event.event_id,
                "sequence": entry.sequence,
                "actor_id": entry.event.actor_id,
                "action": entry.event.action,
                "resource_type": entry.event.resource_type,
                "resource_id": entry.event.resource_id,
                "timestamp": entry.event.timestamp,
                "hash": entry.hash[:16] + "...",
            })
            if len(results) >= limit:
                break
        return results

    def get_entry(self, sequence: int) -> dict | None:
        if sequence < 1 or sequence > len(self._entries):
            return None
        entry = self._entries[sequence - 1]
        return {
            "sequence": entry.sequence,
            "event_id": entry.event.event_id,
            "actor_id": entry.event.actor_id,
            "action": entry.event.action,
            "resource_type": entry.event.resource_type,
            "resource_id": entry.event.resource_id,
            "details": entry.event.details,
            "hash": entry.hash,
            "prev_hash": entry.prev_hash,
        }

    def get_stats(self) -> dict:
        actions: dict[str, int] = {}
        actors: set[str] = set()
        for entry in self._entries:
            actions[entry.event.action] = actions.get(entry.event.action, 0) + 1
            actors.add(entry.event.actor_id)
        return {
            "total_entries": len(self._entries),
            "unique_actors": len(actors),
            "action_counts": actions,
        }
