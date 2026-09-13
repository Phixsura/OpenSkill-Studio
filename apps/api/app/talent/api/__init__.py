"""Talent API router — aggregates all talent sub-routers."""

from fastapi import APIRouter

from app.talent.api.applications import router as applications_router
from app.talent.api.capabilities import router as capabilities_router
from app.talent.api.employers import router as employers_router
from app.talent.api.evidence import router as evidence_router
from app.talent.api.passport import router as passport_router

talent_router = APIRouter()
talent_router.include_router(capabilities_router)
talent_router.include_router(evidence_router)
talent_router.include_router(passport_router)
talent_router.include_router(employers_router)
talent_router.include_router(applications_router)
