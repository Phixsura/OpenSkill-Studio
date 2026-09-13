"""Employer / Opportunity API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.talent.models.employer import EmployerProfile, Opportunity
from app.talent.schemas.employer import (
    CreateEmployerProfileRequest,
    CreateOpportunityRequest,
    EmployerProfileResponse,
    OpportunityResponse,
    UpdateOpportunityRequest,
)

router = APIRouter(prefix="/talent", tags=["Talent — Employers"])


@router.post("/employers/{org_id}", response_model=DataResponse[EmployerProfileResponse], status_code=201)
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
    return DataResponse(data=EmployerProfileResponse.model_validate(profile))


@router.get("/employers/{org_id}", response_model=DataResponse[EmployerProfileResponse])
async def get_employer_profile(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    profile = await db.get(EmployerProfile, org_id)
    if not profile:
        raise HTTPException(404, "Employer profile not found")
    return DataResponse(data=EmployerProfileResponse.model_validate(profile))


@router.patch("/employers/{org_id}", response_model=DataResponse[EmployerProfileResponse])
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
    return DataResponse(data=EmployerProfileResponse.model_validate(profile))


# ---- Opportunities ----

@router.post("/opportunities", response_model=DataResponse[OpportunityResponse], status_code=201)
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
    return DataResponse(data=OpportunityResponse.model_validate(opp))


@router.get("/opportunities", response_model=ListResponse[OpportunityResponse])
async def list_opportunities(
    opportunity_type: str | None = None,
    status: str = "open",
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List open opportunities."""
    q = select(Opportunity).where(Opportunity.status == status)
    if opportunity_type:
        q = q.where(Opportunity.opportunity_type == opportunity_type)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    q = q.order_by(Opportunity.created_at.desc()).limit(per_page).offset((page - 1) * per_page)
    result = await db.execute(q)
    items = result.scalars().all()

    return ListResponse(
        data=[OpportunityResponse.model_validate(o) for o in items],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=page * per_page < total),
    )


@router.get("/opportunities/{opp_id}", response_model=DataResponse[OpportunityResponse])
async def get_opportunity(
    opp_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    opp = await db.get(Opportunity, opp_id)
    if not opp:
        raise HTTPException(404, "Opportunity not found")
    return DataResponse(data=OpportunityResponse.model_validate(opp))


@router.patch("/opportunities/{opp_id}", response_model=DataResponse[OpportunityResponse])
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
    return DataResponse(data=OpportunityResponse.model_validate(opp))
