"""Secret rotation scheduler — manage automatic secret rotation."""
from __future__ import annotations
import secrets
import time


def create_rotation_policy(secret_name: str, rotation_days: int = 90, notify_days: int = 14) -> dict:
    return {"secret_name": secret_name, "rotation_days": rotation_days,
            "notify_days": notify_days, "created_at": time.time()}


def check_rotation_status(policy: dict, last_rotated: float, now: float | None = None) -> dict:
    now = now or time.time()
    age_days = (now - last_rotated) / 86400
    due_in = policy["rotation_days"] - age_days
    needs_rotation = due_in <= 0
    needs_warning = due_in <= policy["notify_days"] and not needs_rotation
    status = "overdue" if needs_rotation else "warning" if needs_warning else "ok"
    return {"secret_name": policy["secret_name"], "age_days": round(age_days, 1),
            "due_in_days": round(max(0, due_in), 1), "status": status,
            "needs_rotation": needs_rotation}


def rotate_secret(length: int = 32) -> dict:
    new_val = secrets.token_urlsafe(length)
    return {"new_secret": new_val, "rotated_at": time.time(), "length": len(new_val)}
