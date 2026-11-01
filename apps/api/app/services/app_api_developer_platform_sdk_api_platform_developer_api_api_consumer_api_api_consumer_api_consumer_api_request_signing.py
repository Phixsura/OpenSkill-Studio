"""Consumer API Request Signing — sign outbound API requests with HMAC."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import hashlib
import hmac
import structlog

log = structlog.get_logger()

@dataclass
class SigningConfig:
    consumer_id: str
    algorithm: str = "sha256"  # "sha256", "sha512"
    header_name: str = "X-Signature"
    timestamp_header: str = "X-Timestamp"
    include_body: bool = True
    include_path: bool = True

@dataclass
class SignedRequest:
    signature: str
    timestamp: int
    headers: dict[str, str]

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestSigning:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], SigningConfig] = {}
        self._secrets: dict[tuple[str, str], str] = {}  # store only for demo; production uses HSM

    def configure(self, installation_id: str, config: SigningConfig, secret: str) -> SigningConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.algorithm not in ("sha256", "sha512"):
            raise ValueError(f"Unsupported algorithm: {config.algorithm}")
        if len(secret) < 32:
            raise ValueError("Secret must be at least 32 characters")
        self._configs[(installation_id, config.consumer_id)] = config
        self._secrets[(installation_id, config.consumer_id)] = secret
        return config

    def sign(self, installation_id: str, consumer_id: str, method: str, path: str, body: str, timestamp: int | None = None) -> SignedRequest:
        config = self._configs.get((installation_id, consumer_id))
        secret = self._secrets.get((installation_id, consumer_id))
        if not config or not secret:
            raise ValueError("Signing not configured")
        if timestamp is None:
            timestamp = int(datetime.utcnow().timestamp())
        parts = [str(timestamp), method.upper()]
        if config.include_path:
            parts.append(path)
        if config.include_body:
            parts.append(body)
        message = "\n".join(parts)
        algo = hashlib.sha256 if config.algorithm == "sha256" else hashlib.sha512
        sig = hmac.new(secret.encode(), message.encode(), algo).hexdigest()
        headers = {config.header_name: sig, config.timestamp_header: str(timestamp)}
        return SignedRequest(signature=sig, timestamp=timestamp, headers=headers)

    def verify(self, installation_id: str, consumer_id: str, method: str, path: str, body: str, signature: str, timestamp: int) -> bool:
        try:
            expected = self.sign(installation_id, consumer_id, method, path, body, timestamp)
            return hmac.compare_digest(expected.signature, signature)
        except ValueError:
            return False

    def get_config(self, installation_id: str, consumer_id: str) -> SigningConfig | None:
        return self._configs.get((installation_id, consumer_id))
