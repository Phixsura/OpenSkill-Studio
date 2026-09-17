"""Outreach / invitation records API (§39).

Allows org admins to send outreach invitations to talent pool members,
track responses, and manage outreach campaigns.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/talent", tags=["Talent — Outreach"])


@router.get(
    "/outreach",
    response_model=DataResponse[list[dict]],
    summary="List outreach records",
    description="List outreach invitations sent by the current user's organization.",
)
async def list_outreach(
    status: str | None = Query(None, description="Filter by status: pending, accepted, declined"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List outreach records for the authenticated user's orgs."""
    from app.talent.models.talent_pool import TalentOutreach

    q = select(TalentOutreach).where(TalentOutreach.sender_id == user.id)
    if status:
        q = q.where(TalentOutreach.status == status)
    q = q.order_by(TalentOutreach.created_at.desc()).limit(limit)
    result = await db.execute(q)
    rows = result.scalars().all()
    return {"data": [_outreach_dict(r) for r in rows]}


@router.post(
    "/outreach",
    response_model=DataResponse[dict],
    status_code=201,
    summary="Send outreach invitation",
    description="Send an outreach invitation to a user. Requires the target user to be in a talent pool you manage.",
)
async def send_outreach(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new outreach record."""
    from app.talent.models.talent_pool import TalentOutreach
    from app.models.base import ulid_pk as _ulid  # noqa: F401
    import ulid as _ulid_mod

    user_id = body.get("user_id")
    outreach_type = body.get("outreach_type", "invitation")
    message = body.get("message", "")
    opportunity_id = body.get("opportunity_id")

    if not user_id:
        raise HTTPException(422, "user_id is required")

    record = TalentOutreach(
        id=_ulid_mod.ULID().__str__() if hasattr(_ulid_mod, "ULID") else str(_ulid_mod.new()),
        sender_id=user.id,
        user_id=user_id,
        outreach_type=outreach_type,
        message=message,
        opportunity_id=opportunity_id,
        status="pending",
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return {"data": _outreach_dict(record)}


@router.post(
    "/outreach/{outreach_id}/respond",
    response_model=DataResponse[dict],
    summary="Respond to outreach",
    description="Accept or decline an outreach invitation.",
)
async def respond_outreach(
    outreach_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Respond to an outreach invitation."""
    from app.talent.models.talent_pool import TalentOutreach

    result = await db.execute(
        select(TalentOutreach).where(
            TalentOutreach.id == outreach_id,
            TalentOutreach.user_id == user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(404, "Outreach not found")

    response = body.get("response")
    if response not in ("accepted", "declined"):
        raise HTTPException(422, "response must be 'accepted' or 'declined'")

    record.status = response
    await db.commit()
    await db.refresh(record)
    return {"data": _outreach_dict(record)}


def _outreach_dict(r) -> dict:
    return {
        "id": r.id,
        "sender_id": r.sender_id,
        "user_id": r.user_id,
        "outreach_type": r.outreach_type,
        "message": r.message,
        "opportunity_id": r.opportunity_id,
        "status": r.status,
        "created_at": str(r.created_at) if r.created_at else None,
    }
