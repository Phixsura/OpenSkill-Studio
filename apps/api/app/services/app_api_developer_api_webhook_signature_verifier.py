"""App API Developer Webhook Signature Verifier — verify webhook delivery signatures."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import hmac
import structlog

log = structlog.get_logger()

@dataclass
class VerificationResult:
    delivery_id: str
    algorithm: str
    valid: bool
    reason: str = ""

class AppAPIDeveloperAPIWebhookSignatureVerifier:
    def __init__(self) -> None:
        self._secrets: dict[tuple[str, str], str] = {}  # (inst, dest) -> secret
        self._results: dict[str, list[VerificationResult]] = {}

    def register_secret(self, installation_id: str, destination: str, secret: str) -> None:
        if not installation_id: raise ValueError("installation_id is required")
        if len(secret) < 16: raise ValueError("secret must be at least 16 characters")
        self._secrets[(installation_id, destination)] = secret

    def verify(self, installation_id: str, destination: str, delivery_id: str, payload: str, signature: str, algorithm: str = "sha256") -> VerificationResult:
        if algorithm not in ("sha256", "sha1"): raise ValueError("unsupported algorithm")
        secret = self._secrets.get((installation_id, destination))
        if secret is None:
            r = VerificationResult(delivery_id=delivery_id, algorithm=algorithm, valid=False, reason="no secret registered")
            self._results.setdefault(installation_id, []).append(r)
            return r
        if algorithm == "sha256":
            expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        else:
            expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha1).hexdigest()
        valid = hmac.compare_digest(signature, expected)
        r = VerificationResult(delivery_id=delivery_id, algorithm=algorithm, valid=valid, reason="" if valid else "signature mismatch")
        self._results.setdefault(installation_id, []).append(r)
        return r

    def stats(self, installation_id: str) -> dict[str, int]:
        results = self._results.get(installation_id, [])
        return {"total": len(results), "valid": sum(1 for r in results if r.valid), "invalid": sum(1 for r in results if not r.valid)}
