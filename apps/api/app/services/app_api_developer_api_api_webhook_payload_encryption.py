"""App API Developer Webhook Payload Encryption — encrypt payloads at rest and in transit."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import base64
import structlog

log = structlog.get_logger()

@dataclass
class EncryptionConfig:
    destination: str
    algorithm: str  # "aes-256-gcm", "chacha20-poly1305"
    key_fingerprint: str
    enabled: bool = True
    payloads_encrypted: int = 0
    total_bytes_encrypted: int = 0

class AppAPIDeveloperAPIApiWebhookPayloadEncryption:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], EncryptionConfig] = {}

    def configure(self, installation_id: str, destination: str, algorithm: str, encryption_key: str) -> EncryptionConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if algorithm not in ("aes-256-gcm", "chacha20-poly1305"): raise ValueError(f"Unsupported algorithm: {algorithm}")
        if len(encryption_key) < 32: raise ValueError("encryption key must be at least 32 bytes")
        fingerprint = hashlib.sha256(encryption_key.encode()).hexdigest()[:16]
        key = (installation_id, destination)
        c = EncryptionConfig(destination=destination, algorithm=algorithm, key_fingerprint=fingerprint)
        self._configs[key] = c
        return c

    def encrypt(self, installation_id: str, destination: str, payload: str) -> tuple[str, int]:
        """Simulate encryption — returns base64 'ciphertext' and original size."""
        key = (installation_id, destination)
        c = self._configs.get(key)
        if c is None: raise KeyError(f"No encryption config for {destination}")
        if not c.enabled: raise ValueError("Encryption disabled")
        payload_bytes = payload.encode("utf-8")
        # Simulate: in production this would use actual crypto
        ciphertext = base64.b64encode(payload_bytes).decode()
        c.payloads_encrypted += 1
        c.total_bytes_encrypted += len(payload_bytes)
        return ciphertext, len(payload_bytes)

    def stats(self, installation_id: str) -> dict[str, int]:
        configs = [c for (inst, _), c in self._configs.items() if inst == installation_id]
        return {"destinations": len(configs), "payloads_encrypted": sum(c.payloads_encrypted for c in configs), "bytes_encrypted": sum(c.total_bytes_encrypted for c in configs)}

    def toggle(self, installation_id: str, destination: str, enabled: bool) -> EncryptionConfig:
        key = (installation_id, destination)
        c = self._configs.get(key)
        if c is None: raise KeyError(f"No config for {destination}")
        c.enabled = enabled
        return c

    def all_configs(self, installation_id: str) -> list[EncryptionConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
