"""Global holdout-group endpoints (ADR-017 §4.12 v2). Platform-admin only."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.experiments.api.deps import require_platform_admin
from app.experiments.schemas import CreateHoldoutGroupRequest, HoldoutGroupResponse
from app.experiments.services.holdouts import HoldoutGroupService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/experiments/holdout-groups", tags=["Experiments — Holdout groups"])


@router.post("", response_model=DataResponse[HoldoutGroupResponse], status_code=201)
async def create_holdout_group(
    body: CreateHoldoutGroupRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    group = await HoldoutGroupService(db).create(
        key=body.key,
        title=body.title,
        domain=body.domain,
        holdout_bp=body.holdout_bp,
        scope_org_id=body.scope_org_id,
        ends_at=body.ends_at,
        actor_id=user.id,
    )
    await db.commit()
    return {"data": group}


@router.get("", response_model=dict)
async def list_holdout_groups(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    rows = await HoldoutGroupService(db).list_groups()
    return {"data": [HoldoutGroupResponse.model_validate(x).model_dump() for x in rows]}


@router.post("/{group_id}/release", response_model=DataResponse[HoldoutGroupResponse])
async def release_holdout_group(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    group = await HoldoutGroupService(db).release(group_id)
    await db.commit()
    return {"data": group}


@router.get("/{group_id}/report", response_model=DataResponse[dict])
async def holdout_group_report(
    group_id: str,
    metric_key: str = Query(min_length=3, max_length=64),
    window_days: int = Query(default=28, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    """Cross-experiment holdout measurement (§4.12 v2): held-out vs general
    population on one metric over the window. Read-only."""
    return {"data": await HoldoutGroupService(db).report(
        group_id, metric_key=metric_key, window_days=window_days
    )}
