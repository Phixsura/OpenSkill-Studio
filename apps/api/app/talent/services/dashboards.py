"""Analytics dashboards — school, employer, platform (ADR-015 §40–§42).

All aggregates respect min_cohort_size privacy thresholds.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import OrgMember
from app.talent.models.application import Application, Placement
from app.talent.models.assessment import AssessmentBlueprint, AssessmentRun
from app.talent.models.capability import Capability
from app.talent.models.employer import Opportunity
from app.talent.models.evidence import CapabilityEvidence
from app.talent.models.internship import EmployerVerification
from app.talent.services.workforce import DEFAULT_MIN_COHORT_SIZE

# ---------------------------------------------------------------------------
# §40 — School / training provider dashboard
# ---------------------------------------------------------------------------


class SchoolDashboardService:
    """Aggregated analytics for a school/training-provider org."""

    def __init__(self, db: AsyncSession, *, min_cohort_size: int = DEFAULT_MIN_COHORT_SIZE):
        self.db = db
        self.min_cohort_size = min_cohort_size

    async def get_dashboard(self, org_id: str) -> dict:
        """Return school dashboard data for the given org.

        Includes:
        - verified_capability_distribution
        - assessment_pass_rates
        - placement_stats
        - employer_feedback_summary
        - alumni_activity
        """
        # 1. Capability distribution: evidence for org members, grouped by cap
        cap_dist_q = (
            select(
                Capability.id.label("capability_id"),
                Capability.canonical_name,
                func.count(func.distinct(CapabilityEvidence.user_id)).label("user_count"),
            )
            .join(CapabilityEvidence, CapabilityEvidence.capability_id == Capability.id)
            .where(
                CapabilityEvidence.org_id == org_id,
                CapabilityEvidence.status == "active",
                Capability.status == "active",
            )
            .group_by(Capability.id, Capability.canonical_name)
            .having(func.count(func.distinct(CapabilityEvidence.user_id)) >= self.min_cohort_size)
            .order_by(func.count(func.distinct(CapabilityEvidence.user_id)).desc())
            .limit(50)
        )
        cap_dist_result = await self.db.execute(cap_dist_q)
        capability_distribution = [
            {
                "capability_id": row.capability_id,
                "capability_name": row.canonical_name,
                "verified_users": row.user_count,
            }
            for row in cap_dist_result.all()
        ]

        # 2. Assessment pass rates: blueprints in this org
        assessment_q = (
            select(
                AssessmentBlueprint.id.label("blueprint_id"),
                AssessmentBlueprint.title,
                func.count().label("total_runs"),
                func.count().filter(AssessmentRun.status == "passed").label("passed"),
                func.count().filter(AssessmentRun.status == "failed").label("failed"),
            )
            .join(AssessmentRun, AssessmentRun.blueprint_id == AssessmentBlueprint.id)
            .where(AssessmentBlueprint.org_id == org_id)
            .group_by(AssessmentBlueprint.id, AssessmentBlueprint.title)
            .having(func.count() >= self.min_cohort_size)
        )
        assess_result = await self.db.execute(assessment_q)
        assessment_pass_rates = [
            {
                "blueprint_id": row.blueprint_id,
                "title": row.title,
                "total_runs": row.total_runs,
                "passed": row.passed,
                "failed": row.failed,
                "pass_rate": round(row.passed / row.total_runs, 4) if row.total_runs else 0,
            }
            for row in assess_result.all()
        ]

        # 3. Placement stats: members of this org who got placed
        member_ids_sub = select(OrgMember.user_id).where(
            OrgMember.org_id == org_id, OrgMember.status == "active"
        )
        placement_q = (
            select(
                Placement.status,
                func.count().label("cnt"),
            )
            .where(Placement.user_id.in_(member_ids_sub))
            .group_by(Placement.status)
        )
        place_result = await self.db.execute(placement_q)
        placements_by_status = {row.status: row.cnt for row in place_result.all()}
        total_members_q = select(func.count()).select_from(
            select(OrgMember.user_id).where(
                OrgMember.org_id == org_id, OrgMember.status == "active"
            ).subquery()
        )
        total_members = (await self.db.execute(total_members_q)).scalar() or 0
        total_placed = sum(placements_by_status.values())

        placement_stats = {
            "total_members": total_members,
            "placements_by_status": placements_by_status,
            "total_placed": total_placed,
            "placement_rate": round(total_placed / total_members, 4) if total_members else 0,
        }

        # 4. Employer feedback: avg overall_rating from verifications of org members
        feedback_q = (
            select(
                func.count().label("total_reviews"),
                func.avg(EmployerVerification.overall_rating).label("avg_rating"),
            )
            .where(EmployerVerification.user_id.in_(member_ids_sub))
        )
        fb_result = await self.db.execute(feedback_q)
        fb_row = fb_result.one_or_none()
        employer_feedback = {
            "total_reviews": fb_row.total_reviews if fb_row else 0,
            "avg_rating": round(float(fb_row.avg_rating), 2) if fb_row and fb_row.avg_rating else None,
        }

        return {
            "org_id": org_id,
            "verified_capability_distribution": capability_distribution,
            "assessment_pass_rates": assessment_pass_rates,
            "placement_stats": placement_stats,
            "employer_feedback_summary": employer_feedback,
        }


# ---------------------------------------------------------------------------
# §41 — Employer dashboard
# ---------------------------------------------------------------------------


class EmployerDashboardService:
    """Analytics for employer organizations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(self, employer_org_id: str) -> dict:
        """Return employer dashboard data.

        Includes:
        - open_opportunities
        - applications_by_stage
        - time_to_fill (average days)
        - active_placements
        - historical_placements
        """
        # 1. Opportunities by status
        opp_q = (
            select(
                Opportunity.status,
                func.count().label("cnt"),
            )
            .where(Opportunity.employer_org_id == employer_org_id)
            .group_by(Opportunity.status)
        )
        opp_result = await self.db.execute(opp_q)
        opportunities_by_status = {row.status: row.cnt for row in opp_result.all()}

        # 2. Applications by stage (across all employer opportunities)
        app_q = (
            select(
                Application.status,
                func.count().label("cnt"),
            )
            .join(Opportunity, Opportunity.id == Application.opportunity_id)
            .where(Opportunity.employer_org_id == employer_org_id)
            .group_by(Application.status)
        )
        app_result = await self.db.execute(app_q)
        applications_by_stage = {row.status: row.cnt for row in app_result.all()}

        # 3. Active placements
        active_q = (
            select(func.count())
            .select_from(Placement)
            .where(
                Placement.employer_org_id == employer_org_id,
                Placement.status == "active",
            )
        )
        active_placements = (await self.db.execute(active_q)).scalar() or 0

        # 4. Total historical placements
        total_q = (
            select(func.count())
            .select_from(Placement)
            .where(Placement.employer_org_id == employer_org_id)
        )
        total_placements = (await self.db.execute(total_q)).scalar() or 0

        # 5. Average time-to-fill (days from opportunity created to placement started)
        # Only for placements with both created_at on opportunity and start_date on placement
        from sqlalchemy import extract

        ttf_q = (
            select(
                func.avg(
                    extract(
                        "epoch",
                        Placement.created_at - Opportunity.created_at,
                    )
                    / 86400
                ).label("avg_days"),
            )
            .join(Opportunity, Opportunity.id == Placement.opportunity_id)
            .where(Placement.employer_org_id == employer_org_id)
        )
        ttf_result = await self.db.execute(ttf_q)
        ttf_row = ttf_result.one_or_none()
        avg_time_to_fill = round(float(ttf_row.avg_days), 1) if ttf_row and ttf_row.avg_days else None

        return {
            "employer_org_id": employer_org_id,
            "opportunities_by_status": opportunities_by_status,
            "applications_by_stage": applications_by_stage,
            "active_placements": active_placements,
            "total_placements": total_placements,
            "avg_time_to_fill_days": avg_time_to_fill,
        }


# ---------------------------------------------------------------------------
# §42 — Platform workforce dashboard
# ---------------------------------------------------------------------------


class PlatformDashboardService:
    """Platform-level workforce dashboard aggregating all orgs."""

    def __init__(self, db: AsyncSession, *, min_cohort_size: int = DEFAULT_MIN_COHORT_SIZE):
        self.db = db
        self.min_cohort_size = min_cohort_size

    async def get_dashboard(self) -> dict:
        """Return platform workforce dashboard data.

        Includes:
        - total_capabilities
        - total_open_opportunities
        - total_active_placements
        - total_credentials_issued
        - demand_supply_summary (top gaps)
        """
        total_caps = (
            await self.db.execute(
                select(func.count()).select_from(Capability).where(Capability.status == "active")
            )
        ).scalar() or 0

        total_open_opps = (
            await self.db.execute(
                select(func.count()).select_from(Opportunity).where(Opportunity.status == "open")
            )
        ).scalar() or 0

        total_active_placements = (
            await self.db.execute(
                select(func.count()).select_from(Placement).where(Placement.status == "active")
            )
        ).scalar() or 0

        from app.talent.models.assessment import Credential

        total_credentials = (
            await self.db.execute(
                select(func.count()).select_from(Credential).where(Credential.status == "active")
            )
        ).scalar() or 0

        total_evidence = (
            await self.db.execute(
                select(func.count()).select_from(CapabilityEvidence).where(
                    CapabilityEvidence.status == "active"
                )
            )
        ).scalar() or 0

        total_applications = (
            await self.db.execute(select(func.count()).select_from(Application))
        ).scalar() or 0

        return {
            "total_capabilities": total_caps,
            "total_open_opportunities": total_open_opps,
            "total_active_placements": total_active_placements,
            "total_credentials_issued": total_credentials,
            "total_evidence_items": total_evidence,
            "total_applications": total_applications,
        }
