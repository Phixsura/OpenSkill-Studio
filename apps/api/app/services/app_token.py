"""Short-lived scoped token generation for sandbox execution.

When a sandbox function runs, it gets a temporary API token scoped
to the installation's granted permissions with a short TTL.
"""

import hashlib
import hmac
import json
import time
from datetime import UTC, datetime, timedelta

import structlog

log = structlog.get_logger()

DEFAULT_TTL_SECONDS = 300  # 5 minutes


def generate_scoped_token(
    *,
    app_id: str,
    installation_id: str,
    org_id: str,
    scopes: list[str],
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    signing_key: str = "",
) -> dict:
    """Generate a short-lived scoped token for sandbox execution.

    Returns a dict with token, expires_at, and scopes.
    The token is an HMAC-signed JSON payload — not a JWT,
    since these are internal-only and never leave the sandbox boundary.
    """
    now = datetime.now(UTC)
    expires_at = now + timedelta(seconds=ttl_seconds)

    payload = {
        "app_id": app_id,
        "installation_id": installation_id,
        "org_id": org_id,
        "scopes": sorted(scopes),
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }

    payload_bytes = json.dumps(payload, sort_keys=True).encode()
    signature = hmac.new(
        signing_key.encode() or b"default-dev-key",
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()

    return {
        "token": f"osk_tmp_{signature[:32]}",
        "payload": payload,
        "signature": signature,
        "expires_at": expires_at.isoformat(),
        "ttl_seconds": ttl_seconds,
        "scopes": sorted(scopes),
    }


def validate_scoped_token(
    token_data: dict,
    *,
    required_scope: str | None = None,
) -> dict:
    """Validate a scoped token is not expired and has required scope.

    Returns {"valid": True/False, "reason": str, ...}
    """
    now = int(datetime.now(UTC).timestamp())
    exp = token_data.get("payload", {}).get("exp", 0)

    if now > exp:
        return {"valid": False, "reason": "token_expired"}

    if required_scope:
        scopes = token_data.get("scopes", [])
        if required_scope not in scopes:
            return {"valid": False, "reason": "insufficient_scope", "required": required_scope}

    return {
        "valid": True,
        "app_id": token_data.get("payload", {}).get("app_id"),
        "installation_id": token_data.get("payload", {}).get("installation_id"),
        "org_id": token_data.get("payload", {}).get("org_id"),
        "scopes": token_data.get("scopes", []),
    }
