"""Webhook Secret Rotation — rotate webhook signing secrets with grace period."""
from __future__ import annotations
from dataclasses import dataclass
import secrets
import time
import hmac
import hashlib


@dataclass
class WebhookSecret:
    secret_id: str
    secret: str
    created_at: float
    expires_at: float  # 0 = no expiry
    active: bool = True


class WebhookSecretRotService:
    GRACE_PERIOD = 300  # 5 minutes

    def __init__(self):
        self._secrets: dict[str, list[WebhookSecret]] = {}  # ext_id -> secrets
        self._counter = 0

    def create(self, extension_id: str) -> WebhookSecret:
        self._counter += 1
        ws = WebhookSecret(
            secret_id=f"whsec-{self._counter}",
            secret=secrets.token_urlsafe(32),
            created_at=time.time(), expires_at=0)
        if extension_id not in self._secrets:
            self._secrets[extension_id] = []
        self._secrets[extension_id].append(ws)
        return ws

    def rotate(self, extension_id: str) -> WebhookSecret:
        old_secrets = self._secrets.get(extension_id, [])
        for s in old_secrets:
            if s.active:
                s.expires_at = time.time() + self.GRACE_PERIOD
        return self.create(extension_id)

    def get_active(self, extension_id: str) -> list[WebhookSecret]:
        now = time.time()
        return [s for s in self._secrets.get(extension_id, [])
                if s.active and (s.expires_at == 0 or s.expires_at > now)]

    def sign(self, extension_id: str, payload: str) -> str | None:
        active = self.get_active(extension_id)
        if not active:
            return None
        # Use the newest (last) active secret
        newest = max(active, key=lambda s: s.created_at)
        return hmac.new(newest.secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

    def verify(self, extension_id: str, payload: str, signature: str) -> bool:
        for s in self.get_active(extension_id):
            expected = hmac.new(s.secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
            if hmac.compare_digest(expected, signature):
                return True
        return False
