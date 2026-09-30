"""Guardrail endpoints (ADR-017 §12, Part D)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.experiments.api.deps import require_platform_admin
from app.experiments.schemas import GuardrailEventResponse, IncidentRequest
from app.experiments.services.experiments import ExperimentService
from app.experiments.services.guardrails import GuardrailService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/experiments", tags=["Experiments — Guardrails"])


@router.get("/{experiment_id}/guardrails/events", response_model=dict)
async def list_guardrail_events(
    experiment_id: str,
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    await ExperimentService(db).get(experiment_id)
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
