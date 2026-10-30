"""API Consumer Payload Encryption — encrypt sensitive payload fields."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import base64
import structlog

log = structlog.get_logger()

@dataclass
class EncryptionConfig:
    consumer_id: str
    algorithm: str = "aes-256-gcm"
    encrypted_fields: list[str] = field(default_factory=list)
    key_fingerprint: str = ""

@dataclass
class EncryptionResult:
    original_field_count: int
    encrypted_field_count: int
    algorithm: str

VALID_ALGORITHMS = {"aes-256-gcm", "aes-256-cbc", "chacha20-poly1305"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiPayloadEncryption:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], EncryptionConfig] = {}
        self._stats: dict[str, dict[str, int]] = {}

    def configure(self, installation_id: str, config: EncryptionConfig) -> EncryptionConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if config.algorithm not in VALID_ALGORITHMS: raise ValueError(f"Invalid algorithm: {config.algorithm}")
        if not config.encrypted_fields: raise ValueError("At least one field to encrypt required")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def encrypt_fields(self, installation_id: str, consumer_id: str, payload: dict) -> tuple[dict, EncryptionResult]:
        config = self._configs.get((installation_id, consumer_id))
        if config is None: return payload, EncryptionResult(len(payload), 0, "none")
        result = dict(payload)
        encrypted_count = 0
        for field_name in config.encrypted_fields:
            if field_name in result:
                # Simulate encryption with base64 (real impl would use actual crypto)
                val = str(result[field_name])
                result[field_name] = f"enc:{base64.b64encode(val.encode()).decode()}"
                encrypted_count += 1
        stats = self._stats.setdefault(installation_id, {"encrypted": 0, "fields": 0})
        stats["encrypted"] += 1
        stats["fields"] += encrypted_count
        return result, EncryptionResult(len(payload), encrypted_count, config.algorithm)

    def stats(self, installation_id: str) -> dict[str, int]:
        return self._stats.get(installation_id, {"encrypted": 0, "fields": 0})

    def list_configs(self, installation_id: str) -> list[EncryptionConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
