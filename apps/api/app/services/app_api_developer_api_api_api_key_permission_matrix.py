"""App API Developer API Key Permission Matrix — fine-grained endpoint permissions per key."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class KeyPermission:
    key_id: str
    allowed_endpoints: dict[str, set[str]] = field(default_factory=dict)  # endpoint -> methods
    denied_endpoints: set[str] = field(default_factory=set)

class AppAPIDeveloperAPIApiApiKeyPermissionMatrix:
    def __init__(self) -> None:
        self._perms: dict[tuple[str, str], KeyPermission] = {}

    def grant(self, installation_id: str, key_id: str, endpoint: str, methods: list[str]) -> KeyPermission:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, key_id)
        if key not in self._perms:
            self._perms[key] = KeyPermission(key_id=key_id)
        p = self._perms[key]
        if endpoint in p.denied_endpoints: raise ValueError(f"{endpoint} is denied for this key")
        p.allowed_endpoints[endpoint] = set(m.upper() for m in methods)
        return p

    def deny(self, installation_id: str, key_id: str, endpoint: str) -> KeyPermission:
        key = (installation_id, key_id)
        if key not in self._perms:
            self._perms[key] = KeyPermission(key_id=key_id)
        p = self._perms[key]
        p.denied_endpoints.add(endpoint)
        p.allowed_endpoints.pop(endpoint, None)
        return p

    def check(self, installation_id: str, key_id: str, endpoint: str, method: str) -> bool:
        key = (installation_id, key_id)
        p = self._perms.get(key)
        if p is None: return False
        if endpoint in p.denied_endpoints: return False
        allowed_methods = p.allowed_endpoints.get(endpoint)
        if allowed_methods is None: return False
        return method.upper() in allowed_methods

    def list_permissions(self, installation_id: str, key_id: str) -> KeyPermission | None:
        return self._perms.get((installation_id, key_id))

    def all_keys(self, installation_id: str) -> list[KeyPermission]:
        return [p for (inst, _), p in self._perms.items() if inst == installation_id]
