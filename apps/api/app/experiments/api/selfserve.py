"""Self-serve resolution surface (ADR-017 §7, client-SDK class).

The authenticated caller is the unit: resolve/record apply to user.id only.
Both run through the fail-safe facade — an experiment must never break a
product path, so errors resolve to the default experience.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.rate_limit import rate_limit
from app.experiments import facade
from app.experiments.api.deps import require_self_serve_user
from app.experiments.schemas import (
    AnonExposureRequest,
    AnonResolveRequest,
    IdentityLinkRequest,
    SelfExposureRequest,
    SelfResolveRequest,
)
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/experiments/self", tags=["Experiments — Self-serve"])


@router.post("/resolve", response_model=DataResponse[dict])
async def self_resolve(
    body: SelfResolveRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_self_serve_user),
):
    # Defect #32: without an org context, org-scoped experiments were
    # unreachable from the self-serve surface. The caller's primary org
    # (min org_id — the same deterministic rule segments use) rides along.
    from sqlalchemy import func, select

    from app.models.organization import OrgMember

    primary_org = (
        await db.execute(
            select(func.min(OrgMember.org_id)).where(OrgMember.user_id == user.id)
        )
    ).scalar_one_or_none()
    resolved = await facade.resolve_variant(
        db,
        experiment_key=body.experiment_key,
        unit_type="user",
        unit_id=user.id,
        context={"org_id": primary_org} if primary_org else None,
    )
    await db.commit()  # persist the sticky assignment the resolve may create
    if resolved is None:
        return {"data": {"variant_key": None, "config": {}}}
    return {
        "data": {
            "variant_key": resolved.variant_key,
            "config": resolved.config,
            "assigned_version": resolved.assigned_version,
        }
    }


@router.post("/exposures", response_model=DataResponse[dict], status_code=201)
async def self_exposure(
    body: SelfExposureRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_self_serve_user),
):
    recorded = await facade.record_exposure(
        db,
        experiment_key=body.experiment_key,
        unit_type="user",
        unit_id=user.id,
        dedup_key=body.dedup_key,
    )
    await db.commit()
    return {"data": {"recorded": bool(recorded)}}


# ── §4.17: pre-login surface (round 211) ──────────────────────────────
anon_router = APIRouter(prefix="/experiments/anon",
                        tags=["Experiments — Anonymous"])


@anon_router.post(
    "/resolve",
    response_model=DataResponse[dict],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def anon_resolve(
    body: AnonResolveRequest,
    db: AsyncSession = Depends(get_db),
):
    """Unauthenticated pre-login resolution: the anonymous id is an ID
    NAMESPACE the service normalizes — a linked id serves the linked
    user's assignments, an unlinked one its own sticky user-typed row.
    Fail-safe like the self-serve surface: errors resolve to the default
    experience."""
    resolved = await facade.resolve_variant(
        db,
        experiment_key=body.experiment_key,
        unit_type="anonymous",
        unit_id=body.anonymous_id,
    )
    await db.commit()
    if resolved is None:
        return {"data": {"variant_key": None, "config": {}}}
    return {
        "data": {
            "variant_key": resolved.variant_key,
            "config": resolved.config,
            "assigned_version": resolved.assigned_version,
        }
    }


@router.post("/identity-link", response_model=DataResponse[dict])
async def link_identity(
    body: IdentityLinkRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_self_serve_user),
):
    """§4.17: claim a pre-login anonymous id as the CALLER's — first link
    wins (422 EXPERIMENT_IDENTITY_CONFLICT on rebinding), re-linking the
    same pair is idempotent, and every anon assignment migrates in place
    to the user key. A platform admin may link on BEHALF of a user
    (support flows, round 232); anyone else naming another user is 403."""
    from app.exceptions import AppError
    from app.experiments.services.assignment import AssignmentService
    from app.models.user import UserRole

    target_user_id = body.user_id or user.id
    if target_user_id != user.id and user.role != UserRole.ADMIN:
        raise AppError(
            "FORBIDDEN",
            "Only platform admins may link an anonymous id for another user",
            403,
        )
    out = await AssignmentService(db).link_identity(
        anonymous_id=body.anonymous_id, user_id=target_user_id
    )
    await db.commit()
    return {"data": out}


@anon_router.post(
    "/exposures",
    response_model=DataResponse[dict],
    status_code=201,
    dependencies=[Depends(rate_limit(120, 60))],
)
async def anon_exposure(
    body: AnonExposureRequest,
    db: AsyncSession = Depends(get_db),
):
    """§4.17 (#75): pre-login exposure recording — the anonymous namespace
    normalizes exactly as resolve does, so a linked id's exposures land on
    the user's assignment."""
    recorded = await facade.record_exposure(
        db,
        experiment_key=body.experiment_key,
        unit_type="anonymous",
        unit_id=body.anonymous_id,
        dedup_key=body.dedup_key,
    )
    await db.commit()
    return {"data": {"recorded": bool(recorded)}}
