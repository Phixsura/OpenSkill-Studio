"""Mutual-exclusion layers & slice allocation (ADR-017 §4.3, Part B).

Same-layer experiments own disjoint slice ranges of the [0, total_slices)
hash space, so one unit can never enter two incompatible experiments.
Overlap is enforced under SELECT ... FOR UPDATE on the layer row — the
get-or-check-then-insert shape is race-unsafe without it (R127/§105 class).
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.experiments.models import (
    Experiment,
    ExperimentLayer,
    ExperimentLayerAllocation,
)
from app.experiments.security import EXPERIMENT_DOMAINS


class LayerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, *, key: str, domain: str) -> ExperimentLayer:
        if domain not in EXPERIMENT_DOMAINS:
            raise AppError(
                "VALIDATION_ERROR",
                f"Unknown domain: {domain} (allowed: {sorted(EXPERIMENT_DOMAINS)})",
                422,
            )
        layer = ExperimentLayer(key=key, domain=domain)
        self.db.add(layer)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            raise AppError("EXPERIMENT_KEY_TAKEN", f"Layer key taken: {key}", 409) from exc
        return layer

    async def list_layers(self) -> list[ExperimentLayer]:
        q = select(ExperimentLayer).order_by(ExperimentLayer.key.asc())
        return list((await self.db.execute(q)).scalars())

    async def list_allocations(self, layer_key: str) -> list[ExperimentLayerAllocation]:
        await self._get_layer(layer_key)
        q = (
            select(ExperimentLayerAllocation)
            .where(ExperimentLayerAllocation.layer_key == layer_key)
            .order_by(ExperimentLayerAllocation.slice_start.asc())
        )
        return list((await self.db.execute(q)).scalars())

    async def _get_layer(self, layer_key: str, *, for_update: bool = False) -> ExperimentLayer:
        q = select(ExperimentLayer).where(ExperimentLayer.key == layer_key)
        if for_update:
            q = q.with_for_update()
        layer = (await self.db.execute(q)).scalar_one_or_none()
        if not layer:
            raise AppError("EXPERIMENT_NOT_FOUND", "Layer not found", 404)
        return layer

    async def allocate(
        self, *, layer_key: str, experiment_id: str, slice_start: int, slice_end: int
    ) -> ExperimentLayerAllocation:
        # Serialize concurrent allocations against the same layer
        layer = await self._get_layer(layer_key, for_update=True)
        if slice_start > slice_end:
            raise AppError("VALIDATION_ERROR", "slice_start must be <= slice_end", 422)
        if slice_end >= layer.total_slices:
            raise AppError(
                "VALIDATION_ERROR",
                f"slice_end must be < total_slices ({layer.total_slices})",
                422,
            )
        exp = await self.db.get(Experiment, experiment_id)
        if not exp:
            raise AppError("EXPERIMENT_NOT_FOUND", "Experiment not found", 404)
        if exp.layer_key != layer_key:
            raise AppError(
                "VALIDATION_ERROR",
                f"Experiment {experiment_id} belongs to layer {exp.layer_key}",
                422,
            )
        existing = await self.list_allocations(layer_key)
        for row in existing:
            if row.slice_start <= slice_end and slice_start <= row.slice_end:
                raise AppError(
                    "LAYER_SLICE_OVERLAP",
                    f"Slices [{slice_start},{slice_end}] overlap "
                    f"[{row.slice_start},{row.slice_end}] (experiment {row.experiment_id})",
                    409,
                )
        allocation = ExperimentLayerAllocation(
            layer_key=layer_key,
            experiment_id=experiment_id,
            slice_start=slice_start,
            slice_end=slice_end,
        )
        self.db.add(allocation)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            # One allocation per experiment (unique constraint)
            raise AppError(
                "LAYER_SLICE_OVERLAP", "Experiment already has a slice allocation", 409
            ) from exc
        return allocation
