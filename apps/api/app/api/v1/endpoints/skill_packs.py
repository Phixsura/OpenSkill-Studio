"""Skill Pack endpoints — CRUD, contents, releases, approval audit trail."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.skill_pack import (
    AddSkillToPackRequest,
    AddTemplateToPackRequest,
    CreateSkillPackRequest,
    PackSkillResponse,
    PackTemplateResponse,
    PublishReleaseRequest,
    RejectPackRequest,
    ReleaseDetailResponse,
    ReleaseResponse,
    SkillPackResponse,
    UpdateSkillPackRequest,
)
from app.services.skill_pack import SkillPackService

router = APIRouter(tags=["Skill Packs"])

INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


# ── Pack CRUD ────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/packs",
    response_model=DataResponse[SkillPackResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_pack(
    org_id: str,
    body: CreateSkillPackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    pack = await svc.create_pack(org_id, user.id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=SkillPackResponse.model_validate(pack))


@router.get(
    "/orgs/{org_id}/packs",
    response_model=ListResponse[SkillPackResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_packs(
    org_id: str,
    status: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    packs, total = await svc.list_packs(org_id, status, page, per_page)
    return ListResponse(
        data=[SkillPackResponse.model_validate(p) for p in packs],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.get(
    "/orgs/{org_id}/packs/{pack_id}",
    response_model=DataResponse[SkillPackResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_pack(
    org_id: str,
    pack_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    pack = await svc.get_pack(pack_id, org_id)
    return DataResponse(data=SkillPackResponse.model_validate(pack))


@router.put(
    "/orgs/{org_id}/packs/{pack_id}",
    response_model=DataResponse[SkillPackResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def update_pack(
    org_id: str,
    pack_id: str,
    body: UpdateSkillPackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    pack = await svc.update_pack(pack_id, org_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=SkillPackResponse.model_validate(pack))


@router.delete(
    "/orgs/{org_id}/packs/{pack_id}", status_code=204, dependencies=[Depends(rate_limit(20, 60))]
)
async def delete_pack(
    org_id: str,
    pack_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    await svc.delete_pack(pack_id, org_id)
    await db.commit()


# ── Pack Skills ──────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/packs/{pack_id}/skills",
    response_model=DataResponse[PackSkillResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def add_skill_to_pack(
    org_id: str,
    pack_id: str,
    body: AddSkillToPackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    await svc.add_skill(pack_id, body.skill_id, org_id, body.sort_order)
    await db.commit()
    return DataResponse(
        data=PackSkillResponse(pack_id=pack_id, skill_id=body.skill_id, sort_order=body.sort_order)
    )


@router.delete(
    "/orgs/{org_id}/packs/{pack_id}/skills/{skill_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def remove_skill_from_pack(
    org_id: str,
    pack_id: str,
    skill_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    await svc.remove_skill(pack_id, skill_id, org_id)
    await db.commit()


@router.get(
    "/orgs/{org_id}/packs/{pack_id}/skills",
    response_model=DataResponse[list[PackSkillResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_pack_skills(
    org_id: str,
    pack_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    await svc.get_pack(pack_id, org_id)  # verify ownership
    items = await svc.list_pack_skills(pack_id)
    return DataResponse(
        data=[
            PackSkillResponse(
                pack_id=entry.pack_id,
                skill_id=entry.skill_id,
                skill_name=name,
                sort_order=entry.sort_order,
            )
            for entry, name in items
        ]
    )


# ── Pack Templates ───────────────────────────────────────


@router.post(
    "/orgs/{org_id}/packs/{pack_id}/templates",
    response_model=DataResponse[PackTemplateResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def add_template_to_pack(
    org_id: str,
    pack_id: str,
    body: AddTemplateToPackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    await svc.add_template(pack_id, body.template_id, org_id, body.sort_order)
    await db.commit()
    return DataResponse(
        data=PackTemplateResponse(
            pack_id=pack_id, template_id=body.template_id, sort_order=body.sort_order
        )
    )


@router.delete(
    "/orgs/{org_id}/packs/{pack_id}/templates/{template_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def remove_template_from_pack(
    org_id: str,
    pack_id: str,
    template_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    await svc.remove_template(pack_id, template_id, org_id)
    await db.commit()


@router.get(
    "/orgs/{org_id}/packs/{pack_id}/templates",
    response_model=DataResponse[list[PackTemplateResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_pack_templates(
    org_id: str,
    pack_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    await svc.get_pack(pack_id, org_id)
    items = await svc.list_pack_templates(pack_id)
    return DataResponse(
        data=[
            PackTemplateResponse(
                pack_id=entry.pack_id,
                template_id=entry.template_id,
                template_name=name,
                sort_order=entry.sort_order,
            )
            for entry, name in items
        ]
    )


# ── Releases ─────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/packs/{pack_id}/releases",
    response_model=DataResponse[ReleaseResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(5, 60))],
)
async def publish_release(
    org_id: str,
    pack_id: str,
    body: PublishReleaseRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    release = await svc.publish_release(pack_id, org_id, body.version, body.changelog, user.id)
    await db.commit()
    return DataResponse(data=ReleaseResponse.model_validate(release))


@router.get(
    "/orgs/{org_id}/packs/{pack_id}/releases",
    response_model=DataResponse[list[ReleaseResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_releases(
    org_id: str,
    pack_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    await svc.get_pack(pack_id, org_id)
    releases = await svc.list_releases(pack_id)
    return DataResponse(data=[ReleaseResponse.model_validate(r) for r in releases])


@router.get(
    "/orgs/{org_id}/packs/{pack_id}/analytics",
    response_model=DataResponse[dict],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_pack_analytics(
    org_id: str,
    pack_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Publisher analytics: install count, rating, installs by version."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    analytics = await svc.get_pack_analytics(pack_id, org_id)
    return DataResponse(data=analytics)


# ── Approval Workflow ───────────────────────────────────


@router.post(
    "/orgs/{org_id}/packs/{pack_id}/submit-for-review",
    response_model=DataResponse[SkillPackResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def submit_for_review(
    org_id: str,
    pack_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a pack for approval review. Sets review_status to 'pending'."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    pack = await svc.submit_for_review(pack_id, org_id, actor_id=user.id)
    await db.commit()
    return DataResponse(data=SkillPackResponse.model_validate(pack))


@router.post(
    "/orgs/{org_id}/packs/{pack_id}/approve",
    response_model=DataResponse[SkillPackResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def approve_pack(
    org_id: str,
    pack_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve a pack for public visibility (owner/admin only)."""
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    svc = SkillPackService(db)
    pack = await svc.approve_pack(pack_id, org_id, actor_id=user.id)
    await db.commit()
    return DataResponse(data=SkillPackResponse.model_validate(pack))


@router.post(
    "/orgs/{org_id}/packs/{pack_id}/reject",
    response_model=DataResponse[SkillPackResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def reject_pack(
    org_id: str,
    pack_id: str,
    body: RejectPackRequest | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject a pack from public visibility (owner/admin only)."""
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    svc = SkillPackService(db)
    reason = body.reason if body else None
    pack = await svc.reject_pack(pack_id, org_id, reason=reason, actor_id=user.id)
    await db.commit()
    return DataResponse(data=SkillPackResponse.model_validate(pack))


class ApprovalEventResponse(BaseModel):
    id: str
    pack_id: str
    action: str
    actor_id: str
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get(
    "/orgs/{org_id}/packs/{pack_id}/approval-history",
    response_model=DataResponse[list[ApprovalEventResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_approval_history(
    org_id: str,
    pack_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the approval audit trail for a pack."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    events = await svc.list_approval_history(pack_id, org_id)
    return DataResponse(data=[ApprovalEventResponse.model_validate(e) for e in events])


@router.get(
    "/orgs/{org_id}/packs/{pack_id}/releases/{version}",
    response_model=DataResponse[ReleaseDetailResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_release(
    org_id: str,
    pack_id: str,
    version: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = SkillPackService(db)
    await svc.get_pack(pack_id, org_id)
    release = await svc.get_release(pack_id, version)
    return DataResponse(data=ReleaseDetailResponse.model_validate(release))
