"""Mutual-exclusion layer endpoints (ADR-017 §12)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.experiments.api.deps import require_platform_admin
from app.experiments.schemas import (
    AllocationResponse,
    CreateAllocationRequest,
    CreateLayerRequest,
    LayerResponse,
)
from app.experiments.services.layers import LayerService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/experiments/layers", tags=["Experiments — Layers"])


@router.post("", response_model=DataResponse[LayerResponse], status_code=201)
async def create_layer(
    body: CreateLayerRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    layer = await LayerService(db).create(key=body.key, domain=body.domain)
    await db.commit()
    return {"data": layer}


@router.get("", response_model=dict)
async def list_layers(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    rows = await LayerService(db).list_layers()
    return {"data": [LayerResponse.model_validate(x).model_dump() for x in rows]}


@router.post("/{layer_key}/allocations", response_model=DataResponse[AllocationResponse], status_code=201)
async def allocate_slices(
    layer_key: str,
    body: CreateAllocationRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    allocation = await LayerService(db).allocate(
        layer_key=layer_key,
        experiment_id=body.experiment_id,
        slice_start=body.slice_start,
        slice_end=body.slice_end,
    )
    await db.commit()
    return {"data": allocation}


@router.get("/{layer_key}/allocations", response_model=dict)
async def list_allocations(
    layer_key: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    rows = await LayerService(db).list_allocations(layer_key)
    return {"data": [AllocationResponse.model_validate(x).model_dump() for x in rows]}


@router.get("/{layer_key}/aa-probe", response_model=dict)
async def layer_aa_probe(
    layer_key: str,
    n: int = 2000,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    """Deterministic A/A hash-health probe for a layer (§4.13 v2)."""
    from app.experiments.services.assignment import aa_probe

    layer = await LayerService(db)._get_layer(layer_key)  # noqa: SLF001 — uniform 404
    return {"data": aa_probe(layer.key, n=n)}
