"""Integration fabric API router aggregation (ADR-018 §15)."""

from fastapi import APIRouter, Depends

from app.core.rate_limit import rate_limit
from app.integrations.api.connections import router as connections_router

integrations_router = APIRouter(dependencies=[Depends(rate_limit(120, 60))])
integrations_router.include_router(connections_router)
