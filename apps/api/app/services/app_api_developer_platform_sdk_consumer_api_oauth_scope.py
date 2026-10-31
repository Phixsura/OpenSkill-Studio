"""Consumer OAuth Scope Manager — OAuth scope management with granular permissions."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class Scope:
    scope_id: str
    name: str
    description: str = ""
    category: str = "general"
    sensitive: bool = False


@dataclass
class ScopeGrant:
    consumer_id: str
    scopes: set[str] = field(default_factory=set)


@dataclass
class OAuthScopeManager:
    """Manage OAuth scopes with granular permission control."""

    _scopes: dict[str, Scope] = field(default_factory=dict)
    _grants: dict[str, ScopeGrant] = field(default_factory=dict)
    _scope_deps: dict[str, set[str]] = field(default_factory=dict)  # scope -> required scopes

    def register_scope(self, scope: Scope) -> dict:
        if scope.scope_id in self._scopes:
            raise ValueError(f"Scope {scope.scope_id} already exists")
        self._scopes[scope.scope_id] = scope
        logger.info("scope_registered", scope_id=scope.scope_id)
        return {"scope_id": scope.scope_id, "total": len(self._scopes)}

    def add_dependency(self, scope_id: str, requires: str) -> dict:
        if scope_id not in self._scopes or requires not in self._scopes:
            raise ValueError("Both scopes must exist")
        if scope_id == requires:
            raise ValueError("Scope cannot require itself")
        self._scope_deps.setdefault(scope_id, set()).add(requires)
        return {"scope_id": scope_id, "requires": requires}

    def grant(self, consumer_id: str, scope_ids: list[str]) -> dict:
        for sid in scope_ids:
            if sid not in self._scopes:
                raise ValueError(f"Scope {sid} not found")
        grant = self._grants.setdefault(consumer_id, ScopeGrant(consumer_id=consumer_id))
        # Include dependencies
        all_scopes = set(scope_ids)
        for sid in scope_ids:
            all_scopes.update(self._scope_deps.get(sid, set()))
        grant.scopes.update(all_scopes)
        logger.info("scopes_granted", consumer_id=consumer_id, count=len(all_scopes))
        return {"consumer_id": consumer_id, "granted": sorted(all_scopes),
                "total_scopes": len(grant.scopes)}

    def revoke(self, consumer_id: str, scope_ids: list[str]) -> dict:
        grant = self._grants.get(consumer_id)
        if not grant:
            return {"revoked": 0}
        before = len(grant.scopes)
        grant.scopes -= set(scope_ids)
        return {"revoked": before - len(grant.scopes), "remaining": len(grant.scopes)}

    def check(self, consumer_id: str, required_scopes: list[str]) -> dict:
        grant = self._grants.get(consumer_id)
        if not grant:
            return {"allowed": False, "reason": "no_grants", "missing": required_scopes}
        required = set(required_scopes)
        missing = required - grant.scopes
        if missing:
            return {"allowed": False, "reason": "insufficient_scopes",
                    "missing": sorted(missing)}
        return {"allowed": True, "matched": sorted(required)}

    def get_consumer_scopes(self, consumer_id: str) -> list[dict]:
        grant = self._grants.get(consumer_id)
        if not grant:
            return []
        return [
            {"scope_id": sid, "name": self._scopes[sid].name,
             "category": self._scopes[sid].category,
             "sensitive": self._scopes[sid].sensitive}
            for sid in sorted(grant.scopes) if sid in self._scopes
        ]

    def list_scopes(self, category: str | None = None) -> list[dict]:
        scopes = list(self._scopes.values())
        if category:
            scopes = [s for s in scopes if s.category == category]
        return [{"scope_id": s.scope_id, "name": s.name, "category": s.category,
                 "sensitive": s.sensitive} for s in scopes]

    def get_stats(self) -> dict:
        return {
            "total_scopes": len(self._scopes),
            "sensitive_scopes": sum(1 for s in self._scopes.values() if s.sensitive),
            "consumers_with_grants": len(self._grants),
        }
