"""Saved search API — persistent searches and talent rediscovery.

Authorization:
  - All endpoints require org membership
  - Update/delete: creator only (or org admin in future)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.schemas.cursor import CursorListResponse, CursorMeta
from app.talent.schemas.saved_search import (
    CreateSavedSearchRequest,
    SavedSearchResponse,
    SavedSearchRunResponse,
    UpdateSavedSearchRequest,
)

router = APIRouter(prefix="/talent", tags=["Talent — Saved Searches"])


@router.post(
    "/orgs/{org_id}/saved-searches",
    response_model=DataResponse[SavedSearchResponse],
    status_code=201,
)
async def create_saved_search(
    org_id: str,
    body: CreateSavedSearchRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a saved search — org member only."""
    await require_org_member(org_id, user, db)

    from app.talent.services.saved_searches import SavedSearchService

    svc = SavedSearchService(db)
    try:
        search = await svc.create(
            org_id=org_id,
            name=body.name,
            description=body.description,
            search_type=body.search_type,
            search_criteria=body.search_criteria,
            notify_frequency=body.notify_frequency,
            created_by=user.id,
        )
    except ValueError as e:
        raise HTTPException(422, str(e)) from None

    await db.commit()
    await db.refresh(search)
    return DataResponse(data=SavedSearchResponse.model_validate(search))


@router.get(
    "/orgs/{org_id}/saved-searches",
    response_model=CursorListResponse[SavedSearchResponse],
)
async def list_saved_searches(
    org_id: str,
    search_type: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List saved searches for an org — org member only."""
    await require_org_member(org_id, user, db)

    from app.talent.services.saved_searches import SavedSearchService

    svc = SavedSearchService(db)
    items, has_more = await svc.list_searches(
        org_id, search_type=search_type, cursor=cursor, limit=limit
    )
    next_cursor = items[-1].id if has_more and items else None
    return CursorListResponse(
        data=[SavedSearchResponse.model_validate(s) for s in items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.get(
    "/saved-searches/{search_id}",
    response_model=DataResponse[SavedSearchResponse],
)
async def get_saved_search(
    search_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a saved search by ID."""
    from app.talent.services.saved_searches import SavedSearchService

    svc = SavedSearchService(db)
    search = await svc.get(search_id)
    if not search:
        raise HTTPException(404, "Saved search not found")
    await require_org_member(search.org_id, user, db)
    return DataResponse(data=SavedSearchResponse.model_validate(search))


@router.patch(
    "/saved-searches/{search_id}",
    response_model=DataResponse[SavedSearchResponse],
)
async def update_saved_search(
    search_id: str,
    body: UpdateSavedSearchRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a saved search — creator only."""
    from app.talent.services.saved_searches import SavedSearchService

    svc = SavedSearchService(db)
    search = await svc.get(search_id)
    if not search:
        raise HTTPException(404, "Saved search not found")
    await require_org_member(search.org_id, user, db)
    if search.created_by != user.id:
        raise HTTPException(403, "Only the creator can update this search")

    updated = await svc.update(
        search_id, **body.model_dump(exclude_unset=True)
    )
    await db.commit()
    await db.refresh(updated)
    return DataResponse(data=SavedSearchResponse.model_validate(updated))


@router.delete("/saved-searches/{search_id}", status_code=204)
async def delete_saved_search(
    search_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a saved search — creator only."""
    from app.talent.services.saved_searches import SavedSearchService

    svc = SavedSearchService(db)
    search = await svc.get(search_id)
    if not search:
        raise HTTPException(404, "Saved search not found")
    await require_org_member(search.org_id, user, db)
    if search.created_by != user.id:
        raise HTTPException(403, "Only the creator can delete this search")

    await svc.delete_search(search_id)
    await db.commit()


@router.post(
    "/saved-searches/{search_id}/run",
    response_model=DataResponse[SavedSearchRunResponse],
)
async def run_saved_search(
    search_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Execute a saved search and return fresh results."""
    from datetime import UTC, datetime

    from app.talent.services.saved_searches import SavedSearchService

    svc = SavedSearchService(db)
    search = await svc.get(search_id)
    if not search:
        raise HTTPException(404, "Saved search not found")
    await require_org_member(search.org_id, user, db)

    result = await svc.run_search(search_id)
    await db.commit()

    return DataResponse(
        data=SavedSearchRunResponse(
            search_id=search_id,
            results=result["results"],
            result_count=result["result_count"],
            run_at=datetime.now(UTC),
        )
    )
