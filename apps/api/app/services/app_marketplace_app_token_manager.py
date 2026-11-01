"""Token manager — manage OAuth tokens and refresh cycles."""

import secrets
import hashlib
from datetime import datetime, timedelta


def issue_token(*, client_id: str, scopes: list[str],
                  expires_in_sec: int = 3600) -> dict:
    access_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(32)
    now = datetime.utcnow()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": expires_in_sec,
        "expires_at": (now + timedelta(seconds=expires_in_sec)).isoformat(),
        "scopes": sorted(scopes),
        "client_id": client_id,
        "token_hash": hashlib.sha256(access_token.encode()).hexdigest()[:16],
    }


def refresh_token(*, refresh_tok: str, client_id: str) -> dict:
    if len(refresh_tok) < 20:
        return {"error": "Invalid refresh token"}
    return issue_token(client_id=client_id, scopes=["read", "write"])


def revoke_token(*, token_hash: str) -> dict:
    return {"revoked": True, "token_hash": token_hash,
            "revoked_at": datetime.utcnow().isoformat()}
