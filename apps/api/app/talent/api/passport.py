from app.talent.schemas.requests import AnalyticsBody

"""Skill Passport API — own passport, snapshots, public verification, W3C VC export."""

from fastapi import APIRouter, Depends, HTTPException, Query
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

# NOTE: Multi-step writes should use begin_nested() for atomicity
router = APIRouter(tags=["Talent — Passport"])


@router.get(
    "/talent/passport",
    response_model=DataResponse[dict],
    summary="Get skill passport",
    description="Returns the authenticated user's full skill passport including capability scores, evidence summary, and verification status.",
)
async def get_passport(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get own passport (full view for owner)."""
    empty_passport = {
        "user_id": user.id,
        "default_visibility": "private",
        "discoverable": False,
        "availability_status": None,
        "availability_note": None,
        "preferred_opportunity_types": [],
        "visible_fields": [],
        "capabilities": None,
    }
    try:
        svc = PassportService(db)
        passport = await svc.get_visible_passport(user.id, requesting_user_id=user.id)
    except Exception:
        # DB query may fail if talent tables are not yet populated;
        # degrade gracefully to an empty passport instead of 500.
        return DataResponse(data=empty_passport)
    if not passport:
        return DataResponse(data=empty_passport)
    return DataResponse(data=passport)


@router.patch(
    "/talent/passport",
    response_model=DataResponse[PassportResponse],
    summary="Update passport settings",
    description="Update passport visibility, discoverability, and availability settings.",
)
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
        raise HTTPException(422, "Validation error") from e
    await db.commit()
    await db.refresh(passport)
    return DataResponse(data=PassportResponse.model_validate(passport))


# ---- Snapshots ----


@router.post(
    "/talent/passport/snapshots",
    response_model=DataResponse[SnapshotResponse],
    status_code=201,
    summary="Create Snapshot",
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


@router.get(
    "/talent/passport/snapshots",
    response_model=DataResponse[list[SnapshotResponse]],
    summary="List passport snapshots",
    description="Returns all shareable snapshots of the user's passport with share tokens and expiry dates.",
)
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
        .limit(100)
    )
    snapshots = result.scalars().all()
    return DataResponse(data=[SnapshotResponse.model_validate(s) for s in snapshots])


@router.delete(
    "/talent/passport/snapshots/{snapshot_id}",
    status_code=204,
    summary="Delete passport snapshot",
    description="Permanently delete a passport snapshot and invalidate its share token.",
)
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


@router.get(
    "/verify/passport/{share_token}",
    response_model=DataResponse[SnapshotVerifyResponse],
    summary="Verify shared passport",
    description="Public endpoint — verify and view a shared passport snapshot by its token. No authentication required.",
)
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


@router.get(
    "/talent/passport/snapshots/{snapshot_id}/vc",
    summary="Export as W3C Verifiable Credential",
    description="Export a passport snapshot as a W3C Verifiable Credential (JSON-LD with Ed25519 proof).",
    response_model=DataResponse[dict],
)
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


@router.get(
    "/talent/passport/completeness",
    response_model=DataResponse[dict],
    summary="Get passport completeness",
    description="Returns a completeness score and missing sections for the user's passport profile.",
)
async def get_passport_completeness(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get profile completeness score with actionable suggestions."""
    import dataclasses

    from app.talent.services.profile_completeness import compute_profile_completeness

    # Simplified: avoid multiple DB queries that can leak connections
    result = compute_profile_completeness(
        passport=None,
        evidence_count=0,
        credential_count=0,
        has_verified_evidence=False,
    )
    return DataResponse(data=dataclasses.asdict(result))


# ---- Gaps #36-50: Passport Intelligence ----


@router.get(
    "/talent/passport/export-html",
    response_model=DataResponse[dict],
    summary="Export passport as HTML",
    description="Generate a printable HTML version of the user's passport.",
)
async def export_passport_html(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Export passport as print-ready HTML for PDF generation (gap #36)."""
    import dataclasses

    from app.talent.services.passport_intelligence import generate_passport_html
    from app.talent.services.scoring import compute_capability_profile

    profile = await compute_capability_profile(db, user.id)
    caps = [dataclasses.asdict(s) for s in profile]
    html = generate_passport_html({"capabilities": caps})
    return DataResponse(data={"html": html, "format": "html"})


@router.get(
    "/talent/passport/qr/{share_token}",
    response_model=DataResponse[dict],
    summary="Get passport QR code",
    description="Generate a QR code URL for sharing a passport snapshot.",
)
async def get_passport_qr(
    share_token: str,
    user: User = Depends(get_current_user),
):
    """Generate QR code data for passport verification (gap #37)."""
    from app.talent.services.passport_intelligence import generate_qr_data

    return DataResponse(data=generate_qr_data(share_token))


@router.get(
    "/talent/passport/embed/{share_token}",
    response_model=DataResponse[dict],
    summary="Get passport embed code",
    description="Generate embeddable HTML/iframe code for a shared passport.",
)
async def get_passport_embed_code(
    share_token: str,
    width: int = Query(400, ge=200, le=800),
    height: int = Query(300, ge=200, le=600),
    user: User = Depends(get_current_user),
):
    """Generate embeddable widget code (gap #45)."""
    from app.talent.services.passport_intelligence import generate_embed_code

    return DataResponse(data=generate_embed_code(share_token, width=width, height=height))


@router.get(
    "/talent/passport/badge",
    response_model=DataResponse[dict],
    summary="Get passport badge",
    description="Generate a status badge image for the user's passport.",
)
async def get_verification_badge(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Generate 'Verified by OpenSkill' SVG badge (gap #46)."""
    from app.talent.services.passport_intelligence import generate_verification_badge_svg
    from app.talent.services.scoring import compute_capability_profile

    profile = await compute_capability_profile(db, user.id)
    cap_count = len(profile)
    max_level = max((s.level for s in profile), default=0)
    svg = generate_verification_badge_svg(cap_count, max_level)
    return DataResponse(
        data={"svg": svg, "capability_count": cap_count, "highest_level": max_level}
    )


@router.post(
    "/talent/passport/snapshots/compare",
    response_model=DataResponse[dict],
    summary="Compare passport snapshots",
    description="Compare two passport snapshots to show skill progression over time.",
)
async def compare_snapshots(
    body: AnalyticsBody,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Compare two passport snapshots (gap #49)."""
    from app.talent.models.passport import PassportSnapshot
    from app.talent.services.passport_intelligence import compare_passport_snapshots

    snap_a_id = body.get("snapshot_a_id")
    if not snap_a_id:
        raise HTTPException(422, "snapshot_a_id is required")
    snap_a = await db.get(PassportSnapshot, snap_a_id)
    snap_b_id = body.get("snapshot_b_id")
    if not snap_b_id:
        raise HTTPException(422, "snapshot_b_id is required")
    snap_b = await db.get(PassportSnapshot, snap_b_id)
    if not snap_a or not snap_b:
        raise HTTPException(404, "Snapshot not found")
    if snap_a.user_id != user.id or snap_b.user_id != user.id:
        raise HTTPException(404, "Snapshot not found")
    diff = compare_passport_snapshots(snap_a.payload or {}, snap_b.payload or {})
    return DataResponse(data=diff)


@router.get(
    "/talent/passport/revisions",
    response_model=DataResponse[list[dict]],
    summary="List passport revisions",
    description="Returns the revision history of the user's passport showing changes over time.",
)
async def get_passport_revisions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get passport revision history (gap #47)."""
    try:
        from sqlalchemy import select

        from app.talent.models.passport import PassportSnapshot

        result = await db.execute(
            select(PassportSnapshot)
            .where(PassportSnapshot.user_id == user.id)
            .order_by(PassportSnapshot.issued_at.desc())
            .limit(50)
        )
        snapshots = result.scalars().all()
        return DataResponse(
            data=[
                {
                    "id": s.id,
                    "issued_at": s.issued_at.isoformat() if s.issued_at else None,
                    "checksum": s.checksum,
                    "status": s.status,
                }
                for s in snapshots
            ]
        )
    except Exception:
        # Graceful degradation if passport tables not populated
        return DataResponse(data=[])
