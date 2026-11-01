"""OAuth client credentials flow — server-to-server authentication."""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta


def generate_client_credentials() -> dict:
    """Generate OAuth client_id and client_secret."""
    client_id = f"osk_{secrets.token_urlsafe(24)}"
    client_secret = secrets.token_urlsafe(48)
    secret_hash = hashlib.sha256(client_secret.encode()).hexdigest()
    return {"client_id": client_id, "client_secret": client_secret, "secret_hash": secret_hash}


def verify_client_secret(secret: str, stored_hash: str) -> bool:
    """Verify a client secret against its stored hash."""
    computed = hashlib.sha256(secret.encode()).hexdigest()
    return hmac.compare_digest(computed, stored_hash)


def generate_access_token(*, client_id: str, scopes: list[str], ttl_seconds: int = 3600) -> dict:
    """Generate an access token for client credentials flow."""
    token = f"osk_at_{secrets.token_urlsafe(32)}"
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ttl_seconds,
        "scope": " ".join(sorted(scopes)),
        "issued_at": datetime.now(UTC).isoformat(),
    }
