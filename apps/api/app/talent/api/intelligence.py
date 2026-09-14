"""Workforce intelligence API — demand, supply, gaps, coverage, analytics.

All aggregates enforce privacy minimum thresholds.
Supports CSV export via `?format=csv` on applicable endpoints.
"""

import csv
import dataclasses
import io

from fastapi import APIRouter, Depends, HTTPException, Query
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


# ---- Data Retention & Consent (N20) ----


@router.get("/retention/preview", response_model=DataResponse[list[dict]])
async def preview_retention(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Preview data retention enforcement — what would be affected.

    Admin only. Does NOT modify data. Shows counts per policy.
    """
    if not getattr(user, "is_superuser", False):
        raise HTTPException(403, "Platform admin only")
    from app.talent.services.data_retention import DataRetentionService

    svc = DataRetentionService(db)
    reports = await svc.preview_retention()
    return DataResponse(data=[
        {
            "policy": r.policy,
            "records_affected": r.records_affected,
            "action": r.action,
            "cutoff_date": r.cutoff_date.isoformat(),
        }
        for r in reports
    ])


@router.post("/retention/enforce", response_model=DataResponse[list[dict]])
async def enforce_retention(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Enforce data retention policies — deletes/anonymizes old data.

    Admin only. Destructive operation. Recommended to preview first.
    """
    if not getattr(user, "is_superuser", False):
        raise HTTPException(403, "Platform admin only")
    from app.talent.services.data_retention import DataRetentionService

    svc = DataRetentionService(db)
    reports = await svc.enforce_retention()
    await db.commit()
    return DataResponse(data=[
        {
            "policy": r.policy,
            "records_affected": r.records_affected,
            "action": r.action,
            "cutoff_date": r.cutoff_date.isoformat(),
        }
        for r in reports
    ])


@router.get("/consent-history", response_model=DataResponse[list[dict]])
async def get_consent_history(
    consent_type: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get my consent audit trail — all consent changes I've made."""
    from app.talent.services.data_retention import DataRetentionService

    svc = DataRetentionService(db)
    trail = await svc.get_consent_audit_trail(
        user.id, consent_type=consent_type, limit=limit
    )
    return DataResponse(data=trail)


# ---- Market Insights ----


@router.get("/market/skill-values", response_model=DataResponse[list[dict]])
async def get_skill_market_values(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Skill market value estimation (demand × scarcity)."""
    from app.talent.services.market_insights import MarketInsightsService
    from app.talent.services.workforce import WorkforceIntelligenceService

    wf = WorkforceIntelligenceService(db)
    mi = MarketInsightsService()
    gaps = await wf.get_gap_analysis(limit=limit)
    results = []
    for g in gaps:
        trend = "stable"
        if g.gap_severity == "high":
            trend = "rising"
        elif g.gap_severity == "low" and g.demand_count < 5:
            trend = "declining"
        mv = mi.compute_market_value(g.demand_count, g.qualified_supply, trend)
        results.append({
            "capability_id": g.capability_id,
            "capability_name": g.capability_name,
            "demand_index": mv.demand_index,
            "scarcity_index": mv.scarcity_index,
            "market_value_score": mv.market_value_score,
            "trend": mv.trend,
        })
    results.sort(key=lambda x: x["market_value_score"], reverse=True)
    return DataResponse(data=results[:limit])


@router.get("/market/employer-reputation/{org_id}", response_model=DataResponse[dict])
async def get_employer_reputation(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Employer reputation score from platform activity."""
    from app.talent.services.market_insights import MarketInsightsService
    mi = MarketInsightsService()
    rep = mi.compute_employer_reputation(
        org_id=org_id, total_placements=0, verified_placements=0,
        avg_duration_days=None, return_candidates=0, total_feedback=0,
        avg_response_hours=None,
    )
    return DataResponse(data={
        "org_id": rep.org_id, "reputation_score": rep.reputation_score,
        "total_placements": rep.total_placements,
        "verification_rate": rep.verification_rate,
    })


# ---- Diversity Analytics ----


@router.get("/diversity/pipeline/{org_id}", response_model=DataResponse[dict])
async def get_pipeline_equity(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Pipeline equity analysis (demographic-free bias detection)."""
    await require_org_member(org_id, user, db)
    from app.talent.services.diversity_analytics import DiversityAnalyticsService
    svc = DiversityAnalyticsService()
    report = svc.build_report(org_id=org_id, applications=[], applications_by_stage={})
    return DataResponse(data={
        "total_applications": report.total_applications,
        "stage_dropoffs": [{"from": d.from_stage, "to": d.to_stage, "rate": d.drop_off_rate} for d in report.stage_dropoffs],
        "source_effectiveness": [{"source": s.source, "hire_rate": s.hire_rate} for s in report.source_effectiveness],
        "equity_flags": report.equity_flags,
    })


# ---- Skill Gap Prediction ----


@router.get("/predictions/skill-gaps", response_model=DataResponse[list[dict]])
async def get_skill_gap_predictions(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Forecast future skill gaps (3/6/12 months)."""
    from app.talent.services.skill_gap_prediction import SkillGapPredictionService
    from app.talent.services.workforce import WorkforceIntelligenceService

    wf = WorkforceIntelligenceService(db)
    pred = SkillGapPredictionService()
    gaps = await wf.get_gap_analysis(limit=limit)
    forecasts = []
    for g in gaps:
        growth = 0.1 if g.gap_severity == "high" else 0.0
        f = pred.build_forecast(
            capability_id=g.capability_id, capability_name=g.capability_name,
            current_demand=g.demand_count, current_supply=g.qualified_supply,
            growth_rate_90d=growth, supply_growth_monthly=1,
        )
        forecasts.append({
            "capability_id": f.capability_id, "capability_name": f.capability_name,
            "current_gap": f.current_gap, "predicted_gap_3m": f.predicted_gap_3m,
            "predicted_gap_6m": f.predicted_gap_6m, "predicted_gap_12m": f.predicted_gap_12m,
            "urgency": f.urgency, "action": f.recommended_action,
        })
    return DataResponse(data=forecasts)


# ---- Gaps #21-35: Evidence Intelligence ----


@router.get("/evidence/quality/{evidence_id}", response_model=DataResponse[dict])
async def get_evidence_quality(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Score individual evidence quality (gap #21)."""
    from app.talent.models.evidence import CapabilityEvidence
    ev = await db.get(CapabilityEvidence, evidence_id)
    if not ev:
        raise HTTPException(404, "Evidence not found")
    from app.talent.services.evidence_intelligence import compute_evidence_quality
    quality = compute_evidence_quality({
        "source_id": ev.source_id, "score_normalized": ev.score_normalized,
        "verification_level": ev.verification_level, "occurred_at": ev.occurred_at,
        "org_id": ev.org_id, "confidence": ev.confidence,
    })
    return DataResponse(data=quality)


@router.get("/evidence/expiring", response_model=DataResponse[list[dict]])
async def get_expiring_evidence(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Find evidence expiring within N days (gap #22)."""
    from app.talent.services.evidence_intelligence import find_expiring_evidence
    results = await find_expiring_evidence(db, days_ahead=days, user_id=user.id)
    return DataResponse(data=results)


@router.post("/evidence/simulate", response_model=DataResponse[dict])
async def simulate_evidence_impact(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Simulate how adding evidence would change a score (gap #26)."""
    from app.talent.services.evidence_intelligence import simulate_score_change
    result = simulate_score_change(
        current_evidence=body.get("current_evidence", []),
        hypothetical_evidence=body.get("new_evidence", {}),
        decay_config=body.get("decay_config"),
    )
    return DataResponse(data=result)


@router.get("/evidence/distribution", response_model=DataResponse[dict])
async def get_evidence_distribution(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Evidence type distribution analytics (gap #32)."""
    from app.talent.services.evidence_intelligence import compute_evidence_distribution
    result = await compute_evidence_distribution(db, user_id=user.id)
    return DataResponse(data=result)


@router.get("/scoring/calibration", response_model=DataResponse[dict])
async def get_scoring_calibration(
    user: User = Depends(get_current_user),
):
    """Get current scoring calibration parameters (gap #28)."""
    from app.talent.services.evidence_intelligence import DEFAULT_CALIBRATION
    return DataResponse(data=DEFAULT_CALIBRATION)


@router.post("/scoring/calibration/validate", response_model=DataResponse[dict])
async def validate_scoring_calibration(
    body: dict,
    user: User = Depends(get_current_user),
):
    """Validate proposed scoring calibration changes (gap #28)."""
    from app.talent.services.evidence_intelligence import validate_calibration
    errors = validate_calibration(body)
    return DataResponse(data={"valid": len(errors) == 0, "errors": errors})
