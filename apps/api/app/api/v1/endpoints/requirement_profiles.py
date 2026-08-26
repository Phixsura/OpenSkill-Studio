"""Requirement profile endpoints (ADR-012, Issue #21 Part C)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.matching import (
    CreateProfileRequest,
    ExtractRequest,
    ProfileResponse,
    UpdateProfileRequest,
)
from app.services.requirement_profile import RequirementProfileService

router = APIRouter(tags=["Requirement Profiles"])

WRITE_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


@router.post(
    "/orgs/{org_id}/requirement-profiles",
    response_model=DataResponse[ProfileResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def create_profile(
    org_id: str,
    body: CreateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = RequirementProfileService(db)
    profile = await svc.create_from_form(
        org_id=org_id,
        user_id=user.id,
        context_type=body.context_type,
        structured=body.structured_requirements,
        raw_request=body.raw_request,
        created_by=user.id,
    )
    await db.commit()
    return DataResponse(data=ProfileResponse.model_validate(profile))


@router.post(
    "/orgs/{org_id}/requirement-profiles/extract",
    response_model=DataResponse[ProfileResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def extract_profile(
    org_id: str,
    body: ExtractRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """LLM extraction behind the extraction_enabled feature flag.

    Extracted fields carry provenance=extracted and never become hard
    constraints until edited/confirmed by a human (R14).
    """
    await require_org_member(org_id, user, db)
    svc = RequirementProfileService(db)
    profile = await svc.extract_from_text(
        org_id=org_id,
        user_id=user.id,
        raw_request=body.raw_request,
        context_type=body.context_type,
        created_by=user.id,
    )
    await db.commit()
    return DataResponse(data=ProfileResponse.model_validate(profile))


@router.post(
    "/orgs/{org_id}/requirement-profiles/from-brief/{brief_id}",
    response_model=DataResponse[ProfileResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def profile_from_brief(
    org_id: str,
    brief_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *WRITE_ROLES)
    svc = RequirementProfileService(db)
    profile = await svc.create_from_brief(org_id, brief_id, created_by=user.id)
    await db.commit()
    return DataResponse(data=ProfileResponse.model_validate(profile))


@router.get(
    "/orgs/{org_id}/requirement-profiles",
    response_model=ListResponse[ProfileResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_profiles(
    org_id: str,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = RequirementProfileService(db)
    profiles, total = await svc.list_profiles(org_id, page=page, per_page=per_page)
    return ListResponse(
        data=[ProfileResponse.model_validate(p) for p in profiles],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=page * per_page < total
        ),
    )


@router.get(
    "/orgs/{org_id}/requirement-profiles/{profile_id}",
    response_model=DataResponse[ProfileResponse],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_profile(
    org_id: str,
    profile_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = RequirementProfileService(db)
    profile = await svc.get_profile(profile_id, org_id)
    return DataResponse(data=ProfileResponse.model_validate(profile))


@router.patch(
    "/orgs/{org_id}/requirement-profiles/{profile_id}",
    response_model=DataResponse[ProfileResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def update_profile(
    org_id: str,
    profile_id: str,
    body: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = RequirementProfileService(db)
    profile = await svc.update_profile(
        profile_id, org_id, body.edits, user.id, member.role in WRITE_ROLES
    )
    await db.commit()
    return DataResponse(data=ProfileResponse.model_validate(profile))


@router.post(
    "/orgs/{org_id}/requirement-profiles/{profile_id}/confirm",
    response_model=DataResponse[ProfileResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def confirm_profile(
    org_id: str,
    profile_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = RequirementProfileService(db)
    profile = await svc.confirm(profile_id, org_id, user.id, member.role in WRITE_ROLES)
    await db.commit()
    return DataResponse(data=ProfileResponse.model_validate(profile))
