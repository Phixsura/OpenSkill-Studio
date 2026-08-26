"""Client brief endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.client_brief import (
    ClientBriefResponse,
    ConvertBriefToProjectRequest,
    CreateClientBriefRequest,
    UpdateClientBriefRequest,
)
from app.schemas.project import ProjectResponse
from app.services.client_brief import ClientBriefService

router = APIRouter(tags=["Client Briefs"])


class ApplyToBriefRequest(BaseModel):
    note: str | None = None


class ReviewApplicationRequest(BaseModel):
    status: str

INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


@router.post(
    "/orgs/{org_id}/briefs", response_model=DataResponse[ClientBriefResponse], status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def create_brief(
    org_id: str,
    body: CreateClientBriefRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ClientBriefService(db)
    brief = await svc.create_brief(org_id, user.id, **body.model_dump())
    await db.commit()
    return DataResponse(data=ClientBriefResponse.model_validate(brief))


@router.get("/orgs/{org_id}/briefs", response_model=ListResponse[ClientBriefResponse], dependencies=[Depends(rate_limit(20, 60))])
async def list_briefs(
    org_id: str,
    status: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ClientBriefService(db)
    briefs, total = await svc.list_briefs(org_id, status, page, per_page)
    return ListResponse(
        data=[ClientBriefResponse.model_validate(b) for b in briefs],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.get(
    "/orgs/{org_id}/briefs/open",
    response_model=DataResponse[list[dict]],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def list_open_briefs(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List briefs that are open for applications (commercial project pool)."""
    await require_org_member(org_id, user, db)

    from sqlalchemy import select as sel

    from app.models.client_brief import BriefStatus, ClientBrief

    result = await db.execute(
        sel(ClientBrief)
        .where(
            ClientBrief.org_id == org_id,
            ClientBrief.status.in_([BriefStatus.OPEN, BriefStatus.ACTIVE]),
        )
        .order_by(ClientBrief.created_at.desc())
    )
    briefs = result.scalars().all()
    return DataResponse(
        data=[
            {
                "id": b.id,
                "title": b.title,
                "client_name": b.client_name,
                "project_type": b.project_type,
                "objective": b.objective,
                "status": b.status.value,
                "created_at": b.created_at.isoformat(),
            }
            for b in briefs
        ]
    )


@router.get("/orgs/{org_id}/briefs/{brief_id}", response_model=DataResponse[ClientBriefResponse], dependencies=[Depends(rate_limit(20, 60))])
async def get_brief(
    org_id: str,
    brief_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Plain members may view OPEN/ACTIVE briefs — the apply flow lives on
    # this page and apply_to_brief already allows any org member. Draft and
    # closed briefs stay instructor-only.
    member = await require_org_member(org_id, user, db)
    svc = ClientBriefService(db)
    brief = await svc.get_brief(brief_id)
    if brief.org_id != org_id:
        raise HTTPException(status_code=404, detail="Brief not found")
    from app.models.client_brief import BriefStatus

    if brief.status not in (BriefStatus.OPEN, BriefStatus.ACTIVE) and member.role not in (
        OrgRole.OWNER,
        OrgRole.ADMIN,
        OrgRole.INSTRUCTOR,
    ):
        raise HTTPException(status_code=404, detail="Brief not found")
    return DataResponse(data=ClientBriefResponse.model_validate(brief))


@router.put("/orgs/{org_id}/briefs/{brief_id}", response_model=DataResponse[ClientBriefResponse], dependencies=[Depends(rate_limit(20, 60))])
async def update_brief(
    org_id: str,
    brief_id: str,
    body: UpdateClientBriefRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ClientBriefService(db)
    brief = await svc.get_brief(brief_id)
    if brief.org_id != org_id:
        raise HTTPException(status_code=404, detail="Brief not found")
    brief = await svc.update_brief(brief_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=ClientBriefResponse.model_validate(brief))


@router.delete("/orgs/{org_id}/briefs/{brief_id}", status_code=204, dependencies=[Depends(rate_limit(20, 60))])
async def delete_brief(
    org_id: str,
    brief_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ClientBriefService(db)
    brief = await svc.get_brief(brief_id)
    if brief.org_id != org_id:
        raise HTTPException(status_code=404, detail="Brief not found")
    await svc.delete_brief(brief_id)
    await db.commit()


@router.post(
    "/orgs/{org_id}/briefs/{brief_id}/convert",
    response_model=DataResponse[ProjectResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def convert_brief_to_project(
    org_id: str,
    brief_id: str,
    body: ConvertBriefToProjectRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ClientBriefService(db)
    project = await svc.convert_to_project(
        brief_id,
        org_id,
        user.id,
        title=body.title,
        cohort_id=body.cohort_id,
        deadline=body.deadline,
        late_deadline=body.late_deadline,
        max_submissions=body.max_submissions,
        rubric=body.rubric,
    )
    await db.commit()
    return DataResponse(data=ProjectResponse.model_validate(project))


# ── Applications ─────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/briefs/{brief_id}/apply",
    response_model=DataResponse[dict],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def apply_to_brief(
    org_id: str,
    brief_id: str,
    body: ApplyToBriefRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Learner applies to work on a commercial project (application mode)."""
    await require_org_member(org_id, user, db)
    from app.models.client_brief import BriefApplication

    svc = ClientBriefService(db)
    brief = await svc.get_brief(brief_id)
    if brief.org_id != org_id:
        raise HTTPException(status_code=404, detail="Brief not found")

    from app.models.client_brief import BriefStatus

    if brief.status not in (BriefStatus.OPEN, BriefStatus.ACTIVE):
        raise HTTPException(
            status_code=422,
            detail="Applications are only accepted for open briefs",
        )

    note = body.note or ""
    if len(note) > 2000:
        raise HTTPException(status_code=422, detail="Note must be 2,000 chars or less")

    from sqlalchemy.exc import IntegrityError

    app_obj = BriefApplication(
        brief_id=brief_id,
        user_id=user.id,
        note=note or None,
    )
    db.add(app_obj)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Already applied") from None
    await db.commit()
    return DataResponse(
        data={
            "id": app_obj.id,
            "brief_id": brief_id,
            "status": app_obj.status.value,
            "applied_at": app_obj.applied_at.isoformat(),
        }
    )


@router.get(
    "/orgs/{org_id}/briefs/{brief_id}/applications",
    response_model=DataResponse[list[dict]],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def list_applications(
    org_id: str,
    brief_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Instructors see ALL applications; plain members see only their own
    (the brief detail page uses this to show the "you have applied" state)."""
    member = await require_org_member(org_id, user, db)
    is_instructor = member.role in INSTRUCTOR_ROLES

    # Verify the brief belongs to this org
    svc = ClientBriefService(db)
    brief = await svc.get_brief(brief_id)
    if brief.org_id != org_id:
        raise HTTPException(status_code=404, detail="Brief not found")

    from sqlalchemy import select

    from app.models.client_brief import BriefApplication
    from app.models.user import User as UserModel

    query = (
        select(BriefApplication, UserModel.display_name)
        .join(UserModel, UserModel.id == BriefApplication.user_id, isouter=True)
        .where(BriefApplication.brief_id == brief_id)
        .order_by(BriefApplication.applied_at)
    )
    if not is_instructor:
        query = query.where(BriefApplication.user_id == user.id)
    result = await db.execute(query)
    return DataResponse(
        data=[
            {
                "id": app.id,
                "user_id": app.user_id,
                "user_name": name,
                "status": app.status.value,
                "note": app.note,
                "applied_at": app.applied_at.isoformat(),
            }
            for app, name in result.all()
        ]
    )


@router.put(
    "/orgs/{org_id}/briefs/{brief_id}/applications/{application_id}",
    response_model=DataResponse[dict],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def review_application(
    org_id: str,
    brief_id: str,
    application_id: str,
    body: ReviewApplicationRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Instructor: accept or reject an application."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)

    # Verify the brief belongs to this org (cross-org IDOR prevention)
    svc = ClientBriefService(db)
    brief = await svc.get_brief(brief_id)
    if brief.org_id != org_id:
        raise HTTPException(status_code=404, detail="Brief not found")

    from datetime import UTC, datetime

    from app.models.client_brief import ApplicationStatus, BriefApplication

    app_obj = await db.get(BriefApplication, application_id)
    if app_obj is None or app_obj.brief_id != brief_id:
        raise HTTPException(status_code=404, detail="Application not found")

    if body.status not in ("accepted", "rejected", "withdrawn"):
        raise HTTPException(status_code=422, detail="Status must be 'accepted', 'rejected', or 'withdrawn'")

    app_obj.status = ApplicationStatus(body.status)
    app_obj.reviewed_at = datetime.now(UTC)
    app_obj.reviewed_by = user.id
    await db.commit()
    return DataResponse(
        data={
            "id": app_obj.id,
            "user_id": app_obj.user_id,
            "status": app_obj.status.value,
            "reviewed_at": app_obj.reviewed_at.isoformat(),
        }
    )


@router.post(
    "/orgs/{org_id}/briefs/{brief_id}/withdraw",
    response_model=DataResponse[dict],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def withdraw_application(
    org_id: str,
    brief_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Learner withdraws their own application."""
    await require_org_member(org_id, user, db)

    from sqlalchemy import select

    from app.models.client_brief import ApplicationStatus, BriefApplication

    result = await db.execute(
        select(BriefApplication).where(
            BriefApplication.brief_id == brief_id,
            BriefApplication.user_id == user.id,
        )
    )
    app_obj = result.scalar_one_or_none()
    if app_obj is None:
        raise HTTPException(status_code=404, detail="No application found")
    if app_obj.status != ApplicationStatus.PENDING:
        raise HTTPException(
            status_code=422,
            detail="Can only withdraw pending applications",
        )

    app_obj.status = ApplicationStatus.WITHDRAWN
    await db.commit()
    return DataResponse(
        data={
            "id": app_obj.id,
            "status": app_obj.status.value,
        }
    )



# list_open_briefs is defined above get_brief to avoid route conflict with /briefs/{brief_id}
