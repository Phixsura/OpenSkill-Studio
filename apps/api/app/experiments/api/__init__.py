"""Experiments API router aggregation (ADR-017 §12).

Rate-limited like the ecosystem surface (shared sliding-window limiter).
NOTE (route shadowing, §106.10): the static /experiments/layers prefix must
register BEFORE the dynamic /experiments/{experiment_id} routes.
"""

from fastapi import APIRouter, Depends

from app.core.rate_limit import rate_limit
from app.experiments.api.assignments import router as assignments_router
from app.experiments.api.experiments import router as experiments_router_module
from app.experiments.api.layers import router as layers_router

experiments_router = APIRouter(dependencies=[Depends(rate_limit(120, 60))])
# Static-prefix router first — /experiments/{experiment_id} would shadow
# /experiments/layers if registered ahead of it.
experiments_router.include_router(layers_router)
experiments_router.include_router(assignments_router)
experiments_router.include_router(experiments_router_module)
