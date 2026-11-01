"""Webhook Signature Verifier — verify HMAC signatures on incoming webhook payloads."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import hmac
import time
import structlog

log = structlog.get_logger()

@dataclass
class VerificationResult:
    valid: bool
    reason: str  # "valid", "invalid_signature", "expired_timestamp", "missing_header", "replay_detected"
    age_seconds: float | None = None

@dataclass
class VerifierConfig:
    webhook_id: str
    secret: str
    algorithm: str = "sha256"  # "sha256", "sha512"
    tolerance_seconds: int = 300  # 5 min default
    replay_window: int = 1000  # track last N signatures

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSignatureVerifier:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], VerifierConfig] = {}
        self._seen: dict[tuple[str, str], list[str]] = {}

    def set_config(self, installation_id: str, config: VerifierConfig) -> VerifierConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.algorithm not in ("sha256", "sha512"):
            raise ValueError(f"Unsupported algorithm: {config.algorithm}")
        self._configs[(installation_id, config.webhook_id)] = config
        return config

    def sign(self, installation_id: str, webhook_id: str, timestamp: int, body: str) -> str:
        config = self._configs.get((installation_id, webhook_id))
        if not config:
            raise ValueError("Config not found")
        message = f"{timestamp}.{body}"
        algo = hashlib.sha256 if config.algorithm == "sha256" else hashlib.sha512
        return hmac.new(config.secret.encode(), message.encode(), algo).hexdigest()

    def verify(self, installation_id: str, webhook_id: str, timestamp: int, body: str, signature: str, now: int | None = None) -> VerificationResult:
        config = self._configs.get((installation_id, webhook_id))
        if not config:
            return VerificationResult(valid=False, reason="missing_header")
        if now is None:
            now = int(time.time())
        age = abs(now - timestamp)
        if age > config.tolerance_seconds:
            return VerificationResult(valid=False, reason="expired_timestamp", age_seconds=float(age))
        expected = self.sign(installation_id, webhook_id, timestamp, body)
        if not hmac.compare_digest(expected, signature):
            return VerificationResult(valid=False, reason="invalid_signature")
        # Replay detection
        key = (installation_id, webhook_id)
        if key not in self._seen:
            self._seen[key] = []
        if signature in self._seen[key]:
            return VerificationResult(valid=False, reason="replay_detected")
        self._seen[key].append(signature)
        if len(self._seen[key]) > config.replay_window:
            self._seen[key] = self._seen[key][-config.replay_window:]
        return VerificationResult(valid=True, reason="valid", age_seconds=float(age))
