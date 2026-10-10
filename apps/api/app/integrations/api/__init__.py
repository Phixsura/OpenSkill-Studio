"""Integration fabric API router aggregation (ADR-018 §15)."""

from fastapi import APIRouter, Depends

from app.core.rate_limit import rate_limit
from app.integrations.api.connections import router as connections_router
from app.integrations.api.events import router as events_router
from app.integrations.api.scim import scim_router
from app.integrations.api.scim import token_admin_router as scim_token_admin_router
from app.integrations.api.sso import admin_router as sso_admin_router
from app.integrations.api.sso import protocol_router as sso_protocol_router

integrations_router = APIRouter(dependencies=[Depends(rate_limit(120, 60))])
integrations_router.include_router(connections_router)
integrations_router.include_router(events_router)
integrations_router.include_router(sso_admin_router)
integrations_router.include_router(scim_token_admin_router)
# Protocol endpoints are tighter-limited: they are unauthenticated.
integrations_router.include_router(
    sso_protocol_router, dependencies=[Depends(rate_limit(30, 60))]
)
# SCIM rides its own bearer auth; IdPs burst during resyncs — keep the
# shared 120/60 window (429 + Retry-After comes from the limiter).
integrations_router.include_router(scim_router)
