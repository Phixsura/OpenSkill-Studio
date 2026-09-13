"""Assessment & credential API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.talent.schemas.assessment import (
    BlueprintResponse,
    CreateBlueprintRequest,
    CreateCredentialRuleRequest,
    CredentialResponse,
    CredentialRuleResponse,
    EvaluateCredentialRequest,
    IssueCredentialRequest,
    ReviewRunRequest,
    RunResponse,
    SubmitRunRequest,
)

router = APIRouter(prefix="/talent", tags=["Talent — Assessments"])

_INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


# ── Blueprints ──

@router.post("/assessments", response_model=DataResponse[BlueprintResponse], status_code=201)
async def create_blueprint(
    body: CreateBlueprintRequest,
    org_id: str = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, *_INSTRUCTOR_ROLES)
    from app.talent.services.assessment import AssessmentService

    svc = AssessmentService(db)
    bp = await svc.create_blueprint(
        org_id=org_id,
        title=body.title,
        description=body.description,
        assessment_type=body.assessment_type,
        capability_requirements=body.capability_requirements,
        config=body.config,
        created_by=user.id,
    )
    await db.commit()
    return DataResponse(data=BlueprintResponse.model_validate(bp))


@router.get("/assessments", response_model=ListResponse[BlueprintResponse])
async def list_blueprints(
    org_id: str = Query(...),
    status: str = "active",
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db)
    from app.talent.services.assessment import AssessmentService

    svc = AssessmentService(db)
    items, total = await svc.list_blueprints(org_id, status=status, limit=per_page, offset=(page - 1) * per_page)
    return ListResponse(
        data=[BlueprintResponse.model_validate(b) for b in items],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=page * per_page < total),
    )


@router.get("/assessments/{blueprint_id}", response_model=DataResponse[BlueprintResponse])
async def get_blueprint(
    blueprint_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.talent.services.assessment import AssessmentService

    svc = AssessmentService(db)
    bp = await svc.get_blueprint(blueprint_id)
    if not bp:
        raise HTTPException(404, "Assessment blueprint not found")
    # Org membership check
    await require_org_member(bp.org_id, user, db)
    return DataResponse(data=BlueprintResponse.model_validate(bp))


# ── Runs ──

@router.post("/assessments/{blueprint_id}/runs", response_model=DataResponse[RunResponse], status_code=201)
async def start_run(
    blueprint_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.talent.services.assessment import AssessmentService

    svc = AssessmentService(db)
    bp = await svc.get_blueprint(blueprint_id)
    if not bp:
        raise HTTPException(404, "Assessment blueprint not found")
    await require_org_member(bp.org_id, user, db)

    try:
        run = await svc.start_run(blueprint_id, user.id, bp.org_id)
    except ValueError as e:
        raise HTTPException(409, str(e)) from e
    await db.commit()
    return DataResponse(data=RunResponse.model_validate(run))


@router.patch("/assessments/{blueprint_id}/runs/{run_id}", response_model=DataResponse[RunResponse])
async def submit_run(
    blueprint_id: str,
    run_id: str,
    body: SubmitRunRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.talent.services.assessment import AssessmentService

    svc = AssessmentService(db)
    try:
        run = await svc.submit_run(run_id, user.id, results=body.results, project_id=body.project_id)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    if not run:
        raise HTTPException(404, "Assessment run not found")
    await db.commit()
    return DataResponse(data=RunResponse.model_validate(run))


@router.post("/assessments/{blueprint_id}/runs/{run_id}/review", response_model=DataResponse[RunResponse])
async def review_run(
    blueprint_id: str,
    run_id: str,
    body: ReviewRunRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.talent.services.assessment import AssessmentService

    svc = AssessmentService(db)
    # Load run to check org
    from app.talent.models.assessment import AssessmentRun

    run = await db.get(AssessmentRun, run_id)
    if not run:
        raise HTTPException(404, "Assessment run not found")
    await require_org_member(run.org_id, user, db, *_INSTRUCTOR_ROLES)

    try:
        result = await svc.review_run(run_id, user.id, results=body.results, status=body.status)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    if not result:
        raise HTTPException(404, "Assessment run not found")
    await db.commit()
    return DataResponse(data=RunResponse.model_validate(result))


# ── Credentials ──

@router.get("/credentials", response_model=DataResponse[list[CredentialResponse]])
async def list_credentials(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.talent.services.assessment import CredentialService

    svc = CredentialService(db)
    creds = await svc.list_user_credentials(user.id, status=status)
    return DataResponse(data=[CredentialResponse.model_validate(c) for c in creds])


@router.get("/credentials/{credential_id}", response_model=DataResponse[CredentialResponse])
async def get_credential(
    credential_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.talent.models.assessment import Credential

    cred = await db.get(Credential, credential_id)
    if not cred:
        raise HTTPException(404, "Credential not found")
    # Users see their own credentials
    if cred.user_id != user.id:
        raise HTTPException(404, "Credential not found")
    return DataResponse(data=CredentialResponse.model_validate(cred))


@router.post("/credential-rules", response_model=DataResponse[CredentialRuleResponse], status_code=201)
async def create_credential_rule(
    body: CreateCredentialRuleRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Platform admin or org admin
    from app.models.user import UserRole

    if user.role != UserRole.ADMIN and body.org_id:
        await require_org_member(body.org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    elif user.role != UserRole.ADMIN:
        raise HTTPException(403, "Only platform admins can create platform-level credential rules")

    from app.talent.services.assessment import CredentialService

    svc = CredentialService(db)
    rule = await svc.create_rule(
        credential_type=body.credential_type,
        display_name=body.display_name,
        description=body.description,
        requirements=body.requirements,
        conditions=body.conditions,
        org_id=body.org_id,
    )
    await db.commit()
    return DataResponse(data=CredentialRuleResponse.model_validate(rule))


@router.post("/credentials/evaluate", response_model=DataResponse[dict])
async def evaluate_credential(
    body: EvaluateCredentialRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.talent.services.assessment import CredentialService

    svc = CredentialService(db)
    target_user_id = body.user_id or user.id
    # Users can only evaluate themselves
    if target_user_id != user.id:
        raise HTTPException(403, "Can only evaluate own credentials")

    result = await svc.evaluate(body.credential_type, target_user_id)
    return DataResponse(data=result)


@router.post("/credentials/issue", response_model=DataResponse[CredentialResponse], status_code=201)
async def issue_credential(
    body: IssueCredentialRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.models.user import UserRole
    from app.talent.services.assessment import CredentialService

    target_user_id = body.user_id or user.id

    # Authorization: issuing to another user requires admin/instructor role + org context
    if target_user_id != user.id:
        if not body.org_id:
            raise HTTPException(403, "Cannot issue credential to another user without org context")
        await require_org_member(body.org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    if body.org_id and user.role != UserRole.ADMIN:
        await require_org_member(body.org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)

    svc = CredentialService(db)
    try:
        cred = await svc.issue_credential(body.credential_type, target_user_id, body.org_id)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    await db.commit()
    return DataResponse(data=CredentialResponse.model_validate(cred))
