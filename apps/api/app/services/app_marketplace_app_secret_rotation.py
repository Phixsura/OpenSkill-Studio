"""Secret rotation — automated rotation schedules for app secrets."""

import hashlib
import secrets
from datetime import datetime, timezone, timedelta


def generate_secret(*, length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def create_rotation_schedule(*, secret_name: str, rotation_days: int, last_rotated: str | None = None) -> dict:
    if rotation_days < 1:
        return {"error": "Rotation interval must be at least 1 day"}
    now = datetime.now(timezone.utc)
    if last_rotated:
        last = datetime.fromisoformat(last_rotated.replace("Z", "+00:00"))
        next_rotation = last + timedelta(days=rotation_days)
        overdue = now > next_rotation
    else:
        next_rotation = now
        overdue = True
    return {
        "secret_name": secret_name, "rotation_days": rotation_days,
        "next_rotation": next_rotation.isoformat(), "overdue": overdue, "error": None,
    }


def rotate_secret(*, secret_name: str, old_hash: str) -> dict:
    new_value = generate_secret()
    new_hash = hashlib.sha256(new_value.encode()).hexdigest()
    return {
        "secret_name": secret_name, "new_hash": new_hash,
        "rotated_at": datetime.now(timezone.utc).isoformat(),
        "grace_period_hours": 24,
    }
