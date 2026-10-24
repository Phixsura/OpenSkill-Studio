"""Developer API key manager — create, rotate, revoke API keys."""

import secrets
import hashlib
from datetime import datetime, timedelta


def create_api_key(*, developer_id: str, label: str, scopes: list[str],
                     expires_days: int = 90) -> dict:
    if not label or len(label) > 64:
        return {"success": False, "error": "Label must be 1-64 characters"}
    valid_scopes = {"read", "write", "admin", "webhook", "analytics"}
    invalid = set(scopes) - valid_scopes
    if invalid:
        return {"success": False, "error": f"Invalid scopes: {', '.join(sorted(invalid))}"}
    raw_key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    prefix = raw_key[:8]
    return {
        "success": True,
        "key": raw_key,
        "key_prefix": prefix,
        "key_hash": key_hash,
        "label": label,
        "scopes": sorted(scopes),
        "expires_at": (datetime.utcnow() + timedelta(days=expires_days)).isoformat(),
        "warning": "Store this key securely — it won't be shown again.",
    }


def revoke_api_key(*, key_prefix: str) -> dict:
    return {"success": True, "revoked": key_prefix, "message": "Key revoked successfully"}


def list_api_keys(*, developer_id: str) -> dict:
    return {
        "developer_id": developer_id,
        "keys": [
            {"prefix": "sk_abc1", "label": "Production", "scopes": ["read", "write"],
             "created_at": "2026-01-01T00:00:00", "last_used": "2026-10-20T12:00:00", "status": "active"},
            {"prefix": "sk_xyz2", "label": "Staging", "scopes": ["read"],
             "created_at": "2026-06-15T00:00:00", "last_used": None, "status": "active"},
        ],
        "total": 2,
    }
