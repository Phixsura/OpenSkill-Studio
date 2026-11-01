"""API key scope validator — check if a token's scopes permit an action."""
from __future__ import annotations

SCOPE_HIERARCHY = {
    "admin": ["read", "write", "delete", "admin"],
    "write": ["read", "write"],
    "read": ["read"],
    "delete": ["read", "delete"],
}


def validate_scopes(*, granted_scopes: list[str], required_scope: str) -> dict:
    effective = set()
    for scope in granted_scopes:
        effective.update(SCOPE_HIERARCHY.get(scope, [scope]))
    allowed = required_scope in effective
    return {
        "allowed": allowed, "required": required_scope,
        "granted": granted_scopes, "effective": sorted(effective),
        "reason": "scope_granted" if allowed else "insufficient_scope",
    }


def check_endpoint_access(*, scopes: list[str], method: str, path: str) -> dict:
    method_scope = {"GET": "read", "HEAD": "read", "OPTIONS": "read",
                     "POST": "write", "PUT": "write", "PATCH": "write",
                     "DELETE": "delete"}.get(method.upper(), "read")
    return validate_scopes(granted_scopes=scopes, required_scope=method_scope)
