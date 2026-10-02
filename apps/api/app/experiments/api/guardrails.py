"""Guardrail endpoints (ADR-017 §12, Part D)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.experiments.api.deps import (
    ReadScope,
    experiment_read_scope,
    require_platform_admin,
)
from app.experiments.schemas import GuardrailEventResponse, IncidentRequest
from app.experiments.services.experiments import ExperimentService
from app.experiments.services.guardrails import GuardrailService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/experiments", tags=["Experiments — Guardrails"])


_EVENT_EXPORT_COLUMNS = (
    "guardrail_key", "metric_key", "observed", "threshold", "action",
    "auto", "created_at",
)


@router.get("/{experiment_id}/guardrails/events/export")
async def export_guardrail_events(
    experiment_id: str,
    limit: int = Query(1000, ge=1, le=5000),
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    """CSV export of the guardrail/incident history (round 96 — the metrics
    export's sibling): same delegated read scope and uniform 404; key
    columns are system-set identifiers (no formula-injection surface) and
    the free-form detail JSON stays out of the flat file."""
    import csv
    import io

    from fastapi.responses import Response

    await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)
    rows = await GuardrailService(db).list_events(experiment_id, limit=limit)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(_EVENT_EXPORT_COLUMNS)
    for row in rows:
        writer.writerow(
            [
                value.isoformat() if hasattr(value := getattr(row, col), "isoformat")
                else value
                for col in _EVENT_EXPORT_COLUMNS
            ]
        )
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                f'attachment; filename="experiment-{experiment_id}-guardrails.csv"'
            )
        },
    )


@router.get("/{experiment_id}/guardrails/events", response_model=dict)
async def list_guardrail_events(
    experiment_id: str,
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    """Delegation consistency: an operator whose experiment auto-paused must
    be able to see WHY — events follow the read scope (uniform 404 outside);
    the manual incident trigger and the force-evaluate stay platform-admin."""
    await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)
    rows = await GuardrailService(db).list_events(experiment_id, limit=limit)
    return {"data": [GuardrailEventResponse.model_validate(x).model_dump() for x in rows]}


@router.post(
    "/{experiment_id}/guardrails/incident",
    response_model=DataResponse[GuardrailEventResponse],
    status_code=201,
)
async def record_incident(
    experiment_id: str,
    body: IncidentRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    """Manual security/privacy incident — immediate pause, never auto-resumed."""
    event = await GuardrailService(db).record_incident(
        experiment_id, actor=user, reason=body.reason
    )
    await db.commit()
    return {"data": event}


@router.post(
    "/{experiment_id}/guardrails/evaluate", response_model=DataResponse[dict]
)
async def evaluate_guardrails_now(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    """Operator-driven immediate evaluation (the sweep runs the same code)."""
    summary = await GuardrailService(db).evaluate_experiment(experiment_id)
    await db.commit()
    return {"data": summary}
