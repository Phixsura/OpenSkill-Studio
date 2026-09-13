"""Talent pool, outreach, and outcome event API endpoints.

Authorization:
  - Pool CRUD: require_org_member(pool.org_id)
  - Membership response: only the member user
  - Outreach send: require_org_member(org_id)
  - Outreach response: only the target user
  - Outcome events: only own events
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.schemas.cursor import CursorListResponse, CursorMeta
from app.talent.schemas.talent_pool import (
    AddMemberRequest,
    CreatePoolRequest,
    MembershipResponse,
    OutcomeEventResponse,
    OutreachResponse,
    PoolResponse,
    RecordOutcomeRequest,
    RespondMembershipRequest,
    RespondOutreachRequest,
    SendOutreachRequest,
    UpdateOutcomeVisibilityRequest,
    UpdatePoolRequest,
)
from app.talent.services.talent_pool import (
    OutcomeEventService,
    OutreachService,
    TalentPoolService,
)

router = APIRouter(prefix="/talent", tags=["Talent — Pools & Outreach"])


# ═══════════════════════════════════════════════════════════════════════════
# Talent Pools
# ═══════════════════════════════════════════════════════════════════════════


@router.post("/pools", response_model=DataResponse[PoolResponse], status_code=201)
async def create_pool(
    body: CreatePoolRequest,
    org_id: str = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db)
    svc = TalentPoolService(db)
    pool = await svc.create_pool(
        org_id=org_id,
        name=body.name,
        description=body.description,
        membership_mode=body.membership_mode,
        rule_config=body.rule_config,
        visibility=body.visibility,
        created_by=user.id,
    )
    await db.commit()
    await db.refresh(pool)
    return DataResponse(data=PoolResponse.model_validate(pool))


@router.get("/pools", response_model=CursorListResponse[PoolResponse])
async def list_pools(
    org_id: str = Query(...),
    cursor: str | None = Query(None, description="Cursor for pagination (last item ID)"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db)
    svc = TalentPoolService(db)
    items, total = await svc.list_pools(org_id, limit=limit, cursor=cursor)
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    next_cursor = items[-1].id if has_more and items else None
    return CursorListResponse(
        data=[PoolResponse.model_validate(p) for p in items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.get("/pools/{pool_id}", response_model=DataResponse[PoolResponse])
async def get_pool(
    pool_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = TalentPoolService(db)
    pool = await svc.get_pool(pool_id)
    if not pool:
        raise HTTPException(404, "Pool not found")
    await require_org_member(pool.org_id, user, db)
    return DataResponse(data=PoolResponse.model_validate(pool))


@router.patch("/pools/{pool_id}", response_model=DataResponse[PoolResponse])
async def update_pool(
    pool_id: str,
    body: UpdatePoolRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = TalentPoolService(db)
    pool = await svc.get_pool(pool_id)
    if not pool:
        raise HTTPException(404, "Pool not found")
    await require_org_member(pool.org_id, user, db)
    updated = await svc.update_pool(pool_id, **body.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(404, "Pool not found")
    await db.commit()
    await db.refresh(updated)
    return DataResponse(data=PoolResponse.model_validate(updated))


# ── Pool Membership ──


@router.post("/pools/{pool_id}/members", response_model=DataResponse[MembershipResponse], status_code=201)
async def add_member(
    pool_id: str,
    body: AddMemberRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = TalentPoolService(db)
    pool = await svc.get_pool(pool_id)
    if not pool:
        raise HTTPException(404, "Pool not found")
    await require_org_member(pool.org_id, user, db)
    try:
        membership = await svc.add_member(pool_id, body.user_id, body.source, added_by=user.id)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    await db.commit()
    await db.refresh(membership)
    return DataResponse(data=MembershipResponse.model_validate(membership))


@router.get("/pools/{pool_id}/members", response_model=CursorListResponse[MembershipResponse])
async def list_members(
    pool_id: str,
    consent_status: str | None = None,
    cursor: str | None = Query(None, description="Cursor for pagination (last item ID)"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = TalentPoolService(db)
    pool = await svc.get_pool(pool_id)
    if not pool:
        raise HTTPException(404, "Pool not found")
    await require_org_member(pool.org_id, user, db)
    items, total = await svc.list_members(
        pool_id, consent_status=consent_status, limit=limit, cursor=cursor
    )
    all_items = list(items) if not isinstance(items, list) else items
    has_more = len(all_items) > limit
    if has_more:
        all_items = all_items[:limit]
    next_cursor = all_items[-1].id if has_more and all_items else None
    return CursorListResponse(
        data=[MembershipResponse.model_validate(m) for m in all_items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.patch(
    "/pools/{pool_id}/members/{membership_id}",
    response_model=DataResponse[MembershipResponse],
)
async def respond_to_membership(
    pool_id: str,
    membership_id: str,
    body: RespondMembershipRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Respond to a pool membership invitation — only the invited user."""
    svc = TalentPoolService(db)
    try:
        membership = await svc.respond_to_membership(membership_id, user.id, accept=body.accept)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    if not membership:
        raise HTTPException(404, "Membership not found")
    await db.commit()
    await db.refresh(membership)
    return DataResponse(data=MembershipResponse.model_validate(membership))


@router.delete("/pools/{pool_id}/members/{user_id}", status_code=204)
async def remove_member(
    pool_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = TalentPoolService(db)
    pool = await svc.get_pool(pool_id)
    if not pool:
        raise HTTPException(404, "Pool not found")
    await require_org_member(pool.org_id, user, db)
    if not await svc.remove_member(pool_id, user_id):
        raise HTTPException(404, "Member not found")
    await db.commit()


# ═══════════════════════════════════════════════════════════════════════════
# Outreach
# ═══════════════════════════════════════════════════════════════════════════


@router.post("/outreach", response_model=DataResponse[OutreachResponse], status_code=201)
async def send_outreach(
    body: SendOutreachRequest,
    org_id: str = Query(..., description="Sending organization ID"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db)
    svc = OutreachService(db)
    try:
        outreach = await svc.send_outreach(
            org_id=org_id,
            user_id=body.user_id,
            outreach_type=body.outreach_type,
            target_type=body.target_type,
            target_id=body.target_id,
            message=body.message,
            expires_at=body.expires_at,
        )
    except ValueError as e:
        err_msg = str(e)
        if "OUTREACH_RATE_LIMITED" in err_msg:
            raise HTTPException(429, err_msg) from e
        raise HTTPException(422, err_msg) from e
    await db.commit()
    await db.refresh(outreach)
    return DataResponse(data=OutreachResponse.model_validate(outreach))


@router.get("/outreach", response_model=CursorListResponse[OutreachResponse])
async def list_outreach(
    org_id: str | None = Query(None, description="Filter by sending org (sent view)"),
    status: str | None = None,
    cursor: str | None = Query(None, description="Cursor for pagination (last item ID)"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List outreach — org_id for sent view, otherwise received view (own user)."""
    if org_id:
        await require_org_member(org_id, user, db)

    svc = OutreachService(db)
    items, total = await svc.list_outreach(
        org_id=org_id,
        user_id=None if org_id else user.id,
        status=status,
        limit=limit,
        cursor=cursor,
    )
    all_items = list(items) if not isinstance(items, list) else items
    has_more = len(all_items) > limit
    if has_more:
        all_items = all_items[:limit]
    next_cursor = all_items[-1].id if has_more and all_items else None
    return CursorListResponse(
        data=[OutreachResponse.model_validate(o) for o in all_items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.patch("/outreach/{outreach_id}", response_model=DataResponse[OutreachResponse])
async def respond_to_outreach(
    outreach_id: str,
    body: RespondOutreachRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Respond to an outreach invitation — only the target user."""
    svc = OutreachService(db)
    try:
        outreach = await svc.respond_to_outreach(outreach_id, user.id, status=body.status)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    if not outreach:
        raise HTTPException(404, "Outreach not found")
    await db.commit()
    await db.refresh(outreach)
    return DataResponse(data=OutreachResponse.model_validate(outreach))


# ═══════════════════════════════════════════════════════════════════════════
# Outcome Events
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/outcomes", response_model=CursorListResponse[OutcomeEventResponse])
async def list_outcomes(
    event_type: str | None = None,
    visibility: str | None = None,
    cursor: str | None = Query(None, description="Cursor for pagination (last item ID)"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List own outcome events."""
    svc = OutcomeEventService(db)
    items, total = await svc.list_events(
        user.id,
        event_type=event_type,
        visibility=visibility,
        limit=limit,
        cursor=cursor,
    )
    all_items = list(items) if not isinstance(items, list) else items
    has_more = len(all_items) > limit
    if has_more:
        all_items = all_items[:limit]
    next_cursor = all_items[-1].id if has_more and all_items else None
    return CursorListResponse(
        data=[OutcomeEventResponse.model_validate(e) for e in all_items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.post("/outcomes", response_model=DataResponse[OutcomeEventResponse], status_code=201)
async def record_outcome(
    body: RecordOutcomeRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Record a career outcome event."""
    svc = OutcomeEventService(db)
    try:
        event = await svc.record_event(
            user_id=user.id,
            event_type=body.event_type,
            source_type=body.source_type,
            source_id=body.source_id,
            occurred_at=body.occurred_at,
            visibility=body.visibility,
            metadata=body.metadata,
        )
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    await db.commit()
    await db.refresh(event)
    return DataResponse(data=OutcomeEventResponse.model_validate(event))


@router.patch("/outcomes/{event_id}", response_model=DataResponse[OutcomeEventResponse])
async def update_outcome_visibility(
    event_id: str,
    body: UpdateOutcomeVisibilityRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update visibility of an outcome event — owner only."""
    svc = OutcomeEventService(db)
    try:
        event = await svc.update_visibility(event_id, user.id, body.visibility)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    if not event:
        raise HTTPException(404, "Outcome event not found")
    await db.commit()
    await db.refresh(event)
    return DataResponse(data=OutcomeEventResponse.model_validate(event))
