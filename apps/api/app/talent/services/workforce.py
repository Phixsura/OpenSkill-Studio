"""Workforce demand intelligence — aggregation, gap analysis, privacy thresholds (ADR-015 D11–D12).

Only aggregate data above safe minimum cohort sizes is returned.
Individual-level data is never exposed through these endpoints.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.application import Application, Placement
from app.talent.models.assessment import AssessmentRun
from app.talent.models.capability import Capability, CapabilityMapping
from app.talent.models.employer import Opportunity
from app.talent.models.evidence import CapabilityEvidence
from app.talent.models.passport import SkillPassport

# Default minimum cohort size — aggregates below this are suppressed
DEFAULT_MIN_COHORT_SIZE = 10

GAP_SEVERITY_THRESHOLDS = {"high": 0.5, "medium": 0.25}


@dataclass(frozen=True, slots=True)
class DemandSignal:
    capability_id: str
    capability_name: str
    category: str
    open_opportunities: int
    total_demand: int


@dataclass(frozen=True, slots=True)
class SupplySignal:
    capability_id: str
    capability_name: str
    category: str
    total_supply: int
    supply_by_level: dict[str, int]


@dataclass(frozen=True, slots=True)
class GapAnalysis:
    capability_id: str
    capability_name: str
    demand_count: int
    qualified_supply: int
    gap: int
    gap_severity: str
    content_coverage: dict[str, int]


class WorkforceIntelligenceService:
    def __init__(self, db: AsyncSession, *, min_cohort_size: int = DEFAULT_MIN_COHORT_SIZE):
        self.db = db
        self.min_cohort_size = min_cohort_size

    async def get_demand_signals(
        self,
        *,
        category: str | None = None,
        limit: int = 50,
    ) -> list[DemandSignal]:
        """Aggregate demand by capability from open opportunities."""
        # Count open opportunities per required capability
        # opportunities.required_capabilities is JSONB array of
        # [{"capability_id": "...", "min_level": N, "required": true}]
        q = text("""
            SELECT
                c.id AS capability_id,
                c.canonical_name,
                c.category,
                COUNT(DISTINCT o.id) AS open_opportunities
            FROM capabilities c
            JOIN opportunities o ON o.status = 'open'
            CROSS JOIN LATERAL jsonb_array_elements(o.required_capabilities) AS rc
            WHERE rc->>'capability_id' = c.id
              AND c.status = 'active'
              {category_filter}
            GROUP BY c.id, c.canonical_name, c.category
            HAVING COUNT(DISTINCT o.id) >= :min_cohort
            ORDER BY COUNT(DISTINCT o.id) DESC
            LIMIT :lim
        """.replace("{category_filter}", "AND c.category = :cat" if category else ""))

        params: dict = {"min_cohort": self.min_cohort_size, "lim": limit}
        if category:
            params["cat"] = category

        result = await self.db.execute(q, params)
        return [
            DemandSignal(
                capability_id=row.capability_id,
                capability_name=row.canonical_name,
                category=row.category,
                open_opportunities=row.open_opportunities,
                total_demand=row.open_opportunities,
            )
            for row in result.all()
        ]

    async def get_supply_signals(
        self,
        *,
        category: str | None = None,
        discoverable_only: bool = True,
        limit: int = 50,
    ) -> list[SupplySignal]:
        """Aggregate verified supply by capability.

        By default, only counts discoverable users (for employer-facing views).
        Set discoverable_only=False for school dashboards (own org members).
        """
        # Count users with active evidence per capability, grouped by level
        base_q = (
            select(
                Capability.id.label("capability_id"),
                Capability.canonical_name,
                Capability.category,
                func.count(func.distinct(CapabilityEvidence.user_id)).label("total_supply"),
            )
            .join(CapabilityEvidence, CapabilityEvidence.capability_id == Capability.id)
            .where(
                Capability.status == "active",
                CapabilityEvidence.status == "active",
            )
        )

        if discoverable_only:
            base_q = base_q.join(
                SkillPassport, SkillPassport.user_id == CapabilityEvidence.user_id
            ).where(
                SkillPassport.discoverable.is_(True),
            )

        if category:
            base_q = base_q.where(Capability.category == category)

        base_q = (
            base_q.group_by(Capability.id, Capability.canonical_name, Capability.category)
            .having(func.count(func.distinct(CapabilityEvidence.user_id)) >= self.min_cohort_size)
            .order_by(func.count(func.distinct(CapabilityEvidence.user_id)).desc())
            .limit(limit)
        )

        result = await self.db.execute(base_q)
        return [
            SupplySignal(
                capability_id=row.capability_id,
                capability_name=row.canonical_name,
                category=row.category,
                total_supply=row.total_supply,
                supply_by_level={},  # Level breakdown computed on demand
            )
            for row in result.all()
        ]

    async def get_gap_analysis(
        self,
        *,
        category: str | None = None,
        limit: int = 50,
    ) -> list[GapAnalysis]:
        """Compute demand-supply gaps per capability."""
        demand = await self.get_demand_signals(category=category, limit=100)
        supply = await self.get_supply_signals(category=category, limit=100)

        supply_map = {s.capability_id: s.total_supply for s in supply}

        # Get content coverage per capability
        coverage_q = (
            select(
                CapabilityMapping.capability_id,
                CapabilityMapping.source_type,
                func.count().label("cnt"),
            )
            .group_by(CapabilityMapping.capability_id, CapabilityMapping.source_type)
        )
        coverage_result = await self.db.execute(coverage_q)
        coverage_map: dict[str, dict[str, int]] = {}
        for row in coverage_result.all():
            if row.capability_id not in coverage_map:
                coverage_map[row.capability_id] = {}
            coverage_map[row.capability_id][row.source_type] = row.cnt

        gaps = []
        for d in demand:
            qualified = supply_map.get(d.capability_id, 0)
            gap = max(0, d.total_demand - qualified)
            ratio = gap / d.total_demand if d.total_demand > 0 else 0

            if ratio > GAP_SEVERITY_THRESHOLDS["high"]:
                severity = "high"
            elif ratio > GAP_SEVERITY_THRESHOLDS["medium"]:
                severity = "medium"
            else:
                severity = "low"

            gaps.append(
                GapAnalysis(
                    capability_id=d.capability_id,
                    capability_name=d.capability_name,
                    demand_count=d.total_demand,
                    qualified_supply=qualified,
                    gap=gap,
                    gap_severity=severity,
                    content_coverage=coverage_map.get(d.capability_id, {}),
                )
            )

        # Sort by gap severity then gap size
        severity_order = {"high": 0, "medium": 1, "low": 2}
        gaps.sort(key=lambda g: (severity_order.get(g.gap_severity, 3), -g.gap))
        return gaps[:limit]

    async def get_coverage_matrix(
        self,
        *,
        capability_id: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """Capability → content coverage matrix for curriculum intelligence."""
        q = (
            select(
                Capability.id.label("capability_id"),
                Capability.canonical_name,
                CapabilityMapping.source_type,
                CapabilityMapping.source_id,
                CapabilityMapping.contribution_weight,
            )
            .join(CapabilityMapping, CapabilityMapping.capability_id == Capability.id)
            .where(Capability.status == "active")
        )
        if capability_id:
            q = q.where(Capability.id == capability_id)

        q = q.order_by(Capability.canonical_name).limit(limit * 10)
        result = await self.db.execute(q)

        # Group by capability
        by_cap: dict[str, dict] = {}
        for row in result.all():
            cid = row.capability_id
            if cid not in by_cap:
                by_cap[cid] = {
                    "capability_id": cid,
                    "capability_name": row.canonical_name,
                    "content": [],
                    "coverage_by_type": {},
                }
            by_cap[cid]["content"].append({
                "source_type": row.source_type,
                "source_id": row.source_id,
                "weight": float(row.contribution_weight),
            })
            by_cap[cid]["coverage_by_type"][row.source_type] = (
                by_cap[cid]["coverage_by_type"].get(row.source_type, 0) + 1
            )

        return list(by_cap.values())[:limit]

    async def get_placement_analytics(
        self,
        *,
        employer_org_id: str | None = None,
        limit: int = 50,
    ) -> dict:
        """Placement funnel analytics."""
        # Application counts by status
        app_q = select(
            Application.status,
            func.count().label("cnt"),
        ).group_by(Application.status)
        if employer_org_id:
            app_q = app_q.join(
                Opportunity, Opportunity.id == Application.opportunity_id
            ).where(Opportunity.employer_org_id == employer_org_id)

        app_result = await self.db.execute(app_q)
        app_by_status = {row.status: row.cnt for row in app_result.all()}

        # Placement counts by status
        place_q = select(
            Placement.status,
            func.count().label("cnt"),
        ).group_by(Placement.status)
        if employer_org_id:
            place_q = place_q.where(Placement.employer_org_id == employer_org_id)

        place_result = await self.db.execute(place_q)
        placements_by_status = {row.status: row.cnt for row in place_result.all()}

        return {
            "applications_by_status": app_by_status,
            "placements_by_status": placements_by_status,
            "total_applications": sum(app_by_status.values()),
            "total_placements": sum(placements_by_status.values()),
        }

    # ------------------------------------------------------------------
    # §36 — Outcome-based curriculum analytics
    # ------------------------------------------------------------------

    async def get_outcome_analytics(
        self,
        *,
        capability_id: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """Connect learning content to downstream outcomes (§36).

        Returns observed associations (not causal claims):
        - Evidence source type → assessment pass rate
        - Evidence source type → placement rate
        - Evidence source type → employer verification rate

        Only rows where evidence_count >= min_cohort_size are returned.
        """
        # Per capability × source_type: count distinct users with evidence
        ev_base = (
            select(
                CapabilityEvidence.capability_id,
                Capability.canonical_name.label("capability_name"),
                CapabilityEvidence.source_type,
                func.count(func.distinct(CapabilityEvidence.user_id)).label("evidence_count"),
            )
            .join(Capability, Capability.id == CapabilityEvidence.capability_id)
            .where(
                CapabilityEvidence.status == "active",
                Capability.status == "active",
            )
        )
        if capability_id:
            ev_base = ev_base.where(CapabilityEvidence.capability_id == capability_id)
        ev_base = (
            ev_base.group_by(
                CapabilityEvidence.capability_id,
                Capability.canonical_name,
                CapabilityEvidence.source_type,
            )
            .having(func.count(func.distinct(CapabilityEvidence.user_id)) >= self.min_cohort_size)
        )

        ev_result = await self.db.execute(ev_base)
        groups = [
            {
                "capability_id": row.capability_id,
                "capability_name": row.capability_name,
                "source_type": row.source_type,
                "evidence_count": row.evidence_count,
            }
            for row in ev_result.all()
        ]

        if not groups:
            return []

        # For each group, compute downstream rates
        results = []
        for g in groups:
            cid = g["capability_id"]
            stype = g["source_type"]
            total_users = g["evidence_count"]

            # Users with this evidence who ALSO passed an assessment for same cap
            passed_q = (
                select(func.count(func.distinct(AssessmentRun.user_id)))
                .where(
                    AssessmentRun.status == "passed",
                    AssessmentRun.user_id.in_(
                        select(CapabilityEvidence.user_id).where(
                            CapabilityEvidence.capability_id == cid,
                            CapabilityEvidence.source_type == stype,
                            CapabilityEvidence.status == "active",
                        )
                    ),
                )
            )
            passed_count = (await self.db.execute(passed_q)).scalar() or 0

            # Users with this evidence who got placed
            placed_q = (
                select(func.count(func.distinct(Placement.user_id)))
                .where(
                    Placement.user_id.in_(
                        select(CapabilityEvidence.user_id).where(
                            CapabilityEvidence.capability_id == cid,
                            CapabilityEvidence.source_type == stype,
                            CapabilityEvidence.status == "active",
                        )
                    ),
                )
            )
            placed_count = (await self.db.execute(placed_q)).scalar() or 0

            # Users who received employer_verified evidence for same cap
            emp_ver_q = (
                select(func.count(func.distinct(CapabilityEvidence.user_id)))
                .where(
                    CapabilityEvidence.capability_id == cid,
                    CapabilityEvidence.verification_level == "employer_verified",
                    CapabilityEvidence.status == "active",
                    CapabilityEvidence.user_id.in_(
                        select(CapabilityEvidence.user_id).where(
                            CapabilityEvidence.capability_id == cid,
                            CapabilityEvidence.source_type == stype,
                            CapabilityEvidence.status == "active",
                        )
                    ),
                )
            )
            emp_ver_count = (await self.db.execute(emp_ver_q)).scalar() or 0

            results.append({
                "capability_id": cid,
                "capability_name": g["capability_name"],
                "source_type": stype,
                "evidence_count": total_users,
                "assessment_pass_rate": round(passed_count / total_users, 4) if total_users else 0,
                "placement_rate": round(placed_count / total_users, 4) if total_users else 0,
                "employer_verification_rate": round(emp_ver_count / total_users, 4) if total_users else 0,
            })

        results.sort(key=lambda r: -r["evidence_count"])
        return results[:limit]

    # ------------------------------------------------------------------
    # §37 — Content improvement recommendations
    # ------------------------------------------------------------------

    async def get_recommendations(
        self,
        *,
        limit: int = 20,
    ) -> list[dict]:
        """Generate curriculum improvement recommendations (§37).

        Recommendations are signals, not actions. All require human
        confirmation before any content changes.
        """
        gaps = await self.get_gap_analysis(limit=100)
        coverage_rows = await self.get_coverage_matrix(limit=200)
        coverage_map = {c["capability_id"]: c.get("coverage_by_type", {}) for c in coverage_rows}

        # Outcome analytics for employer verification rate (if available)
        outcome_rows = await self.get_outcome_analytics(limit=200)
        emp_ver_by_cap: dict[str, float] = {}
        for o in outcome_rows:
            cid = o["capability_id"]
            rate = o["employer_verification_rate"]
            # Keep worst rate per capability for recommendation trigger
            if cid not in emp_ver_by_cap or rate < emp_ver_by_cap[cid]:
                emp_ver_by_cap[cid] = rate

        recommendations: list[dict] = []

        for gap in gaps:
            cid = gap.capability_id
            cname = gap.capability_name
            cov = coverage_map.get(cid, {})

            # Missing assessment → recommend creating one
            if not cov.get("assessment_blueprint"):
                recommendations.append({
                    "recommendation_type": "add_assessment",
                    "capability_id": cid,
                    "capability_name": cname,
                    "reason": f"High demand ({gap.demand_count} opportunities) but no standardized assessment exists",
                    "suggested_action": f"Create a practical assessment blueprint for {cname}",
                    "confidence": "high" if gap.gap_severity == "high" else "medium",
                    "requires_confirmation": True,
                })

            # Missing project template
            if not cov.get("project_template"):
                recommendations.append({
                    "recommendation_type": "add_project_template",
                    "capability_id": cid,
                    "capability_name": cname,
                    "reason": f"No project template maps to {cname}; learners lack hands-on practice",
                    "suggested_action": f"Create an advanced project template for {cname}",
                    "confidence": "medium",
                    "requires_confirmation": True,
                })

            # High demand, low supply → increase capacity
            if gap.gap_severity == "high":
                recommendations.append({
                    "recommendation_type": "increase_training_capacity",
                    "capability_id": cid,
                    "capability_name": cname,
                    "reason": f"Supply-demand gap is severe: {gap.gap} unfilled out of {gap.demand_count} demand",
                    "suggested_action": f"Add more Skill Packs or Learning Paths covering {cname}",
                    "confidence": "high",
                    "requires_confirmation": True,
                })

            # Low employer verification rate → improve practical alignment
            emp_rate = emp_ver_by_cap.get(cid, 1.0)
            if emp_rate < 0.3 and gap.demand_count > 0:
                recommendations.append({
                    "recommendation_type": "improve_practical_alignment",
                    "capability_id": cid,
                    "capability_name": cname,
                    "reason": (
                        f"Employer verification rate is low ({emp_rate:.0%}); "
                        "training may not align with real-world expectations"
                    ),
                    "suggested_action": f"Review rubrics and project briefs for {cname} against employer feedback",
                    "confidence": "medium",
                    "requires_confirmation": True,
                })

        return recommendations[:limit]
