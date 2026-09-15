"""Credential pathway API — stackable credentials (N2).

Authorization:
  - Create/list/update pathways: org member
  - Check progress / auto-issue: any authenticated user (own data)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.schemas.credential_pathway import (
    CreatePathwayRequest,
    PathwayProgressResponse,
    PathwayResponse,
    UpdatePathwayRequest,
)
from app.talent.schemas.cursor import CursorListResponse, CursorMeta

router = APIRouter(prefix="/talent", tags=["Talent — Credential Pathways"])


@router.post(
    "/orgs/{org_id}/credential-pathways",
    response_model=DataResponse[PathwayResponse],
    status_code=201,
)
async def create_pathway(
    org_id: str,
    body: CreatePathwayRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a credential pathway — org member only."""
    await require_org_member(org_id, user, db)

    from app.talent.services.credential_pathways import CredentialPathwayService

    svc = CredentialPathwayService(db)
    try:
        pathway = await svc.create_pathway(
            org_id=org_id,
            name=body.name,
            description=body.description,
            pathway_credential_type=body.pathway_credential_type,
            prerequisite_credential_types=body.prerequisite_credential_types,
            prerequisite_count=body.prerequisite_count,
            auto_issue=body.auto_issue,
            created_by=user.id,
        )
    except ValueError as e:
        raise HTTPException(422, str(e)) from None

    await db.commit()
    await db.refresh(pathway)
    return DataResponse(data=PathwayResponse.model_validate(pathway))


@router.get(
    "/orgs/{org_id}/credential-pathways",
    response_model=CursorListResponse[PathwayResponse],
)
async def list_pathways(
    org_id: str,
    status: str = "active",
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List credential pathways — org member only."""
    await require_org_member(org_id, user, db)

    from app.talent.services.credential_pathways import CredentialPathwayService

    svc = CredentialPathwayService(db)
    items, has_more = await svc.list_pathways(org_id, status=status, cursor=cursor, limit=limit)
    next_cursor = items[-1].id if has_more and items else None
    return CursorListResponse(
        data=[PathwayResponse.model_validate(p) for p in items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.get(
    "/credential-pathways/{pathway_id}",
    response_model=DataResponse[PathwayResponse],
)
async def get_pathway(
    pathway_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get pathway details."""
    from app.talent.services.credential_pathways import CredentialPathwayService

    svc = CredentialPathwayService(db)
    pathway = await svc.get_pathway(pathway_id)
    if not pathway:
        raise HTTPException(404, "Pathway not found")
    return DataResponse(data=PathwayResponse.model_validate(pathway))


@router.patch(
    "/credential-pathways/{pathway_id}",
    response_model=DataResponse[PathwayResponse],
)
async def update_pathway(
    pathway_id: str,
    body: UpdatePathwayRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a pathway — org member only."""
    from app.talent.services.credential_pathways import CredentialPathwayService

    svc = CredentialPathwayService(db)
    pathway = await svc.get_pathway(pathway_id)
    if not pathway:
        raise HTTPException(404, "Pathway not found")
    await require_org_member(pathway.org_id, user, db)

    try:
        updated = await svc.update_pathway(
            pathway_id, **body.model_dump(exclude_unset=True)
        )
    except ValueError as e:
        raise HTTPException(422, str(e)) from None

    await db.commit()
    await db.refresh(updated)
    return DataResponse(data=PathwayResponse.model_validate(updated))


@router.get(
    "/credential-pathways/{pathway_id}/progress",
    response_model=DataResponse[PathwayProgressResponse],
)
async def check_progress(
    pathway_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Check my progress toward a credential pathway."""
    from app.talent.services.credential_pathways import CredentialPathwayService

    svc = CredentialPathwayService(db)
    progress = await svc.check_pathway_completion(user.id, pathway_id)
    return DataResponse(data=PathwayProgressResponse(**progress))


@router.get(
    "/credential-pathways/my-progress",
    response_model=DataResponse[list[PathwayProgressResponse]],
)
async def list_my_progress(
    org_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all pathways with my progress."""
    from app.talent.services.credential_pathways import CredentialPathwayService

    svc = CredentialPathwayService(db)
    progress_list = await svc.list_user_pathway_progress(user.id, org_id=org_id)
    return DataResponse(data=[PathwayProgressResponse(**p) for p in progress_list])


@router.post(
    "/credential-pathways/{pathway_id}/check-issue",
    response_model=DataResponse[dict],
)
async def check_and_issue(
    pathway_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Check pathway completion and auto-issue credential if met."""
    from app.talent.services.credential_pathways import CredentialPathwayService

    svc = CredentialPathwayService(db)
    credential = await svc.check_and_auto_issue(user.id, pathway_id)
    if credential:
        await db.commit()
        await db.refresh(credential)
        return DataResponse(data={
            "issued": True,
            "credential_id": credential.id,
            "credential_type": credential.credential_type,
        })
    progress = await svc.check_pathway_completion(user.id, pathway_id)
    return DataResponse(data={"issued": False, **progress})
