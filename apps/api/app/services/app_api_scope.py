"""App API Scope — manage OAuth-style API scopes.

Manages API access scopes:
- Define available scopes with descriptions
- Assign scopes to API tokens
- Validate scope requirements
- Per-installation scoped definitions
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class APIScope:
    """An API scope definition."""

    scope_id: str
    name: str
    description: str
    category: str = "general"


@dataclass
class TokenScopes:
    """Scopes assigned to a token."""

    token_id: str
    scopes: set[str] = field(default_factory=set)

    def has_scope(self, scope_id: str) -> bool:
        return scope_id in self.scopes

    def has_all(self, required: list[str]) -> bool:
        return all(s in self.scopes for s in required)

    def has_any(self, required: list[str]) -> bool:
        return any(s in self.scopes for s in required)


class AppAPIScope:
    """Manage OAuth-style API scopes."""

    def __init__(self) -> None:
        self._scopes: dict[tuple[str, str], APIScope] = {}
        self._tokens: dict[tuple[str, str], TokenScopes] = {}

    def define_scope(
        self, installation_id: str, scope_id: str, name: str,
        description: str, category: str = "general",
    ) -> APIScope:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not scope_id:
            raise ValueError("scope_id is required")

        scope = APIScope(
            scope_id=scope_id, name=name,
            description=description, category=category,
        )
        self._scopes[(installation_id, scope_id)] = scope
        return scope

    def assign_scopes(
        self, installation_id: str, token_id: str, scopes: list[str],
    ) -> TokenScopes:
        # Validate all scopes exist
        for s in scopes:
            if (installation_id, s) not in self._scopes:
                raise KeyError(f"Scope {s} not defined")

        ts = TokenScopes(token_id=token_id, scopes=set(scopes))
        self._tokens[(installation_id, token_id)] = ts
        return ts

    def check_access(
        self, installation_id: str, token_id: str, required: list[str],
        mode: str = "all",
    ) -> bool:
        """Check if token has required scopes. mode: 'all' or 'any'."""
        ts = self._tokens.get((installation_id, token_id))
        if ts is None:
            return False
        if mode == "any":
            return ts.has_any(required)
        return ts.has_all(required)

    def list_scopes(self, installation_id: str, category: str | None = None) -> list[APIScope]:
        scopes = [s for (inst, _), s in self._scopes.items() if inst == installation_id]
        if category:
            scopes = [s for s in scopes if s.category == category]
        return scopes

    def token_scopes(self, installation_id: str, token_id: str) -> list[str]:
        ts = self._tokens.get((installation_id, token_id))
        return sorted(ts.scopes) if ts else []
