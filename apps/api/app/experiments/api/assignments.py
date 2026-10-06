"""Assignment & exposure diagnostics endpoints (ADR-017 §12)."""

from fastapi import APIRouter, Depends, Query
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


@router.get("/{experiment_id}/assignments/export")
async def export_assignments(
    experiment_id: str,
    limit: int = Query(5000, ge=1, le=20_000),
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    """Round 133: CSV export of raw assignment rows (the audit/compliance
    third of the export trio — snapshots and guardrail events already
    ship). Same read scope and uniform 404 as the stats endpoint. #83
    (round 301): unit ids stopped being purely system-minted when exp15
    added client-supplied anonymous ids — the write boundary now pins
    them to [A-Za-z0-9_-], and this export keeps a defense-in-depth guard
    (any cell starting with = + - @ or a control char is prefixed with
    a quote) so a future id namespace cannot reopen the Excel hole."""
    import csv
    import io

    from fastapi.responses import Response

    def _csv_cell_safe(value):
        # Excel formula-injection guard: neutralize leading = + - @ and
        # tab/CR by prefixing a single quote (OWASP CSV-injection guidance)
        if isinstance(value, str) and value[:1] in ("=", "+", "-", "@", "\t", "\r"):
            return "'" + value
        return value

    await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)
    rows = await AssignmentService(db).list_assignments(experiment_id, limit=limit)
    columns = ("unit_type", "unit_id", "variant_key", "assigned_version",
               "bucket", "is_holdout", "assigned_at")
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(columns)
    for row in rows:
        writer.writerow(
            [
                _csv_cell_safe(
                    value.isoformat()
                    if hasattr(value := getattr(row, col), "isoformat")
                    else value
                )
                for col in columns
            ]
        )
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                f'attachment; filename="experiment-{experiment_id}-assignments.csv"'
            )
        },
    )


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
