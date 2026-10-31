"""Webhook Signature Verifier — HMAC signature verification with replay protection."""
from __future__ import annotations

import hashlib
import hmac
import time
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class SignatureVerifier:
    """Verify webhook signatures and prevent replay attacks."""

    _secrets: dict[str, str] = field(default_factory=dict)
    _seen_nonces: dict[str, float] = field(default_factory=dict)
    _tolerance_seconds: float = 300.0  # 5 minutes

    def register_secret(self, webhook_id: str, secret: str) -> dict:
        if not secret or len(secret) < 16:
            raise ValueError("Secret must be at least 16 characters")
        self._secrets[webhook_id] = secret
        logger.info("webhook_secret_registered", webhook_id=webhook_id)
        return {"webhook_id": webhook_id, "registered": True}

    def sign(self, webhook_id: str, payload: str, timestamp: float | None = None,
             nonce: str | None = None, algorithm: str = "sha256") -> dict:
        secret = self._secrets.get(webhook_id)
        if not secret:
            raise ValueError(f"No secret for webhook {webhook_id}")
        ts = timestamp or time.time()
        n = nonce or f"n_{int(ts * 1000)}"
        message = f"{ts}.{n}.{payload}"
        if algorithm == "sha256":
            sig = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
        elif algorithm == "sha512":
            sig = hmac.new(secret.encode(), message.encode(), hashlib.sha512).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        return {
            "signature": sig,
            "timestamp": ts,
            "nonce": n,
            "algorithm": algorithm,
            "header": f"t={ts},n={n},s={sig}",
        }

    def verify(self, webhook_id: str, payload: str, signature: str,
               timestamp: float, nonce: str, algorithm: str = "sha256",
               current_time: float | None = None) -> dict:
        secret = self._secrets.get(webhook_id)
        if not secret:
            return {"valid": False, "reason": "unknown_webhook"}
        now = current_time or time.time()
        age = abs(now - timestamp)
        if age > self._tolerance_seconds:
            return {"valid": False, "reason": "timestamp_expired", "age_seconds": round(age, 1)}
        # Replay protection
        if nonce in self._seen_nonces:
            return {"valid": False, "reason": "nonce_reused"}
        message = f"{timestamp}.{nonce}.{payload}"
        if algorithm == "sha256":
            expected = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
        elif algorithm == "sha512":
            expected = hmac.new(secret.encode(), message.encode(), hashlib.sha512).hexdigest()
        else:
            return {"valid": False, "reason": "unsupported_algorithm"}
        if not hmac.compare_digest(signature, expected):
            return {"valid": False, "reason": "signature_mismatch"}
        self._seen_nonces[nonce] = now
        logger.info("signature_verified", webhook_id=webhook_id)
        return {"valid": True, "algorithm": algorithm}

    def cleanup_nonces(self, max_age: float = 600.0, current_time: float | None = None) -> dict:
        now = current_time or time.time()
        expired = [n for n, t in self._seen_nonces.items() if now - t > max_age]
        for n in expired:
            del self._seen_nonces[n]
        return {"removed": len(expired), "remaining": len(self._seen_nonces)}

    def rotate_secret(self, webhook_id: str, new_secret: str) -> dict:
        if not new_secret or len(new_secret) < 16:
            raise ValueError("Secret must be at least 16 characters")
        old_existed = webhook_id in self._secrets
        self._secrets[webhook_id] = new_secret
        logger.info("secret_rotated", webhook_id=webhook_id)
        return {"webhook_id": webhook_id, "rotated": True, "had_previous": old_existed}
