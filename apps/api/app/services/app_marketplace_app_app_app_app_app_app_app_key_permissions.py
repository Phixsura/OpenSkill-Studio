"""API key permissions — scope-aware key validation for endpoints."""
from __future__ import annotations

ENDPOINT_SCOPES = {
    "GET /api/v1/apps": ["read:apps"],
    "POST /api/v1/apps": ["write:apps"],
    "DELETE /api/v1/apps/:id": ["delete:apps"],
    "GET /api/v1/analytics": ["read:analytics"],
    "POST /api/v1/webhooks": ["write:webhooks"],
    "GET /api/v1/users": ["read:users"],
    "POST /api/v1/deploy": ["deploy"],
}


def check_key_access(*, key_scopes: list[str], method: str, path: str) -> dict:
    endpoint = f"{method} {path}"
    required = ENDPOINT_SCOPES.get(endpoint, [])
    if not required:
        return {"allowed": True, "reason": "no_restriction"}
    has_all = all(s in key_scopes for s in required)
    missing = [s for s in required if s not in key_scopes]
    return {"allowed": has_all, "required": required, "missing": missing,
            "reason": "granted" if has_all else "insufficient_scopes"}


def list_endpoint_scopes() -> list[dict]:
    return [{"endpoint": k, "scopes": v} for k, v in sorted(ENDPOINT_SCOPES.items())]
