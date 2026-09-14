"""Talent API router — aggregates all talent sub-routers.

Wired features:
  - ETagRoute on GET-heavy routers (capabilities, evidence, passport)
  - Rate limiting dependency on the aggregate router (100 req/min per user)
"""

from fastapi import APIRouter, Depends

from app.talent.api.activity import router as activity_router
from app.talent.api.applications import router as applications_router
from app.talent.api.assessments import router as assessments_router
from app.talent.api.bulk import router as bulk_router
from app.talent.api.candidate_notes import router as candidate_notes_router
from app.talent.api.capabilities import router as capabilities_router
from app.talent.api.career_goals import router as career_goal_router
from app.talent.api.credential_pathways import router as credential_pathway_router
from app.talent.api.dashboards import router as dashboards_router
from app.talent.api.did import router as did_router
from app.talent.api.employers import router as employers_router
from app.talent.api.endorsements import router as endorsements_router
from app.talent.api.etag import ETagRoute
from app.talent.api.evidence import router as evidence_router
from app.talent.api.inference import router as inference_router
from app.talent.api.intelligence import router as intelligence_router
from app.talent.api.matching import router as matching_router
from app.talent.api.notifications import router as notification_router
from app.talent.api.passport import router as passport_router
from app.talent.api.pools import router as pools_router
from app.talent.api.rate_limit import rate_limit_talent
from app.talent.api.saved_searches import router as saved_search_router
from app.talent.api.scheduling import router as scheduling_router
from app.talent.api.scorecards import router as scorecard_router
from app.talent.api.verifications import router as verifications_router

# Apply ETagRoute on GET-heavy routers for conditional request support
capabilities_router.route_class = ETagRoute
evidence_router.route_class = ETagRoute
passport_router.route_class = ETagRoute

talent_router = APIRouter(dependencies=[Depends(rate_limit_talent)])
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
talent_router.include_router(inference_router)
talent_router.include_router(notification_router)
talent_router.include_router(endorsements_router)
talent_router.include_router(activity_router)
talent_router.include_router(candidate_notes_router)
talent_router.include_router(saved_search_router)
talent_router.include_router(scheduling_router)
talent_router.include_router(credential_pathway_router)
talent_router.include_router(career_goal_router)
