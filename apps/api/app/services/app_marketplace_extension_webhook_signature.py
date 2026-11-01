"""Webhook Signature Verifier — HMAC-based webhook payload verification.

Signs outgoing webhooks with HMAC-SHA256 and verifies incoming webhook
signatures with constant-time comparison, timestamp validation, and
replay protection via nonce tracking.
"""
from __future__ import annotations
import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass, field


@dataclass
class WebhookSecret:
    extension_id: str
    secret_key: str
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()


class WebhookSignatureService:
    """Signs and verifies webhook payloads with HMAC-SHA256."""

    TIMESTAMP_TOLERANCE = 300  # 5 minutes

    def __init__(self):
        self._secrets: dict[str, WebhookSecret] = {}
        self._used_nonces: dict[str, set[str]] = {}

    def create_secret(self, extension_id: str) -> WebhookSecret:
        key = f"whsec_{secrets.token_urlsafe(32)}"
        ws = WebhookSecret(extension_id=extension_id, secret_key=key)
        self._secrets[extension_id] = ws
        self._used_nonces[extension_id] = set()
        return ws

    def rotate_secret(self, extension_id: str) -> WebhookSecret | None:
        if extension_id not in self._secrets:
            return None
        return self.create_secret(extension_id)

    def sign(self, extension_id: str, payload: str,
             timestamp: float | None = None) -> dict | None:
        ws = self._secrets.get(extension_id)
        if not ws:
            return None
        ts = timestamp or time.time()
        nonce = secrets.token_urlsafe(16)
        message = f"{int(ts)}.{nonce}.{payload}"
        signature = hmac.new(
            ws.secret_key.encode(), message.encode(), hashlib.sha256
        ).hexdigest()
        return {
            "signature": f"v1={signature}",
            "timestamp": int(ts),
            "nonce": nonce,
        }

    def verify(self, extension_id: str, payload: str,
               signature: str, timestamp: int, nonce: str) -> dict:
        ws = self._secrets.get(extension_id)
        if not ws:
            return {"valid": False, "reason": "No secret configured"}

        # Timestamp check
        now = time.time()
        if abs(now - timestamp) > self.TIMESTAMP_TOLERANCE:
            return {"valid": False, "reason": "Timestamp expired"}

        # Replay protection
        nonces = self._used_nonces.get(extension_id, set())
        if nonce in nonces:
            return {"valid": False, "reason": "Nonce already used (replay)"}

        # Compute expected signature
        message = f"{timestamp}.{nonce}.{payload}"
        expected = hmac.new(
            ws.secret_key.encode(), message.encode(), hashlib.sha256
        ).hexdigest()
        expected_sig = f"v1={expected}"

        # Constant-time comparison
        if not hmac.compare_digest(signature, expected_sig):
            return {"valid": False, "reason": "Invalid signature"}

        nonces.add(nonce)
        return {"valid": True}

    def get_secret(self, extension_id: str) -> str | None:
        ws = self._secrets.get(extension_id)
        return ws.secret_key if ws else None
