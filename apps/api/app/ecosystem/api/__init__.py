"""Ecosystem API router aggregation (ADR-016 Part R)."""

from fastapi import APIRouter

from app.ecosystem.api.benchmarks import router as benchmarks_router
from app.ecosystem.api.catalog import router as catalog_router
from app.ecosystem.api.dashboard import router as dashboard_router
from app.ecosystem.api.drafts import router as drafts_router
from app.ecosystem.api.graph import router as graph_router
from app.ecosystem.api.observations import router as observations_router
from app.ecosystem.api.pricing import router as pricing_router
from app.ecosystem.api.replacements import router as replacements_router
from app.ecosystem.api.rollouts import router as rollouts_router
from app.ecosystem.api.sources import router as sources_router
from app.ecosystem.api.watchlists import router as watchlists_router

ecosystem_router = APIRouter()
ecosystem_router.include_router(sources_router)
ecosystem_router.include_router(observations_router)
ecosystem_router.include_router(catalog_router)
ecosystem_router.include_router(pricing_router)
ecosystem_router.include_router(benchmarks_router)
ecosystem_router.include_router(graph_router)
ecosystem_router.include_router(replacements_router)
ecosystem_router.include_router(drafts_router)
ecosystem_router.include_router(rollouts_router)
ecosystem_router.include_router(watchlists_router)
ecosystem_router.include_router(dashboard_router)
