"""OAuth flow manager — manage OAuth 2.0 authorization flows for apps."""

import hashlib
import secrets
from datetime import datetime, timezone, timedelta


def generate_authorization_url(*, client_id: str, redirect_uri: str, scopes: list[str],
                                  state: str | None = None) -> dict:
    state = state or secrets.token_urlsafe(32)
    scope_str = " ".join(scopes)
    url = (f"https://auth.openskill.dev/authorize?"
           f"client_id={client_id}&redirect_uri={redirect_uri}"
           f"&response_type=code&scope={scope_str}&state={state}")
    return {"url": url, "state": state}


def exchange_code_for_token(*, code: str, client_id: str, client_secret: str) -> dict:
    # Simulated exchange
    token = secrets.token_urlsafe(48)
    refresh = secrets.token_urlsafe(48)
    return {
        "access_token": token, "refresh_token": refresh,
        "token_type": "Bearer", "expires_in": 3600, "scope": "read write",
    }


def refresh_access_token(*, refresh_token: str, client_id: str) -> dict:
    new_token = secrets.token_urlsafe(48)
    return {"access_token": new_token, "token_type": "Bearer", "expires_in": 3600}


def revoke_token(*, token: str) -> dict:
    return {"revoked": True, "revoked_at": datetime.now(timezone.utc).isoformat()}
