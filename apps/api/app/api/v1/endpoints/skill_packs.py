"""Skill Pack endpoints — CRUD, contents, releases."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
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
)
async def list_packs(
    org_id: str,
    status: str | None = None,
    page: int = Query(default=1, ge=1),
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


@router.delete("/orgs/{org_id}/packs/{pack_id}", status_code=204)
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


@router.delete("/orgs/{org_id}/packs/{pack_id}/skills/{skill_id}", status_code=204)
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
            PackSkillResponse(pack_id=entry.pack_id, skill_id=entry.skill_id, skill_name=name, sort_order=entry.sort_order)
            for entry, name in items
        ]
    )


# ── Pack Templates ───────────────────────────────────────


@router.post(
    "/orgs/{org_id}/packs/{pack_id}/templates",
    response_model=DataResponse[PackTemplateResponse],
    status_code=201,
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


@router.delete("/orgs/{org_id}/packs/{pack_id}/templates/{template_id}", status_code=204)
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
                pack_id=entry.pack_id, template_id=entry.template_id,
                template_name=name, sort_order=entry.sort_order
            )
            for entry, name in items
        ]
    )


# ── Releases ─────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/packs/{pack_id}/releases",
    response_model=DataResponse[ReleaseResponse],
    status_code=201,
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
    release = await svc.publish_release(
        pack_id, org_id, body.version, body.changelog, user.id
    )
    await db.commit()
    return DataResponse(data=ReleaseResponse.model_validate(release))


@router.get(
    "/orgs/{org_id}/packs/{pack_id}/releases",
    response_model=DataResponse[list[ReleaseResponse]],
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
    "/orgs/{org_id}/packs/{pack_id}/releases/{version}",
    response_model=DataResponse[ReleaseDetailResponse],
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
