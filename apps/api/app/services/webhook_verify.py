"""Webhook signature verification utility.

Used by app developers to verify incoming webhook payloads from OpenSkill.
Also used internally to sign outgoing webhooks.
"""

import hashlib
import hmac
import secrets


def generate_webhook_secret() -> tuple[str, str]:
    """Generate a webhook secret. Returns (raw_secret, hashed_secret)."""
    raw = f"whsec_{secrets.token_urlsafe(32)}"
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


def sign_payload(payload: bytes, secret: str) -> str:
    """Sign a webhook payload with HMAC-SHA256.

    Args:
        payload: The raw request body bytes
        secret: The webhook secret (raw, not hashed)

    Returns:
        Signature string in format "sha256=<hex>"
    """
    signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"sha256={signature}"


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify a webhook payload signature.

    Args:
        payload: The raw request body bytes
        signature: The X-OpenSkill-Signature header value
        secret: The webhook secret (raw, not hashed)

    Returns:
        True if signature is valid
    """
    if not signature.startswith("sha256="):
        return False
    expected = sign_payload(payload, secret)
    return hmac.compare_digest(signature, expected)
