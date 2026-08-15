from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.project import (
    AssetResponse,
    CreateDeliverableRequest,
    CreateFromTemplateRequest,
    CreateProjectRequest,
    CreateReviewRequest,
    CreateTemplateRequest,
    DeliverableResponse,
    ExtensionResponse,
    FileResponse,
    GrantExtensionRequest,
    ProjectDetailResponse,
    ProjectResponse,
    PromptItemRequest,
    ReviewResponse,
    SubmissionDetailResponse,
    SubmissionItemResponse,
    SubmissionResponse,
    TemplateResponse,
    UpdateDeliverableRequest,
    UpdateProjectRequest,
    UpdateTemplateRequest,
)
from app.services.project import ProjectService

router = APIRouter(tags=["Projects & Submissions"])


INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


async def _verify_project_org(svc: ProjectService, project_id: str, org_id: str):
    """Load project and verify it belongs to the given org."""
    project = await svc.get_project(project_id)
    if project.org_id != org_id:
        raise HTTPException(status_code=404, detail="Project not found in this organization")
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


@router.get("/orgs/{org_id}/projects", response_model=ListResponse[ProjectResponse])
async def list_projects(
    org_id: str,
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    projects, total = await svc.list_projects(org_id, status, page, per_page)
    return ListResponse(
        data=[ProjectResponse.model_validate(p) for p in projects],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.post(
    "/orgs/{org_id}/projects", response_model=DataResponse[ProjectResponse], status_code=201
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
    "/orgs/{org_id}/projects/{project_id}", response_model=DataResponse[ProjectDetailResponse]
)
async def get_project(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    project = await _verify_project_org(svc, project_id, org_id)
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


@router.put("/orgs/{org_id}/projects/{project_id}", response_model=DataResponse[ProjectResponse])
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


@router.delete("/orgs/{org_id}/projects/{project_id}", status_code=204)
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
    "/orgs/{org_id}/projects/{project_id}/publish", response_model=DataResponse[ProjectResponse]
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
    "/orgs/{org_id}/projects/{project_id}/unpublish", response_model=DataResponse[ProjectResponse]
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


@router.put("/orgs/{org_id}/projects/{project_id}/skills", status_code=200)
async def set_project_skills(
    org_id: str,
    project_id: str,
    body: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)
    await svc.set_project_skills(project_id, body.get("skill_ids", []))
    await db.commit()
    return {"message": "Project skills updated"}


@router.post(
    "/orgs/{org_id}/projects/{project_id}/extensions",
    response_model=DataResponse[ExtensionResponse],
    status_code=201,
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
)
async def list_deliverables(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    deliverables = await svc.list_deliverables(project_id)
    return DataResponse(data=[DeliverableResponse.model_validate(d) for d in deliverables])


@router.post(
    "/orgs/{org_id}/projects/{project_id}/deliverables",
    response_model=DataResponse[DeliverableResponse],
    status_code=201,
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
    d = await svc.get_deliverable(deliverable_id)
    if d.project_id != project_id:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    d = await svc.update_deliverable(deliverable_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=DeliverableResponse.model_validate(d))


@router.delete(
    "/orgs/{org_id}/projects/{project_id}/deliverables/{deliverable_id}", status_code=204
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
    d = await svc.get_deliverable(deliverable_id)
    if d.project_id != project_id:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    await svc.delete_deliverable(deliverable_id)
    await db.commit()


# ── Submissions ──────────────────────────────────────────


@router.get(
    "/orgs/{org_id}/projects/{project_id}/submissions",
    response_model=ListResponse[SubmissionResponse],
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
    # Instructor sees all, student sees own
    uid = None if member.role in INSTRUCTOR_ROLES else user.id
    submissions, total = await svc.list_submissions(project_id, uid, page, per_page)
    return ListResponse(
        data=[SubmissionResponse.model_validate(s) for s in submissions],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.post(
    "/orgs/{org_id}/projects/{project_id}/submissions",
    response_model=DataResponse[SubmissionResponse],
    status_code=201,
)
async def create_submission(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)
    sub = await svc.create_submission(org_id, project_id, user.id)
    await db.commit()
    return DataResponse(data=SubmissionResponse.model_validate(sub))


@router.get(
    "/orgs/{org_id}/projects/{project_id}/submissions/{submission_id}",
    response_model=DataResponse[SubmissionDetailResponse],
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

    # Only owner or instructor+ can view
    if sub.user_id != user.id and member.role not in INSTRUCTOR_ROLES:
        raise HTTPException(status_code=403, detail="Access denied")

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

    resp = SubmissionDetailResponse(
        **SubmissionResponse.model_validate(sub).model_dump(),
        items=[SubmissionItemResponse.model_validate(i) for i in items_r.scalars()],
        reviews=[ReviewResponse.model_validate(r) for r in reviews_r.scalars()],
    )
    return DataResponse(data=resp)


@router.put(
    "/orgs/{org_id}/projects/{project_id}/submissions/{submission_id}",
    response_model=DataResponse[SubmissionResponse],
)
async def update_submission(
    org_id: str,
    project_id: str,
    submission_id: str,
    body: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a draft submission (e.g. add text/link items)."""
    await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    sub = await svc.get_submission(submission_id)
    if sub.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your submission")
    if sub.status.value != "draft":
        raise HTTPException(status_code=422, detail="Only drafts can be updated")
    # Allow adding text/link items via body
    from app.models.project import ItemType, SubmissionItem

    for item_data in body.get("items", []):
        item = SubmissionItem(
            submission_id=submission_id,
            deliverable_id=item_data.get("deliverable_id"),
            type=ItemType(item_data.get("type", "text")),
            content=item_data.get("content"),
        )
        db.add(item)
    await db.commit()
    await db.refresh(sub)
    return DataResponse(data=SubmissionResponse.model_validate(sub))


@router.post(
    "/orgs/{org_id}/projects/{project_id}/submissions/{submission_id}/submit",
    response_model=DataResponse[SubmissionResponse],
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
    sub = await svc.submit_draft(submission_id, user.id)
    await db.commit()
    return DataResponse(data=SubmissionResponse.model_validate(sub))


@router.delete("/orgs/{org_id}/projects/{project_id}/submissions/{submission_id}", status_code=204)
async def delete_submission(
    org_id: str,
    project_id: str,
    submission_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    await svc.delete_submission(submission_id, user.id)
    await db.commit()


# ── Files ────────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/submissions/{submission_id}/files",
    response_model=DataResponse[FileResponse],
    status_code=201,
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


@router.get("/orgs/{org_id}/submissions/{submission_id}/files/{file_id}/download")
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
    # Only owner or instructor+ can download
    if sub.user_id != user.id and member.role not in INSTRUCTOR_ROLES:
        raise HTTPException(status_code=403, detail="Access denied")
    url = await svc.get_download_url(file_id)
    return {"download_url": url}


@router.delete("/orgs/{org_id}/submissions/{submission_id}/files/{file_id}", status_code=204)
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


@router.get("/orgs/{org_id}/reviews/pending", response_model=ListResponse[SubmissionResponse])
async def pending_reviews(
    org_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ProjectService(db)
    submissions, total = await svc.get_pending_reviews(org_id, page, per_page)
    return ListResponse(
        data=[SubmissionResponse.model_validate(s) for s in submissions],
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


@router.get("/orgs/{org_id}/project-templates", response_model=DataResponse[list[TemplateResponse]])
async def list_templates(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
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
)
async def get_template(
    org_id: str,
    template_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    template = await svc.get_template(template_id, org_id)
    return DataResponse(data=_template_response(template))


@router.put(
    "/orgs/{org_id}/project-templates/{template_id}",
    response_model=DataResponse[TemplateResponse],
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


@router.delete("/orgs/{org_id}/project-templates/{template_id}", status_code=204)
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
)
async def list_assets(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = ProjectService(db)
    await _verify_project_org(svc, project_id, org_id)
    assets = await svc.list_assets(project_id)
    return DataResponse(data=[AssetResponse.model_validate(a) for a in assets])


@router.post(
    "/orgs/{org_id}/projects/{project_id}/assets",
    response_model=DataResponse[AssetResponse],
    status_code=201,
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


@router.get("/orgs/{org_id}/projects/{project_id}/assets/{asset_id}/download")
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


@router.delete("/orgs/{org_id}/projects/{project_id}/assets/{asset_id}", status_code=204)
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
        "tool": body.tool,
        "model": body.model,
        "parameters": body.parameters,
        "notes": body.notes,
    }
    item = await svc.add_prompt_item(submission_id, body.deliverable_id, prompt_data, user.id)
    await db.commit()
    return DataResponse(data=SubmissionItemResponse.model_validate(item))
