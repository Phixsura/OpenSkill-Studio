"""API key rotation policy — automated key rotation with zero downtime."""

import secrets
from datetime import datetime, timedelta


def rotate_api_key(*, current_key_prefix: str, overlap_hours: int = 24) -> dict:
    new_key = secrets.token_urlsafe(32)
    now = datetime.utcnow()
    return {
        "old_key_prefix": current_key_prefix,
        "new_key": new_key,
        "new_key_prefix": new_key[:8],
        "overlap_until": (now + timedelta(hours=overlap_hours)).isoformat(),
        "old_key_expires": (now + timedelta(hours=overlap_hours)).isoformat(),
        "rotated_at": now.isoformat(),
        "message": f"Both keys valid for {overlap_hours}h overlap period",
    }


def get_rotation_policy(*, max_age_days: int = 90, overlap_hours: int = 24,
                          auto_rotate: bool = True) -> dict:
    return {
        "max_age_days": max_age_days,
        "overlap_hours": overlap_hours,
        "auto_rotate": auto_rotate,
        "next_rotation_in_days": max_age_days,
        "policy_summary": f"Keys auto-rotate every {max_age_days} days with {overlap_hours}h overlap"
            if auto_rotate else f"Manual rotation required every {max_age_days} days",
    }
