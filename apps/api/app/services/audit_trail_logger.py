"""Audit Trail Logger — structured immutable audit log for security-sensitive actions.

Provides compliance-grade audit logging for the developer platform:
- Immutable append-only log with sequence numbers
- Structured events: actor, action, resource, outcome
- IP/user-agent tracking
- Filterable by actor, action, resource, time range
- Tamper detection via hash chaining
- Retention policy enforcement
- Export in JSON-lines format
"""

from __future__ import annotations

import hashlib
import json
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

import structlog

log = structlog.get_logger()


class AuditAction(str, Enum):
    # Auth
    LOGIN = "auth.login"
    LOGOUT = "auth.logout"
    TOKEN_ISSUED = "auth.token_issued"
    TOKEN_REVOKED = "auth.token_revoked"
    PASSWORD_CHANGED = "auth.password_changed"
    # App lifecycle
    APP_CREATED = "app.created"
    APP_PUBLISHED = "app.published"
    APP_INSTALLED = "app.installed"
    APP_UNINSTALLED = "app.uninstalled"
    APP_SUSPENDED = "app.suspended"
    APP_REVOKED = "app.revoked"
    # API keys
    API_KEY_CREATED = "api_key.created"
    API_KEY_ROTATED = "api_key.rotated"
    API_KEY_REVOKED = "api_key.revoked"
    # Permissions
    PERMISSION_GRANTED = "permission.granted"
    PERMISSION_REVOKED = "permission.revoked"
    # Data
    DATA_EXPORTED = "data.exported"
    DATA_DELETED = "data.deleted"
    # Admin
    SETTINGS_CHANGED = "settings.changed"
    MEMBER_ADDED = "member.added"
    MEMBER_REMOVED = "member.removed"
    ROLE_CHANGED = "role.changed"


class AuditOutcome(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"


@dataclass
class AuditEntry:
    """An immutable audit log entry."""

    sequence: int
    timestamp: datetime
    action: AuditAction
    outcome: AuditOutcome
    actor_id: str | None       # user or app ID
    actor_type: str             # "user", "app", "system"
    resource_type: str | None   # e.g. "developer_app", "api_key"
    resource_id: str | None
    org_id: str | None
    ip_address: str | None = None
    user_agent: str | None = None
    details: dict = field(default_factory=dict)
    chain_hash: str = ""        # hash of previous entry + this entry


@dataclass
class AuditQuery:
    """Query parameters for filtering audit entries."""

    actor_id: str | None = None
    action: AuditAction | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    org_id: str | None = None
    outcome: AuditOutcome | None = None
    since: datetime | None = None
    until: datetime | None = None
    limit: int = 50


@dataclass
class AuditStats:
    """Summary statistics for audit entries."""

    total_entries: int
    actions_breakdown: dict[str, int]
    outcomes_breakdown: dict[str, int]
    unique_actors: int


def _hash_entry(prev_hash: str, entry_data: str) -> str:
    """Chain hash: SHA-256(previous_hash + entry_data)."""
    return hashlib.sha256((prev_hash + entry_data).encode()).hexdigest()


class AuditTrailLogger:
    """Append-only audit trail with hash chaining."""

    def __init__(self, max_entries: int = 100_000):
        self._entries: list[AuditEntry] = []
        self._sequence = 0
        self._last_hash = "0" * 64  # genesis hash
        self._max_entries = max_entries

    def record(
        self,
        action: AuditAction,
        outcome: AuditOutcome,
        actor_id: str | None = None,
        actor_type: str = "user",
        resource_type: str | None = None,
        resource_id: str | None = None,
        org_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: dict | None = None,
    ) -> AuditEntry:
        """Record an audit event. Returns the created entry."""
        self._sequence += 1
        now = datetime.now(UTC)

        entry_data = json.dumps({
            "seq": self._sequence,
            "ts": now.isoformat(),
            "action": action.value,
            "outcome": outcome.value,
            "actor": actor_id,
            "actor_type": actor_type,
            "resource": f"{resource_type}:{resource_id}",
            "org_id": org_id,
            "ip": ip_address,
            "ua": user_agent,
            "details": json.dumps(details or {}, sort_keys=True),
        }, sort_keys=True)

        chain_hash = _hash_entry(self._last_hash, entry_data)

        entry = AuditEntry(
            sequence=self._sequence,
            timestamp=now,
            action=action,
            outcome=outcome,
            actor_id=actor_id,
            actor_type=actor_type,
            resource_type=resource_type,
            resource_id=resource_id,
            org_id=org_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
            chain_hash=chain_hash,
        )
        self._entries.append(entry)
        self._last_hash = chain_hash

        # Enforce max entries (FIFO)
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]

        return entry

    def query(self, q: AuditQuery) -> list[AuditEntry]:
        """Query audit entries with filters."""
        results = self._entries

        if q.actor_id:
            results = [e for e in results if e.actor_id == q.actor_id]
        if q.action:
            results = [e for e in results if e.action == q.action]
        if q.resource_type:
            results = [e for e in results if e.resource_type == q.resource_type]
        if q.resource_id:
            results = [e for e in results if e.resource_id == q.resource_id]
        if q.org_id:
            results = [e for e in results if e.org_id == q.org_id]
        if q.outcome:
            results = [e for e in results if e.outcome == q.outcome]
        if q.since:
            results = [e for e in results if e.timestamp >= q.since]
        if q.until:
            results = [e for e in results if e.timestamp <= q.until]

        # Most recent first, limited
        results = sorted(results, key=lambda e: e.sequence, reverse=True)
        return results[: q.limit]

    def verify_chain(self) -> tuple[bool, int | None]:
        """Verify the hash chain integrity.

        Returns (valid, broken_at_sequence). broken_at_sequence is None if valid.
        """
        prev_hash = "0" * 64
        for entry in self._entries:
            entry_data = json.dumps({
                "seq": entry.sequence,
                "ts": entry.timestamp.isoformat(),
                "action": entry.action.value,
                "outcome": entry.outcome.value,
                "actor": entry.actor_id,
                "actor_type": entry.actor_type,
                "resource": f"{entry.resource_type}:{entry.resource_id}",
                "org_id": entry.org_id,
                "ip": entry.ip_address,
                "ua": entry.user_agent,
                "details": json.dumps(entry.details or {}, sort_keys=True),
            }, sort_keys=True)
            expected = _hash_entry(prev_hash, entry_data)
            if entry.chain_hash != expected:
                return False, entry.sequence
            prev_hash = entry.chain_hash
        return True, None

    def get_stats(self) -> AuditStats:
        """Get summary statistics."""
        actions: dict[str, int] = {}
        outcomes: dict[str, int] = {}
        actors: set[str] = set()

        for e in self._entries:
            actions[e.action.value] = actions.get(e.action.value, 0) + 1
            outcomes[e.outcome.value] = outcomes.get(e.outcome.value, 0) + 1
            if e.actor_id:
                actors.add(e.actor_id)

        return AuditStats(
            total_entries=len(self._entries),
            actions_breakdown=actions,
            outcomes_breakdown=outcomes,
            unique_actors=len(actors),
        )

    def export_jsonl(self, q: AuditQuery | None = None) -> str:
        """Export entries as JSON-lines."""
        entries = self.query(q) if q else self._entries
        lines = []
        for e in entries:
            lines.append(json.dumps({
                "sequence": e.sequence,
                "timestamp": e.timestamp.isoformat(),
                "action": e.action.value,
                "outcome": e.outcome.value,
                "actor_id": e.actor_id,
                "actor_type": e.actor_type,
                "resource_type": e.resource_type,
                "resource_id": e.resource_id,
                "org_id": e.org_id,
                "details": e.details,
                "chain_hash": e.chain_hash,
            }))
        return "\n".join(lines)

    @property
    def total_entries(self) -> int:
        return len(self._entries)
