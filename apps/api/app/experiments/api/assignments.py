"""Assignment & exposure diagnostics endpoints (ADR-017 §12)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.experiments.api.deps import (
    ReadScope,
    experiment_read_scope,
)
from app.experiments.schemas import PreviewAssignmentRequest
from app.experiments.services.assignment import AssignmentService
from app.experiments.services.experiments import ExperimentService
from app.schemas.base import DataResponse

router = APIRouter(prefix="/experiments", tags=["Experiments — Assignments"])


@router.get("/{experiment_id}/assignments", response_model=dict)
async def assignment_stats(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)
    return {"data": await AssignmentService(db).assignment_stats(experiment_id)}


@router.post("/{experiment_id}/assignments:preview", response_model=DataResponse[dict])
async def preview_assignment(
    experiment_id: str,
    body: PreviewAssignmentRequest,
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    """Dry-run the full resolution pipeline — no writes (debugging surface).
    Computes against THIS experiment row by id — key-based lookup would bind
    to a newer live experiment after key reuse."""
    exp = await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)
    result = await AssignmentService(db).compute(
        experiment=exp,
        unit_type=body.unit_type,
        unit_id=body.unit_id,
        context=body.context,
    )
    return {"data": result}


@router.get("/{experiment_id}/exposures/stats", response_model=DataResponse[dict])
async def exposure_stats(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)
    return {"data": await AssignmentService(db).exposure_stats(experiment_id)}
