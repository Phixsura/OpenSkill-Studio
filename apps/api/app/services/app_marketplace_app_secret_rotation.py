"""Secret rotation — automated rotation of API keys and secrets."""

import secrets
import hashlib
from datetime import datetime, timedelta


def rotate_secret(*, secret_id: str, rotation_type: str = "api_key") -> dict:
    new_value = secrets.token_urlsafe(32)
    old_hash = hashlib.sha256(f"old_{secret_id}".encode()).hexdigest()[:12]
    new_hash = hashlib.sha256(new_value.encode()).hexdigest()[:12]
    grace_period = timedelta(hours=24)
    return {
        "secret_id": secret_id,
        "rotation_type": rotation_type,
        "old_hash": old_hash,
        "new_hash": new_hash,
        "new_value": new_value,
        "rotated_at": datetime.utcnow().isoformat(),
        "grace_period_ends": (datetime.utcnow() + grace_period).isoformat(),
        "both_valid_until": (datetime.utcnow() + grace_period).isoformat(),
        "warning": "Store new value securely. Old value valid for 24h grace period.",
    }


def get_rotation_schedule(*, secrets_list: list[dict]) -> dict:
    schedule = []
    for s in secrets_list:
        age_days = s.get("age_days", 0)
        max_age = s.get("max_age_days", 90)
        needs_rotation = age_days >= max_age
        days_until = max(max_age - age_days, 0)
        schedule.append({
            "secret_id": s["id"],
            "name": s["name"],
            "age_days": age_days,
            "max_age_days": max_age,
            "needs_rotation": needs_rotation,
            "days_until_rotation": days_until,
            "urgency": "critical" if days_until == 0 else "soon" if days_until <= 7 else "ok",
        })
    overdue = sum(1 for s in schedule if s["needs_rotation"])
    return {"schedule": schedule, "total": len(schedule),
            "overdue_count": overdue, "all_current": overdue == 0}
