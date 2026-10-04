"""Self-serve resolution surface (ADR-017 §7, client-SDK class).

The authenticated caller is the unit: resolve/record apply to user.id only.
Both run through the fail-safe facade — an experiment must never break a
product path, so errors resolve to the default experience.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.experiments import facade
from app.experiments.api.deps import require_self_serve_user
from app.experiments.schemas import SelfExposureRequest, SelfResolveRequest
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
