"""Skill Passport API — own passport, snapshots, public verification, W3C VC export."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
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
    await db.refresh(passport)
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
    await db.refresh(snapshot)
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


# ---- W3C Verifiable Credential export ----

@router.get("/talent/passport/snapshots/{snapshot_id}/vc")
async def export_snapshot_as_vc(
    snapshot_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Export a passport snapshot as a W3C Verifiable Credential (JSON-LD).

    Requires authentication — only the snapshot owner can export.
    Returns application/ld+json content type.
    """
    from app.talent.models.passport import PassportSnapshot
    from app.talent.services.credential_signing import SigningKeyService
    from app.talent.services.vc_export import export_passport_as_vc

    snapshot = await db.get(PassportSnapshot, snapshot_id)
    if not snapshot or snapshot.user_id != user.id:
        raise HTTPException(404, "Snapshot not found")

    if snapshot.status != "active":
        raise HTTPException(410, "Snapshot has been revoked")

    # Get the passport's org — use the first org the user belongs to
    from sqlalchemy import select

    from app.models.organization import OrgMembership

    org_result = await db.execute(
        select(OrgMembership.org_id).where(OrgMembership.user_id == user.id).limit(1)
    )
    org_id = org_result.scalar_one_or_none()
    if not org_id:
        raise HTTPException(
            422,
            "No organization found — a VC requires an issuing organization",
        )

    key_svc = SigningKeyService(db)
    signing_key = await key_svc.get_or_create_active_key(org_id)
    await db.commit()
    await db.refresh(signing_key)

    vc = export_passport_as_vc(
        snapshot_payload=snapshot.payload,
        snapshot_id=snapshot.id,
        user_id=user.id,
        issued_at=snapshot.issued_at,
        expires_at=snapshot.expires_at,
        org_id=org_id,
        signing_key_id=signing_key.id,
        private_key_pem=signing_key.private_key_encrypted,
        public_key_pem=signing_key.public_key,
        checksum=snapshot.checksum,
    )

    return JSONResponse(content=vc, media_type="application/ld+json")
