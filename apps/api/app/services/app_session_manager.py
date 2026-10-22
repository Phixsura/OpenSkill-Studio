"""OAuth session manager — track active OAuth sessions and tokens."""

from datetime import UTC, datetime, timedelta
from collections import defaultdict

_sessions: dict[str, dict] = {}
_auth_codes: dict[str, dict] = {}


def create_auth_code(*, client_id: str, redirect_uri: str, scopes: list[str], user_id: str, state: str) -> str:
    """Create an OAuth authorization code."""
    import secrets
    code = secrets.token_urlsafe(32)
    _auth_codes[code] = {
        "client_id": client_id, "redirect_uri": redirect_uri,
        "scopes": scopes, "user_id": user_id, "state": state,
        "created_at": datetime.now(UTC).isoformat(),
        "expires_at": (datetime.now(UTC) + timedelta(minutes=10)).isoformat(),
        "used": False,
    }
    return code


def consume_auth_code(code: str, *, client_id: str, redirect_uri: str) -> dict | None:
    """Consume an authorization code (one-time use, expiry enforced, redirect_uri bound)."""
    entry = _auth_codes.get(code)
    if not entry:
        return None
    if entry["used"]:
        _auth_codes.pop(code, None)
        return None
    # Enforce expiry
    if datetime.fromisoformat(entry["expires_at"]) < datetime.now(UTC):
        _auth_codes.pop(code, None)
        return None
    # Bind client_id + redirect_uri
    if entry["client_id"] != client_id or entry["redirect_uri"] != redirect_uri:
        return None
    # Delete rather than flag (prevent replay)
    _auth_codes.pop(code, None)
    return entry


def revoke_session(session_id: str) -> bool:
    """Revoke an active session."""
    return _sessions.pop(session_id, None) is not None
