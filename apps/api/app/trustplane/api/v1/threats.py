"""Threat Modeling & Red-Team API (ADR-017 Part E)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.trustplane.schemas.threats import (
    CreateSuiteRequest,
    CreateThreatModelRequest,
    FindingResponse,
    RunResponse,
    SuiteResponse,
    ThreatModelResponse,
)
from app.trustplane.services import threats as threats_svc

router = APIRouter(tags=["Trust — Threats & Red-Team"])
ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


@router.post("/orgs/{org_id}/trust/threats", response_model=DataResponse[ThreatModelResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_threat_model(org_id: str, body: CreateThreatModelRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    model = await threats_svc.create_threat_model(db, org_id, user.id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=ThreatModelResponse.model_validate(model))


@router.get("/orgs/{org_id}/trust/threats", response_model=ListResponse[ThreatModelResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_threat_models(org_id: str, category: str | None = None, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    models, total = await threats_svc.list_threat_models(db, org_id, category=category, page=page, per_page=per_page)
    return ListResponse(data=[ThreatModelResponse.model_validate(m) for m in models], meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total))


@router.get("/orgs/{org_id}/trust/threats/{threat_id}", response_model=DataResponse[ThreatModelResponse], dependencies=[Depends(rate_limit(30, 60))])
async def get_threat_model(org_id: str, threat_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    model = await threats_svc.get_threat_model(db, threat_id, org_id)
    return DataResponse(data=ThreatModelResponse.model_validate(model))


@router.post("/orgs/{org_id}/trust/redteam/suites", response_model=DataResponse[SuiteResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_suite(org_id: str, body: CreateSuiteRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    suite = await threats_svc.create_suite(db, org_id, user.id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=SuiteResponse.model_validate(suite))


@router.get("/orgs/{org_id}/trust/redteam/suites", response_model=ListResponse[SuiteResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_suites(org_id: str, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    suites, total = await threats_svc.list_suites(db, org_id, page=page, per_page=per_page)
    return ListResponse(data=[SuiteResponse.model_validate(s) for s in suites], meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total))


@router.post("/orgs/{org_id}/trust/redteam/suites/{suite_id}/run", response_model=DataResponse[RunResponse], status_code=201, dependencies=[Depends(rate_limit(5, 60))])
async def start_run(org_id: str, suite_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    run = await threats_svc.start_run(db, org_id, user.id, suite_id)
    await db.commit()
    return DataResponse(data=RunResponse.model_validate(run))


@router.get("/orgs/{org_id}/trust/redteam/runs", response_model=ListResponse[RunResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_runs(org_id: str, suite_id: str | None = None, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    runs, total = await threats_svc.list_runs(db, org_id, suite_id=suite_id, page=page, per_page=per_page)
    return ListResponse(data=[RunResponse.model_validate(r) for r in runs], meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total))


@router.get("/orgs/{org_id}/trust/redteam/runs/{run_id}/findings", response_model=DataResponse[list[FindingResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_findings(org_id: str, run_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    findings = await threats_svc.list_findings(db, run_id, org_id)
    return DataResponse(data=[FindingResponse.model_validate(f) for f in findings])
