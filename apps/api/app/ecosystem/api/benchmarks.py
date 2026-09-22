"""Benchmark Lab endpoints (Part F): suites, cases, runs, blind review."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.api.deps import require_platform_admin
from app.ecosystem.schemas import (
    CaseResponse,
    CreateCaseRequest,
    CreateReviewBatchRequest,
    CreateRunRequest,
    CreateSuiteRequest,
    ResultResponse,
    RunResponse,
    SubmitReviewRequest,
    SuiteResponse,
    UpdateSuiteRequest,
)
from app.ecosystem.services.benchmark import BenchmarkService
from app.ecosystem.services.blind_review import BlindReviewService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/ecosystem/benchmark", tags=["Ecosystem — Benchmark Lab"])


@router.post("/suites", response_model=DataResponse[SuiteResponse], status_code=201)
async def create_suite(
    body: CreateSuiteRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    suite = await BenchmarkService(db).create_suite(created_by=user.id, **body.model_dump())
    await db.commit()
    return {"data": suite}


@router.get("/suites", response_model=DataResponse[list[SuiteResponse]])
async def list_suites(
    family: str | None = None,
    status: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {"data": await BenchmarkService(db).list_suites(family=family, status=status, limit=limit)}


@router.post("/suites/import", response_model=DataResponse[SuiteResponse], status_code=201)
async def import_suite(
    document: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    """Import a portable suite export (draft status; key collisions rejected)."""
    suite = await BenchmarkService(db).import_suite(document, created_by=user.id)
    await db.commit()
    return {"data": suite}


@router.get("/suites/{suite_id}/export", response_model=DataResponse[dict])
async def export_suite(
    suite_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Portable suite document (definition + cases + fingerprint; no runs)."""
    return {"data": await BenchmarkService(db).export_suite(suite_id)}


@router.get("/suites/{suite_id}", response_model=DataResponse[SuiteResponse])
async def get_suite(
    suite_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {"data": await BenchmarkService(db).get_suite(suite_id)}


@router.patch("/suites/{suite_id}", response_model=DataResponse[SuiteResponse])
async def update_suite(
    suite_id: str,
    body: UpdateSuiteRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    suite = await BenchmarkService(db).update_suite(suite_id, body.model_dump(exclude_unset=True))
    await db.commit()
    return {"data": suite}


@router.post("/suites/{suite_id}/cases", response_model=DataResponse[CaseResponse], status_code=201)
async def add_case(
    suite_id: str,
    body: CreateCaseRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    case = await BenchmarkService(db).add_case(suite_id, **body.model_dump())
    await db.commit()
    return {"data": case}


@router.get("/suites/{suite_id}/cases", response_model=DataResponse[list[CaseResponse]])
async def list_cases(
    suite_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    await BenchmarkService(db).get_suite(suite_id)
    return {"data": await BenchmarkService(db).list_cases(suite_id)}


@router.post("/suites/{suite_id}/runs", response_model=DataResponse[RunResponse], status_code=201)
async def create_run(
    suite_id: str,
    body: CreateRunRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    svc = BenchmarkService(db)
    run = await svc.create_run(
        suite_id,
        target=body.target,
        budget_usd_cap=body.budget_usd_cap,
        seed_settings=body.seed_settings,
        triggered_by=user.id,
    )
    if body.execute_now:
        run = await svc.execute_run(run.id)
    else:
        from app.controlplane.models.outbox import enqueue

        enqueue(db, "eco.run_benchmark", {"run_id": run.id})
    await db.commit()
    return {"data": run}


@router.get("/leaderboard", response_model=DataResponse[dict])
async def benchmark_leaderboard(
    family: str | None = None,
    suite_id: str | None = None,
    dimension: str = Query("reliability", max_length=60),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """§15 (LMArena/AA): latest completed run per target, rankable by any
    preserved dimension — never a collapsed universal score."""
    return {
        "data": await BenchmarkService(db).leaderboard(
            family=family, suite_id=suite_id, dimension=dimension, limit=limit
        )
    }


@router.get("/score-history", response_model=DataResponse[dict])
async def benchmark_score_history(
    entity_kind: str = Query(...),
    entity_id: str = Query(...),
    dimension: str = Query("reliability", max_length=40),
    suite_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Score-over-time for one entity + advisory linear trend."""
    out = await BenchmarkService(db).score_history(
        entity_kind=entity_kind, entity_id=entity_id,
        dimension=dimension, suite_id=suite_id,
    )
    return {"data": out}


@router.get("/runs", response_model=DataResponse[list[RunResponse]])
async def list_runs(
    suite_id: str | None = None,
    status: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {"data": await BenchmarkService(db).list_runs(suite_id=suite_id, status=status, limit=limit)}


@router.get("/runs/compare", response_model=DataResponse[dict])
async def compare_runs(
    ids: str = Query(..., description="Comma-separated run ids"),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    run_ids = [x.strip() for x in ids.split(",") if x.strip()]
    return {"data": await BenchmarkService(db).compare_runs(run_ids)}


@router.post("/runs/{run_id}/cancel", response_model=DataResponse[RunResponse])
async def cancel_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    """§17: fence-aware cancel — only queued runs; racing an executor claim
    has exactly one winner."""
    run = await BenchmarkService(db).cancel_run(run_id, actor_id=user.id)
    await db.commit()
    return {"data": run}


@router.get("/runs/{run_id}", response_model=DataResponse[RunResponse])
async def get_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {"data": await BenchmarkService(db).get_run(run_id)}


@router.get("/runs/{run_id}/results", response_model=DataResponse[list[ResultResponse]])
async def list_results(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    await BenchmarkService(db).get_run(run_id)
    return {"data": await BenchmarkService(db).list_results(run_id)}


# ── Blind review ────────────────────────────────────────────────────


@router.post("/review-batches", response_model=dict, status_code=201)
async def create_review_batch(
    body: CreateReviewBatchRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    batch = await BlindReviewService(db).create_batch(
        suite_id=body.suite_id,
        run_ids=body.run_ids,
        reviewer_ids=body.reviewer_ids,
        blind=body.blind,
        created_by=user.id,
    )
    await db.commit()
    # alias_map deliberately excluded (blind until reveal)
    return {
        "data": {
            "id": batch.id,
            "suite_id": batch.suite_id,
            "status": batch.status,
            "reviewer_ids": batch.reviewer_ids,
            "blind": batch.blind,
        }
    }


@router.get("/review-batches/{batch_id}/assignments", response_model=DataResponse[list])
async def my_assignments(
    batch_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return {"data": await BlindReviewService(db).assignments_for(batch_id, user.id)}


@router.post("/reviews/{review_id}/submit", response_model=dict)
async def submit_review(
    review_id: str,
    body: SubmitReviewRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    review = await BlindReviewService(db).submit(
        review_id, reviewer_id=user.id, scores=body.scores, comment=body.comment
    )
    await db.commit()
    return {"data": {"id": review.id, "submitted_at": review.submitted_at}}


@router.post("/review-batches/{batch_id}/reveal", response_model=DataResponse[dict])
async def reveal_batch(
    batch_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    revealed = await BlindReviewService(db).reveal(batch_id)
    await db.commit()
    return {"data": revealed}
