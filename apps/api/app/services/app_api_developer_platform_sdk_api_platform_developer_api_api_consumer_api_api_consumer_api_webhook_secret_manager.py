"""API Consumer Webhook Secret Manager — manage webhook signing secrets securely."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import secrets
import time
import structlog

log = structlog.get_logger()

@dataclass
class WebhookSecret:
    secret_id: str
    consumer_id: str
    secret_hash: str
    masked_value: str
    created_at: float = field(default_factory=time.time)
    rotated: bool = False
    version: int = 1

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSecretManager:
    def __init__(self) -> None:
        self._secrets: dict[tuple[str, str], WebhookSecret] = {}

    def generate_secret(self, installation_id: str, consumer_id: str) -> dict[str, str]:
        if not installation_id: raise ValueError("installation_id is required")
        raw = secrets.token_urlsafe(32)
        secret_hash = hashlib.sha256(raw.encode()).hexdigest()
        masked = "whsec_***" + raw[-4:]
        key = (installation_id, consumer_id)
        existing = self._secrets.get(key)
        version = (existing.version + 1) if existing else 1
        if existing: existing.rotated = True
        ws = WebhookSecret(secret_id=f"ws-{secrets.token_hex(8)}", consumer_id=consumer_id, secret_hash=secret_hash, masked_value=masked, version=version)
        self._secrets[key] = ws
        return {"secret": raw, "secret_id": ws.secret_id, "masked": masked, "version": version}

    def verify(self, installation_id: str, consumer_id: str, raw_secret: str) -> bool:
        ws = self._secrets.get((installation_id, consumer_id))
        if ws is None: return False
        return hashlib.sha256(raw_secret.encode()).hexdigest() == ws.secret_hash

    def get_masked(self, installation_id: str, consumer_id: str) -> str | None:
        ws = self._secrets.get((installation_id, consumer_id))
        return ws.masked_value if ws else None

    def current_version(self, installation_id: str, consumer_id: str) -> int:
        ws = self._secrets.get((installation_id, consumer_id))
        return ws.version if ws else 0

    def list_secrets(self, installation_id: str) -> list[WebhookSecret]:
        return [s for (inst, _), s in self._secrets.items() if inst == installation_id]
