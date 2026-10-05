"""Experiments API router aggregation (ADR-017 §12).

Rate-limited like the ecosystem surface (shared sliding-window limiter).
NOTE (route shadowing, §106.10): the static /experiments/layers prefix must
register BEFORE the dynamic /experiments/{experiment_id} routes.
"""

from fastapi import APIRouter, Depends

from app.core.rate_limit import rate_limit
from app.experiments.api.analysis import router as analysis_router
from app.experiments.api.assignments import router as assignments_router
from app.experiments.api.decisions import router as decisions_router
from app.experiments.api.experiments import router as experiments_router_module
from app.experiments.api.guardrails import router as guardrails_router
from app.experiments.api.holdouts import router as holdouts_router
from app.experiments.api.layers import router as layers_router
from app.experiments.api.metrics import router as metrics_router
from app.experiments.api.selfserve import anon_router as anon_selfserve_router
from app.experiments.api.selfserve import router as selfserve_router

experiments_router = APIRouter(dependencies=[Depends(rate_limit(120, 60))])
# Static-prefix routers first — /experiments/{experiment_id} would shadow
# /experiments/layers and /experiments/metric-definitions if registered
# ahead of them (§106.10 route-shadowing class).
experiments_router.include_router(layers_router)
experiments_router.include_router(metrics_router)
experiments_router.include_router(decisions_router)
experiments_router.include_router(assignments_router)
experiments_router.include_router(selfserve_router)
experiments_router.include_router(anon_selfserve_router)
experiments_router.include_router(holdouts_router)
experiments_router.include_router(guardrails_router)
experiments_router.include_router(analysis_router)
experiments_router.include_router(experiments_router_module)
