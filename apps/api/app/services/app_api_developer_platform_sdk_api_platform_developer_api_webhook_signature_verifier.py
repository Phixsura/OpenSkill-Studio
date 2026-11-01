"""API Webhook Signature Verifier — verify webhook payload signatures."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import hmac
import time
import structlog

log = structlog.get_logger()

@dataclass
class SignatureConfig:
    consumer_id: str
    algorithm: str = "sha256"  # "sha256", "sha512"
    header_name: str = "X-Webhook-Signature"
    timestamp_tolerance_s: int = 300

@dataclass
class VerificationResult:
    valid: bool
    reason: str = ""  # "ok", "invalid_signature", "expired_timestamp", "missing_header", "unknown_consumer"

VALID_ALGORITHMS = {"sha256", "sha512"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookSignatureVerifier:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], SignatureConfig] = {}
        self._secrets: dict[tuple[str, str], str] = {}  # hashed secrets
        self._stats: dict[tuple[str, str], dict[str, int]] = {}

    def configure(self, installation_id: str, consumer_id: str, secret: str, algorithm: str = "sha256", timestamp_tolerance_s: int = 300) -> SignatureConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if algorithm not in VALID_ALGORITHMS: raise ValueError(f"Invalid algorithm: {algorithm}")
        if len(secret) < 16: raise ValueError("Secret must be at least 16 characters")
        config = SignatureConfig(consumer_id=consumer_id, algorithm=algorithm, timestamp_tolerance_s=timestamp_tolerance_s)
        self._configs[(installation_id, consumer_id)] = config
        self._secrets[(installation_id, consumer_id)] = secret
        self._stats[(installation_id, consumer_id)] = {"valid": 0, "invalid": 0}
        return config

    def sign(self, installation_id: str, consumer_id: str, payload: str, timestamp: int | None = None) -> str:
        secret = self._secrets.get((installation_id, consumer_id))
        if secret is None: raise KeyError(f"No config for {consumer_id}")
        config = self._configs[(installation_id, consumer_id)]
        ts = timestamp or int(time.time())
        message = f"{ts}.{payload}"
        algo = hashlib.sha512 if config.algorithm == "sha512" else hashlib.sha256
        sig = hmac.new(secret.encode(), message.encode(), algo).hexdigest()
        return f"t={ts},v1={sig}"

    def verify(self, installation_id: str, consumer_id: str, payload: str, signature: str) -> VerificationResult:
        config = self._configs.get((installation_id, consumer_id))
        if config is None: return VerificationResult(valid=False, reason="unknown_consumer")
        try:
            parts = dict(p.split("=", 1) for p in signature.split(","))
        except ValueError:
            self._stats[(installation_id, consumer_id)]["invalid"] += 1
            return VerificationResult(valid=False, reason="invalid_signature")
        ts = int(parts.get("t", "0"))
        sig = parts.get("v1", "")
        if abs(time.time() - ts) > config.timestamp_tolerance_s:
            self._stats[(installation_id, consumer_id)]["invalid"] += 1
            return VerificationResult(valid=False, reason="expired_timestamp")
        expected = self.sign(installation_id, consumer_id, payload, ts)
        expected_sig = dict(p.split("=", 1) for p in expected.split(",")).get("v1", "")
        if hmac.compare_digest(sig, expected_sig):
            self._stats[(installation_id, consumer_id)]["valid"] += 1
            return VerificationResult(valid=True, reason="ok")
        self._stats[(installation_id, consumer_id)]["invalid"] += 1
        return VerificationResult(valid=False, reason="invalid_signature")

    def get_stats(self, installation_id: str, consumer_id: str) -> dict[str, int]:
        return self._stats.get((installation_id, consumer_id), {"valid": 0, "invalid": 0})

    def list_configs(self, installation_id: str) -> list[SignatureConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
