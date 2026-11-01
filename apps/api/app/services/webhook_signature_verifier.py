"""Webhook Signature Verifier — validate inbound webhook payloads from external services.

Verifies HMAC signatures on incoming webhook payloads:
- Multiple algorithm support: SHA-256, SHA-1 (legacy), SHA-512
- Constant-time comparison to prevent timing attacks
- Timestamp validation to prevent replay attacks
- Signature header parsing (multiple formats)
- Configurable tolerance window
- Verification audit logging
"""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()


class Algorithm(str, Enum):
    SHA256 = "sha256"
    SHA1 = "sha1"
    SHA512 = "sha512"


class VerifyResult(str, Enum):
    VALID = "valid"
    INVALID_SIGNATURE = "invalid_signature"
    EXPIRED_TIMESTAMP = "expired_timestamp"
    MISSING_SIGNATURE = "missing_signature"
    UNSUPPORTED_ALGORITHM = "unsupported_algorithm"
    MALFORMED_HEADER = "malformed_header"


HASH_FUNCS = {
    Algorithm.SHA256: hashlib.sha256,
    Algorithm.SHA1: hashlib.sha1,
    Algorithm.SHA512: hashlib.sha512,
}

DEFAULT_TOLERANCE_SECONDS = 300  # 5 minutes


@dataclass
class VerificationResult:
    """Result of verifying a webhook signature."""

    result: VerifyResult
    algorithm: str | None = None
    timestamp_age_seconds: float | None = None
    details: str = ""


@dataclass
class VerificationLog:
    """Audit log entry for a webhook verification attempt."""

    source: str
    result: VerifyResult
    algorithm: str | None
    timestamp: datetime
    ip_address: str | None = None


def compute_hmac(payload: bytes, secret: str, algorithm: Algorithm = Algorithm.SHA256) -> str:
    """Compute HMAC signature of a payload."""
    hash_func = HASH_FUNCS.get(algorithm)
    if hash_func is None:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    return hmac.new(secret.encode("utf-8"), payload, hash_func).hexdigest()


def compute_signed_payload(timestamp: int, payload: bytes) -> bytes:
    """Build the signed payload: timestamp.payload (Stripe-style)."""
    return f"{timestamp}.".encode("utf-8") + payload


def parse_signature_header(header: str) -> dict[str, str]:
    """Parse a signature header into components.

    Supports formats:
    - "sha256=<hex>"                          (GitHub style)
    - "t=<timestamp>,v1=<hex>"                (Stripe style)
    - "v0=<hex>"                              (Slack style)
    - Plain hex string                        (simple)
    """
    parts: dict[str, str] = {}

    if "=" not in header:
        # Plain hex
        parts["signature"] = header.strip()
        return parts

    if "," in header:
        # Stripe style: t=123,v1=abc
        for segment in header.split(","):
            segment = segment.strip()
            if "=" in segment:
                key, value = segment.split("=", 1)
                parts[key.strip()] = value.strip()
    else:
        # GitHub style: sha256=abc or v0=abc
        key, value = header.split("=", 1)
        key = key.strip().lower()
        if key in ("sha256", "sha1", "sha512"):
            parts["algorithm"] = key
            parts["signature"] = value.strip()
        else:
            parts[key] = value.strip()

    return parts


class WebhookSignatureVerifier:
    """Verify webhook signatures with replay protection."""

    def __init__(self, secret: str, algorithm: Algorithm = Algorithm.SHA256,
                 tolerance_seconds: int = DEFAULT_TOLERANCE_SECONDS):
        self._secret = secret
        self._algorithm = algorithm
        self._tolerance = tolerance_seconds
        self._log: list[VerificationLog] = []

    def verify(self, payload: bytes, signature_header: str,
               timestamp: int | None = None, now: float | None = None,
               source: str = "unknown") -> VerificationResult:
        """Verify a webhook payload signature.

        Args:
            payload: Raw request body bytes
            signature_header: The signature header value
            timestamp: Unix timestamp from header (for replay protection)
            now: Current time override (for testing)
            source: Identifier for the webhook source (for logging)
        """
        now = now or time.time()

        if not signature_header:
            self._record(source, VerifyResult.MISSING_SIGNATURE, None)
            return VerificationResult(
                result=VerifyResult.MISSING_SIGNATURE,
                details="No signature header provided",
            )

        # Parse the header
        parsed = parse_signature_header(signature_header)

        # Extract algorithm if specified
        algo_str = parsed.get("algorithm")
        try:
            algo = Algorithm(algo_str) if algo_str else self._algorithm
        except ValueError:
            self._record(source, VerifyResult.UNSUPPORTED_ALGORITHM, algo_str)
            return VerificationResult(
                result=VerifyResult.UNSUPPORTED_ALGORITHM,
                algorithm=algo_str,
                details=f"Unsupported algorithm: {algo_str}",
            )

        # Determine the signature to verify against
        expected_sig = parsed.get("signature") or parsed.get("v1") or parsed.get("v0")
        if not expected_sig:
            self._record(source, VerifyResult.MALFORMED_HEADER, algo.value)
            return VerificationResult(
                result=VerifyResult.MALFORMED_HEADER,
                algorithm=algo.value,
                details="Could not extract signature from header",
            )

        # Timestamp validation (replay protection)
        ts = timestamp
        if ts is None and "t" in parsed:
            try:
                ts = int(parsed["t"])
            except ValueError:
                pass

        timestamp_age: float | None = None
        if ts is not None:
            timestamp_age = now - ts
            if abs(timestamp_age) > self._tolerance:
                self._record(source, VerifyResult.EXPIRED_TIMESTAMP, algo.value)
                return VerificationResult(
                    result=VerifyResult.EXPIRED_TIMESTAMP,
                    algorithm=algo.value,
                    timestamp_age_seconds=timestamp_age,
                    details=f"Timestamp too old: {timestamp_age:.0f}s (tolerance: {self._tolerance}s)",
                )

        # Compute expected signature
        if ts is not None:
            signed_payload = compute_signed_payload(ts, payload)
        else:
            signed_payload = payload

        computed = compute_hmac(signed_payload, self._secret, algo)

        # Constant-time comparison
        if hmac.compare_digest(computed, expected_sig):
            self._record(source, VerifyResult.VALID, algo.value)
            return VerificationResult(
                result=VerifyResult.VALID,
                algorithm=algo.value,
                timestamp_age_seconds=timestamp_age,
                details="Signature verified",
            )
        else:
            self._record(source, VerifyResult.INVALID_SIGNATURE, algo.value)
            return VerificationResult(
                result=VerifyResult.INVALID_SIGNATURE,
                algorithm=algo.value,
                timestamp_age_seconds=timestamp_age,
                details="Signature mismatch",
            )

    def verify_github(self, payload: bytes, signature_header: str,
                      source: str = "github") -> VerificationResult:
        """Verify a GitHub-style signature (X-Hub-Signature-256: sha256=<hex>)."""
        return self.verify(payload, signature_header, source=source)

    def verify_stripe(self, payload: bytes, signature_header: str,
                      source: str = "stripe", now: float | None = None) -> VerificationResult:
        """Verify a Stripe-style signature (Stripe-Signature: t=<ts>,v1=<hex>)."""
        parsed = parse_signature_header(signature_header)
        ts = None
        if "t" in parsed:
            try:
                ts = int(parsed["t"])
            except ValueError:
                pass
        return self.verify(payload, signature_header, timestamp=ts, now=now, source=source)

    def get_audit_log(self, limit: int = 50) -> list[VerificationLog]:
        return self._log[-limit:]

    def _record(self, source: str, result: VerifyResult, algorithm: str | None) -> None:
        entry = VerificationLog(
            source=source,
            result=result,
            algorithm=algorithm,
            timestamp=datetime.now(UTC),
        )
        self._log.append(entry)
        if result != VerifyResult.VALID:
            log.warning("webhook.verification_failed", source=source, result=result.value)
