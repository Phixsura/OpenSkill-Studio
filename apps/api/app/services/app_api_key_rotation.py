"""API key rotation — create new key and schedule old key expiry."""

from datetime import UTC, datetime, timedelta


def create_rotation_plan(*, current_key_id: str, grace_period_hours: int = 24) -> dict:
    """Create a key rotation plan with grace period."""
    now = datetime.now(UTC)
    return {
        "current_key_id": current_key_id,
        "action": "rotate",
        "grace_period_hours": grace_period_hours,
        "old_key_expires_at": (now + timedelta(hours=grace_period_hours)).isoformat(),
        "created_at": now.isoformat(),
        "status": "pending",
    }


def should_rotate(*, last_rotated: str | None, max_age_days: int = 90) -> bool:
    """Check if a key should be rotated based on age."""
    if not last_rotated:
        return True
    rotated = datetime.fromisoformat(last_rotated.replace("Z", "+00:00"))
    age = (datetime.now(UTC) - rotated).days
    return age >= max_age_days


def is_in_grace_period(rotation_plan: dict) -> bool:
    """Check if we're still in the grace period."""
    expires = datetime.fromisoformat(rotation_plan["old_key_expires_at"].replace("Z", "+00:00"))
    return datetime.now(UTC) < expires
