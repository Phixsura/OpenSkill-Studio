"""App usage metering — tracks API calls, sandbox executions, and webhook deliveries.

Integrates with the control plane UsageEvent model for billing.
"""

from datetime import UTC, datetime
from typing import Any

import structlog

log = structlog.get_logger()

# Usage types specific to the developer platform
APP_USAGE_TYPES = {
    "app.api_call": "API call made by/for an app",
    "app.sandbox_execution": "Sandbox function execution",
    "app.webhook_delivery": "Webhook delivery attempt",
    "app.event_subscription": "Event subscription active",
    "app.storage_secret": "Encrypted secret stored",
}


async def record_app_usage(
    db: Any,
    *,
    tenant_id: str | None = None,
    org_id: str,
    app_id: str,
    installation_id: str | None = None,
    usage_type: str,
    quantity: int = 1,
    metadata: dict | None = None,
) -> None:
    """Record an app usage event for metering/billing.

    In production, this creates a UsageEvent via the control plane.
    For now, logs the usage for observability.
    """
    log.info(
        "app_usage_recorded",
        tenant_id=tenant_id,
        org_id=org_id,
        app_id=app_id,
        installation_id=installation_id,
        usage_type=usage_type,
        quantity=quantity,
        timestamp=datetime.now(UTC).isoformat(),
    )

    # TODO: Wire into control plane UsageEvent when tenant_id is available
    # from app.controlplane.facade import record_usage_event
    # await record_usage_event(db, tenant_id=tenant_id, ...)


async def get_app_usage_summary(
    db: Any,
    *,
    app_id: str,
    period: str = "current_month",
) -> dict:
    """Get usage summary for an app across all installations.

    Returns aggregate counts by usage type.
    """
    # TODO: Query UsageEvent when wired to control plane
    return {
        "app_id": app_id,
        "period": period,
        "usage": {
            "api_calls": 0,
            "sandbox_executions": 0,
            "webhook_deliveries": 0,
            "active_subscriptions": 0,
            "stored_secrets": 0,
        },
        "note": "Usage metering integration pending — tracking via logs",
    }


async def get_installation_usage_summary(
    db: Any,
    *,
    installation_id: str,
    period: str = "current_month",
) -> dict:
    """Get usage summary for a specific installation."""
    return {
        "installation_id": installation_id,
        "period": period,
        "usage": {
            "api_calls": 0,
            "sandbox_executions": 0,
            "webhook_deliveries": 0,
        },
        "note": "Usage metering integration pending — tracking via logs",
    }
