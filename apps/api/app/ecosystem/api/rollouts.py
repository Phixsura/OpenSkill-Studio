"""Controlled rollout endpoints (Part M)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.api.deps import eco_audit, require_platform_admin
from app.ecosystem.schemas import CreateRolloutRequest, DecisionRequest, RolloutResponse
from app.ecosystem.services.rollout import RolloutService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/ecosystem/rollouts", tags=["Ecosystem — Rollouts"])


@router.post("", response_model=DataResponse[RolloutResponse], status_code=201)
async def create_rollout(
    body: CreateRolloutRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    plan = await RolloutService(db).create(
        replacement_candidate_id=body.replacement_candidate_id,
        scope_type=body.scope_type,
        scope_ref=body.scope_ref,
        guardrails=body.guardrails,
    )
    await db.commit()
    return {"data": plan}


@router.get("", response_model=DataResponse[list[RolloutResponse]])
async def list_rollouts(
    status: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {"data": await RolloutService(db).list(status=status, limit=limit)}


@router.get("/{plan_id}", response_model=DataResponse[RolloutResponse])
async def get_rollout(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {"data": await RolloutService(db).get(plan_id)}


@router.post("/{plan_id}/start", response_model=DataResponse[RolloutResponse])
async def start_rollout(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    plan = await RolloutService(db).start(plan_id)
    await db.commit()
    return {"data": plan}


@router.post("/{plan_id}/evaluate", response_model=DataResponse[RolloutResponse])
async def evaluate_rollout(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    plan = await RolloutService(db).evaluate(plan_id)
    await db.commit()
    return {"data": plan}


@router.post("/{plan_id}/decide", response_model=DataResponse[RolloutResponse])
async def decide_rollout(
    plan_id: str,
    body: DecisionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    plan = await RolloutService(db).decide(
        plan_id, decision=body.decision, actor_id=user.id, note=body.note
    )
    await eco_audit(
        db, user, action="eco.rollout_decided", target_type="eco_rollout_plan",
        target_id=plan_id, after={"decision": body.decision, "status": plan.status},
        reason=body.note,
    )
    await db.commit()
    return {"data": plan}
