"""Webhook secret rotator — rotate webhook signing secrets with grace period."""
from __future__ import annotations
import secrets
import hmac
import hashlib
import time

_HMAC_KEY = secrets.token_bytes(32)


class WebhookSecretRotator:
    def __init__(self):
        self._webhooks: dict[str, dict] = {}

    def register(self, webhook_id: str) -> dict:
        secret = secrets.token_urlsafe(32)
        self._webhooks[webhook_id] = {
            "current_secret": secret, "previous_secret": None,
            "rotated_at": time.time(), "grace_period_sec": 3600,
        }
        return {"webhook_id": webhook_id, "secret": secret}

    def rotate(self, webhook_id: str) -> dict:
        wh = self._webhooks.get(webhook_id)
        if not wh:
            return {"error": "Webhook not found"}
        wh["previous_secret"] = wh["current_secret"]
        wh["current_secret"] = secrets.token_urlsafe(32)
        wh["rotated_at"] = time.time()
        return {"webhook_id": webhook_id, "new_secret": wh["current_secret"],
                "grace_period_sec": wh["grace_period_sec"]}

    def verify(self, webhook_id: str, *, payload: str, signature: str,
                now: float | None = None) -> dict:
        wh = self._webhooks.get(webhook_id)
        if not wh:
            return {"valid": False, "reason": "webhook_not_found"}
        ts = now if now is not None else time.time()
        current_sig = hmac.new(wh["current_secret"].encode(), payload.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(signature, current_sig):
            return {"valid": True, "matched": "current"}
        if wh["previous_secret"] and ts - wh["rotated_at"] < wh["grace_period_sec"]:
            prev_sig = hmac.new(wh["previous_secret"].encode(), payload.encode(), hashlib.sha256).hexdigest()
            if hmac.compare_digest(signature, prev_sig):
                return {"valid": True, "matched": "previous", "warning": "Using previous secret — update soon"}
        return {"valid": False, "reason": "signature_mismatch"}
