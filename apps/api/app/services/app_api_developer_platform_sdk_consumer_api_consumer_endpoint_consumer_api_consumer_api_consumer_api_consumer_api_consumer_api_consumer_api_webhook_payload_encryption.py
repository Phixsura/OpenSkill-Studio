"""Consumer API Webhook Payload Encryption — encrypt webhook payloads before delivery."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import hashlib
import hmac
import base64
import structlog

log = structlog.get_logger()

@dataclass
class EncryptionConfig:
    webhook_id: str
    consumer_id: str
    algorithm: str = "aes-256-gcm"  # "aes-256-gcm", "aes-256-cbc", "none"
    key_version: int = 1
    enabled: bool = True

@dataclass
class EncryptedPayload:
    ciphertext: str  # base64 encoded
    algorithm: str
    key_version: int
    iv: str  # base64 encoded initialization vector

VALID_ALGORITHMS = {"aes-256-gcm", "aes-256-cbc", "none"}

class AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiWebhookPayloadEncryption:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str, str], EncryptionConfig] = {}

    def configure(self, installation_id: str, config: EncryptionConfig) -> EncryptionConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.algorithm not in VALID_ALGORITHMS:
            raise ValueError(f"Invalid algorithm: {config.algorithm}")
        if config.key_version < 1:
            raise ValueError("key_version must be positive")
        self._configs[(installation_id, config.consumer_id, config.webhook_id)] = config
        return config

    def encrypt(self, installation_id: str, consumer_id: str, webhook_id: str, payload: str) -> EncryptedPayload | None:
        config = self._configs.get((installation_id, consumer_id, webhook_id))
        if not config or not config.enabled or config.algorithm == "none":
            return None
        # Simulated encryption for demo — in production use cryptography library
        iv = hashlib.sha256(f"{installation_id}:{webhook_id}:{len(payload)}".encode()).hexdigest()[:24]
        ciphertext = base64.b64encode(payload.encode()).decode()
        return EncryptedPayload(ciphertext=ciphertext, algorithm=config.algorithm, key_version=config.key_version, iv=iv)

    def is_encryption_enabled(self, installation_id: str, consumer_id: str, webhook_id: str) -> bool:
        config = self._configs.get((installation_id, consumer_id, webhook_id))
        return config is not None and config.enabled and config.algorithm != "none"

    def get_config(self, installation_id: str, consumer_id: str, webhook_id: str) -> EncryptionConfig | None:
        return self._configs.get((installation_id, consumer_id, webhook_id))

    def list_configs(self, installation_id: str, consumer_id: str) -> list[EncryptionConfig]:
        return [c for (inst, cid, _), c in self._configs.items() if inst == installation_id and cid == consumer_id]
