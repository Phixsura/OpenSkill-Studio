"""Trusted device — manage trusted devices for enhanced security."""

import secrets
import hashlib
from datetime import datetime, timedelta


def register_device(*, user_id: str, device_name: str, device_fingerprint: str,
                      trust_duration_days: int = 90) -> dict:
    device_id = f"dev_{secrets.token_urlsafe(8)}"
    fp_hash = hashlib.sha256(device_fingerprint.encode()).hexdigest()[:16]
    now = datetime.utcnow()
    return {
        "device_id": device_id,
        "user_id": user_id,
        "device_name": device_name,
        "fingerprint_hash": fp_hash,
        "trusted_until": (now + timedelta(days=trust_duration_days)).isoformat(),
        "registered_at": now.isoformat(),
        "trusted": True,
    }


def is_trusted(*, fingerprint_hash: str, trusted_devices: list[dict]) -> dict:
    now = datetime.utcnow().isoformat()
    for d in trusted_devices:
        if d.get("fingerprint_hash") == fingerprint_hash and d.get("trusted_until", "") > now:
            return {"trusted": True, "device_name": d.get("device_name"), "skip_mfa": True}
    return {"trusted": False, "require_mfa": True}


def list_devices(*, devices: list[dict]) -> dict:
    active = [d for d in devices if d.get("trusted_until", "") > datetime.utcnow().isoformat()]
    return {"devices": active, "total": len(active)}
