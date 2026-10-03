"""Analysis endpoint (ADR-017 §10, §12)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.experiments.api.deps import (
    ReadScope,
    experiment_read_scope,
)
from app.experiments.services.analysis_service import AnalysisService
from app.schemas.base import DataResponse

router = APIRouter(prefix="/experiments", tags=["Experiments — Analysis"])


@router.post("/{experiment_id}/analysis", response_model=DataResponse[dict])
async def run_analysis(
    experiment_id: str,
    segment: str | None = None,
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    """Run the configured analysis. O'Brien-Fleming experiments consume one
    look per call (422 EXPERIMENT_LOOKS_EXHAUSTED past the budget); mSPRT
    experiments peek freely with always-valid p-values. ?segment=org:<id>
    analyzes one breakdown slice — informational, no look consumed, never a
    decision basis (§4.8)."""
    from app.experiments.services.experiments import ExperimentService

    await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)
    payload = await AnalysisService(db).run(
        experiment_id, actor=scope.user, segment=segment
    )
    await db.commit()
    return {"data": payload}


@router.get("/{experiment_id}/analysis/latest", response_model=DataResponse[dict | None])
async def latest_analysis(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    """The most recent analysis look (scorecard summary) — read-only, from
    the audit trail; null when no analysis has ever run. Same delegated read
    scope and uniform 404 as the analysis itself."""
    from app.experiments.services.experiments import ExperimentService

    await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)
    return {"data": await AnalysisService(db).latest_look(experiment_id)}


@router.get("/{experiment_id}/analysis/history", response_model=dict)
async def analysis_history(
    experiment_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    """Round 137: the full look sequence, newest first (audit-trail reads
    only, same delegated scope as the scorecard)."""
    from app.experiments.services.experiments import ExperimentService

    await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)
    return {"data": await AnalysisService(db).look_history(experiment_id, limit=limit)}


@router.get("/{experiment_id}/segments", response_model=dict)
async def list_segments(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    """Distinct snapshot segments available for breakdown analysis (§4.8)."""
    from sqlalchemy import select

    from app.experiments.models import MetricSnapshot
    from app.experiments.services.experiments import ExperimentService

    await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)

    rows = (
        await db.execute(
            select(MetricSnapshot.segment)
            .where(
                MetricSnapshot.experiment_id == experiment_id,
                MetricSnapshot.segment != "",
            )
            .distinct()
            .order_by(MetricSnapshot.segment)
        )
    ).scalars()
    return {"data": list(rows)}
