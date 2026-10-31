"""Release Gates & Runtime Guardrails API (ADR-017 Phases 3-4).

Org-scoped endpoints for assurance profiles, gate checks, gate evaluation,
guardrail policies, guardrail evaluations, and action boundaries.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.trustplane.schemas.gates import (
    AddCheckRequest,
    BoundaryResponse,
    CheckResponse,
    CreateBoundaryRequest,
    CreateGuardrailRequest,
    CreateProfileRequest,
    EvaluateGateRequest,
    GateResultResponse,
    GuardrailEvalResponse,
    GuardrailResponse,
    GuardrailSummaryResponse,
    OverrideGateRequest,
    ProfileResponse,
)
from app.trustplane.services import gates as gates_svc
from app.trustplane.services import guardrails as guardrails_svc

router = APIRouter(tags=["Trust — Gates & Guardrails"])

ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


# ── Assurance Profiles ───────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/profiles",
    response_model=DataResponse[ProfileResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_profile(
    org_id: str,
    body: CreateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    profile = await gates_svc.create_profile(
        db, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=ProfileResponse.model_validate(profile))


@router.get(
    "/orgs/{org_id}/trust/profiles",
    response_model=ListResponse[ProfileResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_profiles(
    org_id: str,
    trigger: str | None = None,
    status: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    profiles, total = await gates_svc.list_profiles(
        db, org_id, trigger=trigger, status=status, page=page, per_page=per_page,
    )
    return ListResponse(
        data=[ProfileResponse.model_validate(p) for p in profiles],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total),
    )


@router.get(
    "/orgs/{org_id}/trust/profiles/{profile_id}",
    response_model=DataResponse[ProfileResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_profile(
    org_id: str,
    profile_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    profile = await gates_svc.get_profile(db, profile_id, org_id)
    return DataResponse(data=ProfileResponse.model_validate(profile))


@router.post(
    "/orgs/{org_id}/trust/profiles/{profile_id}/activate",
    response_model=DataResponse[ProfileResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def activate_profile(
    org_id: str,
    profile_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    profile = await gates_svc.activate_profile(db, profile_id, org_id, user.id)
    await db.commit()
    return DataResponse(data=ProfileResponse.model_validate(profile))


# ── Gate Checks ──────────────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/profiles/{profile_id}/checks",
    response_model=DataResponse[CheckResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def add_check(
    org_id: str,
    profile_id: str,
    body: AddCheckRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    check = await gates_svc.add_check(
        db, profile_id, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=CheckResponse.model_validate(check))


@router.get(
    "/orgs/{org_id}/trust/profiles/{profile_id}/checks",
    response_model=DataResponse[list[CheckResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_checks(
    org_id: str,
    profile_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    checks = await gates_svc.list_checks(db, profile_id, org_id)
    return DataResponse(data=[CheckResponse.model_validate(c) for c in checks])


# ── Gate Evaluation ──────────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/gates/evaluate",
    response_model=DataResponse[GateResultResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def evaluate_gate(
    org_id: str,
    body: EvaluateGateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    result = await gates_svc.evaluate_gate(
        db, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=GateResultResponse.model_validate(result))


@router.post(
    "/orgs/{org_id}/trust/gates/{result_id}/override",
    response_model=DataResponse[GateResultResponse],
    dependencies=[Depends(rate_limit(5, 60))],
)
async def override_gate(
    org_id: str,
    result_id: str,
    body: OverrideGateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER)
    result = await gates_svc.override_gate(db, result_id, org_id, user.id, body.justification)
    await db.commit()
    return DataResponse(data=GateResultResponse.model_validate(result))


@router.get(
    "/orgs/{org_id}/trust/gates",
    response_model=ListResponse[GateResultResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_gate_results(
    org_id: str,
    target_type: str | None = None,
    target_id: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    results, total = await gates_svc.list_gate_results(
        db, org_id, target_type=target_type, target_id=target_id,
        page=page, per_page=per_page,
    )
    return ListResponse(
        data=[GateResultResponse.model_validate(r) for r in results],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total),
    )


# ── Guardrail Policies ──────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/guardrails",
    response_model=DataResponse[GuardrailResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_guardrail(
    org_id: str,
    body: CreateGuardrailRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    policy = await guardrails_svc.create_guardrail(
        db, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=GuardrailResponse.model_validate(policy))


@router.get(
    "/orgs/{org_id}/trust/guardrails",
    response_model=ListResponse[GuardrailSummaryResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_guardrails(
    org_id: str,
    guardrail_type: str | None = None,
    system_id: str | None = None,
    status: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    policies, total = await guardrails_svc.list_guardrails(
        db, org_id, guardrail_type=guardrail_type, system_id=system_id,
        status=status, page=page, per_page=per_page,
    )
    return ListResponse(
        data=[GuardrailSummaryResponse.model_validate(p) for p in policies],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total),
    )


@router.get(
    "/orgs/{org_id}/trust/guardrails/{guardrail_id}",
    response_model=DataResponse[GuardrailResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_guardrail(
    org_id: str,
    guardrail_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    policy = await guardrails_svc.get_guardrail(db, guardrail_id, org_id)
    return DataResponse(data=GuardrailResponse.model_validate(policy))


@router.post(
    "/orgs/{org_id}/trust/guardrails/{guardrail_id}/activate",
    response_model=DataResponse[GuardrailResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def activate_guardrail(
    org_id: str,
    guardrail_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    policy = await guardrails_svc.activate_guardrail(db, guardrail_id, org_id, user.id)
    await db.commit()
    return DataResponse(data=GuardrailResponse.model_validate(policy))


@router.post(
    "/orgs/{org_id}/trust/guardrails/{guardrail_id}/disable",
    response_model=DataResponse[GuardrailResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def disable_guardrail(
    org_id: str,
    guardrail_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    policy = await guardrails_svc.disable_guardrail(db, guardrail_id, org_id, user.id)
    await db.commit()
    return DataResponse(data=GuardrailResponse.model_validate(policy))


# ── Guardrail Evaluations ───────────────────────────────────────────


@router.get(
    "/orgs/{org_id}/trust/guardrail-evaluations",
    response_model=ListResponse[GuardrailEvalResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_guardrail_evaluations(
    org_id: str,
    policy_id: str | None = None,
    verdict: str | None = None,
    run_id: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    evals, total = await guardrails_svc.list_evaluations(
        db, org_id, policy_id=policy_id, verdict=verdict,
        run_id=run_id, page=page, per_page=per_page,
    )
    return ListResponse(
        data=[GuardrailEvalResponse.model_validate(e) for e in evals],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total),
    )


# ── Action Boundaries ───────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/boundaries",
    response_model=DataResponse[BoundaryResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_boundary(
    org_id: str,
    body: CreateBoundaryRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    boundary = await guardrails_svc.create_boundary(
        db, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=BoundaryResponse.model_validate(boundary))


@router.get(
    "/orgs/{org_id}/trust/boundaries",
    response_model=ListResponse[BoundaryResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_boundaries(
    org_id: str,
    system_id: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    boundaries, total = await guardrails_svc.list_boundaries(
        db, org_id, system_id=system_id, page=page, per_page=per_page,
    )
    return ListResponse(
        data=[BoundaryResponse.model_validate(b) for b in boundaries],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total),
    )
