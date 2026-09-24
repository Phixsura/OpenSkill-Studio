"""Source registry endpoints (ADR-016 Part A)."""

import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.api.deps import eco_audit, require_platform_admin
from app.ecosystem.schemas import (
    CreateSourceRequest,
    SourceResponse,
    SyncRunResponse,
    SyncSourceRequest,
    UpdateSourceRequest,
)
from app.ecosystem.services.sources import SourceService
from app.ecosystem.services.sync import SyncService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/ecosystem/sources", tags=["Ecosystem — Sources"])


@router.post("", response_model=DataResponse[SourceResponse], status_code=201)
async def create_source(
    body: CreateSourceRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    source = await SourceService(db).create(created_by=user.id, **body.model_dump())
    await eco_audit(
        db, user, action="eco.source_created", target_type="eco_source",
        target_id=source.id,
        after={"name": source.name, "trust_level": source.trust_level},
    )
    await db.commit()
    return {"data": source}


@router.get("", response_model=dict)
async def list_sources(
    status: str | None = None,
    source_type: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    sources, total = await SourceService(db).list_sources(
        status=status, source_type=source_type, limit=limit, offset=offset
    )
    return {
        "data": [SourceResponse.model_validate(s).model_dump() for s in sources],
        "meta": {"total": total, "limit": limit, "offset": offset},
    }


@router.get("/{source_id}", response_model=DataResponse[SourceResponse])
async def get_source(
    source_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {"data": await SourceService(db).get(source_id)}


@router.patch("/{source_id}", response_model=DataResponse[SourceResponse])
async def update_source(
    source_id: str,
    body: UpdateSourceRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    updates = body.model_dump(exclude_unset=True)
    source = await SourceService(db).update(source_id, updates)
    await eco_audit(
        db, _user, action="eco.source_updated", target_type="eco_source",
        target_id=source.id, after={k: str(v)[:200] for k, v in updates.items()},
    )
    await db.commit()
    return {"data": source}


@router.post("/{source_id}/replay", response_model=DataResponse[dict])
async def replay_source(
    source_id: str,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    """Re-run the current parser over retained raw snapshots (append-only:
    changed output supersedes, never rewrites; curated links inherited)."""
    from app.ecosystem.services.sync import SyncService

    out = await SyncService(db).replay_source(source_id, limit=limit)
    await db.commit()
    return {"data": out}


@router.post("/{source_id}/sync", response_model=DataResponse[SyncRunResponse])
async def sync_source(
    source_id: str,
    body: SyncSourceRequest | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    raw_payload = None
    if body and body.payload is not None:
        raw_payload = json.dumps(body.payload).encode()
    run = await SyncService(db).run_sync(source_id, raw_payload=raw_payload)
    await db.commit()
    return {"data": run}


@router.get("/{source_id}/health", response_model=DataResponse[dict])
async def source_health(
    source_id: str,
    window_days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """§13: per-source health summary (success rate, volume, last error)."""
    return {"data": await SourceService(db).health(source_id, window_days=window_days)}


@router.get("/{source_id}/sync-runs", response_model=DataResponse[list[SyncRunResponse]])
async def list_sync_runs(
    source_id: str,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {"data": await SourceService(db).list_sync_runs(source_id, limit=limit)}
