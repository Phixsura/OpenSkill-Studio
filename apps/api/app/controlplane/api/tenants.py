"""Tenant-facing endpoints: my tenants, detail, members, audit subset,
org-under-tenant creation (ADR-014 §1.8)."""

import structlog
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.controlplane.api.deps import make_actor
from app.controlplane.models.audit import CommercialAuditEvent
from app.controlplane.models.tenant import TenantAccount, TenantMember
from app.controlplane.schemas.tenant import (
    AddTenantMemberRequest,
    AuditEventResponse,
    CreateOrgUnderTenantRequest,
    SuspendTenantRequest,  # noqa: F401 — re-exported for tests
    TenantMemberResponse,
    TenantResponse,
    UpdateTenantRequest,
)
from app.controlplane.services import tenants as tenant_svc
from app.controlplane.services.audit import TENANT_VISIBLE_ACTIONS, record_audit
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta

log = structlog.get_logger()

router = APIRouter(prefix="/tenants", tags=["Tenants"])

# Impersonated sessions must not manage tenant membership — enforced globally
# by ImpersonationGuardMiddleware (read-only outside whitelist), so no
# per-endpoint deny dependency is needed here.


@router.get(
    "/mine",
    response_model=ListResponse[dict],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def my_tenants(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = (
        await db.execute(
            select(TenantAccount, TenantMember.role)
            .join(TenantMember, TenantMember.tenant_id == TenantAccount.id)
            .where(TenantMember.user_id == user.id)
            .order_by(TenantAccount.created_at)
        )
    ).all()
    data = [{**TenantResponse.model_validate(t).model_dump(), "my_role": role} for t, role in rows]
    return ListResponse(
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=len(data) or 1, has_more=False),
    )


@router.get(
    "/{tenant_id}",
    response_model=DataResponse[TenantResponse],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_tenant(
    tenant_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    tenant = await db.get(TenantAccount, tenant_id)
    return DataResponse(data=TenantResponse.model_validate(tenant))


@router.patch(
    "/{tenant_id}",
    response_model=DataResponse[TenantResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def update_tenant(
    tenant_id: str,
    body: UpdateTenantRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner")
    tenant = await db.get(TenantAccount, tenant_id)
    updates = body.model_dump(exclude_unset=True)
    # R60[46]: capture pre-change values — country is a rev-share rule
    # dimension and timezone shifts budget/rating period boundaries; a silent
    # flip must be reconstructible from the audit trail.
    before = {field: getattr(tenant, field) for field in updates}
    for field, value in updates.items():
        setattr(tenant, field, value)
    if updates:
        await record_audit(
            db,
            actor=make_actor(request, user, "tenant"),
            action="tenant.updated",
            target_type="tenant",
            target_id=tenant.id,
            tenant_id=tenant.id,
            before=before,
            after=updates,
        )
    await db.commit()
    await db.refresh(tenant)
    return DataResponse(data=TenantResponse.model_validate(tenant))


# ── Members ──────────────────────────────────────────────────


@router.get(
    "/{tenant_id}/members",
    response_model=ListResponse[TenantMemberResponse],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def list_members(
    tenant_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    rows = (
        (
            await db.execute(
                select(TenantMember)
                .where(TenantMember.tenant_id == tenant_id)
                .order_by(TenantMember.created_at)
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[TenantMemberResponse.model_validate(m) for m in rows],
        meta=PaginationMeta(total=len(rows), page=1, per_page=len(rows) or 1, has_more=False),
    )


@router.post(
    "/{tenant_id}/members",
    response_model=DataResponse[TenantMemberResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def add_member(
    tenant_id: str,
    body: AddTenantMemberRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner")
    tenant = await db.get(TenantAccount, tenant_id)
    member = await tenant_svc.add_tenant_member(
        db,
        tenant,
        user_id=body.user_id,
        role=body.role,
        actor=make_actor(request, user, "tenant"),
    )
    await db.commit()
    return DataResponse(data=TenantMemberResponse.model_validate(member))


@router.delete(
    "/{tenant_id}/members/{member_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def remove_member(
    tenant_id: str,
    member_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner")
    tenant = await db.get(TenantAccount, tenant_id)
    await tenant_svc.remove_tenant_member(db, tenant, member_id)
    await db.commit()


# ── Tenant-scoped audit subset ───────────────────────────────


@router.get(
    "/{tenant_id}/audit-events",
    response_model=ListResponse[AuditEventResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def tenant_audit_events(
    tenant_id: str,
    action: str | None = Query(default=None, max_length=60),
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner", "billing_admin")
    query = select(CommercialAuditEvent).where(
        CommercialAuditEvent.tenant_id == tenant_id,
        # Platform-internal actions (cost rates, settlements, impersonation
        # of other tenants) are never visible tenant-side.
        CommercialAuditEvent.action.in_(TENANT_VISIBLE_ACTIONS),
    )
    if action:
        query = query.where(CommercialAuditEvent.action == action)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (
            await db.execute(
                query.order_by(CommercialAuditEvent.created_at.desc())
                .offset(offset)
                .limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[AuditEventResponse.model_validate(e) for e in rows],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(offset + per_page) < total
        ),
    )


# ── Org creation under a tenant ──────────────────────────────


@router.post(
    "/{tenant_id}/orgs",
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_org_under_tenant(
    tenant_id: str,
    body: CreateOrgUnderTenantRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner", "billing_admin")
    tenant = await db.get(TenantAccount, tenant_id)
    tenant_svc.require_tenant_active(tenant)

    # Entitlement: max_organizations (facade — engine lands in P2, the stub
    # counts and passes; wire is in place from day one)
    from sqlalchemy import func as _f

    from app.controlplane import facade
    from app.models.organization import Organization, OrgStatus

    current = (
        await db.execute(
            select(_f.count(Organization.id)).where(
                Organization.tenant_id == tenant_id,
                Organization.status != OrgStatus.ARCHIVED,
            )
        )
    ).scalar_one()
    await facade.check_quota(db, tenant, "max_organizations", current=current)

    from app.services.organization import OrganizationService

    svc = OrganizationService(db)
    org = await svc.create(
        name=body.name,
        slug=body.slug,
        description=body.description,
        created_by=user.id,
        tenant_id=tenant_id,
    )
    await db.commit()
    return {
        "data": {
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "tenant_id": org.tenant_id,
        }
    }
