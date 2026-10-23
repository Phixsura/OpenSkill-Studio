"""API key rotation scheduler — automate key rotation lifecycle."""
from __future__ import annotations
import secrets
import time


def create_rotation_schedule(key_name: str, rotation_days: int = 90) -> dict:
    return {"key_name": key_name, "rotation_days": rotation_days,
            "last_rotated": time.time(), "next_rotation": time.time() + rotation_days * 86400,
            "rotation_count": 0}


def rotate_key(schedule: dict) -> dict:
    new_key = f"sk_{secrets.token_urlsafe(32)}"
    schedule["rotation_count"] += 1
    schedule["last_rotated"] = time.time()
    schedule["next_rotation"] = time.time() + schedule["rotation_days"] * 86400
    return {"rotated": True, "new_key_prefix": new_key[:8],
            "rotation_number": schedule["rotation_count"]}


def check_rotation_needed(schedules: list[dict], now: float | None = None) -> dict:
    now = now or time.time()
    due = [s for s in schedules if now >= s["next_rotation"]]
    upcoming = [s for s in schedules if 0 < s["next_rotation"] - now <= 7 * 86400]
    return {"due_count": len(due), "upcoming_count": len(upcoming),
            "due_keys": [s["key_name"] for s in due],
            "upcoming_keys": [s["key_name"] for s in upcoming],
            "action_needed": len(due) > 0}
