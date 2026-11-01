"""Consumer API Key Permission Matrix — manage per-key per-endpoint permissions."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class PermissionEntry:
    key_id: str
    endpoint_path: str
    method: str  # "GET", "POST", etc. or "*"
    allowed: bool = True

@dataclass
class PermissionMatrix:
    consumer_id: str
    entries: list[PermissionEntry] = field(default_factory=list)

@dataclass
class AccessCheck:
    allowed: bool
    key_id: str
    endpoint: str
    method: str
    reason: str  # "explicit_allow", "explicit_deny", "default"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiKeyPermissionMatrix:
    def __init__(self, default_allow: bool = False) -> None:
        self._entries: dict[tuple[str, str, str, str, str], PermissionEntry] = {}
        self._default = default_allow

    def set_permission(self, installation_id: str, consumer_id: str, entry: PermissionEntry) -> PermissionEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, consumer_id, entry.key_id, entry.endpoint_path, entry.method.upper())
        self._entries[key] = entry
        return entry

    def check(self, installation_id: str, consumer_id: str, key_id: str, endpoint: str, method: str) -> AccessCheck:
        # Check exact match
        exact = self._entries.get((installation_id, consumer_id, key_id, endpoint, method.upper()))
        if exact:
            return AccessCheck(allowed=exact.allowed, key_id=key_id, endpoint=endpoint, method=method, reason="explicit_allow" if exact.allowed else "explicit_deny")
        # Check wildcard method
        wildcard = self._entries.get((installation_id, consumer_id, key_id, endpoint, "*"))
        if wildcard:
            return AccessCheck(allowed=wildcard.allowed, key_id=key_id, endpoint=endpoint, method=method, reason="explicit_allow" if wildcard.allowed else "explicit_deny")
        return AccessCheck(allowed=self._default, key_id=key_id, endpoint=endpoint, method=method, reason="default")

    def get_matrix(self, installation_id: str, consumer_id: str, key_id: str) -> list[PermissionEntry]:
        return [e for (inst, cid, kid, _, _), e in self._entries.items() if inst == installation_id and cid == consumer_id and kid == key_id]

    def revoke_all(self, installation_id: str, consumer_id: str, key_id: str) -> int:
        to_remove = [k for k in self._entries if k[0] == installation_id and k[1] == consumer_id and k[2] == key_id]
        for k in to_remove:
            del self._entries[k]
        return len(to_remove)
