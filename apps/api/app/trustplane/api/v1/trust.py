"""Trust & Safety API endpoints (ADR-017 Phase 1).

Org-scoped endpoints for AI System Inventory, Risk Classification,
and Trust Audit Log.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.trustplane.models.audit import TrustAuditEvent
from app.trustplane.schemas.inventory import (
    ChangeLifecycleRequest,
    CreateSystemRequest,
    CreateUseCaseRequest,
    LinkEntityRequest,
    SystemResponse,
    SystemSummaryResponse,
    UpdateSystemRequest,
    UpdateUseCaseRequest,
    UseCaseResponse,
)
from app.trustplane.schemas.risk import (
    AssessmentResponse,
    AssessmentSummaryResponse,
    CreateAssessmentRequest,
    CreatePolicyRequest,
    OverrideTierRequest,
    PolicyResponse,
    RejectAssessmentRequest,
    ReviewDecisionRequest,
    TrustAuditEventResponse,
)
from app.trustplane.services import inventory as inventory_svc
from app.trustplane.services import risk as risk_svc

router = APIRouter(tags=["Trust & Safety"])

ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


# ── AI System CRUD ───────────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/systems",
    response_model=DataResponse[SystemResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_system(
    org_id: str,
    body: CreateSystemRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    system = await inventory_svc.create_system(
        db, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=SystemResponse.model_validate(system))


@router.get(
    "/orgs/{org_id}/trust/systems",
    response_model=ListResponse[SystemSummaryResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_systems(
    org_id: str,
    lifecycle: str | None = None,
    system_type: str | None = None,
    risk_tier: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    systems, total = await inventory_svc.list_systems(
        db, org_id, lifecycle=lifecycle, system_type=system_type,
        risk_tier=risk_tier, page=page, per_page=per_page,
    )
    return ListResponse(
        data=[SystemSummaryResponse.model_validate(s) for s in systems],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page,
            has_more=(page * per_page) < total,
        ),
    )


@router.get(
    "/orgs/{org_id}/trust/systems/{system_id}",
    response_model=DataResponse[SystemResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_system(
    org_id: str,
    system_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    system = await inventory_svc.get_system(db, system_id, org_id)
    return DataResponse(data=SystemResponse.model_validate(system))


@router.patch(
    "/orgs/{org_id}/trust/systems/{system_id}",
    response_model=DataResponse[SystemResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def update_system(
    org_id: str,
    system_id: str,
    body: UpdateSystemRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    system = await inventory_svc.update_system(
        db, system_id, org_id, user.id, **body.model_dump(exclude_unset=True)
    )
    await db.commit()
    return DataResponse(data=SystemResponse.model_validate(system))


@router.post(
    "/orgs/{org_id}/trust/systems/{system_id}/lifecycle",
    response_model=DataResponse[SystemResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def change_lifecycle(
    org_id: str,
    system_id: str,
    body: ChangeLifecycleRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    system = await inventory_svc.change_lifecycle(
        db, system_id, org_id, user.id, body.lifecycle, body.reason
    )
    await db.commit()
    return DataResponse(data=SystemResponse.model_validate(system))


@router.post(
    "/orgs/{org_id}/trust/systems/{system_id}/link",
    response_model=DataResponse[SystemResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def link_entity(
    org_id: str,
    system_id: str,
    body: LinkEntityRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    system = await inventory_svc.link_entity(
        db, system_id, org_id, user.id, body.entity_type, body.entity_id
    )
    await db.commit()
    return DataResponse(data=SystemResponse.model_validate(system))


# ── Use Cases ────────────────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/systems/{system_id}/use-cases",
    response_model=DataResponse[UseCaseResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_use_case(
    org_id: str,
    system_id: str,
    body: CreateUseCaseRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    use_case = await inventory_svc.create_use_case(
        db, system_id, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=UseCaseResponse.model_validate(use_case))


@router.get(
    "/orgs/{org_id}/trust/systems/{system_id}/use-cases",
    response_model=DataResponse[list[UseCaseResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_use_cases(
    org_id: str,
    system_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    use_cases = await inventory_svc.list_use_cases(db, system_id, org_id)
    return DataResponse(data=[UseCaseResponse.model_validate(u) for u in use_cases])


@router.patch(
    "/orgs/{org_id}/trust/systems/{system_id}/use-cases/{use_id}",
    response_model=DataResponse[UseCaseResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def update_use_case(
    org_id: str,
    system_id: str,
    use_id: str,
    body: UpdateUseCaseRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    use_case = await inventory_svc.update_use_case(
        db, use_id, system_id, org_id, user.id, **body.model_dump(exclude_unset=True)
    )
    await db.commit()
    return DataResponse(data=UseCaseResponse.model_validate(use_case))


@router.delete(
    "/orgs/{org_id}/trust/systems/{system_id}/use-cases/{use_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def delete_use_case(
    org_id: str,
    system_id: str,
    use_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    await inventory_svc.delete_use_case(db, use_id, system_id, org_id, user.id)
    await db.commit()


# ── Risk Assessments ─────────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/systems/{system_id}/assessments",
    response_model=DataResponse[AssessmentResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_assessment(
    org_id: str,
    system_id: str,
    body: CreateAssessmentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    assessment = await risk_svc.create_assessment(
        db, system_id, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=AssessmentResponse.model_validate(assessment))


@router.get(
    "/orgs/{org_id}/trust/systems/{system_id}/assessments",
    response_model=ListResponse[AssessmentSummaryResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_assessments(
    org_id: str,
    system_id: str,
    status: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    assessments, total = await risk_svc.list_assessments(
        db, system_id, org_id, status=status, page=page, per_page=per_page,
    )
    return ListResponse(
        data=[AssessmentSummaryResponse.model_validate(a) for a in assessments],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page,
            has_more=(page * per_page) < total,
        ),
    )


@router.get(
    "/orgs/{org_id}/trust/systems/{system_id}/assessments/{assessment_id}",
    response_model=DataResponse[AssessmentResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_assessment(
    org_id: str,
    system_id: str,
    assessment_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    assessment = await risk_svc.get_assessment(db, assessment_id, org_id)
    return DataResponse(data=AssessmentResponse.model_validate(assessment))


@router.post(
    "/orgs/{org_id}/trust/systems/{system_id}/assessments/{assessment_id}/submit",
    response_model=DataResponse[AssessmentResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def submit_assessment(
    org_id: str,
    system_id: str,
    assessment_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    assessment = await risk_svc.submit_assessment(db, assessment_id, org_id, user.id)
    await db.commit()
    return DataResponse(data=AssessmentResponse.model_validate(assessment))


@router.post(
    "/orgs/{org_id}/trust/systems/{system_id}/assessments/{assessment_id}/approve",
    response_model=DataResponse[AssessmentResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def approve_assessment(
    org_id: str,
    system_id: str,
    assessment_id: str,
    body: ReviewDecisionRequest | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    assessment = await risk_svc.approve_assessment(db, assessment_id, org_id, user.id)
    await db.commit()
    return DataResponse(data=AssessmentResponse.model_validate(assessment))


@router.post(
    "/orgs/{org_id}/trust/systems/{system_id}/assessments/{assessment_id}/reject",
    response_model=DataResponse[AssessmentResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def reject_assessment(
    org_id: str,
    system_id: str,
    assessment_id: str,
    body: RejectAssessmentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    assessment = await risk_svc.reject_assessment(
        db, assessment_id, org_id, user.id, body.justification
    )
    await db.commit()
    return DataResponse(data=AssessmentResponse.model_validate(assessment))


@router.post(
    "/orgs/{org_id}/trust/systems/{system_id}/assessments/{assessment_id}/override-tier",
    response_model=DataResponse[AssessmentResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def override_tier(
    org_id: str,
    system_id: str,
    assessment_id: str,
    body: OverrideTierRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER)
    assessment = await risk_svc.override_tier(
        db, assessment_id, org_id, user.id, body.tier, body.justification
    )
    await db.commit()
    return DataResponse(data=AssessmentResponse.model_validate(assessment))


# ── Risk Policies ────────────────────────────────────────────────────


@router.get(
    "/orgs/{org_id}/trust/risk-policies",
    response_model=DataResponse[list[PolicyResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_policies(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    policies = await risk_svc.list_policies(db, org_id)
    return DataResponse(data=[PolicyResponse.model_validate(p) for p in policies])


@router.post(
    "/orgs/{org_id}/trust/risk-policies",
    response_model=DataResponse[PolicyResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(5, 60))],
)
async def create_policy(
    org_id: str,
    body: CreatePolicyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER)
    policy = await risk_svc.create_policy(
        db, org_id, user.id, name=body.name,
        dimensions=body.dimensions, tier_thresholds=body.tier_thresholds,
    )
    await db.commit()
    return DataResponse(data=PolicyResponse.model_validate(policy))


# ── Trust Audit Log ──────────────────────────────────────────────────


@router.get(
    "/orgs/{org_id}/trust/audit-log",
    response_model=ListResponse[TrustAuditEventResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_audit_events(
    org_id: str,
    action: str | None = None,
    target_type: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    from sqlalchemy import func as sa_func

    base = select(TrustAuditEvent).where(TrustAuditEvent.org_id == org_id)
    count_base = (
        select(sa_func.count())
        .select_from(TrustAuditEvent)
        .where(TrustAuditEvent.org_id == org_id)
    )

    if action:
        base = base.where(TrustAuditEvent.action == action)
        count_base = count_base.where(TrustAuditEvent.action == action)
    if target_type:
        base = base.where(TrustAuditEvent.target_type == target_type)
        count_base = count_base.where(TrustAuditEvent.target_type == target_type)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(TrustAuditEvent.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    events = list(result.scalars().all())
    return ListResponse(
        data=[TrustAuditEventResponse.model_validate(e) for e in events],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page,
            has_more=(page * per_page) < total,
        ),
    )
