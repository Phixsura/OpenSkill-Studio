"""Platform control-plane endpoints: tenants lifecycle, platform roles,
impersonation grants, audit explorer (ADR-014 §1.8)."""

import structlog
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.controlplane.api.deps import make_actor, require_platform_role
from app.controlplane.models.audit import CommercialAuditEvent
from app.controlplane.models.tenant import (
    PLATFORM_ROLES,
    PlatformRoleAssignment,
    SupportImpersonationGrant,
    TenantAccount,
    TenantAccountType,
    TenantStatus,
)
from app.controlplane.schemas.tenant import (
    AuditEventResponse,
    CreateImpersonationGrantRequest,
    CreateTenantRequest,
    GrantPlatformRoleRequest,
    ImpersonationGrantResponse,
    ImpersonationTokenResponse,
    PlatformRoleResponse,
    SuspendTenantRequest,
    TenantResponse,
)
from app.controlplane.services import tenants as tenant_svc
from app.controlplane.services.audit import record_audit
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.schemas.base import DataResponse, ListResponse, PaginationMeta

log = structlog.get_logger()

router = APIRouter(prefix="/platform", tags=["Platform"])


# ── Tenants ──────────────────────────────────────────────────


@router.post(
    "/tenants",
    response_model=DataResponse[TenantResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def create_tenant(
    body: CreateTenantRequest,
    request: Request,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    try:
        account_type = TenantAccountType(body.account_type)
    except ValueError as exc:
        raise AppError(
            "VALIDATION_ERROR", f"Unknown account_type '{body.account_type}'", 422
        ) from exc
    tenant = await tenant_svc.create_tenant(
        db,
        name=body.name,
        slug=body.slug,
        actor=make_actor(request, user),
        # Platform-created tenants are commercial acts — ACTIVE, no trial.
        status=TenantStatus.ACTIVE,
        with_trial=False,
        account_type=account_type,
        currency=body.currency,
        timezone=body.timezone,
        billing_email=body.billing_email,
        country=body.country,
    )
    await db.commit()
    return DataResponse(data=TenantResponse.model_validate(tenant))


@router.get(
    "/tenants",
    response_model=ListResponse[TenantResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def search_tenants(
    status: str | None = Query(default=None),
    account_type: str | None = Query(default=None),
    q: str | None = Query(default=None, max_length=200),
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(
        require_platform_role("platform_admin", "platform_support", "billing_admin")
    ),
    db: AsyncSession = Depends(get_db),
):
    query = select(TenantAccount)
    if status:
        try:
            query = query.where(TenantAccount.status == TenantStatus(status))
        except ValueError as exc:
            raise AppError("VALIDATION_ERROR", f"Unknown status '{status}'", 422) from exc
    if account_type:
        try:
            query = query.where(TenantAccount.account_type == TenantAccountType(account_type))
        except ValueError as exc:
            raise AppError(
                "VALIDATION_ERROR", f"Unknown account_type '{account_type}'", 422
            ) from exc
    if q:
        # R96[m11]: escape LIKE wildcards — a raw '%'/'_' in q matched
        # everything (pattern probing + pathological-pattern DoS on long
        # alternating wildcards).
        escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        like = f"%{escaped}%"
        query = query.where(
            or_(
                TenantAccount.name.ilike(like, escape="\\"),
                TenantAccount.slug.ilike(like, escape="\\"),
                TenantAccount.billing_email.ilike(like, escape="\\"),
            )
        )
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (
            await db.execute(
                query.order_by(TenantAccount.created_at.desc()).offset(offset).limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[TenantResponse.model_validate(t) for t in rows],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(offset + per_page) < total
        ),
    )


@router.get(
    "/tenants/{tenant_id}",
    response_model=DataResponse[dict],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_tenant_detail(
    tenant_id: str,
    user: User = Depends(
        require_platform_role("platform_admin", "platform_support", "billing_admin")
    ),
    db: AsyncSession = Depends(get_db),
):
    tenant = await db.get(TenantAccount, tenant_id)
    if tenant is None:
        raise AppError("TENANT_NOT_FOUND", "Tenant not found", 404)
    orgs = (
        await db.execute(
            select(Organization.id, Organization.name, Organization.slug, Organization.status)
            .where(Organization.tenant_id == tenant_id)
            .order_by(Organization.created_at)
        )
    ).all()
    return DataResponse(
        data={
            "tenant": TenantResponse.model_validate(tenant).model_dump(),
            "organizations": [
                {"id": o.id, "name": o.name, "slug": o.slug, "status": o.status.value} for o in orgs
            ],
        }
    )


@router.post(
    "/tenants/{tenant_id}/suspend",
    response_model=DataResponse[TenantResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def suspend_tenant(
    tenant_id: str,
    body: SuspendTenantRequest,
    request: Request,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    tenant = await db.get(TenantAccount, tenant_id)
    if tenant is None:
        raise AppError("TENANT_NOT_FOUND", "Tenant not found", 404)
    tenant = await tenant_svc.transition_status(
        db,
        tenant,
        TenantStatus.SUSPENDED,
        actor=make_actor(request, user),
        reason=body.reason,
    )
    await db.commit()
    return DataResponse(data=TenantResponse.model_validate(tenant))


@router.post(
    "/tenants/{tenant_id}/reactivate",
    response_model=DataResponse[TenantResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def reactivate_tenant(
    tenant_id: str,
    request: Request,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    tenant = await db.get(TenantAccount, tenant_id)
    if tenant is None:
        raise AppError("TENANT_NOT_FOUND", "Tenant not found", 404)
    tenant = await tenant_svc.transition_status(
        db, tenant, TenantStatus.ACTIVE, actor=make_actor(request, user)
    )
    await db.commit()
    return DataResponse(data=TenantResponse.model_validate(tenant))


# ── Platform roles ───────────────────────────────────────────


@router.post(
    "/platform-roles",
    response_model=DataResponse[PlatformRoleResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def grant_platform_role(
    body: GrantPlatformRoleRequest,
    request: Request,
    admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    if body.role not in PLATFORM_ROLES:
        raise AppError("VALIDATION_ERROR", f"Unknown platform role '{body.role}'", 422)
    target = await db.get(User, body.user_id)
    if target is None or not target.is_active:
        raise AppError("USER_NOT_FOUND", "User not found", 404)
    exists = await db.execute(
        select(PlatformRoleAssignment.id)
        .where(
            PlatformRoleAssignment.user_id == body.user_id,
            PlatformRoleAssignment.role == body.role,
        )
        .limit(1)
    )
    if exists.scalar_one_or_none() is not None:
        raise AppError("PLATFORM_ROLE_EXISTS", "User already holds this role", 409)
    assignment = PlatformRoleAssignment(user_id=body.user_id, role=body.role, granted_by=admin.id)
    db.add(assignment)
    await db.flush()
    await record_audit(
        db,
        actor=make_actor(request, admin),
        action="platform_role.granted",
        target_type="user",
        target_id=body.user_id,
        after={"role": body.role},
    )
    await db.commit()
    return DataResponse(data=PlatformRoleResponse.model_validate(assignment))


@router.delete(
    "/platform-roles/{assignment_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def revoke_platform_role(
    assignment_id: str,
    request: Request,
    admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    assignment = await db.get(PlatformRoleAssignment, assignment_id)
    if assignment is None:
        raise AppError("PLATFORM_ROLE_NOT_FOUND", "Role assignment not found", 404)
    await record_audit(
        db,
        actor=make_actor(request, admin),
        action="platform_role.revoked",
        target_type="user",
        target_id=assignment.user_id,
        before={"role": assignment.role},
    )
    await db.delete(assignment)
    await db.commit()


# ── Impersonation ────────────────────────────────────────────


@router.post(
    "/impersonation-grants",
    response_model=DataResponse[ImpersonationGrantResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_impersonation_grant(
    body: CreateImpersonationGrantRequest,
    request: Request,
    user: User = Depends(require_platform_role("platform_admin", "platform_support")),
    db: AsyncSession = Depends(get_db),
):
    grant = await tenant_svc.create_impersonation_grant(
        db,
        platform_user=user,
        target_user_id=body.target_user_id,
        tenant_id=body.tenant_id,
        reason=body.reason,
        expires_in_minutes=body.expires_in_minutes,
        actor=make_actor(request, user),
    )
    await db.commit()
    return DataResponse(data=ImpersonationGrantResponse.model_validate(grant))


@router.post(
    "/impersonation-grants/{grant_id}/token",
    response_model=DataResponse[ImpersonationTokenResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def mint_impersonation_token(
    grant_id: str,
    request: Request,
    user: User = Depends(require_platform_role("platform_admin", "platform_support")),
    db: AsyncSession = Depends(get_db),
):
    grant = await db.get(SupportImpersonationGrant, grant_id)
    if grant is None or grant.platform_user_id != user.id:
        # Only the grant creator may mint from it (uniform 404)
        raise AppError("IMPERSONATION_GRANT_NOT_FOUND", "Grant not found", 404)
    token, expires_in = await tenant_svc.mint_impersonation_token(
        db, grant, actor=make_actor(request, user)
    )
    await db.commit()
    return DataResponse(data=ImpersonationTokenResponse(access_token=token, expires_in=expires_in))


@router.post(
    "/impersonation-grants/{grant_id}/revoke",
    response_model=DataResponse[ImpersonationGrantResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def revoke_impersonation_grant(
    grant_id: str,
    request: Request,
    user: User = Depends(require_platform_role("platform_admin", "platform_support")),
    db: AsyncSession = Depends(get_db),
):
    from datetime import UTC, datetime

    grant = await db.get(SupportImpersonationGrant, grant_id)
    if grant is None:
        raise AppError("IMPERSONATION_GRANT_NOT_FOUND", "Grant not found", 404)
    if grant.revoked_at is None:
        grant.revoked_at = datetime.now(UTC)
        await record_audit(
            db,
            actor=make_actor(request, user),
            action="impersonation.grant_revoked",
            target_type="user",
            target_id=grant.target_user_id,
            tenant_id=grant.tenant_id,
        )
    await db.commit()
    return DataResponse(data=ImpersonationGrantResponse.model_validate(grant))


# ── Audit explorer ───────────────────────────────────────────


@router.get(
    "/audit-events",
    response_model=ListResponse[AuditEventResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_audit_events(
    tenant_id: str | None = Query(default=None),
    action: str | None = Query(default=None, max_length=60),
    target_type: str | None = Query(default=None, max_length=40),
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=50, ge=1, le=200),
    user: User = Depends(
        require_platform_role("platform_admin", "platform_support", "billing_admin")
    ),
    db: AsyncSession = Depends(get_db),
):
    query = select(CommercialAuditEvent)
    if tenant_id:
        query = query.where(CommercialAuditEvent.tenant_id == tenant_id)
    if action:
        query = query.where(CommercialAuditEvent.action == action)
    if target_type:
        query = query.where(CommercialAuditEvent.target_type == target_type)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (
            await db.execute(
                # R101[L21]: id tiebreak — same-tx audit rows share created_at
                query.order_by(
                    CommercialAuditEvent.created_at.desc(), CommercialAuditEvent.id.desc()
                )
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
