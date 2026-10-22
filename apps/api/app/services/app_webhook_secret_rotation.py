"""Webhook secret rotation — rotate webhook signing secrets safely."""

from datetime import UTC, datetime, timedelta
from app.services.webhook_verify import generate_webhook_secret


def create_rotation(*, current_secret_id: str, grace_hours: int = 24) -> dict:
    """Create a webhook secret rotation with grace period."""
    _, new_secret = generate_webhook_secret()
    now = datetime.now(UTC)
    return {
        "old_secret_id": current_secret_id,
        "new_secret": new_secret,
        "grace_until": (now + timedelta(hours=grace_hours)).isoformat(),
        "created_at": now.isoformat(),
        "status": "active",
    }


def is_in_grace(rotation: dict) -> bool:
    grace = datetime.fromisoformat(rotation["grace_until"].replace("Z", "+00:00"))
    return datetime.now(UTC) < grace


def should_accept_old_secret(rotation: dict | None) -> bool:
    """During grace period, accept both old and new secrets."""
    if not rotation:
        return False
    return is_in_grace(rotation)
