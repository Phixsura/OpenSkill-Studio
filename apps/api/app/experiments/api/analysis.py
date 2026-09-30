"""Analysis endpoint (ADR-017 §10, §12)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.experiments.api.deps import require_platform_admin
from app.experiments.services.analysis_service import AnalysisService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/experiments", tags=["Experiments — Analysis"])


@router.post("/{experiment_id}/analysis", response_model=DataResponse[dict])
async def run_analysis(
    experiment_id: str,
    segment: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    """Run the configured analysis. O'Brien-Fleming experiments consume one
    look per call (422 EXPERIMENT_LOOKS_EXHAUSTED past the budget); mSPRT
    experiments peek freely with always-valid p-values. ?segment=org:<id>
    analyzes one breakdown slice — informational, no look consumed, never a
    decision basis (§4.8)."""
    payload = await AnalysisService(db).run(experiment_id, actor=user, segment=segment)
    await db.commit()
    return {"data": payload}


@router.get("/{experiment_id}/segments", response_model=dict)
async def list_segments(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    """Distinct snapshot segments available for breakdown analysis (§4.8)."""
    from sqlalchemy import select

    from app.experiments.models import MetricSnapshot

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
