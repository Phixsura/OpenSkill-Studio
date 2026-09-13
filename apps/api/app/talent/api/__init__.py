"""Talent API router — aggregates all talent sub-routers."""

from fastapi import APIRouter

from app.talent.api.applications import router as applications_router
from app.talent.api.assessments import router as assessments_router
from app.talent.api.capabilities import router as capabilities_router
from app.talent.api.employers import router as employers_router
from app.talent.api.evidence import router as evidence_router
from app.talent.api.intelligence import router as intelligence_router
from app.talent.api.matching import router as matching_router
from app.talent.api.passport import router as passport_router
from app.talent.api.pools import router as pools_router
from app.talent.api.verifications import router as verifications_router

talent_router = APIRouter()
talent_router.include_router(capabilities_router)
talent_router.include_router(evidence_router)
talent_router.include_router(passport_router)
talent_router.include_router(employers_router)
talent_router.include_router(applications_router)
talent_router.include_router(assessments_router)
talent_router.include_router(matching_router)
talent_router.include_router(intelligence_router)
talent_router.include_router(verifications_router)
talent_router.include_router(pools_router)
