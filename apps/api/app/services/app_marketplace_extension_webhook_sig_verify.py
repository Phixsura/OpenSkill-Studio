"""Webhook Signature Verifier — verify webhook authenticity with replay protection.

Implements:
- HMAC-SHA256 signature computation and verification
- Timestamp-based replay protection (reject old webhooks)
- Multiple signing versions (v1, v2) for rotation
- Constant-time signature comparison
- Tolerance window for clock skew
"""
from __future__ import annotations
import hashlib
import hmac
import time


class WebhookSigError(Exception):
    pass


class WebhookSigVerifyService:
    DEFAULT_TOLERANCE = 300  # 5 minutes

    def __init__(self):
        self._secrets: dict[str, list[str]] = {}  # endpoint_id -> [secrets] (newest first)

    def register_secret(self, endpoint_id: str, secret: str) -> None:
        if endpoint_id not in self._secrets:
            self._secrets[endpoint_id] = []
        self._secrets[endpoint_id].insert(0, secret)  # newest first

    def sign(self, secret: str, payload: str, timestamp: int | None = None) -> str:
        """Generate signature header value."""
        ts = timestamp or int(time.time())
        signed_payload = f"{ts}.{payload}"
        sig = hmac.new(secret.encode(), signed_payload.encode(),
                       hashlib.sha256).hexdigest()
        return f"t={ts},v1={sig}"

    def verify(self, endpoint_id: str, payload: str, signature_header: str,
               tolerance: int = 0) -> dict:
        """Verify webhook signature. Returns parsed claims or raises."""
        tolerance = tolerance or self.DEFAULT_TOLERANCE
        secrets = self._secrets.get(endpoint_id)
        if not secrets:
            raise WebhookSigError("No secrets registered for endpoint")

        # Parse signature header
        parsed = self._parse_header(signature_header)
        timestamp = parsed.get("t")
        signatures = parsed.get("signatures", [])

        if not timestamp:
            raise WebhookSigError("Missing timestamp in signature")
        if not signatures:
            raise WebhookSigError("Missing signature value")

        # Replay protection
        ts = int(timestamp)
        now = int(time.time())
        age = abs(now - ts)
        if age > tolerance:
            raise WebhookSigError(
                f"Timestamp too old: {age}s exceeds {tolerance}s tolerance")

        # Try each registered secret (supports rotation)
        signed_payload = f"{ts}.{payload}"
        for secret in secrets:
            expected = hmac.new(secret.encode(), signed_payload.encode(),
                                hashlib.sha256).hexdigest()
            for sig in signatures:
                if hmac.compare_digest(expected, sig):
                    return {"verified": True, "timestamp": ts, "age_seconds": age}

        raise WebhookSigError("Signature verification failed")

    def _parse_header(self, header: str) -> dict:
        """Parse 't=123,v1=abc,v1=def' format."""
        result: dict = {"signatures": []}
        for part in header.split(","):
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key == "t":
                result["t"] = value
            elif key.startswith("v"):
                result["signatures"].append(value)
        return result

    def rotate_secret(self, endpoint_id: str, new_secret: str,
                      keep_old: int = 2) -> None:
        """Add new secret, keep last N for grace period."""
        self.register_secret(endpoint_id, new_secret)
        if len(self._secrets[endpoint_id]) > keep_old:
            self._secrets[endpoint_id] = self._secrets[endpoint_id][:keep_old]
