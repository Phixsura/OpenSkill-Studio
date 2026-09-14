"""Opportunity bookmarking API — save opportunities for later (N13).

Authorization:
  - All operations are user-scoped (own bookmarks only)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.schemas.bookmark import BookmarkRequest, BookmarkResponse
from app.talent.schemas.cursor import CursorListResponse, CursorMeta

router = APIRouter(prefix="/talent", tags=["Talent — Bookmarks"])


@router.post(
    "/opportunities/{opp_id}/bookmark",
    response_model=DataResponse[BookmarkResponse | None],
)
async def toggle_bookmark(
    opp_id: str,
    body: BookmarkRequest | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Toggle bookmark on an opportunity. Creates if not exists, removes if exists."""
    from app.talent.services.bookmarks import BookmarkService

    svc = BookmarkService(db)
    bookmark, created = await svc.toggle_bookmark(
        user.id, opp_id, notes=body.notes if body else None
    )
    await db.commit()

    if created and bookmark:
        await db.refresh(bookmark)
        return DataResponse(data=BookmarkResponse.model_validate(bookmark))
    return DataResponse(data=None)


@router.get("/bookmarks", response_model=CursorListResponse[BookmarkResponse])
async def list_bookmarks(
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List my bookmarked opportunities."""
    from app.talent.services.bookmarks import BookmarkService

    svc = BookmarkService(db)
    items, has_more = await svc.list_bookmarks(user.id, cursor=cursor, limit=limit)
    next_cursor = items[-1].id if has_more and items else None
    return CursorListResponse(
        data=[BookmarkResponse.model_validate(b) for b in items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.get(
    "/opportunities/{opp_id}/bookmarked",
    response_model=DataResponse[dict],
)
async def check_bookmarked(
    opp_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Check if an opportunity is bookmarked by the current user."""
    from app.talent.services.bookmarks import BookmarkService

    svc = BookmarkService(db)
    is_bookmarked = await svc.is_bookmarked(user.id, opp_id)
    return DataResponse(data={"bookmarked": is_bookmarked})


@router.patch(
    "/bookmarks/{bookmark_id}/notes",
    response_model=DataResponse[BookmarkResponse],
)
async def update_bookmark_notes(
    bookmark_id: str,
    body: BookmarkRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update bookmark notes — owner only."""
    from app.talent.services.bookmarks import BookmarkService

    svc = BookmarkService(db)
    bookmark = await svc.update_notes(user.id, bookmark_id, body.notes)
    if not bookmark:
        raise HTTPException(404, "Bookmark not found")

    await db.commit()
    await db.refresh(bookmark)
    return DataResponse(data=BookmarkResponse.model_validate(bookmark))
