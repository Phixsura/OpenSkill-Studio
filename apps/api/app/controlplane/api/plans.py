"""Plan catalog + platform plan management + tenant entitlements endpoints
(ADR-014 §2.7)."""

import structlog
from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.controlplane.api.deps import make_actor, require_platform_role
from app.controlplane.models.plan import PlanPrice, PlanVersion, ProductPlan
from app.controlplane.models.tenant import TenantAccount
from app.controlplane.schemas.plan import (
    CreatePlanRequest,
    PlanPriceResponse,
    PlanResponse,
    PlanVersionResponse,
    SetOverrideRequest,
    UpdateDraftVersionRequest,
)
from app.controlplane.services import plans as plan_svc
from app.controlplane.services import tenants as tenant_svc
from app.controlplane.services.entitlements import ENTITLEMENT_DEFS, get_effective
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta

log = structlog.get_logger()

router = APIRouter(tags=["Plans & Entitlements"])


async def _version_with_prices(db: AsyncSession, version: PlanVersion) -> PlanVersionResponse:
    prices = (
        (
            await db.execute(
                select(PlanPrice)
                .where(PlanPrice.plan_version_id == version.id)
                .order_by(PlanPrice.currency, PlanPrice.interval)
            )
        )
        .scalars()
        .all()
    )
    resp = PlanVersionResponse.model_validate(version)
    resp.prices = [PlanPriceResponse.model_validate(p) for p in prices]
    return resp


# ── Public catalog ───────────────────────────────────────────


@router.get("/plans", dependencies=[Depends(rate_limit(30, 60))])
async def public_plan_catalog(db: AsyncSession = Depends(get_db)):
    """Active plans with their active version + prices — public pricing page."""
    rows = (
        await db.execute(
            select(ProductPlan, PlanVersion)
            .join(PlanVersion, PlanVersion.plan_id == ProductPlan.id)
            .where(ProductPlan.is_active.is_(True), PlanVersion.status == "active")
            .order_by(ProductPlan.sort_order)
        )
    ).all()
    data = []
    for plan, version in rows:
        v = await _version_with_prices(db, version)
        data.append(
            {
                **PlanResponse.model_validate(plan).model_dump(),
                "active_version": v.model_dump(),
            }
        )
    return ListResponse(
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=len(data) or 1, has_more=False),
    )


# ── Platform plan management ─────────────────────────────────


@router.get("/platform/plans", dependencies=[Depends(rate_limit(30, 60))])
async def list_plans_admin(
    user: User = Depends(require_platform_role("platform_admin", "billing_admin")),
    db: AsyncSession = Depends(get_db),
):
    plans = (await db.execute(select(ProductPlan).order_by(ProductPlan.sort_order))).scalars().all()
    data = []
    for plan in plans:
        versions = (
            (
                await db.execute(
                    select(PlanVersion)
                    .where(PlanVersion.plan_id == plan.id)
                    .order_by(PlanVersion.version.desc())
                )
            )
            .scalars()
            .all()
        )
        data.append(
            {
                **PlanResponse.model_validate(plan).model_dump(),
                "versions": [(await _version_with_prices(db, v)).model_dump() for v in versions],
            }
        )
    return ListResponse(
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=len(data) or 1, has_more=False),
    )


@router.post(
    "/platform/plans",
    response_model=DataResponse[PlanResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_plan(
    body: CreatePlanRequest,
    request: Request,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    plan = await plan_svc.create_plan(
        db,
        key=body.key,
        name=body.name,
        description=body.description,
        actor=make_actor(request, user),
    )
    await db.commit()
    return DataResponse(data=PlanResponse.model_validate(plan))


@router.post(
    "/platform/plans/{plan_id}/versions",
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_draft_version(
    plan_id: str,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    plan = await db.get(ProductPlan, plan_id)
    if plan is None:
        raise AppError("PLAN_NOT_FOUND", "Plan not found", 404)
    draft = await plan_svc.create_draft_version(db, plan, created_by=user.id)
    await db.commit()
    return DataResponse(data=await _version_with_prices(db, draft))


@router.patch(
    "/platform/plan-versions/{version_id}",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def update_draft_version(
    version_id: str,
    body: UpdateDraftVersionRequest,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    version = await db.get(PlanVersion, version_id)
    if version is None:
        raise AppError("PLAN_NOT_FOUND", "Plan version not found", 404)
    version = await plan_svc.update_draft(
        db,
        version,
        entitlements=body.entitlements,
        prices=[p.model_dump() for p in body.prices] if body.prices is not None else None,
    )
    await db.commit()
    return DataResponse(data=await _version_with_prices(db, version))


@router.post(
    "/platform/plan-versions/{version_id}/activate",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def activate_version(
    version_id: str,
    request: Request,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    version = await db.get(PlanVersion, version_id)
    if version is None:
        raise AppError("PLAN_NOT_FOUND", "Plan version not found", 404)
    version = await plan_svc.activate_version(db, version, actor=make_actor(request, user))
    await db.commit()
    return DataResponse(data=await _version_with_prices(db, version))


# ── Tenant entitlements ──────────────────────────────────────


@router.get(
    "/tenants/{tenant_id}/entitlements",
    dependencies=[Depends(rate_limit(60, 60))],
)
async def tenant_entitlements(
    tenant_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Effective entitlements + sources + usage snapshot (§2.7 example)."""
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    tenant = await db.get(TenantAccount, tenant_id)
    eff = await get_effective(db, tenant)
    usage = await _usage_snapshot(db, tenant_id)
    entitlements = {}
    for key, d in ENTITLEMENT_DEFS.items():
        entry: dict = {"value": eff.values.get(key), "source": eff.sources.get(key)}
        if key in eff.enforcement:
            entry["enforcement"] = eff.enforcement[key]
        if d.type != "bool" and key in usage:
            entry["usage"] = usage[key]
        entitlements[key] = entry
    return DataResponse(
        data={
            "plan": {
                "key": eff.plan_key,
                "version": eff.plan_version,
                "trial": eff.trial,
                "trial_ends_at": (
                    tenant.trial_ends_at.isoformat() if tenant.trial_ends_at else None
                ),
            },
            "entitlements": entitlements,
        }
    )


async def _usage_snapshot(db: AsyncSession, tenant_id: str) -> dict:
    """Current usage per numeric entitlement (only cheap, indexed counts)."""
    from app.models.organization import Organization, OrgMember, OrgRole, OrgStatus

    org_count = (
        await db.execute(
            select(func.count(Organization.id)).where(
                Organization.tenant_id == tenant_id,
                Organization.status != OrgStatus.ARCHIVED,
            )
        )
    ).scalar_one()
    learner_q = (
        select(func.count(func.distinct(OrgMember.user_id)))
        .select_from(OrgMember)
        .join(Organization, Organization.id == OrgMember.org_id)
        .where(Organization.tenant_id == tenant_id, OrgMember.status == "ACTIVE")
    )
    learners = (await db.execute(learner_q.where(OrgMember.role == OrgRole.STUDENT))).scalar_one()
    instructors = (
        await db.execute(
            learner_q.where(OrgMember.role.in_([OrgRole.INSTRUCTOR, OrgRole.ADMIN, OrgRole.OWNER]))
        )
    ).scalar_one()
    return {
        "max_organizations": org_count,
        "max_active_learners": learners,
        "max_instructors": instructors,
    }


@router.put(
    "/platform/tenants/{tenant_id}/entitlements/{key}",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def set_override(
    tenant_id: str,
    key: str,
    body: SetOverrideRequest,
    request: Request,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    tenant = await db.get(TenantAccount, tenant_id)
    if tenant is None:
        raise AppError("TENANT_NOT_FOUND", "Tenant not found", 404)
    override = await plan_svc.set_override(
        db,
        tenant_id,
        key,
        value=body.value,
        enforcement=body.enforcement,
        expires_at=body.expires_at,
        reason=body.reason,
        actor=make_actor(request, user),
    )
    await db.commit()
    return DataResponse(
        data={
            "tenant_id": tenant_id,
            "key": key,
            "value": override.value.get("v"),
            "enforcement": override.enforcement,
            "expires_at": override.expires_at.isoformat() if override.expires_at else None,
        }
    )


@router.delete(
    "/platform/tenants/{tenant_id}/entitlements/{key}",
    status_code=204,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def remove_override(
    tenant_id: str,
    key: str,
    request: Request,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    await plan_svc.remove_override(db, tenant_id, key, actor=make_actor(request, user))
    await db.commit()
