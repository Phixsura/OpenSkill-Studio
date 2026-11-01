"""Governance Templates & Compliance Reporting API (ADR-017 Phase 6)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.trustplane.schemas.governance import (
    CreatePolicyOverrideRequest,
    CreateReportRequest,
    CreateTemplateRequest,
    PolicyOverrideResponse,
    ReportResponse,
    ReportSummaryResponse,
    TemplateResponse,
    TemplateSummaryResponse,
)
from app.trustplane.services import governance as gov_svc

router = APIRouter(tags=["Trust — Governance & Compliance"])

ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


# ── Templates ────────────────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/templates",
    response_model=DataResponse[TemplateResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_template(
    org_id: str,
    body: CreateTemplateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    template = await gov_svc.create_template(
        db, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=TemplateResponse.model_validate(template))


@router.get(
    "/orgs/{org_id}/trust/templates",
    response_model=ListResponse[TemplateSummaryResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_templates(
    org_id: str,
    scope: str | None = None,
    status: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    templates, total = await gov_svc.list_templates(
        db, org_id, scope=scope, status=status, page=page, per_page=per_page,
    )
    return ListResponse(
        data=[TemplateSummaryResponse.model_validate(t) for t in templates],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total),
    )


@router.get(
    "/orgs/{org_id}/trust/templates/{template_id}",
    response_model=DataResponse[TemplateResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_template(
    org_id: str,
    template_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    template = await gov_svc.get_template(db, template_id, org_id)
    return DataResponse(data=TemplateResponse.model_validate(template))


@router.post(
    "/orgs/{org_id}/trust/templates/{template_id}/activate",
    response_model=DataResponse[TemplateResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def activate_template(
    org_id: str,
    template_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    template = await gov_svc.activate_template(db, template_id, org_id, user.id)
    await db.commit()
    return DataResponse(data=TemplateResponse.model_validate(template))


# ── Compliance Reports ───────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/reports",
    response_model=DataResponse[ReportResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(5, 60))],
)
async def create_report(
    org_id: str,
    body: CreateReportRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    report = await gov_svc.create_report(
        db, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=ReportResponse.model_validate(report))


@router.get(
    "/orgs/{org_id}/trust/reports",
    response_model=ListResponse[ReportSummaryResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_reports(
    org_id: str,
    report_type: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    reports, total = await gov_svc.list_reports(
        db, org_id, report_type=report_type, page=page, per_page=per_page,
    )
    return ListResponse(
        data=[ReportSummaryResponse.model_validate(r) for r in reports],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total),
    )


@router.get(
    "/orgs/{org_id}/trust/reports/{report_id}",
    response_model=DataResponse[ReportResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_report(
    org_id: str,
    report_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    report = await gov_svc.get_report(db, report_id, org_id)
    return DataResponse(data=ReportResponse.model_validate(report))


# ── Tenant Policy Overrides ─────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/policies",
    response_model=DataResponse[PolicyOverrideResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_policy_override(
    org_id: str,
    body: CreatePolicyOverrideRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER)
    override = await gov_svc.create_policy_override(
        db, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=PolicyOverrideResponse.model_validate(override))


@router.get(
    "/orgs/{org_id}/trust/policies",
    response_model=ListResponse[PolicyOverrideResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_policy_overrides(
    org_id: str,
    override_type: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    overrides, total = await gov_svc.list_policy_overrides(
        db, org_id, override_type=override_type, page=page, per_page=per_page,
    )
    return ListResponse(
        data=[PolicyOverrideResponse.model_validate(o) for o in overrides],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total),
    )


@router.get(
    "/orgs/{org_id}/trust/policies/{override_id}",
    response_model=DataResponse[PolicyOverrideResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_policy_override(
    org_id: str,
    override_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    override = await gov_svc.get_policy_override(db, override_id, org_id)
    return DataResponse(data=PolicyOverrideResponse.model_validate(override))
