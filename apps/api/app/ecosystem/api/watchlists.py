"""Watchlist endpoints (Part P) — owned by the requesting user."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.schemas import (
    AddWatchItemRequest,
    ChangeEventResponse,
    CreateWatchlistRequest,
    WatchItemResponse,
    WatchlistResponse,
)
from app.ecosystem.services.watchlists import WatchlistService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/ecosystem/watchlists", tags=["Ecosystem — Watchlists"])


@router.post("", response_model=DataResponse[WatchlistResponse], status_code=201)
async def create_watchlist(
    body: CreateWatchlistRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    watchlist = await WatchlistService(db).create(
        owner_id=user.id, name=body.name, org_id=body.org_id
    )
    await db.commit()
    return {"data": watchlist}


@router.get("", response_model=DataResponse[list[WatchlistResponse]])
async def list_watchlists(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return {"data": await WatchlistService(db).list_for_owner(user.id)}


@router.delete("/{watchlist_id}", status_code=204)
async def delete_watchlist(
    watchlist_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await WatchlistService(db).delete(watchlist_id, user.id)
    await db.commit()


@router.post("/{watchlist_id}/items", response_model=DataResponse[WatchItemResponse], status_code=201)
async def add_watch_item(
    watchlist_id: str,
    body: AddWatchItemRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = await WatchlistService(db).add_item(
        watchlist_id,
        user.id,
        target_kind=body.target_kind,
        target_id=body.target_id,
        target_ref=body.target_ref,
    )
    await db.commit()
    return {"data": item}


@router.get("/{watchlist_id}/items", response_model=DataResponse[list[WatchItemResponse]])
async def list_watch_items(
    watchlist_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return {"data": await WatchlistService(db).list_items(watchlist_id, user.id)}


@router.delete("/{watchlist_id}/items/{item_id}", status_code=204)
async def remove_watch_item(
    watchlist_id: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await WatchlistService(db).remove_item(watchlist_id, item_id, user.id)
    await db.commit()


@router.get("/changes/feed", response_model=DataResponse[list[ChangeEventResponse]])
async def watched_changes(
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return {"data": await WatchlistService(db).matching_changes(user.id, limit=limit)}
