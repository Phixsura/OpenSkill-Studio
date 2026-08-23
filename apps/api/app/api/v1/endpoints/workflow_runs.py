"""Workflow run endpoints (ADR-010 D6).

The executor runs as tracked background tasks dispatched AFTER commit so its
independent sessions can see the run rows.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.workflow_run import (
    CreateRunRequest,
    DecideReviewRequest,
    RunEventResponse,
    StepReviewResponse,
    StepRunResponse,
    WorkflowRunDetailResponse,
    WorkflowRunResponse,
)
from app.services.workflow_runtime import (
    WorkflowRuntimeService,
    dispatch_advance,
    sweep_stale,
)

router = APIRouter(tags=["Workflow Runs"])


@router.post(
    "/orgs/{org_id}/workflow-runs",
    response_model=DataResponse[WorkflowRunResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def create_run(
    org_id: str,
    body: CreateRunRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = WorkflowRuntimeService(db)
    run = await svc.create_run(
        org_id=org_id,
        installation_id=body.installation_id,
        inputs=body.inputs,
        started_by=user.id,
        idempotency_key=body.idempotency_key,
    )
    await db.commit()
    # Dispatch AFTER commit — the executor uses its own session
    dispatch_advance(run.id)
    return DataResponse(data=WorkflowRunResponse.model_validate(run))


@router.get(
    "/orgs/{org_id}/workflow-runs",
    response_model=ListResponse[WorkflowRunResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_runs(
    org_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = WorkflowRuntimeService(db)
    runs, total = await svc.list_runs(org_id, page=page, per_page=per_page)
    return ListResponse(
        data=[WorkflowRunResponse.model_validate(r) for r in runs],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=page * per_page < total
        ),
    )


@router.get(
    "/orgs/{org_id}/workflow-runs/{run_id}",
    response_model=DataResponse[WorkflowRunDetailResponse],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_run(
    org_id: str,
    run_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = WorkflowRuntimeService(db)
    run = await svc.get_run(run_id, org_id)

    # Lazy sweep: recover crashed executors / expire overdue reviews (cheap)
    swept = await sweep_stale(db, org_id)
    if swept["expired_leases"] or swept["expired_reviews"]:
        await db.commit()
        dispatch_advance(run_id)
        run = await svc.get_run(run_id, org_id)

    step_runs = await svc.get_step_runs(run_id)
    events = await svc.get_events(run_id)
    detail = WorkflowRunDetailResponse.model_validate(run)
    detail.step_runs = [StepRunResponse.model_validate(s) for s in step_runs]
    detail.events = [RunEventResponse.model_validate(e) for e in events]
    return DataResponse(data=detail)


@router.post(
    "/orgs/{org_id}/workflow-runs/{run_id}/cancel",
    response_model=DataResponse[WorkflowRunResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def cancel_run(
    org_id: str,
    run_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = WorkflowRuntimeService(db)
    run = await svc.cancel_run(run_id, org_id)
    await db.commit()
    return DataResponse(data=WorkflowRunResponse.model_validate(run))


# ── Step reviews ──────────────────────────────────────────


@router.get(
    "/orgs/{org_id}/step-reviews",
    response_model=DataResponse[list[StepReviewResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_open_reviews(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = WorkflowRuntimeService(db)
    reviews = await svc.get_open_reviews(org_id)
    return DataResponse(data=[StepReviewResponse.model_validate(r) for r in reviews])


@router.post(
    "/orgs/{org_id}/step-reviews/{review_id}/decide",
    response_model=DataResponse[StepReviewResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def decide_review(
    org_id: str,
    review_id: str,
    body: DecideReviewRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Synchronous validate-then-accept decision (Temporal Update semantics)."""
    await require_org_member(org_id, user, db)
    svc = WorkflowRuntimeService(db)
    review = await svc.decide_review(
        review_id, org_id, decision=body.decision, note=body.note, decided_by=user.id
    )
    # Find the run to resume before commit
    from app.models.workflow_run import WorkflowStepRun

    step_run = await db.get(WorkflowStepRun, review.step_run_id)
    run_id = step_run.run_id if step_run else None
    await db.commit()
    if run_id:
        dispatch_advance(run_id)
    return DataResponse(data=StepReviewResponse.model_validate(review))
