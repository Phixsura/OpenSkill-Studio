"""Experiment lifecycle endpoints (ADR-017 §12)."""

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
    CloneExperimentRequest,
    CreateExperimentRequest,
    CreateVersionRequest,
    ExperimentEventResponse,
    ExperimentResponse,
    RampRequest,
    TransitionRequest,
    VersionResponse,
)
from app.experiments.security import EXPERIMENT_DOMAINS, EXPERIMENT_STATUSES
from app.experiments.services.experiments import ExperimentService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/experiments", tags=["Experiments"])


@router.post("", response_model=DataResponse[ExperimentResponse], status_code=201)
async def create_experiment(
    body: CreateExperimentRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    exp = await ExperimentService(db).create(
        key=body.key,
        title=body.title,
        domain=body.domain,
        layer_key=body.layer_key,
        owner_user_id=user.id,
        scope_org_id=body.scope_org_id,
        risk_class=body.risk_class,
        holdout_bp=body.holdout_bp,
    )
    await db.commit()
    return {"data": exp}


@router.get("", response_model=dict)
async def list_experiments(
    status: str | None = None,
    domain: str | None = None,
    q: str | None = Query(default=None, max_length=120),
    cursor: str | None = Query(default=None, max_length=26),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    check_enum(status, EXPERIMENT_STATUSES, "status")
    check_enum(domain, EXPERIMENT_DOMAINS, "domain")
    rows, total, next_cursor = await ExperimentService(db).list_experiments(
        status=status, domain=domain, q=q, cursor=cursor, limit=limit,
        scope_org_ids=scope.org_ids,
    )
    return {
        "data": [ExperimentResponse.model_validate(x).model_dump() for x in rows],
        "meta": {"total": total, "limit": limit, "next_cursor": next_cursor},
    }


@router.get("/{experiment_id}", response_model=DataResponse[ExperimentResponse])
async def get_experiment(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    return {"data": await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)}


@router.post("/{experiment_id}/versions", response_model=DataResponse[VersionResponse], status_code=201)
async def create_version(
    experiment_id: str,
    body: CreateVersionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    version = await ExperimentService(db).create_version(experiment_id, spec=body.spec, actor=user)
    await db.commit()
    return {"data": version}


@router.get("/{experiment_id}/versions", response_model=dict)
async def list_versions(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)
    rows = await ExperimentService(db).get_versions(experiment_id)
    return {"data": [VersionResponse.model_validate(x).model_dump() for x in rows]}


@router.post("/{experiment_id}/transition", response_model=DataResponse[ExperimentResponse])
async def transition_experiment(
    experiment_id: str,
    body: TransitionRequest,
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    """Lifecycle transitions. Org-admin delegation (§18): an org admin may
    operate experiments scoped to their org — out-of-scope is a uniform 404
    and the promoted/rejected states stay behind the decision runtime gate
    (EXPERIMENT_DECISION_REQUIRED) for EVERY caller; decisions and
    promotions remain platform-admin surfaces."""
    check_enum(body.to_status, EXPERIMENT_STATUSES, "to_status")
    await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)
    exp = await ExperimentService(db).transition(
        experiment_id,
        to_status=body.to_status,
        actor=scope.user,
        reason=body.reason,
        checklist=body.checklist,
        start_at=body.start_at,
    )
    await db.commit()
    return {"data": exp}


@router.patch("/{experiment_id}/ramp", response_model=DataResponse[ExperimentResponse])
async def set_ramp(
    experiment_id: str,
    body: RampRequest,
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)
    exp = await ExperimentService(db).set_ramp(
        experiment_id, ramp_bp=body.ramp_bp, actor=scope.user
    )
    await db.commit()
    return {"data": exp}


@router.get("/{experiment_id}/events", response_model=dict)
async def list_events(
    experiment_id: str,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    scope: ReadScope = Depends(experiment_read_scope),
):
    await ExperimentService(db).get_scoped(experiment_id, scope.org_ids)
    rows = await ExperimentService(db).list_events(experiment_id, limit=limit)
    return {"data": [ExperimentEventResponse.model_validate(x).model_dump() for x in rows]}


@router.post(
    "/{experiment_id}/clone",
    response_model=DataResponse[ExperimentResponse],
    status_code=201,
)
async def clone_experiment(
    experiment_id: str,
    body: CloneExperimentRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    """Duplicate an experiment: a NEW draft carrying the source's current
    spec as v1 — no layer allocation (slices are claimed deliberately)."""
    experiment = await ExperimentService(db).clone(
        experiment_id, new_key=body.key, actor=user
    )
    await db.commit()
    return {"data": experiment}
