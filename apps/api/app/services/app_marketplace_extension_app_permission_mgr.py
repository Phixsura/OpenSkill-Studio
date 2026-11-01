"""App Permission Manager — granular permission grants for installed apps."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


VALID_SCOPES = frozenset([
    "read:profile", "write:profile", "read:data", "write:data",
    "read:analytics", "admin:settings", "webhook:manage",
    "sandbox:execute", "connector:manage", "marketplace:publish",
])


@dataclass
class PermissionGrant:
    app_id: str
    user_id: str
    scopes: set[str] = field(default_factory=set)
    granted_at: float = 0.0
    expires_at: float = 0.0  # 0 = no expiry

    def __post_init__(self):
        if not self.granted_at:
            self.granted_at = time.time()


class AppPermissionMgrService:
    def __init__(self):
        self._grants: dict[str, PermissionGrant] = {}  # key: app_id:user_id

    def _key(self, app_id: str, user_id: str) -> str:
        return f"{app_id}:{user_id}"

    def grant(self, app_id: str, user_id: str, scopes: list[str],
              ttl_seconds: int = 0) -> PermissionGrant:
        valid = {s for s in scopes if s in VALID_SCOPES}
        if not valid:
            raise ValueError("No valid scopes provided")
        key = self._key(app_id, user_id)
        g = self._grants.get(key)
        if g:
            g.scopes |= valid
        else:
            g = PermissionGrant(app_id=app_id, user_id=user_id, scopes=valid)
            if ttl_seconds > 0:
                g.expires_at = time.time() + ttl_seconds
            self._grants[key] = g
        return g

    def revoke(self, app_id: str, user_id: str, scopes: list[str] | None = None) -> bool:
        key = self._key(app_id, user_id)
        g = self._grants.get(key)
        if not g:
            return False
        if scopes:
            g.scopes -= set(scopes)
            if not g.scopes:
                del self._grants[key]
        else:
            del self._grants[key]
        return True

    def check(self, app_id: str, user_id: str, scope: str) -> bool:
        key = self._key(app_id, user_id)
        g = self._grants.get(key)
        if not g:
            return False
        if g.expires_at != 0 and time.time() > g.expires_at:
            del self._grants[key]
            return False
        return scope in g.scopes

    def get_grants(self, user_id: str) -> list[PermissionGrant]:
        return [g for g in self._grants.values() if g.user_id == user_id]

    def get_app_users(self, app_id: str) -> list[PermissionGrant]:
        return [g for g in self._grants.values() if g.app_id == app_id]
