"""App Webhook Signature — sign and verify webhook payloads.

Manages webhook payload signing:
- HMAC-SHA256 signature generation
- Signature verification with timing-safe comparison
- Multiple signing keys (rotation support)
- Per-installation scoped keys
"""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class SigningKey:
    """A webhook signing key."""

    key_id: str
    secret: str
    active: bool = True
    created_at: float = field(default_factory=time.time)


@dataclass
class SignatureResult:
    """Result of signing a payload."""

    signature: str
    key_id: str
    algorithm: str = "hmac-sha256"


class AppWebhookSignature:
    """Sign and verify webhook payloads."""

    def __init__(self) -> None:
        self._keys: dict[tuple[str, str], SigningKey] = {}

    def add_key(
        self, installation_id: str, key_id: str, secret: str,
    ) -> SigningKey:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not key_id:
            raise ValueError("key_id is required")
        if not secret:
            raise ValueError("secret is required")
        if len(secret) < 16:
            raise ValueError("secret must be at least 16 characters")

        key = SigningKey(key_id=key_id, secret=secret)
        self._keys[(installation_id, key_id)] = key
        return key

    def sign(
        self, installation_id: str, key_id: str, payload: str,
    ) -> SignatureResult:
        key = self._get_key(installation_id, key_id)
        if not key.active:
            raise ValueError(f"Key {key_id} is not active")

        sig = hmac.new(
            key.secret.encode(), payload.encode(), hashlib.sha256,
        ).hexdigest()

        return SignatureResult(signature=sig, key_id=key_id)

    def verify(
        self, installation_id: str, payload: str, signature: str,
    ) -> bool:
        """Verify signature against all active keys (timing-safe)."""
        active_keys = [
            k for (inst, _), k in self._keys.items()
            if inst == installation_id and k.active
        ]
        for key in active_keys:
            expected = hmac.new(
                key.secret.encode(), payload.encode(), hashlib.sha256,
            ).hexdigest()
            if hmac.compare_digest(expected, signature):
                return True
        return False

    def deactivate_key(self, installation_id: str, key_id: str) -> SigningKey:
        key = self._get_key(installation_id, key_id)
        key.active = False
        return key

    def list_keys(self, installation_id: str, active_only: bool = False) -> list[SigningKey]:
        keys = [k for (inst, _), k in self._keys.items() if inst == installation_id]
        if active_only:
            keys = [k for k in keys if k.active]
        return keys

    def _get_key(self, installation_id: str, key_id: str) -> SigningKey:
        key = (installation_id, key_id)
        k = self._keys.get(key)
        if k is None:
            raise KeyError(f"Key {key_id} not found")
        return k
