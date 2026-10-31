"""App Webhook Signer — sign and verify webhook payloads with HMAC-SHA256.

Manages webhook signing for installed apps:
- Generate signing secrets per installation
- Sign payloads with HMAC-SHA256
- Verify signatures with timing-safe comparison
- Timestamp-based replay protection
- Multiple secret rotation support
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()

DEFAULT_TOLERANCE_SECONDS = 300  # 5 minutes


@dataclass
class SigningSecret:
    """A webhook signing secret."""

    secret_id: str
    secret: str
    created_at: float = field(default_factory=time.time)
    active: bool = True


@dataclass
class SignedPayload:
    """A signed webhook payload."""

    signature: str
    timestamp: int
    body: str


@dataclass
class VerificationResult:
    """Result of verifying a webhook signature."""

    valid: bool
    reason: str = ""  # "valid", "invalid_signature", "expired", "no_secret"


class AppWebhookSigner:
    """Sign and verify webhook payloads with HMAC-SHA256."""

    def __init__(self, tolerance_seconds: int = DEFAULT_TOLERANCE_SECONDS) -> None:
        self._tolerance = tolerance_seconds
        # (installation_id, secret_id) → SigningSecret
        self._secrets: dict[tuple[str, str], SigningSecret] = {}

    def create_secret(
        self, installation_id: str, secret_id: str
    ) -> SigningSecret:
        """Generate a new signing secret."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not secret_id:
            raise ValueError("secret_id is required")

        key = (installation_id, secret_id)
        if key in self._secrets:
            raise ValueError(f"Secret {secret_id} already exists")

        raw = secrets.token_hex(32)
        secret = SigningSecret(secret_id=secret_id, secret=raw)
        self._secrets[key] = secret
        return secret

    def sign(
        self,
        installation_id: str,
        body: str,
        now: int | None = None,
    ) -> SignedPayload:
        """Sign a payload using the active secret."""
        secret = self._get_active_secret(installation_id)
        timestamp = now or int(time.time())
        signed_content = f"{timestamp}.{body}"
        sig = hmac.new(
            secret.secret.encode(),
            signed_content.encode(),
            hashlib.sha256,
        ).hexdigest()

        return SignedPayload(
            signature=f"v1={sig}",
            timestamp=timestamp,
            body=body,
        )

    def verify(
        self,
        installation_id: str,
        body: str,
        signature: str,
        timestamp: int,
        now: int | None = None,
    ) -> VerificationResult:
        """Verify a webhook signature."""
        now_ts = now or int(time.time())

        # Check replay window
        if abs(now_ts - timestamp) > self._tolerance:
            return VerificationResult(valid=False, reason="expired")

        # Try all active secrets (supports rotation)
        active_secrets = self._get_all_active(installation_id)
        if not active_secrets:
            return VerificationResult(valid=False, reason="no_secret")

        # Extract hash from "v1=<hex>"
        if not signature.startswith("v1="):
            return VerificationResult(valid=False, reason="invalid_signature")
        provided_hash = signature[3:]

        signed_content = f"{timestamp}.{body}"
        for sec in active_secrets:
            expected = hmac.new(
                sec.secret.encode(),
                signed_content.encode(),
                hashlib.sha256,
            ).hexdigest()
            if hmac.compare_digest(expected, provided_hash):
                return VerificationResult(valid=True, reason="valid")

        return VerificationResult(valid=False, reason="invalid_signature")

    def rotate_secret(
        self, installation_id: str, old_secret_id: str, new_secret_id: str
    ) -> SigningSecret:
        """Create a new secret and deactivate the old one."""
        old_key = (installation_id, old_secret_id)
        old = self._secrets.get(old_key)
        if old is None:
            raise KeyError(f"Secret {old_secret_id} not found")

        new_secret = self.create_secret(installation_id, new_secret_id)
        old.active = False
        return new_secret

    def revoke_secret(self, installation_id: str, secret_id: str) -> None:
        """Deactivate a secret."""
        key = (installation_id, secret_id)
        secret = self._secrets.get(key)
        if secret is None:
            raise KeyError(f"Secret {secret_id} not found")
        secret.active = False

    def list_secrets(self, installation_id: str) -> list[SigningSecret]:
        return [
            s for (inst, _), s in self._secrets.items()
            if inst == installation_id
        ]

    def _get_active_secret(self, installation_id: str) -> SigningSecret:
        active = self._get_all_active(installation_id)
        if not active:
            raise KeyError(f"No active secret for {installation_id}")
        return active[-1]  # newest

    def _get_all_active(self, installation_id: str) -> list[SigningSecret]:
        return [
            s for (inst, _), s in self._secrets.items()
            if inst == installation_id and s.active
        ]
