"""OAuth token introspection — check token validity and metadata."""

from datetime import UTC, datetime


def introspect_token(token_data: dict) -> dict:
    """Introspect an access token — RFC 7662 style response."""
    if not token_data:
        return {"active": False}
    
    exp = token_data.get("expires_at") or token_data.get("exp")
    if exp:
        try:
            if isinstance(exp, (int, float)):
                expired = datetime.now(UTC).timestamp() > exp
            else:
                expired = datetime.now(UTC) > datetime.fromisoformat(str(exp).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            expired = True
        if expired:
            return {"active": False, "reason": "expired"}
    
    return {
        "active": True,
        "scope": token_data.get("scope", ""),
        "client_id": token_data.get("client_id", ""),
        "token_type": "bearer",
        "exp": exp,
    }
