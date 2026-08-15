from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    evaluation,
    health,
    organizations,
    overview,
    peer_review,
    portfolio,
    projects,
    skills,
)

api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(admin.router)
api_v1_router.include_router(organizations.router)
api_v1_router.include_router(skills.router)
api_v1_router.include_router(projects.router)
api_v1_router.include_router(peer_review.router)
api_v1_router.include_router(overview.router)
api_v1_router.include_router(evaluation.router)
api_v1_router.include_router(portfolio.router)
