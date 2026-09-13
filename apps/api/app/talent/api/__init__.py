"""Talent API router — aggregates all talent sub-routers."""

from fastapi import APIRouter

from app.talent.api.applications import router as applications_router
from app.talent.api.assessments import router as assessments_router
from app.talent.api.bulk import router as bulk_router
from app.talent.api.capabilities import router as capabilities_router
from app.talent.api.dashboards import router as dashboards_router
from app.talent.api.did import router as did_router
from app.talent.api.employers import router as employers_router
from app.talent.api.evidence import router as evidence_router
from app.talent.api.intelligence import router as intelligence_router
from app.talent.api.matching import router as matching_router
from app.talent.api.passport import router as passport_router
from app.talent.api.pools import router as pools_router
from app.talent.api.scorecards import router as scorecard_router
from app.talent.api.verifications import router as verifications_router

talent_router = APIRouter()
talent_router.include_router(capabilities_router)
talent_router.include_router(evidence_router)
talent_router.include_router(passport_router)
# matching_router BEFORE employers_router: /opportunities/matches must
# resolve before /opportunities/{opp_id} catches "matches" as an ID
talent_router.include_router(matching_router)
talent_router.include_router(employers_router)
talent_router.include_router(applications_router)
talent_router.include_router(assessments_router)
talent_router.include_router(intelligence_router)
talent_router.include_router(dashboards_router)
talent_router.include_router(verifications_router)
talent_router.include_router(pools_router)
talent_router.include_router(did_router)
talent_router.include_router(bulk_router)
talent_router.include_router(scorecard_router)
