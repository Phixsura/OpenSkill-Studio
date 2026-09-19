"""Talent webhook event emission — fires events through existing WebhookService.

All calls are fail-safe: delivery errors are logged and swallowed so they
never corrupt the caller's session or transaction.
"""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.webhook import WebhookService

log = structlog.get_logger()

TALENT_EVENT_TYPES = frozenset(
    {
        "credential.issued",
        "credential.revoked",
        "application.submitted",
        "application.stage_changed",
        "offer.created",
        "placement.started",
        "placement.completed",
        "capability.verified",
        "employer_verification.submitted",
        "outreach.sent",
        "outreach.responded",
        "talent_pool.member_added",
    }
)


async def emit_talent_event(
    db: AsyncSession,
    *,
    org_id: str,
    event_type: str,
    payload: dict,
) -> None:
    """Fire a talent webhook event. Fail-safe (never raises)."""
    if event_type not in TALENT_EVENT_TYPES:
        log.warning("unknown_talent_event_type", event_type=event_type)
        return
    try:
        svc = WebhookService(db)
        await svc.trigger_event(org_id, event_type, payload)
    except Exception:
        log.warning(
            "talent_webhook_emit_failed",
            org_id=org_id,
            event_type=event_type,
            exc_info=True,
        )
