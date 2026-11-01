"""API key creation wizard — guided key creation with scope selection."""
from __future__ import annotations
import secrets
import hmac
import hashlib
import html

_HMAC_KEY = secrets.token_bytes(32)

AVAILABLE_SCOPES = [
    {"id": "read:apps", "label": "Read Apps", "description": "List and view applications", "risk": "low"},
    {"id": "write:apps", "label": "Manage Apps", "description": "Create, update, delete apps", "risk": "medium"},
    {"id": "read:analytics", "label": "Read Analytics", "description": "View usage data", "risk": "low"},
    {"id": "webhooks", "label": "Webhooks", "description": "Manage webhook endpoints", "risk": "medium"},
    {"id": "deploy", "label": "Deploy", "description": "Deploy to environments", "risk": "high"},
    {"id": "admin", "label": "Admin", "description": "Full administrative access", "risk": "critical"},
]


def create_key(*, name: str, scopes: list[str], expires_days: int = 365) -> dict:
    valid_ids = {s["id"] for s in AVAILABLE_SCOPES}
    unknown = set(scopes) - valid_ids
    if unknown:
        return {"error": f"Unknown scopes: {sorted(unknown)}"}
    raw = f"sk_live_{secrets.token_urlsafe(32)}"
    integrity = hmac.new(_HMAC_KEY, raw.encode(), hashlib.sha256).hexdigest()[:16]
    selected = [s for s in AVAILABLE_SCOPES if s["id"] in scopes]
    max_risk = "critical" if any(s["risk"] == "critical" for s in selected) else \
               "high" if any(s["risk"] == "high" for s in selected) else \
               "medium" if any(s["risk"] == "medium" for s in selected) else "low"
    return {
        "key": raw, "name": html.escape(name), "scopes": [s["id"] for s in selected],
        "scope_count": len(selected), "max_risk": max_risk,
        "expires_days": expires_days, "integrity": integrity,
        "warning": "This key has admin access!" if "admin" in scopes else None,
    }


def list_scopes() -> list[dict]:
    return AVAILABLE_SCOPES
