"""Assessment & credential API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse
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
from app.talent.schemas.cursor import CursorListResponse, CursorMeta

router = APIRouter(prefix="/talent", tags=["Talent — Assessments"])

_INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


# ── Blueprints ──


@router.post(
    "/assessments",
    response_model=DataResponse[BlueprintResponse],
    status_code=201,
    summary="Create assessment blueprint",
    description="Create a standardized assessment with criteria, rubric, and passing thresholds.",
)
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
    await db.refresh(bp)
    return DataResponse(data=BlueprintResponse.model_validate(bp))


@router.get(
    "/assessments",
    response_model=CursorListResponse[BlueprintResponse],
    summary="List assessment blueprints",
    description="Returns paginated list of assessment blueprints.",
)
async def list_blueprints(
    org_id: str = Query(...),
    status: str = "active",
    cursor: str | None = Query(None, description="Cursor for pagination (last item ID)"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db)
    from app.talent.services.assessment import AssessmentService

    svc = AssessmentService(db)
    items, total = await svc.list_blueprints(org_id, status=status, limit=limit, cursor=cursor)
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    next_cursor = items[-1].id if has_more and items else None
    return CursorListResponse(
        data=[BlueprintResponse.model_validate(b) for b in items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.get(
    "/assessments/{blueprint_id}",
    response_model=DataResponse[BlueprintResponse],
    summary="Get assessment blueprint",
    description="Returns full details of an assessment blueprint.",
)
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


@router.post(
    "/assessments/{blueprint_id}/runs",
    response_model=DataResponse[RunResponse],
    status_code=201,
    summary="Start assessment run",
    description="Begin a new assessment run against a blueprint.",
)
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
        raise HTTPException(409, "Resource conflict") from e
    await db.commit()
    await db.refresh(run)
    return DataResponse(data=RunResponse.model_validate(run))


@router.patch(
    "/assessments/{blueprint_id}/runs/{run_id}",
    response_model=DataResponse[RunResponse],
    summary="Update assessment run",
    description="Update an in-progress assessment run with answers.",
)
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
        run = await svc.submit_run(
            run_id, user.id, results=body.results, project_id=body.project_id
        )
    except ValueError as e:
        raise HTTPException(422, "Validation error") from e
    if not run:
        raise HTTPException(404, "Assessment run not found")
    await db.commit()
    await db.refresh(run)
    return DataResponse(data=RunResponse.model_validate(run))


@router.post(
    "/assessments/{blueprint_id}/runs/{run_id}/review",
    response_model=DataResponse[RunResponse],
    summary="Review assessment run",
    description="Submit review and scoring for a completed assessment.",
)
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
        raise HTTPException(422, "Validation error") from e
    if not result:
        raise HTTPException(404, "Assessment run not found")
    await db.commit()
    await db.refresh(result)
    return DataResponse(data=RunResponse.model_validate(result))


# ── Credentials ──


@router.get(
    "/credentials",
    response_model=DataResponse[list[CredentialResponse]],
    summary="List credentials",
    description="Returns all credentials earned by the authenticated user.",
)
async def list_credentials(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.talent.services.assessment import CredentialService

    svc = CredentialService(db)
    creds = await svc.list_user_credentials(user.id, status=status)
    return DataResponse(data=[CredentialResponse.model_validate(c) for c in creds])


@router.get(
    "/credentials/{credential_id}",
    response_model=DataResponse[CredentialResponse],
    summary="Get credential detail",
    description="Returns full credential details including issuer and verification.",
)
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


@router.post(
    "/credential-rules",
    response_model=DataResponse[CredentialRuleResponse],
    status_code=201,
    summary="Create credential rule",
    description="Define automatic credential issuance based on assessment results.",
)
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
    await db.refresh(rule)
    return DataResponse(data=CredentialRuleResponse.model_validate(rule))


@router.post(
    "/credentials/evaluate",
    response_model=DataResponse[dict],
    summary="Evaluate credential eligibility",
    description="Check if user meets requirements for a credential.",
)
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
        raise HTTPException(404, "Credential not found")

    result = await svc.evaluate(body.credential_type, target_user_id)
    return DataResponse(data=result)


@router.post(
    "/credentials/issue",
    response_model=DataResponse[CredentialResponse],
    status_code=201,
    summary="Issue credential",
    description="Manually issue a credential with Ed25519 digital signature.",
)
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
            raise HTTPException(404, "Credential not found")
        await require_org_member(
            body.org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR
        )
    if body.org_id and user.role != UserRole.ADMIN:
        await require_org_member(
            body.org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR
        )

    svc = CredentialService(db)
    try:
        cred = await svc.issue_credential(body.credential_type, target_user_id, org_id=body.org_id)
    except ValueError as e:
        raise HTTPException(422, "Validation error") from e
    await db.commit()

    # Webhook: credential.issued
    if body.org_id:
        from app.talent.services.webhook_events import emit_talent_event

        await emit_talent_event(
            db,
            org_id=body.org_id,
            event_type="credential.issued",
            payload={
                "credential_id": cred.id,
                "credential_type": cred.credential_type,
                "user_id": target_user_id,
            },
        )

    await db.refresh(cred)
    return DataResponse(data=CredentialResponse.model_validate(cred))


# ── Open Badges 3.0 export ──


@router.get(
    "/credentials/{credential_id}/badge",
    summary="Export as Open Badge 3.0",
    description="Export credential as Open Badges 3.0 AchievementCredential.",
    response_model=DataResponse[dict],
)
async def export_credential_as_badge(
    credential_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Export a credential as an Open Badges 3.0 OpenBadgeCredential (JSON-LD).

    Only the credential owner can export.
    """
    from fastapi.responses import JSONResponse
    from sqlalchemy import select

    from app.talent.models.assessment import Credential
    from app.talent.models.capability import Capability
    from app.talent.services.credential_signing import SigningKeyService
    from app.talent.services.openbadges import export_credential_as_ob3

    cred = await db.get(Credential, credential_id)
    if not cred or cred.user_id != user.id:
        raise HTTPException(404, "Credential not found")

    if cred.status != "active":
        raise HTTPException(410, "Credential is no longer active")

    org_id = cred.issuer_org_id
    if not org_id:
        raise HTTPException(
            422,
            "Credential has no issuing organization — cannot produce a badge",
        )

    key_svc = SigningKeyService(db)
    signing_key = await key_svc.get_or_create_active_key(org_id)
    await db.commit()
    await db.refresh(signing_key)

    # Load capability details for alignment
    cap_ids = [c.get("capability_id") for c in (cred.capabilities or []) if c.get("capability_id")]
    capability_details = []
    if cap_ids:
        result = await db.execute(select(Capability).where(Capability.id.in_(cap_ids)))
        for cap in result.scalars().all():
            capability_details.append(
                {
                    "id": cap.id,
                    "canonical_name": cap.canonical_name,
                    "description": cap.description,
                    "external_ids": cap.external_ids or {},
                }
            )

    ob3 = export_credential_as_ob3(
        credential_id=cred.id,
        credential_type=cred.credential_type,
        user_id=cred.user_id,
        issued_at=cred.issued_at,
        expires_at=cred.expires_at,
        capabilities=cred.capabilities or [],
        org_id=org_id,
        signing_key_id=signing_key.id,
        private_key_pem=signing_key.private_key_encrypted,
        capability_details=capability_details,
    )

    return JSONResponse(content=ob3, media_type="application/ld+json")


# ---- Public credential verification ----


@router.get(
    "/verify/credential/{credential_id}",
    response_model=DataResponse[dict],
    summary="Verify credential",
    description="Public endpoint to verify credential authenticity. No auth required.",
)
async def verify_credential_public(
    credential_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Public credential verification page data — no auth required."""
    from app.talent.models.assessment import Credential
    from app.talent.services.interview_intelligence import build_credential_verification_data

    cred = await db.get(Credential, credential_id)
    if not cred:
        raise HTTPException(404, "Credential not found")
    cap_data = None
    if cred.capabilities:
        cap_ids = [c.get("capability_id") for c in cred.capabilities if c.get("capability_id")]
        if cap_ids:
            from app.talent.models.capability import Capability

            cap = await db.get(Capability, cap_ids[0])
            if cap:
                cap_data = {"canonical_name": cap.canonical_name}
    data = build_credential_verification_data(
        {
            "credential_type": cred.credential_type,
            "status": cred.status,
            "issued_at": cred.issued_at.isoformat() if cred.issued_at else None,
            "expires_at": cred.expires_at.isoformat() if cred.expires_at else None,
            "org_id": cred.org_id,
        },
        cap_data,
    )
    return DataResponse(data=data)
