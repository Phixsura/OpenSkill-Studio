"""Career goal API — user-side goal tracking (N3).

All endpoints require auth and are scoped to the authenticated user's own goals.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.schemas.career_goal import (
    CreateGoalRequest,
    GoalProgressResponse,
    GoalResponse,
    UpdateGoalRequest,
)
from app.talent.schemas.cursor import CursorListResponse, CursorMeta

router = APIRouter(prefix="/talent", tags=["Talent — Career Goals"])


@router.post(
    "/career-goals",
    response_model=DataResponse[GoalResponse],
    status_code=201,
)
async def create_goal(
    body: CreateGoalRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a career goal."""
    from app.talent.services.career_goals import CareerGoalService

    svc = CareerGoalService(db)
    try:
        goal = await svc.create_goal(
            user_id=user.id,
            title=body.title,
            description=body.description,
            target_role=body.target_role,
            target_capabilities=body.target_capabilities,
            target_date=body.target_date,
        )
    except ValueError as e:
        raise HTTPException(422, str(e)) from None

    await db.commit()
    await db.refresh(goal)
    return DataResponse(data=GoalResponse.model_validate(goal))


@router.get(
    "/career-goals",
    response_model=CursorListResponse[GoalResponse],
)
async def list_goals(
    status: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List my career goals."""
    from app.talent.services.career_goals import CareerGoalService

    svc = CareerGoalService(db)
    items, has_more = await svc.list_goals(
        user.id, status=status, cursor=cursor, limit=limit
    )
    next_cursor = items[-1].id if has_more and items else None
    return CursorListResponse(
        data=[GoalResponse.model_validate(g) for g in items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.get(
    "/career-goals/{goal_id}",
    response_model=DataResponse[GoalResponse],
)
async def get_goal(
    goal_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a career goal."""
    from app.talent.services.career_goals import CareerGoalService

    svc = CareerGoalService(db)
    goal = await svc.get_goal(goal_id)
    if not goal or goal.user_id != user.id:
        raise HTTPException(404, "Goal not found")
    return DataResponse(data=GoalResponse.model_validate(goal))


@router.patch(
    "/career-goals/{goal_id}",
    response_model=DataResponse[GoalResponse],
)
async def update_goal(
    goal_id: str,
    body: UpdateGoalRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a career goal."""
    from app.talent.services.career_goals import CareerGoalService

    svc = CareerGoalService(db)
    updated = await svc.update_goal(
        goal_id, user.id, **body.model_dump(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(404, "Goal not found")
    await db.commit()
    await db.refresh(updated)
    return DataResponse(data=GoalResponse.model_validate(updated))


@router.post(
    "/career-goals/{goal_id}/complete",
    response_model=DataResponse[GoalResponse],
)
async def complete_goal(
    goal_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Mark a career goal as completed."""
    from app.talent.services.career_goals import CareerGoalService

    svc = CareerGoalService(db)
    try:
        goal = await svc.complete_goal(goal_id, user.id)
    except ValueError as e:
        raise HTTPException(422, str(e)) from None
    if not goal:
        raise HTTPException(404, "Goal not found")
    await db.commit()
    await db.refresh(goal)
    return DataResponse(data=GoalResponse.model_validate(goal))


@router.post(
    "/career-goals/{goal_id}/abandon",
    response_model=DataResponse[GoalResponse],
)
async def abandon_goal(
    goal_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Mark a career goal as abandoned."""
    from app.talent.services.career_goals import CareerGoalService

    svc = CareerGoalService(db)
    try:
        goal = await svc.abandon_goal(goal_id, user.id)
    except ValueError as e:
        raise HTTPException(422, str(e)) from None
    if not goal:
        raise HTTPException(404, "Goal not found")
    await db.commit()
    await db.refresh(goal)
    return DataResponse(data=GoalResponse.model_validate(goal))


@router.get(
    "/career-goals/{goal_id}/progress",
    response_model=DataResponse[GoalProgressResponse],
)
async def check_progress(
    goal_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Check progress toward a career goal."""
    from app.talent.services.career_goals import CareerGoalService

    svc = CareerGoalService(db)
    progress = await svc.check_goal_progress(goal_id, user.id)
    if not progress.get("title"):
        raise HTTPException(404, "Goal not found")
    return DataResponse(data=GoalProgressResponse(**progress))
