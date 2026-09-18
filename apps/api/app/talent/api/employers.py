"""Employer / Opportunity API — includes public career page (I6)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.models.employer import EmployerProfile, Opportunity
from app.talent.schemas.cursor import CursorListResponse, CursorMeta
from app.talent.schemas.employer import (
    CreateEmployerProfileRequest,
    CreateOpportunityRequest,
    EmployerProfileResponse,
    OpportunityResponse,
    UpdateOpportunityRequest,
)

router = APIRouter(prefix="/talent", tags=["Talent — Employers"])


@router.post("/employers/{org_id}", response_model=DataResponse[EmployerProfileResponse], status_code=201,
    summary="Create employer profile",
    description="Register an organization as an employer with company details and branding.",
)
async def create_employer_profile(
    org_id: str,
    body: CreateEmployerProfileRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Register an employer profile for an org."""
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)

    existing = await db.get(EmployerProfile, org_id)
    if existing:
        raise HTTPException(409, "Employer profile already exists")

    profile = EmployerProfile(
        org_id=org_id,
        company_size=body.company_size,
        industry=body.industry,
        website_url=body.website_url,
        logo_url=body.logo_url,
        description=body.description,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return DataResponse(data=EmployerProfileResponse.model_validate(profile))


@router.get("/employers/{org_id}", response_model=DataResponse[EmployerProfileResponse],
    summary="Get employer profile",
    description="Returns the employer profile for an organization.",
)
async def get_employer_profile(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    profile = await db.get(EmployerProfile, org_id)
    if not profile:
        raise HTTPException(404, "Employer profile not found")
    return DataResponse(data=EmployerProfileResponse.model_validate(profile))


@router.patch("/employers/{org_id}", response_model=DataResponse[EmployerProfileResponse],
    summary="Update employer profile",
    description="Update employer profile details like description, industry, logo, and career page settings.",
)
async def update_employer_profile(
    org_id: str,
    body: CreateEmployerProfileRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update an employer profile — admin+ only."""
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    profile = await db.get(EmployerProfile, org_id)
    if not profile:
        raise HTTPException(404, "Employer profile not found")
    # Allowlist: only user-editable fields (not verification_status, verified_at)
    editable = {"company_size", "industry", "website_url", "logo_url", "description"}
    for key, value in body.model_dump(exclude_unset=True).items():
        if key in editable:
            setattr(profile, key, value)
    await db.commit()
    await db.refresh(profile)
    return DataResponse(data=EmployerProfileResponse.model_validate(profile))


# ---- Opportunities ----

@router.post("/opportunities", response_model=DataResponse[OpportunityResponse], status_code=201,
    summary="Create opportunity",
    description="Post a new job, internship, or project role with capability requirements.",
)
async def create_opportunity(
    body: CreateOpportunityRequest,
    org_id: str = Query(..., description="Employer org ID"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new opportunity posting."""
    await require_org_member(org_id, user, db)

    profile = await db.get(EmployerProfile, org_id)
    if not profile:
        raise HTTPException(404, "Employer profile not found — register first")

    opp = Opportunity(
        employer_org_id=org_id,
        title=body.title,
        description=body.description,
        opportunity_type=body.opportunity_type,
        location_mode=body.location_mode,
        location_text=body.location_text,
        compensation_display=body.compensation_display,
        required_capabilities=body.required_capabilities,
        preferred_capabilities=body.preferred_capabilities,
        minimum_verification=body.minimum_verification,
        portfolio_requirements=body.portfolio_requirements,
        application_deadline=body.application_deadline,
        openings=body.openings,
        created_by=user.id,
    )
    db.add(opp)
    await db.commit()
    await db.refresh(opp)
    return DataResponse(data=OpportunityResponse.model_validate(opp))


@router.get("/opportunities", response_model=CursorListResponse[OpportunityResponse],
    summary="List opportunities",
    description="Returns paginated list of opportunities with filtering by type, location, status.",
)
async def list_opportunities(
    q: str | None = Query(None, description="Full-text search on title/description"),
    opportunity_type: str | None = None,
    location_mode: str | None = Query(None, description="remote, hybrid, onsite"),
    capabilities: str | None = Query(None, description="Comma-separated capability IDs"),
    sort: str = Query("newest", description="newest, deadline, relevance"),
    status: str = "open",
    cursor: str | None = Query(None, description="Cursor for pagination (last item ID)"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Search and list open opportunities.

    Supports full-text search (q), faceted filters (opportunity_type,
    location_mode, capabilities), and sort (newest, deadline, relevance).
    """
    from app.talent.services.opportunity_search import OpportunitySearchService

    svc = OpportunitySearchService(db)
    cap_ids = [c.strip() for c in capabilities.split(",") if c.strip()] if capabilities else None
    items, has_more = await svc.search(
        q=q,
        capability_ids=cap_ids,
        opportunity_type=opportunity_type,
        location_mode=location_mode,
        status=status,
        sort=sort,
        cursor=cursor,
        limit=limit,
    )
    next_cursor = items[-1].id if has_more and items else None
    return CursorListResponse(
        data=[OpportunityResponse.model_validate(o) for o in items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.get("/opportunities/{opp_id}", response_model=DataResponse[OpportunityResponse],
    summary="Get opportunity detail",
    description="Returns full details of an opportunity including requirements and application stats.",
)
async def get_opportunity(
    opp_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    opp = await db.get(Opportunity, opp_id)
    if not opp:
        raise HTTPException(404, "Opportunity not found")
    return DataResponse(data=OpportunityResponse.model_validate(opp))


@router.patch("/opportunities/{opp_id}", response_model=DataResponse[OpportunityResponse],
    summary="Update opportunity",
    description="Update opportunity details, requirements, or status. Employer org member only.",
)
async def update_opportunity(
    opp_id: str,
    body: UpdateOpportunityRequest,
    org_id: str = Query(..., description="Employer org ID"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db)
    opp = await db.get(Opportunity, opp_id)
    if not opp:
        raise HTTPException(404, "Opportunity not found")
    if opp.employer_org_id != org_id:
        raise HTTPException(404, "Opportunity not found")

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(opp, key, value)

    await db.commit()
    await db.refresh(opp)
    return DataResponse(data=OpportunityResponse.model_validate(opp))


# ---- Public Career Page (I6) ----


@router.get("/employers/{org_id}/career-page", response_model=DataResponse[dict],
    summary="Get career page",
    description="Returns public career page data for an employer.",
)
async def get_career_page(
    org_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Public career page — employer profile + open opportunities.

    No authentication required. Returns employer branding and open positions.
    """
    from sqlalchemy import select as sa_select

    profile = await db.get(EmployerProfile, org_id)
    if not profile:
        raise HTTPException(404, "Employer not found")

    opp_q = (
        sa_select(Opportunity)
        .where(Opportunity.employer_org_id == org_id, Opportunity.status == "open")
        .order_by(Opportunity.created_at.desc())
        .limit(50)
    )
    opp_result = await db.execute(opp_q)
    opportunities = opp_result.scalars().all()

    return DataResponse(data={
        "profile": {
            "org_id": profile.org_id,
            "company_size": profile.company_size,
            "industry": profile.industry,
            "website_url": profile.website_url,
            "logo_url": profile.logo_url,
            "description": profile.description,
            "cover_image_url": getattr(profile, "cover_image_url", None),
            "culture_text": getattr(profile, "culture_text", None),
            "benefits": getattr(profile, "benefits", None) or [],
            "values": getattr(profile, "values", None) or [],
            "social_links": getattr(profile, "social_links", None) or {},
            "verification_status": profile.verification_status,
        },
        "opportunities": [
            OpportunityResponse.model_validate(o).model_dump()
            for o in opportunities
        ],
    })
