"""Invite manager — team invitation with role assignment."""

import secrets
import html
import hmac
import hashlib
import re
from datetime import datetime, timezone, timedelta

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
HMAC_KEY = secrets.token_bytes(32)
VALID_ROLES = {"viewer", "editor", "admin"}


def create_invite(*, email: str, role: str, inviter: str, expires_hours: int = 72) -> dict:
    if not EMAIL_RE.match(email):
        return {"error": "Invalid email format"}
    if role not in VALID_ROLES:
        return {"error": f"Invalid role. Must be one of: {', '.join(sorted(VALID_ROLES))}"}
    token = secrets.token_urlsafe(32)
    sig = hmac.new(HMAC_KEY, token.encode(), hashlib.sha256).hexdigest()[:16]
    expires = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    return {"token": token, "signature": sig, "email": email, "role": role,
            "inviter": html.escape(inviter), "expires_at": expires.isoformat(),
            "status": "pending"}


def verify_invite_token(*, token: str, signature: str) -> bool:
    expected = hmac.new(HMAC_KEY, token.encode(), hashlib.sha256).hexdigest()[:16]
    return hmac.compare_digest(expected, signature)
