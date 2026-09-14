"""Portfolio showcase API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.models.portfolio import (
    PORTFOLIO_ITEM_TYPES,
    PORTFOLIO_VISIBILITY_OPTIONS,
    PortfolioItem,
)
from app.talent.schemas.cursor import CursorListResponse, CursorMeta

router = APIRouter(prefix="/talent", tags=["Talent — Portfolio"])


@router.post("/portfolio", response_model=DataResponse[dict], status_code=201)
async def create_portfolio_item(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item_type = body.get("item_type", "project")
    if item_type not in PORTFOLIO_ITEM_TYPES:
        raise HTTPException(422, f"Invalid item_type. Must be one of {sorted(PORTFOLIO_ITEM_TYPES)}")
    visibility = body.get("visibility", "private")
    if visibility not in PORTFOLIO_VISIBILITY_OPTIONS:
        raise HTTPException(422, f"Invalid visibility. Must be one of {sorted(PORTFOLIO_VISIBILITY_OPTIONS)}")
    item = PortfolioItem(
        user_id=user.id,
        item_type=item_type,
        title=body.get("title", "Untitled"),
        description=body.get("description"),
        url=body.get("url"),
        image_url=body.get("image_url"),
        capability_ids=body.get("capability_ids", []),
        visibility=visibility,
        pinned=body.get("pinned", False),
        sort_order=body.get("sort_order", 0),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return DataResponse(data={"id": item.id, "title": item.title, "item_type": item.item_type, "visibility": item.visibility})


@router.get("/portfolio", response_model=CursorListResponse[dict])
async def list_portfolio(
    visibility: str | None = None,
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = select(PortfolioItem).where(PortfolioItem.user_id == user.id)
    if visibility:
        q = q.where(PortfolioItem.visibility == visibility)
    if cursor:
        q = q.where(PortfolioItem.id < cursor)
    q = q.order_by(PortfolioItem.sort_order, PortfolioItem.created_at.desc()).limit(limit + 1)
    result = await db.execute(q)
    items = list(result.scalars().all())
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    next_cursor = items[-1].id if has_more and items else None
    return CursorListResponse(
        data=[{"id": i.id, "title": i.title, "item_type": i.item_type, "url": i.url, "visibility": i.visibility, "pinned": i.pinned} for i in items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.get("/portfolio/quality", response_model=DataResponse[dict])
async def get_portfolio_quality(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    import dataclasses

    from app.talent.services.portfolio_showcase import PortfolioItem as PIDataclass
    from app.talent.services.portfolio_showcase import PortfolioShowcaseService
    q = select(PortfolioItem).where(PortfolioItem.user_id == user.id)
    result = await db.execute(q)
    db_items = result.scalars().all()
    items = [
        PIDataclass(
            id=i.id, user_id=i.user_id, item_type=i.item_type, title=i.title,
            description=i.description or "", url=i.url, image_url=i.image_url,
            capability_ids=i.capability_ids or [], visibility=i.visibility,
            pinned=i.pinned, sort_order=i.sort_order, created_at=i.created_at,
        )
        for i in db_items
    ]
    svc = PortfolioShowcaseService()
    quality = svc.assess_quality(items)
    return DataResponse(data=dataclasses.asdict(quality))


@router.delete("/portfolio/{item_id}", response_model=DataResponse[dict])
async def delete_portfolio_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = await db.get(PortfolioItem, item_id)
    if not item or item.user_id != user.id:
        raise HTTPException(404, "Portfolio item not found")
    await db.delete(item)
    await db.commit()
    return DataResponse(data={"deleted": True})
