"""App webhook management service — register, validate, and deliver webhooks.

Extends the event dispatch engine with webhook-specific functionality:
- Webhook URL validation and testing
- Delivery retry with exponential backoff
- Delivery logging to app_webhook_deliveries table
- Webhook secret rotation
"""

import hashlib
import secrets
from datetime import UTC, datetime

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook_delivery import AppWebhookDelivery

log = structlog.get_logger()


def generate_webhook_secret() -> tuple[str, str]:
    """Generate a webhook secret pair (raw, hashed)."""
    raw = f"whsec_{secrets.token_urlsafe(32)}"
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


async def log_delivery(
    db: AsyncSession,
    *,
    app_id: str,
    installation_id: str | None,
    event_type: str,
    event_id: str,
    url: str,
    status: str,
    http_status: int | None = None,
    attempt: int = 1,
    max_attempts: int = 3,
    error_message: str | None = None,
    duration_ms: int | None = None,
) -> AppWebhookDelivery:
    """Log a webhook delivery attempt."""
    delivery = AppWebhookDelivery(
        app_id=app_id,
        installation_id=installation_id,
        event_type=event_type,
        event_id=event_id,
        url=url,
        status=status,
        http_status=http_status,
        attempt=attempt,
        max_attempts=max_attempts,
        error_message=error_message,
        duration_ms=duration_ms,
        delivered_at=datetime.now(UTC) if status == "DELIVERED" else None,
    )
    db.add(delivery)
    await db.flush()
    return delivery


async def get_delivery_stats(
    db: AsyncSession, app_id: str
) -> dict:
    """Get webhook delivery statistics for an app."""
    from sqlalchemy import func, select

    result = await db.execute(
        select(
            AppWebhookDelivery.status,
            func.count().label("count"),
        )
        .where(AppWebhookDelivery.app_id == app_id)
        .group_by(AppWebhookDelivery.status)
    )
    breakdown = {
        row.status.value if hasattr(row.status, "value") else str(row.status): row.count
        for row in result.all()
    }

    avg_result = await db.execute(
        select(func.avg(AppWebhookDelivery.duration_ms)).where(
            AppWebhookDelivery.app_id == app_id,
            AppWebhookDelivery.duration_ms.isnot(None),
        )
    )
    avg_ms = avg_result.scalar() or 0

    return {
        "delivery_breakdown": breakdown,
        "avg_duration_ms": round(avg_ms, 1),
        "total": sum(breakdown.values()),
    }


def validate_webhook_url(url: str) -> list[str]:
    """Validate a webhook URL. Returns list of errors."""
    errors = []
    if not url:
        errors.append("URL is required")
        return errors
    if not url.startswith("https://"):
        errors.append("URL must use HTTPS")
    if len(url) > 500:
        errors.append("URL must be 500 characters or less")

    # Check for blocked hosts
    from app.services.event_dispatch import _is_safe_url

    if url.startswith("https://") and not _is_safe_url(url):
        errors.append("URL points to a blocked or private address")

    return errors
