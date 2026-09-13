"""Skill Passport API — own passport, snapshots, public verification."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.schemas.passport import (
    CreateSnapshotRequest,
    PassportResponse,
    SnapshotResponse,
    SnapshotVerifyResponse,
    UpdatePassportRequest,
)
from app.talent.services.passport import PassportService

router = APIRouter(tags=["Talent — Passport"])


@router.get("/talent/passport", response_model=DataResponse[dict])
async def get_passport(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get own passport (full view for owner)."""
    svc = PassportService(db)
    passport = await svc.get_visible_passport(user.id, requesting_user_id=user.id)
    if not passport:
        # Lazy init
        await svc.get_or_create_passport(user.id)
        await db.commit()
        passport = await svc.get_visible_passport(user.id, requesting_user_id=user.id)
    return DataResponse(data=passport)


@router.patch("/talent/passport", response_model=DataResponse[PassportResponse])
async def update_passport(
    body: UpdatePassportRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = PassportService(db)
    try:
        passport = await svc.update_passport(
            user.id,
            **body.model_dump(exclude_unset=True),
        )
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    await db.commit()
    return DataResponse(data=PassportResponse.model_validate(passport))


# ---- Snapshots ----

@router.post(
    "/talent/passport/snapshots",
    response_model=DataResponse[SnapshotResponse],
    status_code=201,
)
async def create_snapshot(
    body: CreateSnapshotRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = PassportService(db)
    snapshot = await svc.create_snapshot(
        user.id,
        included_fields=body.included_fields,
        expires_at=body.expires_at,
    )
    await db.commit()
    return DataResponse(data=SnapshotResponse.model_validate(snapshot))


@router.get("/talent/passport/snapshots", response_model=DataResponse[list[SnapshotResponse]])
async def list_snapshots(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from sqlalchemy import select

    from app.talent.models.passport import PassportSnapshot

    result = await db.execute(
        select(PassportSnapshot)
        .where(PassportSnapshot.user_id == user.id)
        .order_by(PassportSnapshot.issued_at.desc())
    )
    snapshots = result.scalars().all()
    return DataResponse(data=[SnapshotResponse.model_validate(s) for s in snapshots])


@router.delete("/talent/passport/snapshots/{snapshot_id}", status_code=204)
async def revoke_snapshot(
    snapshot_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = PassportService(db)
    result = await svc.revoke_snapshot(snapshot_id, user.id)
    if not result:
        raise HTTPException(404, "Snapshot not found or already revoked")
    await db.commit()


# ---- Public verification (no auth required) ----

@router.get("/verify/passport/{share_token}", response_model=DataResponse[SnapshotVerifyResponse])
async def verify_passport(
    share_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint — verify a passport snapshot by share token."""
    svc = PassportService(db)
    result = await svc.verify_snapshot(share_token)
    if not result:
        raise HTTPException(404, "Snapshot not found")

    if result.get("revoked"):
        raise HTTPException(410, "Snapshot has been revoked")

    return DataResponse(data=SnapshotVerifyResponse(**result))
