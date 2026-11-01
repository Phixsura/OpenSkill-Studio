"""API Key Scope Manager — assign and enforce fine-grained permission scopes per API key."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class KeyScope:
    key_id: str
    scopes: set[str] = field(default_factory=set)  # e.g. {"read:users", "write:orders"}
    deny_scopes: set[str] = field(default_factory=set)  # explicit denials override grants

@dataclass
class ScopeCheckResult:
    allowed: bool
    key_id: str
    requested: str
    reason: str

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyScopeManager:
    def __init__(self) -> None:
        self._keys: dict[tuple[str, str], KeyScope] = {}

    def set_scopes(self, installation_id: str, key_scope: KeyScope) -> KeyScope:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, key_scope.key_id)
        self._keys[key] = key_scope
        log.info("scopes_set", installation_id=installation_id, key_id=key_scope.key_id, count=len(key_scope.scopes))
        return key_scope

    def get_scopes(self, installation_id: str, key_id: str) -> KeyScope | None:
        return self._keys.get((installation_id, key_id))

    def grant(self, installation_id: str, key_id: str, scope: str) -> KeyScope:
        key = (installation_id, key_id)
        ks = self._keys.get(key)
        if not ks:
            ks = KeyScope(key_id=key_id)
            self._keys[key] = ks
        ks.scopes.add(scope)
        ks.deny_scopes.discard(scope)
        return ks

    def deny(self, installation_id: str, key_id: str, scope: str) -> KeyScope:
        key = (installation_id, key_id)
        ks = self._keys.get(key)
        if not ks:
            ks = KeyScope(key_id=key_id)
            self._keys[key] = ks
        ks.deny_scopes.add(scope)
        ks.scopes.discard(scope)
        return ks

    def check(self, installation_id: str, key_id: str, scope: str) -> ScopeCheckResult:
        ks = self._keys.get((installation_id, key_id))
        if not ks:
            return ScopeCheckResult(allowed=False, key_id=key_id, requested=scope, reason="key_not_found")
        if scope in ks.deny_scopes:
            return ScopeCheckResult(allowed=False, key_id=key_id, requested=scope, reason="explicitly_denied")
        if scope in ks.scopes:
            return ScopeCheckResult(allowed=True, key_id=key_id, requested=scope, reason="granted")
        # Check wildcard: "read:*" grants "read:users"
        prefix = scope.split(":")[0] + ":*"
        if prefix in ks.scopes and prefix not in ks.deny_scopes:
            return ScopeCheckResult(allowed=True, key_id=key_id, requested=scope, reason="wildcard_match")
        return ScopeCheckResult(allowed=False, key_id=key_id, requested=scope, reason="not_granted")

    def list_keys(self, installation_id: str) -> list[KeyScope]:
        return [ks for (inst, _), ks in self._keys.items() if inst == installation_id]
