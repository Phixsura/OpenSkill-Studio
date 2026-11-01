"""API Consumer Request Signing — sign outgoing API requests for authenticity."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import hmac
import time
import structlog

log = structlog.get_logger()

@dataclass
class SigningConfig:
    consumer_id: str
    algorithm: str = "hmac-sha256"
    signed_headers: list[str] = field(default_factory=lambda: ["content-type", "x-timestamp"])
    include_body: bool = True

@dataclass
class SignedRequest:
    signature: str
    signed_at: float
    algorithm: str
    headers_signed: list[str]

VALID_ALGORITHMS = {"hmac-sha256", "hmac-sha512"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestSigning:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], SigningConfig] = {}
        self._secrets: dict[tuple[str, str], str] = {}
        self._stats: dict[str, dict[str, int]] = {}

    def configure(self, installation_id: str, consumer_id: str, secret: str, algorithm: str = "hmac-sha256", signed_headers: list[str] | None = None) -> SigningConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if algorithm not in VALID_ALGORITHMS: raise ValueError(f"Invalid algorithm: {algorithm}")
        if len(secret) < 16: raise ValueError("Secret must be at least 16 characters")
        config = SigningConfig(consumer_id=consumer_id, algorithm=algorithm, signed_headers=signed_headers or ["content-type", "x-timestamp"])
        self._configs[(installation_id, consumer_id)] = config
        self._secrets[(installation_id, consumer_id)] = secret
        return config

    def sign(self, installation_id: str, consumer_id: str, method: str, path: str, headers: dict[str, str], body: str = "") -> SignedRequest:
        config = self._configs.get((installation_id, consumer_id))
        if config is None: raise KeyError(f"No signing config for {consumer_id}")
        secret = self._secrets[(installation_id, consumer_id)]
        now = time.time()
        # Build canonical string
        header_vals = ";".join(headers.get(h, "") for h in sorted(config.signed_headers))
        canonical = f"{method.upper()}\n{path}\n{header_vals}"
        if config.include_body: canonical += f"\n{hashlib.sha256(body.encode()).hexdigest()}"
        algo = hashlib.sha512 if config.algorithm == "hmac-sha512" else hashlib.sha256
        sig = hmac.new(secret.encode(), canonical.encode(), algo).hexdigest()
        stats = self._stats.setdefault(installation_id, {"signed": 0})
        stats["signed"] += 1
        return SignedRequest(signature=sig, signed_at=now, algorithm=config.algorithm, headers_signed=config.signed_headers)

    def verify(self, installation_id: str, consumer_id: str, method: str, path: str, headers: dict[str, str], body: str, provided_sig: str) -> bool:
        result = self.sign(installation_id, consumer_id, method, path, headers, body)
        return hmac.compare_digest(result.signature, provided_sig)

    def list_configs(self, installation_id: str) -> list[SigningConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
