"""Metric definition & snapshot endpoints (ADR-017 §12).

NOTE (route shadowing, §106.10): /experiments/metric-definitions is a static
single-segment path under /experiments — this router must register BEFORE the
dynamic /experiments/{experiment_id} routes.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.experiments.api.deps import check_enum, require_platform_admin
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
    _user: User = Depends(get_current_user),
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
    _user: User = Depends(get_current_user),
):
    await ExperimentService(db).get(experiment_id)
    rows = await MetricService(db).list_snapshots(
        experiment_id, metric_key=metric_key, limit=limit
    )
    return {"data": [MetricSnapshotResponse.model_validate(x).model_dump() for x in rows]}
