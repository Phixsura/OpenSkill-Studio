"""Endorsement API — peer skill verification flow.

Authorization:
  - Endorse: any authenticated user can endorse anyone (except self)
  - List own endorsements: authenticated user
  - List user's endorsements: public (endorsements are social proof)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.schemas.cursor import CursorListResponse, CursorMeta
from app.talent.schemas.endorsement import (
    CreateEndorsementRequest,
    EndorsementResponse,
    EndorsementSummaryResponse,
)

router = APIRouter(prefix="/talent", tags=["Talent — Endorsements"])


@router.post(
    "/users/{user_id}/endorse",
    response_model=DataResponse[EndorsementResponse],
    status_code=201,
)
async def endorse_user(
    user_id: str,
    body: CreateEndorsementRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Endorse a user's capability. Creates peer_verified evidence."""
    from app.talent.services.endorsements import EndorsementService

    svc = EndorsementService(db)
    try:
        endorsement = await svc.endorse(
            user_id=user_id,
            endorser_id=user.id,
            capability_id=body.capability_id,
            relationship=body.relationship,
            message=body.message,
        )
    except ValueError:
        raise HTTPException(422, "Validation error") from None

    await db.commit()
    await db.refresh(endorsement)

    # Send notification to endorsed user
    from app.talent.services.notifications import TalentNotificationService

    notif_svc = TalentNotificationService(db)
    try:
        await notif_svc.send(
            user_id=user_id,
            event_type="endorsement_received",
            title="New Skill Endorsement",
            message="Someone endorsed your capability",
            metadata={
                "endorser_id": user.id,
                "capability_id": body.capability_id,
                "relationship": body.relationship,
            },
        )
        await db.commit()
    except Exception:
        pass  # Notification failure should not block endorsement

    return DataResponse(data=EndorsementResponse.model_validate(endorsement))


@router.get(
    "/endorsements",
    response_model=CursorListResponse[EndorsementResponse],
)
async def list_my_endorsements(
    capability_id: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List endorsements received by the current user."""
    from app.talent.services.endorsements import EndorsementService

    svc = EndorsementService(db)
    items, has_more = await svc.list_endorsements(
        user.id, capability_id=capability_id, cursor=cursor, limit=limit
    )
    next_cursor = items[-1].id if has_more and items else None
    return CursorListResponse(
        data=[EndorsementResponse.model_validate(e) for e in items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.get(
    "/endorsements/summary",
    response_model=DataResponse[EndorsementSummaryResponse],
)
async def get_endorsement_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get endorsement summary for the current user."""
    from app.talent.services.endorsements import EndorsementService

    svc = EndorsementService(db)
    summary = await svc.get_endorsement_summary(user.id)
    return DataResponse(data=EndorsementSummaryResponse(**summary))


# ---- Leaderboard (N12) ----


@router.get(
    "/endorsements/leaderboard/users",
    response_model=DataResponse[list[dict]],
    summary="Get endorsement leaderboard",
    description="Top endorsed users ranked by count and rating.",
)
async def get_top_endorsed_users(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Top endorsed users (discoverable only)."""
    from app.talent.services.endorsement_leaderboard import (
        EndorsementLeaderboardService,
    )

    svc = EndorsementLeaderboardService(db)
    entries = await svc.get_top_endorsed_users(limit=limit)
    return DataResponse(
        data=[
            {
                "user_id": e.user_id,
                "total_endorsements": e.total_endorsements,
                "unique_endorsers": e.unique_endorsers,
            }
            for e in entries
        ]
    )


@router.get(
    "/endorsements/leaderboard/capabilities",
    response_model=DataResponse[list[dict]],
)
async def get_top_endorsed_capabilities(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Top capabilities by endorsement count."""
    from app.talent.services.endorsement_leaderboard import (
        EndorsementLeaderboardService,
    )

    svc = EndorsementLeaderboardService(db)
    entries = await svc.get_top_endorsed_capabilities(limit=limit)
    return DataResponse(
        data=[
            {
                "capability_id": e.capability_id,
                "capability_name": e.capability_name,
                "endorsement_count": e.endorsement_count,
                "unique_users": e.unique_users,
            }
            for e in entries
        ]
    )


@router.get(
    "/endorsements/stats",
    response_model=DataResponse[dict],
    summary="Get endorsement statistics",
    description="User endorsement stats including given, received, and top capabilities.",
)
async def get_endorsement_stats(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Platform-wide endorsement statistics."""
    from app.talent.services.endorsement_leaderboard import (
        EndorsementLeaderboardService,
    )

    svc = EndorsementLeaderboardService(db)
    stats = await svc.get_endorsement_stats()
    return DataResponse(
        data={
            "total_endorsements": stats.total_endorsements,
            "total_endorsers": stats.total_endorsers,
            "total_endorsed_users": stats.total_endorsed_users,
            "avg_per_user": stats.avg_per_user,
        }
    )


@router.get(
    "/users/{user_id}/endorsements",
    response_model=CursorListResponse[EndorsementResponse],
)
async def list_user_endorsements(
    user_id: str,
    capability_id: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """View another user's endorsements (respects passport privacy)."""
    from app.talent.models.passport import SkillPassport
    from app.talent.services.endorsements import EndorsementService

    # Check passport privacy — only show endorsements if passport is not private
    passport = await db.get(SkillPassport, user_id)
    if passport and passport.default_visibility == "private" and _user.id != user_id:
        raise HTTPException(404, "User not found")

    svc = EndorsementService(db)
    items, has_more = await svc.list_endorsements(
        user_id, capability_id=capability_id, cursor=cursor, limit=limit
    )
    next_cursor = items[-1].id if has_more and items else None
    return CursorListResponse(
        data=[EndorsementResponse.model_validate(e) for e in items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )
