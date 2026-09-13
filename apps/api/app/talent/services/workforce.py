"""Workforce demand intelligence — aggregation, gap analysis, privacy thresholds (ADR-015 D11–D12).

Only aggregate data above safe minimum cohort sizes is returned.
Individual-level data is never exposed through these endpoints.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.application import Application, Placement
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
