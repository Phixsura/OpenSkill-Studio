"""App API Developer API Key Audit Trail — track all API key operations."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class KeyAuditEntry:
    entry_id: str
    key_id: str
    action: str  # "created", "rotated", "revoked", "suspended", "reactivated", "used"
    actor: str
    timestamp: float = field(default_factory=time.time)
    ip_address: str = ""

class AppAPIDeveloperPlatformSDKApiKeyAuditTrail:
    def __init__(self, max_entries: int = 10000) -> None:
        self._max = max(1, max_entries)
        self._entries: dict[str, list[KeyAuditEntry]] = {}

    def log(self, installation_id: str, entry_id: str, key_id: str, action: str, actor: str, ip_address: str = "") -> KeyAuditEntry:
        if not installation_id: raise ValueError("installation_id is required")
        valid = {"created", "rotated", "revoked", "suspended", "reactivated", "used"}
        if action not in valid: raise ValueError(f"Invalid action: {action}")
        e = KeyAuditEntry(entry_id=entry_id, key_id=key_id, action=action, actor=actor, ip_address=ip_address)
        entries = self._entries.setdefault(installation_id, [])
        entries.append(e)
        if len(entries) > self._max: self._entries[installation_id] = entries[-self._max:]
        return e

    def by_key(self, installation_id: str, key_id: str) -> list[KeyAuditEntry]:
        return [e for e in self._entries.get(installation_id, []) if e.key_id == key_id]

    def by_actor(self, installation_id: str, actor: str) -> list[KeyAuditEntry]:
        return [e for e in self._entries.get(installation_id, []) if e.actor == actor]

    def recent(self, installation_id: str, limit: int = 50) -> list[KeyAuditEntry]:
        return list(reversed(self._entries.get(installation_id, [])[-limit:]))

    def action_counts(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for e in self._entries.get(installation_id, []):
            counts[e.action] = counts.get(e.action, 0) + 1
        return counts
