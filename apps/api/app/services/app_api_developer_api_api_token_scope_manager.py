"""App API Developer API Token Scope Manager — fine-grained token permissions."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

VALID_SCOPES = {"read", "write", "admin", "webhooks:read", "webhooks:write", "users:read", "users:write", "billing:read", "billing:write"}

@dataclass
class TokenScope:
    token_id: str
    name: str
    scopes: set[str] = field(default_factory=set)
    revoked: bool = False

class AppAPIDeveloperAPIApiTokenScopeManager:
    def __init__(self) -> None:
        self._tokens: dict[tuple[str, str], TokenScope] = {}

    def create(self, installation_id: str, token_id: str, name: str, scopes: list[str]) -> TokenScope:
        if not installation_id: raise ValueError("installation_id is required")
        if not scopes: raise ValueError("at least one scope is required")
        invalid = set(scopes) - VALID_SCOPES
        if invalid: raise ValueError(f"Invalid scopes: {invalid}")
        key = (installation_id, token_id)
        if key in self._tokens: raise ValueError(f"Token {token_id} exists")
        t = TokenScope(token_id=token_id, name=name, scopes=set(scopes))
        self._tokens[key] = t
        return t

    def check(self, installation_id: str, token_id: str, required_scope: str) -> bool:
        t = self._get(installation_id, token_id)
        if t.revoked: return False
        if "admin" in t.scopes: return True
        return required_scope in t.scopes

    def revoke(self, installation_id: str, token_id: str) -> TokenScope:
        t = self._get(installation_id, token_id)
        t.revoked = True
        return t

    def list_tokens(self, installation_id: str, include_revoked: bool = False) -> list[TokenScope]:
        tokens = [t for (inst, _), t in self._tokens.items() if inst == installation_id]
        if not include_revoked: tokens = [t for t in tokens if not t.revoked]
        return tokens

    def _get(self, installation_id: str, token_id: str) -> TokenScope:
        key = (installation_id, token_id)
        t = self._tokens.get(key)
        if t is None: raise KeyError(f"Token {token_id} not found")
        return t
