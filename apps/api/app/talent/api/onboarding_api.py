"""Onboarding workflow API."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.models.application import Placement
from app.talent.models.onboarding import OnboardingChecklist, OnboardingTemplate
from app.talent.schemas.cursor import CursorListResponse, CursorMeta

router = APIRouter(prefix="/talent", tags=["Talent — Onboarding"])


async def _check_placement_access(
    placement_id: str, user: User, db: AsyncSession,
) -> Placement:
    """Verify user is placement candidate or employer org member."""
    placement = await db.get(Placement, placement_id)
    if not placement:
        raise HTTPException(404, "Placement not found")
    if placement.user_id != user.id:
        await require_org_member(placement.employer_org_id, user, db)
    return placement

@router.post("/orgs/{org_id}/onboarding-templates", response_model=DataResponse[dict], status_code=201)
async def create_onboarding_template(org_id: str, body: dict, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await require_org_member(org_id, user, db)
    t = OnboardingTemplate(org_id=org_id, name=body.get("name", "Untitled"), description=body.get("description"), tasks=body.get("tasks", []), created_by=user.id)
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return DataResponse(data={"id": t.id, "name": t.name, "tasks_count": len(t.tasks)})

@router.get("/orgs/{org_id}/onboarding-templates", response_model=CursorListResponse[dict])
async def list_onboarding_templates(org_id: str, cursor: str | None = Query(None), limit: int = Query(50, ge=1, le=100), db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await require_org_member(org_id, user, db)
    q = select(OnboardingTemplate).where(OnboardingTemplate.org_id == org_id)
    if cursor:
        q = q.where(OnboardingTemplate.id < cursor)
    q = q.order_by(OnboardingTemplate.created_at.desc()).limit(limit + 1)
    result = await db.execute(q)
    items = list(result.scalars().all())
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    nc = items[-1].id if has_more and items else None
    return CursorListResponse(data=[{"id": t.id, "name": t.name, "status": t.status} for t in items], meta=CursorMeta(next_cursor=nc, has_more=has_more))

@router.post("/placements/{placement_id}/onboarding", response_model=DataResponse[dict], status_code=201)
async def create_onboarding_checklist(placement_id: str, body: dict, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await _check_placement_access(placement_id, user, db)
    cl = OnboardingChecklist(placement_id=placement_id, template_id=body.get("template_id"), tasks=body.get("tasks", []))
    db.add(cl)
    await db.commit()
    await db.refresh(cl)
    return DataResponse(data={"id": cl.id, "placement_id": cl.placement_id, "completion_percentage": cl.completion_percentage})

@router.get("/placements/{placement_id}/onboarding", response_model=DataResponse[dict])
async def get_onboarding_progress(placement_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await _check_placement_access(placement_id, user, db)
    q = select(OnboardingChecklist).where(OnboardingChecklist.placement_id == placement_id)
    result = await db.execute(q)
    cl = result.scalar_one_or_none()
    if not cl:
        raise HTTPException(404, "Onboarding checklist not found")
    return DataResponse(data={"id": cl.id, "tasks": cl.tasks, "completion_percentage": cl.completion_percentage, "current_phase": cl.current_phase})
