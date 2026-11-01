"""OAuth flow — authorization code flow state management."""

import secrets
import hashlib
import hmac
import html
from urllib.parse import urlencode, urlparse


HMAC_KEY = secrets.token_bytes(32)


def generate_auth_url(*, client_id: str, redirect_uri: str,
                       scopes: list[str], provider: str = "openskill") -> dict:
    parsed = urlparse(redirect_uri)
    if parsed.scheme not in ("https", "http"):
        return {"error": "Invalid redirect URI scheme"}
    state = secrets.token_urlsafe(32)
    state_sig = hmac.new(HMAC_KEY, state.encode(), hashlib.sha256).hexdigest()[:16]
    params = urlencode({
        "client_id": client_id, "redirect_uri": redirect_uri,
        "scope": " ".join(scopes), "state": state, "response_type": "code",
    })
    base = f"https://auth.openskill.dev/oauth/authorize" if provider == "openskill" else f"https://accounts.google.com/o/oauth2/v2/auth"
    return {"url": f"{base}?{params}", "state": state, "state_sig": state_sig,
            "scopes": scopes, "provider": provider}


def verify_state(*, state: str, signature: str) -> bool:
    expected = hmac.new(HMAC_KEY, state.encode(), hashlib.sha256).hexdigest()[:16]
    return hmac.compare_digest(expected, signature)
