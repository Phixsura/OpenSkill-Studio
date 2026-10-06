"""Experiment webhook emission — ADR-017 §4.18.

Org-scoped experiments fire through the platform WebhookService;
platform-wide experiments (scope_org_id IS NULL) never fan out to
tenant webhooks — cross-tenant information containment. Fail-safe:
delivery errors are logged and swallowed, never the caller's 500.
"""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

log = structlog.get_logger()

EXPERIMENT_EVENT_TYPES = frozenset(
    {
        "experiment.status_changed",
        "experiment.guardrail_breach",
        "experiment.decision_recorded",
    }
)


async def emit_experiment_event(
    db: AsyncSession,
    *,
    scope_org_id: str | None,
    event_type: str,
    payload: dict,
) -> None:
    """Fire an experiment webhook event. Fail-safe (never raises)."""
    if scope_org_id is None:
        return  # platform-wide: no tenant webhook fan-out by design
    if event_type not in EXPERIMENT_EVENT_TYPES:
        log.warning("unknown_experiment_event_type", event_type=event_type)
        return
    try:
        from app.services.webhook import WebhookService

        await WebhookService(db).trigger_event(
            scope_org_id, event_type, payload, defer_until_commit=True
        )
    except Exception:
        log.warning(
            "experiment_webhook_emit_failed",
            org_id=scope_org_id,
            event_type=event_type,
            exc_info=True,
        )
