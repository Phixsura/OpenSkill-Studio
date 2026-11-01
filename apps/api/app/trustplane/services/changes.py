"""Change Management & Revalidation service (ADR-017 Part K)."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.trustplane.models.changes import (
    ChangeEvent,
    ChangeImpact,
    ChangeType,
    RevalidationStatus,
)
from app.trustplane.models.inventory import AISystem
from app.trustplane.services.audit import record_trust_audit
from app.trustplane.services.inventory import SystemNotFoundError


class ChangeEventNotFoundError(AppError):
    def __init__(self):
        super().__init__("CHANGE_EVENT_NOT_FOUND", "Change event not found", 404)


async def create_change_event(
    db: AsyncSession, org_id: str, user_id: str, **data
) -> ChangeEvent:
    system_id = data["system_id"]
    r = await db.execute(select(AISystem.id).where(AISystem.id == system_id, AISystem.org_id == org_id))
    if r.scalar_one_or_none() is None:
        raise SystemNotFoundError()

    impact = ChangeImpact(data.get("impact", "low"))
    event = ChangeEvent(
        org_id=org_id,
        system_id=system_id,
        change_type=ChangeType(data["change_type"]),
        title=data["title"],
        description=data.get("description"),
        before_value=data.get("before_value"),
        after_value=data.get("after_value"),
        impact=impact,
        requires_revalidation=impact == ChangeImpact.REQUIRES_REVALIDATION,
        detected_by=data.get("detected_by", "manual"),
        created_by=user_id,
    )
    db.add(event)
    await db.flush()

    await record_trust_audit(
        db, org_id=org_id, actor_user_id=user_id, actor_type="user",
        action="change.recorded", target_type="change_event", target_id=event.id,
        after={"change_type": data["change_type"], "impact": impact.value},
    )
    return event


async def get_change_event(db: AsyncSession, event_id: str, org_id: str) -> ChangeEvent:
    result = await db.execute(
        select(ChangeEvent).where(ChangeEvent.id == event_id, ChangeEvent.org_id == org_id)
    )
    event = result.scalar_one_or_none()
    if event is None:
        raise ChangeEventNotFoundError()
    return event


async def list_change_events(
    db: AsyncSession, org_id: str, *,
    system_id: str | None = None, change_type: str | None = None,
    impact: str | None = None, page: int = 1, per_page: int = 20,
) -> tuple[list[ChangeEvent], int]:
    base = select(ChangeEvent).where(ChangeEvent.org_id == org_id)
    count_q = select(func.count()).select_from(ChangeEvent).where(ChangeEvent.org_id == org_id)

    if system_id:
        base = base.where(ChangeEvent.system_id == system_id)
        count_q = count_q.where(ChangeEvent.system_id == system_id)
    if change_type:
        base = base.where(ChangeEvent.change_type == change_type)
        count_q = count_q.where(ChangeEvent.change_type == change_type)
    if impact:
        base = base.where(ChangeEvent.impact == impact)
        count_q = count_q.where(ChangeEvent.impact == impact)

    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(base.order_by(ChangeEvent.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
    return list(result.scalars().all()), total


async def mark_revalidated(
    db: AsyncSession, event_id: str, org_id: str, user_id: str,
) -> ChangeEvent:
    event = await get_change_event(db, event_id, org_id)
    event.revalidation_status = RevalidationStatus.COMPLETED
    event.revalidated_at = datetime.now(UTC)
    event.revalidated_by = user_id
    await db.flush()

    await record_trust_audit(
        db, org_id=org_id, actor_user_id=user_id, actor_type="user",
        action="change.revalidated", target_type="change_event", target_id=event_id,
    )
    return event
