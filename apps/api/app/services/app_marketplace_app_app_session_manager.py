"""Session manager — active session tracking and revocation."""

import secrets
import hmac
import hashlib
import html
from datetime import datetime, timezone, timedelta

HMAC_KEY = secrets.token_bytes(32)


def create_session(*, user_id: str, device: str, ip: str) -> dict:
    token = secrets.token_urlsafe(48)
    sig = hmac.new(HMAC_KEY, token.encode(), hashlib.sha256).hexdigest()[:16]
    return {"token": token, "signature": sig, "user_id": user_id,
            "device": html.escape(device), "ip": ip,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "active": True}


def list_sessions(*, sessions: list[dict], current_token: str = "") -> dict:
    items = []
    for s in sessions:
        items.append({**s, "is_current": s.get("token", "") == current_token})
    active = sum(1 for s in items if s.get("active"))
    return {"sessions": items, "total": len(items), "active": active}


def revoke_session(*, sessions: list[dict], token: str) -> dict:
    for s in sessions:
        if s.get("token") == token:
            s["active"] = False
            return {"revoked": True, "token_prefix": token[:8]}
    return {"revoked": False, "error": "Session not found"}
