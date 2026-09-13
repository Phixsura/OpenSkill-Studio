from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    certificates,
    client_briefs,
    cohorts,
    composer,
    discussions,
    duplicate,
    evaluation,
    gamification,
    health,
    installations,
    learning_paths,
    lti,
    matching,
    notifications,
    organizations,
    overview,
    pack_io,
    pack_reviews,
    pack_sharing,
    peer_review,
    portfolio,
    projects,
    providers,
    registry,
    requirement_profiles,
    skill_packs,
    skills,
    webhooks,
    workflow_installations,
    workflow_packs,
    workflow_registry,
    workflow_runs,
)
from app.controlplane.api import billing as cp_billing
from app.controlplane.api import client_portal as cp_client_portal
from app.controlplane.api import credits as cp_credits
from app.controlplane.api import marketplace as cp_marketplace
from app.controlplane.api import partners as cp_partners
from app.controlplane.api import plans as cp_plans
from app.controlplane.api import platform as cp_platform
from app.controlplane.api import platform_dashboard as cp_platform_dashboard
from app.controlplane.api import pricing as cp_pricing
from app.controlplane.api import tenants as cp_tenants
from app.controlplane.api import usage as cp_usage
from app.controlplane.api import whitelabel as cp_whitelabel

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
api_v1_router.include_router(cohorts.router)
api_v1_router.include_router(client_briefs.router)
api_v1_router.include_router(portfolio.router)
api_v1_router.include_router(skill_packs.router)
api_v1_router.include_router(registry.router)
api_v1_router.include_router(pack_reviews.router)
api_v1_router.include_router(installations.router)
api_v1_router.include_router(learning_paths.router)
api_v1_router.include_router(pack_io.router)
api_v1_router.include_router(notifications.router)
api_v1_router.include_router(certificates.router)
api_v1_router.include_router(lti.router)
api_v1_router.include_router(webhooks.router)
api_v1_router.include_router(discussions.router)
api_v1_router.include_router(gamification.router)
api_v1_router.include_router(duplicate.router)
api_v1_router.include_router(pack_sharing.router)
api_v1_router.include_router(providers.router)
api_v1_router.include_router(workflow_packs.router)
api_v1_router.include_router(workflow_runs.router)
api_v1_router.include_router(composer.router)
api_v1_router.include_router(workflow_installations.router)
api_v1_router.include_router(workflow_registry.router)
api_v1_router.include_router(requirement_profiles.router)
api_v1_router.include_router(matching.router)

# ── Control plane (Issue #27) ──
api_v1_router.include_router(cp_platform.router)
api_v1_router.include_router(cp_platform_dashboard.router)
api_v1_router.include_router(cp_tenants.router)
api_v1_router.include_router(cp_plans.router)
api_v1_router.include_router(cp_usage.router)
api_v1_router.include_router(cp_pricing.router)
api_v1_router.include_router(cp_credits.router)
api_v1_router.include_router(cp_billing.router)
api_v1_router.include_router(cp_partners.router)
api_v1_router.include_router(cp_marketplace.router)
api_v1_router.include_router(cp_client_portal.router)
api_v1_router.include_router(cp_whitelabel.router)
