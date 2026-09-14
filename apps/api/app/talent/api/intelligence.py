"""Workforce intelligence API — demand, supply, gaps, coverage, analytics.

All aggregates enforce privacy minimum thresholds.
Supports CSV export via `?format=csv` on applicable endpoints.
"""

import csv
import dataclasses
import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.services.workforce import WorkforceIntelligenceService


def _safe_csv_cell(v: object) -> object:
    """Sanitize a cell value to prevent CSV formula injection."""
    if isinstance(v, str) and v and v[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + v
    return v


def _to_csv_response(rows: list[dict], filename: str) -> StreamingResponse:
    """Convert a list of dicts to a CSV streaming response."""
    if not rows:
        return StreamingResponse(
            iter(["No data"]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    # Sanitize all cell values to prevent formula injection
    safe_rows = [{k: _safe_csv_cell(v) for k, v in row.items()} for row in rows]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=safe_rows[0].keys())
    writer.writeheader()
    writer.writerows(safe_rows)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

router = APIRouter(prefix="/talent/intelligence", tags=["Talent — Intelligence"])


@router.get("/trends", response_model=DataResponse[list[dict]])
async def get_skill_trends(
    direction: str | None = Query(None, description="rising, stable, cooling, emerging"),
    category: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Skill trending and obsolescence detection.

    Analyzes evidence creation patterns over 90-day rolling windows
    to identify rising, cooling, stable, and emerging skills.
    """

    from app.talent.services.skill_trends import compute_skill_trends

    trends = await compute_skill_trends(
        db, direction=direction, category=category, limit=limit,
    )
    return DataResponse(data=[dataclasses.asdict(t) for t in trends])


@router.get("/demand", response_model=DataResponse[list[dict]])
async def get_demand(
    category: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Demand by capability (aggregated, privacy-safe)."""
    svc = WorkforceIntelligenceService(db)
    signals = await svc.get_demand_signals(category=category, limit=limit)
    return DataResponse(data=[
        {
            "capability_id": s.capability_id,
            "capability_name": s.capability_name,
            "category": s.category,
            "open_opportunities": s.open_opportunities,
            "total_demand": s.total_demand,
        }
        for s in signals
    ])


@router.get("/supply", response_model=DataResponse[list[dict]])
async def get_supply(
    category: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Verified supply by capability (aggregated, privacy-safe)."""
    svc = WorkforceIntelligenceService(db)
    signals = await svc.get_supply_signals(category=category, limit=limit)
    return DataResponse(data=[
        {
            "capability_id": s.capability_id,
            "capability_name": s.capability_name,
            "category": s.category,
            "total_supply": s.total_supply,
        }
        for s in signals
    ])


@router.get("/gaps", response_model=DataResponse[list[dict]])
async def get_gaps(
    category: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Demand-supply gap analysis (aggregated, privacy-safe)."""
    svc = WorkforceIntelligenceService(db)
    gaps = await svc.get_gap_analysis(category=category, limit=limit)
    return DataResponse(data=[
        {
            "capability_id": g.capability_id,
            "capability_name": g.capability_name,
            "demand_count": g.demand_count,
            "qualified_supply": g.qualified_supply,
            "gap": g.gap,
            "gap_severity": g.gap_severity,
            "content_coverage": g.content_coverage,
        }
        for g in gaps
    ])


@router.get("/coverage", response_model=DataResponse[list[dict]])
async def get_coverage(
    capability_id: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Curriculum coverage matrix."""
    svc = WorkforceIntelligenceService(db)
    return DataResponse(
        data=await svc.get_coverage_matrix(capability_id=capability_id, limit=limit)
    )


@router.get("/placements", response_model=DataResponse[dict])
async def get_placement_analytics(
    employer_org_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Placement funnel analytics."""
    if employer_org_id:
        await require_org_member(employer_org_id, user, db)
    svc = WorkforceIntelligenceService(db)
    return DataResponse(
        data=await svc.get_placement_analytics(employer_org_id=employer_org_id)
    )


@router.get("/outcomes", response_model=DataResponse[list[dict]])
async def get_outcome_analytics(
    capability_id: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Outcome-based curriculum analytics (§36).

    Returns observed associations between learning content and downstream
    outcomes: assessment pass rates, placement rates, employer verification
    rates. These are correlations, not causal claims.
    """
    svc = WorkforceIntelligenceService(db)
    return DataResponse(
        data=await svc.get_outcome_analytics(capability_id=capability_id, limit=limit)
    )


@router.get("/recommendations", response_model=DataResponse[list[dict]])
async def get_recommendations(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Content improvement recommendations (§37).

    All recommendations require human confirmation before action.
    The system never auto-publishes or auto-edits content.
    """
    svc = WorkforceIntelligenceService(db)
    return DataResponse(data=await svc.get_recommendations(limit=limit))


# ---- Hiring Analytics (I1) ----


@router.get("/hiring", response_model=DataResponse[dict])
async def get_hiring_analytics(
    org_id: str = Query(..., description="Employer organization ID"),
    days_back: int = Query(90, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Hiring funnel analytics — time-to-hire, conversion rates, pipeline velocity.

    Employer org member only.
    """
    await require_org_member(org_id, user, db)

    from app.talent.services.hiring_analytics import HiringAnalyticsService

    svc = HiringAnalyticsService(db)
    analytics = await svc.compute(org_id, days_back=days_back)
    return DataResponse(data=dataclasses.asdict(analytics))


# ---- CSV Export (N5) ----


@router.get("/gaps/export")
async def export_gaps_csv(
    category: str | None = None,
    limit: int = Query(200, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Export demand-supply gaps as CSV."""
    svc = WorkforceIntelligenceService(db)
    gaps = await svc.get_gap_analysis(category=category, limit=limit)
    rows = [
        {
            "capability_id": g.capability_id,
            "capability_name": g.capability_name,
            "demand_count": g.demand_count,
            "qualified_supply": g.qualified_supply,
            "gap": g.gap,
            "gap_severity": g.gap_severity,
            "content_coverage": g.content_coverage,
        }
        for g in gaps
    ]
    return _to_csv_response(rows, "talent-gaps.csv")


# ---- GDPR (I5) ----


@router.get("/my-data/export", response_model=DataResponse[dict])
async def export_my_data(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Export all your talent data (GDPR Article 20 — portability)."""
    from app.talent.services.gdpr import GDPRService

    svc = GDPRService(db)
    data = await svc.export_user_data(user.id)
    return DataResponse(data=data)


@router.post("/my-data/deletion-request", response_model=DataResponse[dict])
async def request_data_deletion(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Request deletion of all your talent data (GDPR Article 17 — erasure).

    Sets a 30-day grace period. Profile is made private immediately.
    """
    from app.talent.services.gdpr import GDPRService

    svc = GDPRService(db)
    result = await svc.request_deletion(user.id)
    await db.commit()
    return DataResponse(data=result)


@router.get("/my-data/consent-log", response_model=DataResponse[list[dict]])
async def get_consent_log(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """View your consent change history."""
    from app.talent.services.gdpr import GDPRService

    svc = GDPRService(db)
    log = await svc.get_consent_log(user.id)
    return DataResponse(data=log)


# ---- Badge Sharing (I2) ----


@router.get("/credentials/{credential_id}/share-links", response_model=DataResponse[dict])
async def get_share_links(
    credential_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get share links for a credential — owner only."""
    from app.talent.models.assessment import Credential

    cred = await db.get(Credential, credential_id)
    if not cred:
        from fastapi import HTTPException

        raise HTTPException(404, "Credential not found")
    if cred.user_id != user.id:
        from fastapi import HTTPException

        raise HTTPException(404, "Credential not found")

    from app.talent.services.badge_sharing import generate_share_links

    links = generate_share_links(
        credential_id=credential_id,
        credential_name=cred.credential_type,
        credential_type=cred.credential_type,
        issued_at=cred.issued_at,
        expires_at=cred.expires_at,
    )
    return DataResponse(data=dataclasses.asdict(links))


# ---- Team Skill Analytics (N9) ----


@router.get("/analytics/team/{org_id}", response_model=DataResponse[dict])
async def get_team_analytics(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get team skill analytics for an organization — org member only."""
    await require_org_member(org_id, user, db)

    from app.talent.services.team_analytics import TeamAnalyticsService

    svc = TeamAnalyticsService(db)
    analytics = await svc.get_team_analytics(org_id)
    return DataResponse(data={
        "org_id": analytics.org_id,
        "total_members": analytics.total_members,
        "total_capabilities_covered": analytics.total_capabilities_covered,
        "skill_distribution": [dataclasses.asdict(s) for s in analytics.skill_distribution],
        "team_strengths": analytics.team_strengths,
        "team_gaps": analytics.team_gaps,
    })


@router.get("/analytics/team/{org_id}/coverage", response_model=DataResponse[list[dict]])
async def get_team_coverage(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get skill coverage matrix — who covers what capabilities."""
    await require_org_member(org_id, user, db)

    from app.talent.services.team_analytics import TeamAnalyticsService

    svc = TeamAnalyticsService(db)
    matrix = await svc.get_skill_coverage_matrix(org_id)
    return DataResponse(data=matrix)


@router.get(
    "/analytics/team/{org_id}/vs/{opportunity_id}",
    response_model=DataResponse[dict],
)
async def compare_team_vs_opportunity(
    org_id: str,
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Compare team capabilities against opportunity requirements."""
    await require_org_member(org_id, user, db)

    from app.talent.services.team_analytics import TeamAnalyticsService

    svc = TeamAnalyticsService(db)
    comparison = await svc.compare_team_to_requirements(org_id, opportunity_id)
    return DataResponse(data=comparison)
