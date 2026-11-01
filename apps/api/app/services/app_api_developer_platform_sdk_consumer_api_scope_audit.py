"""Consumer API Key Scope Audit — audit key scope usage and over-permissions."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class KeyScopeInfo:
    key_id: str
    consumer_id: str
    granted_scopes: set[str] = field(default_factory=set)
    used_scopes: set[str] = field(default_factory=set)


@dataclass
class ScopeAudit:
    """Audit API key scope usage to detect over-permissioned keys."""

    _keys: dict[str, KeyScopeInfo] = field(default_factory=dict)

    def register_key(self, key_id: str, consumer_id: str,
                     granted_scopes: list[str]) -> dict:
        if key_id in self._keys:
            raise ValueError(f"Key {key_id} already registered")
        self._keys[key_id] = KeyScopeInfo(
            key_id=key_id, consumer_id=consumer_id,
            granted_scopes=set(granted_scopes),
        )
        return {"key_id": key_id, "granted": len(granted_scopes)}

    def record_usage(self, key_id: str, scope: str) -> dict:
        info = self._keys.get(key_id)
        if not info:
            raise ValueError(f"Key {key_id} not registered")
        info.used_scopes.add(scope)
        in_grant = scope in info.granted_scopes
        if not in_grant:
            logger.warning("scope_not_granted", key_id=key_id, scope=scope)
        return {"key_id": key_id, "scope": scope, "granted": in_grant}

    def audit_key(self, key_id: str) -> dict:
        info = self._keys.get(key_id)
        if not info:
            return {"key_id": key_id, "error": "not_found"}
        unused = sorted(info.granted_scopes - info.used_scopes)
        used_outside = sorted(info.used_scopes - info.granted_scopes)
        over_perm_pct = round(len(unused) / len(info.granted_scopes) * 100, 1) if info.granted_scopes else 0
        if over_perm_pct > 50:
            recommendation = "reduce_scopes"
        elif used_outside:
            recommendation = "expand_grant"
        else:
            recommendation = "optimal"
        return {
            "key_id": key_id,
            "consumer_id": info.consumer_id,
            "granted": sorted(info.granted_scopes),
            "used": sorted(info.used_scopes),
            "unused_scopes": unused,
            "used_outside_grant": used_outside,
            "over_permission_pct": over_perm_pct,
            "recommendation": recommendation,
        }

    def audit_all(self) -> list[dict]:
        results = [self.audit_key(kid) for kid in self._keys]
        results.sort(key=lambda x: x.get("over_permission_pct", 0), reverse=True)
        return results

    def get_over_permissioned(self, threshold_pct: float = 50.0) -> list[dict]:
        return [
            a for a in self.audit_all()
            if a.get("over_permission_pct", 0) >= threshold_pct
        ]

    def get_stats(self) -> dict:
        audits = self.audit_all()
        total = len(audits)
        over = sum(1 for a in audits if a.get("over_permission_pct", 0) > 50)
        optimal = sum(1 for a in audits if a.get("recommendation") == "optimal")
        return {
            "total_keys": total,
            "over_permissioned": over,
            "optimal": optimal,
            "needs_expansion": sum(1 for a in audits if a.get("recommendation") == "expand_grant"),
        }
