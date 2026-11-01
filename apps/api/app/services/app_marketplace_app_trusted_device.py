"""Trusted device — manage trusted devices for enhanced security."""

import secrets
import hmac
import hashlib
from datetime import datetime, timedelta

_SERVER_KEY = secrets.token_bytes(32)


def _compute_device_hmac(device_fingerprint: str, user_id: str) -> str:
    payload = f"{user_id}:{device_fingerprint}"
    return hmac.new(_SERVER_KEY, payload.encode(), hashlib.sha256).hexdigest()[:24]


def register_device(*, user_id: str, device_name: str, device_fingerprint: str,
                      trust_duration_days: int = 90) -> dict:
    device_id = f"dev_{secrets.token_urlsafe(8)}"
    token = _compute_device_hmac(device_fingerprint, user_id)
    now = datetime.utcnow()
    return {
        "device_id": device_id,
        "user_id": user_id,
        "device_name": device_name,
        "device_token": token,
        "trusted_until": (now + timedelta(days=trust_duration_days)).isoformat(),
        "registered_at": now.isoformat(),
        "trusted": True,
    }


def is_trusted(*, device_token: str, user_id: str, trusted_devices: list[dict]) -> dict:
    now = datetime.utcnow().isoformat()
    for d in trusted_devices:
        if (hmac.compare_digest(d.get("device_token", ""), device_token)
                and d.get("user_id") == user_id
                and d.get("trusted_until", "") > now):
            return {"trusted": True, "device_name": d.get("device_name"), "skip_mfa": True}
    return {"trusted": False, "require_mfa": True}


def list_devices(*, devices: list[dict]) -> dict:
    active = [d for d in devices if d.get("trusted_until", "") > datetime.utcnow().isoformat()]
    # Strip tokens from response
    safe = [{"device_id": d.get("device_id"), "device_name": d.get("device_name"),
             "trusted_until": d.get("trusted_until")} for d in active]
    return {"devices": safe, "total": len(safe)}
