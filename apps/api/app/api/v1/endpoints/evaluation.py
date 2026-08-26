from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.evaluation import (
    EvalSettingsResponse,
    EvalTaskResponse,
    EvalUsageResponse,
    TriggerEvaluationRequest,
    UpdateEvalSettingsRequest,
)
from app.services.evaluation import EvaluationService

router = APIRouter(tags=["AI Evaluation"])

INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


# ── Trigger ──────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/evaluation/trigger",
    response_model=DataResponse[EvalTaskResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def trigger_evaluation(
    org_id: str,
    body: TriggerEvaluationRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = EvaluationService(db)
    task = await svc.trigger_evaluation(org_id, body.submission_id, body.type)
    await db.commit()
    return DataResponse(data=EvalTaskResponse.model_validate(task))


# ── Tasks CRUD ───────────────────────────────────────────


@router.get("/orgs/{org_id}/evaluation/tasks", response_model=ListResponse[EvalTaskResponse], dependencies=[Depends(rate_limit(20, 60))])
async def list_eval_tasks(
    org_id: str,
    status: str | None = None,
    eval_type: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = EvaluationService(db)
    tasks, total = await svc.list_tasks(org_id, status, eval_type, page, per_page)
    return ListResponse(
        data=[EvalTaskResponse.model_validate(t) for t in tasks],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.get(
    "/orgs/{org_id}/evaluation/tasks/{task_id}", response_model=DataResponse[EvalTaskResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def get_eval_task(
    org_id: str,
    task_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = EvaluationService(db)
    task = await svc.get_task(task_id)
    if task.org_id != org_id:
        raise HTTPException(status_code=404, detail="Task not found in this organization")
    return DataResponse(data=EvalTaskResponse.model_validate(task))


@router.post(
    "/orgs/{org_id}/evaluation/tasks/{task_id}/retry", response_model=DataResponse[EvalTaskResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def retry_eval_task(
    org_id: str,
    task_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = EvaluationService(db)
    task = await svc.get_task(task_id)
    if task.org_id != org_id:
        raise HTTPException(status_code=404, detail="Task not found in this organization")
    task = await svc.retry_task(task_id)
    await db.commit()
    return DataResponse(data=EvalTaskResponse.model_validate(task))


@router.post(
    "/orgs/{org_id}/evaluation/tasks/{task_id}/cancel",
    response_model=DataResponse[EvalTaskResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def cancel_eval_task(
    org_id: str,
    task_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = EvaluationService(db)
    task = await svc.get_task(task_id)
    if task.org_id != org_id:
        raise HTTPException(status_code=404, detail="Task not found in this organization")
    task = await svc.cancel_task(task_id)
    await db.commit()
    return DataResponse(data=EvalTaskResponse.model_validate(task))


# ── Usage ────────────────────────────────────────────────


@router.get("/orgs/{org_id}/evaluation/usage", response_model=DataResponse[EvalUsageResponse], dependencies=[Depends(rate_limit(20, 60))])
async def get_eval_usage(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = EvaluationService(db)
    usage = await svc.get_usage(org_id)
    return DataResponse(data=usage)


# ── Settings ─────────────────────────────────────────────


@router.get("/orgs/{org_id}/settings/evaluation", response_model=DataResponse[EvalSettingsResponse], dependencies=[Depends(rate_limit(20, 60))])
async def get_eval_settings(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = EvaluationService(db)
    settings = await svc.get_eval_settings(org_id)
    return DataResponse(data=settings)


@router.put("/orgs/{org_id}/settings/evaluation", response_model=DataResponse[EvalSettingsResponse], dependencies=[Depends(rate_limit(20, 60))])
async def update_eval_settings(
    org_id: str,
    body: UpdateEvalSettingsRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    svc = EvaluationService(db)
    # exclude_unset (NOT exclude_none): an explicit {"monthly_budget_usd": null}
    # must reach the service to CLEAR the budget, while absent fields stay
    # untouched. exclude_none silently dropped explicit nulls, making a budget
    # impossible to remove once set.
    result = await svc.update_eval_settings(org_id, body.model_dump(exclude_unset=True))
    await db.commit()
    return DataResponse(data=result)
