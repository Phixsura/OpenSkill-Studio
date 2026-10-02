"""Metric definition & snapshot endpoints (ADR-017 §12).

NOTE (route shadowing, §106.10): /experiments/metric-definitions is a static
single-segment path under /experiments — this router must register BEFORE the
dynamic /experiments/{experiment_id} routes.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.experiments.api.deps import (
    ReadScope,
    check_enum,
    experiment_read_scope,
    require_platform_admin,
)
from app.experiments.schemas import (
    CreateMetricDefinitionRequest,
    MetricDefinitionResponse,
    MetricSnapshotResponse,
)
from app.experiments.security import EXPERIMENT_DOMAINS
from app.experiments.services.experiments import ExperimentService
from app.experiments.services.metrics import MetricService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/experiments", tags=["Experiments — Metrics"])


@router.post(
    "/metric-definitions", response_model=DataResponse[MetricDefinitionResponse], status_code=201
)
async def create_metric_definition(
    body: CreateMetricDefinitionRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    definition = await MetricService(db).create_definition(**body.model_dump(exclude_none=True))
    await db.commit()
    return {"data": definition}


@router.get("/metric-definitions", response_model=dict)
async def list_metric_definitions(
    domain: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    check_enum(domain, EXPERIMENT_DOMAINS, "domain")
    rows = await MetricService(db).list_definitions(domain=domain)
    return {"data": [MetricDefinitionResponse.model_validate(x).model_dump() for x in rows]}


@router.post("/metric-definitions/seed", response_model=DataResponse[dict])
async def seed_metric_definitions(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    """Idempotent: inserts missing built-in definitions, never overwrites."""
    created = await MetricService(db).ensure_seed_definitions()
    await db.commit()
    return {"data": {"created": created}}


@router.get("/{experiment_id}/metrics", response_model=dict)
async def list_metric_snapshots(
    experiment_id: str,
    metric_key: str | None = Query(default=None, max_length=64),
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)
    rows = await MetricService(db).list_snapshots(
        experiment_id, metric_key=metric_key, limit=limit
    )
    return {"data": [MetricSnapshotResponse.model_validate(x).model_dump() for x in rows]}


_EXPORT_COLUMNS = (
    "metric_key", "variant_key", "segment", "window_start", "window_end",
    "n", "numerator", "denominator", "sum_value", "sum_sq",
    "cov_sum", "cov_sum_sq", "cov_xy_sum", "computed_at",
)


@router.get("/{experiment_id}/metrics/export")
async def export_metric_snapshots(
    experiment_id: str,
    metric_key: str | None = Query(default=None, max_length=64),
    limit: int = Query(5000, ge=1, le=20_000),
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    """CSV export of metric snapshots (§12 v3 — the industry-standard
    results-export surface). Same read scope and uniform 404 as the JSON
    listing; key columns are pattern-validated lowercase (no Excel formula
    injection surface) and provenance stays out of the flat file."""
    import csv
    import io

    from fastapi.responses import Response

    await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)
    rows = await MetricService(db).list_snapshots(
        experiment_id, metric_key=metric_key, limit=limit
    )
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(_EXPORT_COLUMNS)
    for row in rows:
        writer.writerow(
            [
                value.isoformat() if hasattr(value := getattr(row, col), "isoformat")
                else value
                for col in _EXPORT_COLUMNS
            ]
        )
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                f'attachment; filename="experiment-{experiment_id}-snapshots.csv"'
            )
        },
    )
