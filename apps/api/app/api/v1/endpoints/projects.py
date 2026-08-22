import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.project import (
    AssetResponse,
    CommentResponse,
    CreateCommentRequest,
    CreateDeliverableRequest,
    CreateFromTemplateRequest,
    CreateProjectRequest,
    CreateReviewRequest,
    CreateTemplateRequest,
    CreatorAssignmentResponse,
    DeliverableResponse,
    ExtensionResponse,
    FileResponse,
    GrantExtensionRequest,
    PendingReviewResponse,
    ProjectDetailResponse,
    ProjectResponse,
    PromptItemRequest,
    ReviewResponse,
    SubmissionDetailResponse,
    SubmissionItemResponse,
    SubmissionResponse,
    SubmissionWithAuthorResponse,
    TemplateResponse,
    UpdateDeliverableRequest,
    UpdateProjectRequest,
    UpdateTemplateRequest,
)
from app.services.project import ProjectService

router = APIRouter(tags=["Projects & Submissions"])
log = structlog.get_logger()


INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


class SetProjectSkillsRequest(BaseModel):
    skill_ids: list[str] = []


class SubmissionItemInput(BaseModel):
    type: str = "text"
    deliverable_id: str
    content: str | None = None


class UpdateSubmissionRequest(BaseModel):
    items: list[SubmissionItemInput] = []


class SetCommentCompletedRequest(BaseModel):
    completed: bool = False


class AssignCreatorRequest(BaseModel):
    user_id: str


async def _verify_project_org(svc: ProjectService, project_id: str, org_id: str):
    """Load project and verify it belongs to the given org."""
    project = await svc.get_project(project_id)
    if project.org_id != org_id:
        raise HTTPException(status_code=404, detail="Project not found in this organization")
    return project


async def _verify_project_visible(svc: ProjectService, project_id: str, org_id: str, member):
    """Like _verify_project_org, but a draft project is invisible (404) to
    non-instructors — its content must not leak before publication."""
    from app.models.skill import ContentStatus

    project = await _verify_project_org(svc, project_id, org_id)
    if member.role not in INSTRUCTOR_ROLES and project.status != ContentStatus.PUBLISHED:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def _verify_submission_org(svc: ProjectService, submission_id: str, org_id: str):
    """Load submission and verify it belongs to the given org."""
    sub = await svc.get_submission(submission_id)
    if sub.org_id != org_id:
        raise HTTPException(status_code=404, detail="Submission not found in this organization")
    return sub


async def _read_limited(file: UploadFile, limit: int = 50 * 1024 * 1024) -> bytes:
    """Read an upload in chunks, aborting as soon as it exceeds the limit.

    Prevents an oversized body from being fully buffered in memory before
    the size check runs.
    """
    chunks: list[bytes] = []
    total = 0
    while chunk := await file.read(1024 * 1024):
        total += len(chunk)
        if total > limit:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds maximum size of {limit // (1024 * 1024)}MB",
            )
        chunks.append(chunk)
    return b"".join(chunks)


# ── Project CRUD ─────────────────────────────────────────


@router.get("/orgs/{org_id}/projects", response_model=ListResponse[ProjectResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_projects(
    org_id: str,
    status: str | None = None,
    cohort_id: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    # Students only see published projects; instructors see drafts too.
    published_only = member.role not in INSTRUCTOR_ROLES
    projects, total = await svc.list_projects(
        org_id,
        status,
        page,
        per_page,
        published_only=published_only,
        cohort_id=cohort_id,
        user_id=user.id if published_only else None,
    )
    return ListResponse(
        data=[ProjectResponse.model_validate(p) for p in projects],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.post(
    "/orgs/{org_id}/projects", response_model=DataResponse[ProjectResponse], status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_project(
    org_id: str,
    body: CreateProjectRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    project = await svc.create_project(
        org_id,
        body.title,
        body.slug,
        body.description,
        body.instructions,
        body.difficulty,
        body.max_score,
        body.rubric,
        body.deadline,
        body.late_deadline,
        body.late_penalty_pct,
        body.max_submissions,
        body.skill_ids,
        user.id,
        project_type=body.project_type,
    )
    await db.commit()
    return DataResponse(data=ProjectResponse.model_validate(project))


@router.get(
    "/orgs/{org_id}/projects/{project_id}", response_model=DataResponse[ProjectDetailResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_project(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    # A draft project is only visible to instructors — a student with the id
    # must not read its instructions/deadline/rubric before it's published.
    project = await _verify_project_visible(svc, project_id, org_id, member)
    deliverables = await svc.list_deliverables(project_id)
    skill_ids = await svc.get_project_skill_ids(project_id)

    resp = ProjectDetailResponse(
        **ProjectResponse.model_validate(project).model_dump(),
        instructions=project.instructions,
        rubric=project.rubric,
        deliverables=[DeliverableResponse.model_validate(d) for d in deliverables],
        skill_ids=skill_ids,
    )
    return DataResponse(data=resp)


@router.put("/orgs/{org_id}/projects/{project_id}", response_model=DataResponse[ProjectResponse], dependencies=[Depends(rate_limit(10, 60))])
async def update_project(
    org_id: str,
    project_id: str,
    body: UpdateProjectRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)
    project = await svc.update_project(project_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=ProjectResponse.model_validate(project))


@router.delete("/orgs/{org_id}/projects/{project_id}", status_code=204, dependencies=[Depends(rate_limit(10, 60))])
async def delete_project(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)
    await svc.delete_project(project_id)
    await db.commit()


@router.post(
    "/orgs/{org_id}/projects/{project_id}/publish", response_model=DataResponse[ProjectResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def publish_project(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)
    project = await svc.publish_project(project_id)
    await db.commit()
    return DataResponse(data=ProjectResponse.model_validate(project))


@router.post(
    "/orgs/{org_id}/projects/{project_id}/unpublish", response_model=DataResponse[ProjectResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def unpublish_project(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)
    project = await svc.unpublish_project(project_id)
    await db.commit()
    return DataResponse(data=ProjectResponse.model_validate(project))


@router.put("/orgs/{org_id}/projects/{project_id}/skills", status_code=204, dependencies=[Depends(rate_limit(10, 60))])
async def set_project_skills(
    org_id: str,
    project_id: str,
    body: SetProjectSkillsRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)
    await svc.set_project_skills(project_id, body.skill_ids)
    await db.commit()


@router.post(
    "/orgs/{org_id}/projects/{project_id}/extensions",
    response_model=DataResponse[ExtensionResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def grant_extension(
    org_id: str,
    project_id: str,
    body: GrantExtensionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)
    ext = await svc.grant_extension(
        project_id, body.user_id, body.new_deadline, body.reason, user.id
    )
    await db.commit()
    return DataResponse(data=ExtensionResponse.model_validate(ext))


# ── Deliverables ─────────────────────────────────────────


@router.get(
    "/orgs/{org_id}/projects/{project_id}/deliverables",
    response_model=DataResponse[list[DeliverableResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_deliverables(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    await _verify_project_visible(svc, project_id, org_id, member)
    deliverables = await svc.list_deliverables(project_id)
    return DataResponse(data=[DeliverableResponse.model_validate(d) for d in deliverables])


@router.post(
    "/orgs/{org_id}/projects/{project_id}/deliverables",
    response_model=DataResponse[DeliverableResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_deliverable(
    org_id: str,
    project_id: str,
    body: CreateDeliverableRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)
    d = await svc.create_deliverable(
        project_id,
        body.name,
        body.description,
        body.type,
        body.required,
        body.config,
        body.sort_order,
    )
    await db.commit()
    return DataResponse(data=DeliverableResponse.model_validate(d))


@router.put(
    "/orgs/{org_id}/projects/{project_id}/deliverables/{deliverable_id}",
    response_model=DataResponse[DeliverableResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def update_deliverable(
    org_id: str,
    project_id: str,
    deliverable_id: str,
    body: UpdateDeliverableRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)
    d = await svc.get_deliverable(deliverable_id)
    if d.project_id != project_id:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    d = await svc.update_deliverable(deliverable_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=DeliverableResponse.model_validate(d))


@router.delete(
    "/orgs/{org_id}/projects/{project_id}/deliverables/{deliverable_id}", status_code=204,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def delete_deliverable(
    org_id: str,
    project_id: str,
    deliverable_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)
    d = await svc.get_deliverable(deliverable_id)
    if d.project_id != project_id:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    await svc.delete_deliverable(deliverable_id)
    await db.commit()


# ── Submissions ──────────────────────────────────────────


@router.get(
    "/orgs/{org_id}/projects/{project_id}/submissions",
    response_model=ListResponse[SubmissionWithAuthorResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_submissions(
    org_id: str,
    project_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    # Project must belong to this org — otherwise a member of org A could list
    # submissions of org B's project by embedding B's project_id in A's path.
    await _verify_project_org(svc, project_id, org_id)
    # Instructor sees all, student sees own
    uid = None if member.role in INSTRUCTOR_ROLES else user.id
    rows, total = await svc.list_submissions(project_id, uid, page, per_page)
    return ListResponse(
        data=[
            SubmissionWithAuthorResponse(
                **SubmissionResponse.model_validate(sub).model_dump(),
                author_name=author_name,
            )
            for sub, author_name in rows
        ],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.post(
    "/orgs/{org_id}/projects/{project_id}/submissions",
    response_model=DataResponse[SubmissionResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_submission(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    project = await _verify_project_org(svc, project_id, org_id)
    # Students may only submit to a published project; instructors can submit
    # to a draft to test the flow before publishing.
    from app.models.skill import ContentStatus

    if project.status != ContentStatus.PUBLISHED and member.role not in INSTRUCTOR_ROLES:
        raise HTTPException(status_code=422, detail="Project is not open for submissions")
    sub = await svc.create_submission(org_id, project_id, user.id)
    await db.commit()
    return DataResponse(data=SubmissionResponse.model_validate(sub))


@router.get(
    "/orgs/{org_id}/projects/{project_id}/submissions/{submission_id}",
    response_model=DataResponse[SubmissionDetailResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_submission(
    org_id: str,
    project_id: str,
    submission_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    sub = await _verify_submission_org(svc, submission_id, org_id)

    # Owner, instructor+, or an allocated peer reviewer can view
    mask_author = False
    if sub.user_id != user.id and member.role not in INSTRUCTOR_ROLES:
        from sqlalchemy import select as _select

        from app.models.project import PeerAssessment, PeerReviewRound

        pr = await db.execute(
            _select(PeerReviewRound.anonymous)
            .join(PeerAssessment, PeerAssessment.round_id == PeerReviewRound.id)
            .where(
                PeerAssessment.submission_id == submission_id,
                PeerAssessment.reviewer_id == user.id,
            )
        )
        row = pr.first()
        if row is None:
            raise HTTPException(status_code=403, detail="Access denied")
        # Anonymous round: the reviewer must not learn whose work this is.
        mask_author = bool(row[0])

    # Load items and reviews
    from sqlalchemy import select

    from app.models.project import SubmissionItem, SubmissionReview

    items_r = await db.execute(
        select(SubmissionItem).where(SubmissionItem.submission_id == submission_id)
    )
    reviews_r = await db.execute(
        select(SubmissionReview)
        .where(SubmissionReview.submission_id == submission_id)
        .order_by(SubmissionReview.created_at.desc())
    )

    base = SubmissionResponse.model_validate(sub).model_dump()
    if mask_author:
        base["user_id"] = ""
    resp = SubmissionDetailResponse(
        **base,
        items=[SubmissionItemResponse.model_validate(i) for i in items_r.scalars()],
        reviews=[ReviewResponse.model_validate(r) for r in reviews_r.scalars()],
    )
    return DataResponse(data=resp)


@router.put(
    "/orgs/{org_id}/projects/{project_id}/submissions/{submission_id}",
    response_model=DataResponse[SubmissionResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def update_submission(
    org_id: str,
    project_id: str,
    submission_id: str,
    body: UpdateSubmissionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a draft submission (e.g. add text/markdown/link items)."""
    await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    sub = await _verify_submission_org(svc, submission_id, org_id)
    if sub.project_id != project_id:
        raise HTTPException(status_code=404, detail="Submission not found in this project")
    if sub.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your submission")
    # A submission is editable while it's a draft OR after an instructor sent
    # it back for revision — otherwise the revision loop is a dead end.
    if sub.status.value not in ("draft", "revision_requested"):
        raise HTTPException(status_code=422, detail="This submission can no longer be edited")

    from sqlalchemy import select as _select

    from app.models.project import ItemType, SubmissionItem

    # File and prompt items have dedicated endpoints with their own
    # validation (upload / prompt-items) — only inline content types here.
    allowed_types = {ItemType.TEXT, ItemType.MARKDOWN, ItemType.LINK}
    max_content = 100_000  # 100KB of text is beyond any legitimate inline item

    # Validate every deliverable belongs to THIS project before writing rows
    project_deliverables = {d.id for d in await svc.list_deliverables(project_id)}

    for item_data in body.items:
        raw_type = item_data.type
        try:
            item_type = ItemType(raw_type)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=f"Invalid item type: {raw_type}") from exc
        if item_type not in allowed_types:
            raise HTTPException(
                status_code=422,
                detail=f"Item type '{raw_type}' must be created via its dedicated endpoint",
            )
        deliverable_id = item_data.deliverable_id
        if not deliverable_id or deliverable_id not in project_deliverables:
            raise HTTPException(status_code=422, detail="Unknown deliverable for this project")
        content = item_data.content
        if content is not None and len(content) > max_content:
            raise HTTPException(status_code=422, detail="Item content too large or invalid")
        # A link item's content is rendered as a clickable href — restrict to
        # http(s) so a stored javascript:/data: URL can't become an XSS vector.
        if item_type == ItemType.LINK and content:
            import re as _re

            if not _re.match(r"^https?://", content.strip(), _re.IGNORECASE):
                raise HTTPException(
                    status_code=422, detail="Link must start with http:// or https://"
                )
        # Inline items are single-value per deliverable: editing replaces the
        # existing row rather than piling up stale duplicates (which would
        # confuse the required-deliverable check and reviewers).
        existing = await db.execute(
            _select(SubmissionItem).where(
                SubmissionItem.submission_id == submission_id,
                SubmissionItem.deliverable_id == deliverable_id,
                SubmissionItem.type == item_type,
            )
        )
        row = existing.scalars().first()
        if row is not None:
            row.content = content
        else:
            db.add(
                SubmissionItem(
                    submission_id=submission_id,
                    deliverable_id=deliverable_id,
                    type=item_type,
                    content=content,
                )
            )
    await db.commit()
    await db.refresh(sub)
    return DataResponse(data=SubmissionResponse.model_validate(sub))


@router.post(
    "/orgs/{org_id}/projects/{project_id}/submissions/{submission_id}/submit",
    response_model=DataResponse[SubmissionResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def submit_draft(
    org_id: str,
    project_id: str,
    submission_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    sub = await _verify_submission_org(svc, submission_id, org_id)
    if sub.project_id != project_id:
        raise HTTPException(status_code=404, detail="Submission not found in this project")
    sub = await svc.submit_draft(submission_id, user.id)
    await db.commit()

    # Auto-evaluate on submission when the org has enabled it — otherwise the
    # "Auto-evaluate on submission" setting is a no-op. Best-effort: never let
    # an eval failure (budget, LLM error) block the submission itself.
    from app.services.evaluation import EvaluationService

    eval_svc = EvaluationService(db)
    settings_ = await eval_svc.get_eval_settings(org_id)
    if settings_.get("enabled") and settings_.get("auto_evaluate"):
        try:
            await eval_svc.trigger_evaluation(org_id, submission_id, "submission_review")
            await db.commit()
        except Exception:  # noqa: BLE001 — auto-eval is best-effort
            await db.rollback()
            log.warning("auto_evaluation_failed", submission_id=submission_id)

    return DataResponse(data=SubmissionResponse.model_validate(sub))


@router.delete("/orgs/{org_id}/projects/{project_id}/submissions/{submission_id}", status_code=204, dependencies=[Depends(rate_limit(10, 60))])
async def delete_submission(
    org_id: str,
    project_id: str,
    submission_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    sub = await _verify_submission_org(svc, submission_id, org_id)
    if sub.project_id != project_id:
        raise HTTPException(status_code=404, detail="Submission not found in this project")
    await svc.delete_submission(submission_id, user.id)
    await db.commit()


# ── Files ────────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/submissions/{submission_id}/files",
    response_model=DataResponse[FileResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def upload_file(
    org_id: str,
    submission_id: str,
    deliverable_id: str = Form(...),
    note: str | None = Form(default=None),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    # Version note is a short annotation, not a document — unbounded Text
    # would be another storage-abuse vector.
    if note is not None and len(note) > 2000:
        raise HTTPException(status_code=422, detail="Note must be 2,000 characters or less")
    svc = ProjectService(db)
    await _verify_submission_org(svc, submission_id, org_id)
    content = await _read_limited(file)
    item = await svc.upload_file(
        submission_id,
        deliverable_id,
        file.filename or "unnamed",
        content,
        file.content_type or "application/octet-stream",
        user.id,
        note=note,
    )
    await db.commit()
    return DataResponse(data=FileResponse.model_validate(item))


@router.get("/orgs/{org_id}/submissions/{submission_id}/files/{file_id}/download", dependencies=[Depends(rate_limit(30, 60))])
async def download_file(
    org_id: str,
    submission_id: str,
    file_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    sub = await _verify_submission_org(svc, submission_id, org_id)
    # Owner, instructor+, or an allocated peer reviewer can download
    if sub.user_id != user.id and member.role not in INSTRUCTOR_ROLES:
        from sqlalchemy import select as _select

        from app.models.project import PeerAssessment

        pr = await db.execute(
            _select(PeerAssessment.id).where(
                PeerAssessment.submission_id == submission_id,
                PeerAssessment.reviewer_id == user.id,
            )
        )
        if pr.scalar_one_or_none() is None:
            raise HTTPException(status_code=403, detail="Access denied")
    url = await svc.get_download_url(file_id, submission_id=submission_id)
    return {"download_url": url}


@router.delete("/orgs/{org_id}/submissions/{submission_id}/files/{file_id}", status_code=204, dependencies=[Depends(rate_limit(10, 60))])
async def delete_file(
    org_id: str,
    submission_id: str,
    file_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    await svc.delete_file(file_id, user.id)
    await db.commit()


# ── Reviews ──────────────────────────────────────────────


@router.get(
    "/orgs/{org_id}/submissions/{submission_id}/reviews",
    response_model=DataResponse[list[ReviewResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_reviews(
    org_id: str,
    submission_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    sub = await _verify_submission_org(svc, submission_id, org_id)
    if sub.user_id != user.id and member.role not in INSTRUCTOR_ROLES:
        raise HTTPException(status_code=403, detail="Access denied")
    reviews = await svc.list_reviews(submission_id)
    return DataResponse(data=[ReviewResponse.model_validate(r) for r in reviews])


@router.post(
    "/orgs/{org_id}/submissions/{submission_id}/reviews",
    response_model=DataResponse[ReviewResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_review(
    org_id: str,
    submission_id: str,
    body: CreateReviewRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    await _verify_submission_org(svc, submission_id, org_id)
    review = await svc.create_review(
        submission_id,
        user.id,
        body.status,
        body.score,
        body.score_breakdown,
        body.feedback,
    )
    await db.commit()
    return DataResponse(data=ReviewResponse.model_validate(review))


# ── Review Dashboard ─────────────────────────────────────


@router.get("/orgs/{org_id}/reviews/pending", response_model=ListResponse[PendingReviewResponse], dependencies=[Depends(rate_limit(30, 60))])
async def pending_reviews(
    org_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    rows, total = await svc.get_pending_reviews(org_id, page, per_page)
    return ListResponse(
        data=[
            PendingReviewResponse(
                **SubmissionResponse.model_validate(sub).model_dump(),
                author_name=author_name,
                project_title=project_title,
            )
            for sub, author_name, project_title, _pid in rows
        ],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


# ── Project Templates ────────────────────────────────────


def _template_response(t) -> TemplateResponse:  # noqa: ANN001
    if isinstance(t, dict):
        return TemplateResponse(
            id=t["id"],
            name=t["name"],
            description=t["description"],
            instructions=t["instructions"],
            project_type=t.get("project_type", "general"),
            difficulty=t.get("difficulty", "intermediate"),
            suggested_minutes=t.get("suggested_minutes"),
            max_score=t.get("max_score", 100),
            rubric=t.get("rubric", []),
            deliverables=t.get("deliverables", []),
            skill_names=t.get("skill_names", []),
            builtin=True,
        )
    return TemplateResponse(
        id=t.id,
        name=t.name,
        description=t.description,
        instructions=t.instructions,
        project_type=t.project_type,
        difficulty=t.difficulty.value,
        suggested_minutes=t.suggested_minutes,
        max_score=t.max_score,
        rubric=t.rubric,
        deliverables=t.deliverables,
        skill_names=t.skill_names,
        builtin=False,
        created_at=t.created_at,
    )


@router.get("/orgs/{org_id}/project-templates", response_model=DataResponse[list[TemplateResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_templates(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Templates are an instructor authoring tool (blueprints for creating
    # projects) — students have no reason to browse them, and create/update/
    # delete/instantiate are all instructor-only. Reads were the gap.
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    builtins, org_templates = await svc.list_templates(org_id)
    return DataResponse(
        data=[_template_response(t) for t in builtins]
        + [_template_response(t) for t in org_templates]
    )


@router.post(
    "/orgs/{org_id}/project-templates",
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
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    template = await svc.create_template(
        org_id,
        user.id,
        name=body.name,
        description=body.description,
        instructions=body.instructions,
        project_type=body.project_type,
        difficulty=body.difficulty,
        suggested_minutes=body.suggested_minutes,
        max_score=body.max_score,
        rubric=body.rubric,
        deliverables=body.deliverables,
        skill_names=body.skill_names,
    )
    await db.commit()
    return DataResponse(data=_template_response(template))


@router.get(
    "/orgs/{org_id}/project-templates/{template_id}",
    response_model=DataResponse[TemplateResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_template(
    org_id: str,
    template_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    template = await svc.get_template(template_id, org_id)
    return DataResponse(data=_template_response(template))


@router.put(
    "/orgs/{org_id}/project-templates/{template_id}",
    response_model=DataResponse[TemplateResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def update_template(
    org_id: str,
    template_id: str,
    body: UpdateTemplateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    template = await svc.update_template(template_id, org_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=_template_response(template))


@router.delete("/orgs/{org_id}/project-templates/{template_id}", status_code=204, dependencies=[Depends(rate_limit(10, 60))])
async def delete_template(
    org_id: str,
    template_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    await svc.delete_template(template_id, org_id)
    await db.commit()


@router.post(
    "/orgs/{org_id}/projects/from-template",
    response_model=DataResponse[ProjectResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_from_template(
    org_id: str,
    body: CreateFromTemplateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    project = await svc.create_project_from_template(org_id, body.template_id, user.id, body.title)
    await db.commit()
    return DataResponse(data=ProjectResponse.model_validate(project))


# ── Project Assets (reference material) ──────────────────


@router.get(
    "/orgs/{org_id}/projects/{project_id}/assets",
    response_model=DataResponse[list[AssetResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_assets(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    await _verify_project_visible(svc, project_id, org_id, member)
    assets = await svc.list_assets(project_id)
    return DataResponse(data=[AssetResponse.model_validate(a) for a in assets])


@router.post(
    "/orgs/{org_id}/projects/{project_id}/assets",
    response_model=DataResponse[AssetResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def upload_asset(
    org_id: str,
    project_id: str,
    name: str = Form(...),
    description: str | None = Form(default=None),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    # name/description arrive as form fields (no Pydantic schema) — bound them.
    name = name.strip()
    if len(name) < 1 or len(name) > 200:
        raise HTTPException(status_code=422, detail="Asset name must be 1-200 characters")
    if description is not None and len(description) > 2000:
        raise HTTPException(status_code=422, detail="Asset description must be 2000 chars or less")
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)
    content = await _read_limited(file)
    asset = await svc.upload_asset(
        org_id,
        project_id,
        name,
        description,
        file.filename or "unnamed",
        content,
        file.content_type or "application/octet-stream",
        user.id,
    )
    await db.commit()
    return DataResponse(data=AssetResponse.model_validate(asset))


@router.get("/orgs/{org_id}/projects/{project_id}/assets/{asset_id}/download", dependencies=[Depends(rate_limit(30, 60))])
async def download_asset(
    org_id: str,
    project_id: str,
    asset_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)
    asset = await svc.get_asset(asset_id, org_id)
    if asset.project_id != project_id:
        raise HTTPException(status_code=404, detail="Asset not found")
    url = await svc.get_asset_download_url(asset_id, org_id)
    return {"download_url": url}


@router.delete("/orgs/{org_id}/projects/{project_id}/assets/{asset_id}", status_code=204, dependencies=[Depends(rate_limit(10, 60))])
async def delete_asset(
    org_id: str,
    project_id: str,
    asset_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    asset = await svc.get_asset(asset_id, org_id)
    if asset.project_id != project_id:
        raise HTTPException(status_code=404, detail="Asset not found")
    await svc.delete_asset(asset_id, org_id)
    await db.commit()


# ── Prompt Items ─────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/submissions/{submission_id}/prompt-items",
    response_model=DataResponse[SubmissionItemResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def add_prompt_item(
    org_id: str,
    submission_id: str,
    body: PromptItemRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    await _verify_submission_org(svc, submission_id, org_id)
    prompt_data = {
        "prompt": body.prompt,
        "negative_prompt": body.negative_prompt,
        "tool": body.tool,
        "model": body.model,
        "seed": body.seed,
        "cfg_scale": body.cfg_scale,
        "steps": body.steps,
        "sampler": body.sampler,
        "resources": body.resources,
        "parameters": body.parameters,
        "notes": body.notes,
    }
    # Drop nulls to keep stored JSON compact
    prompt_data = {k: v for k, v in prompt_data.items() if v is not None}
    item = await svc.add_prompt_item(submission_id, body.deliverable_id, prompt_data, user.id)
    await db.commit()
    return DataResponse(data=SubmissionItemResponse.model_validate(item))


# ── Anchored Comments ────────────────────────────────────


@router.get(
    "/orgs/{org_id}/submissions/{submission_id}/comments",
    response_model=DataResponse[list[CommentResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_comments(
    org_id: str,
    submission_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    sub = await _verify_submission_org(svc, submission_id, org_id)
    # Same visibility as the submission itself: owner or instructor+
    if sub.user_id != user.id and member.role not in INSTRUCTOR_ROLES:
        raise HTTPException(status_code=403, detail="Access denied")
    comments = await svc.list_comments(submission_id)
    return DataResponse(
        data=[
            CommentResponse(
                **CommentResponse.model_validate(cm).model_dump() | {"author_name": name}
            )
            for cm, name in comments
        ]
    )


@router.post(
    "/orgs/{org_id}/submissions/{submission_id}/comments",
    response_model=DataResponse[CommentResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_comment(
    org_id: str,
    submission_id: str,
    body: CreateCommentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    sub = await _verify_submission_org(svc, submission_id, org_id)
    # Owner and instructors can comment (feedback is a two-way conversation)
    if sub.user_id != user.id and member.role not in INSTRUCTOR_ROLES:
        raise HTTPException(status_code=403, detail="Access denied")
    comment = await svc.add_comment(
        org_id,
        submission_id,
        body.item_id,
        user.id,
        text=body.text,
        anchor_type=body.anchor_type,
        timestamp_ms=body.timestamp_ms,
        duration_ms=body.duration_ms,
        region=body.region,
        parent_id=body.parent_id,
    )
    await db.commit()
    return DataResponse(data=CommentResponse.model_validate(comment))


@router.put(
    "/orgs/{org_id}/comments/{comment_id}/completed",
    response_model=DataResponse[CommentResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def set_comment_completed(
    org_id: str,
    comment_id: str,
    body: SetCommentCompletedRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    comment = await svc.get_comment(comment_id, org_id)
    sub = await svc.get_submission(comment.submission_id)
    if sub.user_id != user.id and member.role not in INSTRUCTOR_ROLES:
        raise HTTPException(status_code=403, detail="Access denied")
    comment = await svc.set_comment_completed(comment_id, org_id, body.completed)
    await db.commit()
    return DataResponse(data=CommentResponse.model_validate(comment))


@router.delete("/orgs/{org_id}/comments/{comment_id}", status_code=204, dependencies=[Depends(rate_limit(10, 60))])
async def delete_comment(
    org_id: str,
    comment_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    await svc.delete_comment(comment_id, org_id, user.id)
    await db.commit()


# ── Creator Assignment (individual) ──────────────────────


@router.post(
    "/orgs/{org_id}/projects/{project_id}/creators",
    response_model=DataResponse[CreatorAssignmentResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def assign_creator(
    org_id: str,
    project_id: str,
    body: AssignCreatorRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Assign a commercial project to an individual creator."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)

    # Verify user is an org member
    from sqlalchemy import select as _sel

    from app.models.organization import MemberStatus, OrgMember

    mem_r = await db.execute(
        _sel(OrgMember.id).where(
            OrgMember.org_id == org_id,
            OrgMember.user_id == body.user_id,
            OrgMember.status == MemberStatus.ACTIVE,
        )
    )
    if mem_r.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="User is not a member of this organization")

    from sqlalchemy.exc import IntegrityError

    from app.models.project import ProjectCreatorAssignment

    assignment = ProjectCreatorAssignment(
        project_id=project_id,
        user_id=body.user_id,
        assigned_by=user.id,
    )
    db.add(assignment)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Creator already assigned") from None
    await db.commit()
    return DataResponse(
        data=CreatorAssignmentResponse(
            id=assignment.id,
            project_id=project_id,
            user_id=body.user_id,
            assigned_at=assignment.assigned_at,
        )
    )


@router.delete(
    "/orgs/{org_id}/projects/{project_id}/creators/{user_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def unassign_creator(
    org_id: str,
    project_id: str,
    user_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove an individual creator assignment."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)

    from sqlalchemy import select

    from app.models.project import ProjectCreatorAssignment

    result = await db.execute(
        select(ProjectCreatorAssignment).where(
            ProjectCreatorAssignment.project_id == project_id,
            ProjectCreatorAssignment.user_id == user_id,
        )
    )
    assignment = result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(status_code=404, detail="Creator assignment not found")
    await db.delete(assignment)
    await db.commit()


@router.get(
    "/orgs/{org_id}/projects/{project_id}/creators",
    response_model=DataResponse[list[CreatorAssignmentResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_creators(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List individual creators assigned to a project."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)

    from sqlalchemy import select

    from app.models.project import ProjectCreatorAssignment

    result = await db.execute(
        select(ProjectCreatorAssignment, User.display_name)
        .join(User, User.id == ProjectCreatorAssignment.user_id, isouter=True)
        .where(ProjectCreatorAssignment.project_id == project_id)
        .order_by(ProjectCreatorAssignment.assigned_at)
    )
    return DataResponse(
        data=[
            CreatorAssignmentResponse(
                id=a.id,
                project_id=project_id,
                user_id=a.user_id,
                user_name=name,
                assigned_at=a.assigned_at,
            )
            for a, name in result.all()
        ]
    )
