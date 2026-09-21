"""Market insights — compensation benchmarks, skill market value, employer reputation.

Features:
  - Skill market value estimation (demand × scarcity)
  - Compensation band analytics (aggregated, privacy-safe)
  - Employer reputation scoring (from placements, verifications, feedback)
  - Industry-level trend reports
  - Skill ROI estimation (learning cost vs salary uplift)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SkillMarketValue:
    """Market value signal for a capability."""

    capability_id: str
    capability_name: str
    demand_index: float  # 0-100
    scarcity_index: float  # 0-100 (higher = rarer)
    market_value_score: float  # 0-100 composite
    trend: str  # rising, stable, declining
    avg_opportunity_count: int
    qualified_supply: int


@dataclass(frozen=True, slots=True)
class CompensationBenchmark:
    """Aggregated compensation data (privacy-safe, min cohort enforced)."""

    opportunity_type: str
    capability_category: str
    sample_size: int
    min_display: str | None  # only shown if sample >= 10
    max_display: str | None
    median_display: str | None
    suppressed: bool  # True if sample too small


@dataclass(frozen=True, slots=True)
class EmployerReputation:
    """Employer reputation from platform activity."""

    org_id: str
    total_placements: int
    avg_placement_duration_days: float | None
    verification_rate: float  # % of placements with employer verification
    candidate_return_rate: float  # % of candidates who'd work there again (from feedback)
    response_time_hours: float | None  # avg time to first application response
    reputation_score: float  # 0-100


@dataclass(frozen=True, slots=True)
class SkillROI:
    """Estimated return on investment for learning a skill."""

    capability_id: str
    capability_name: str
    demand_uplift: float  # how much demand increases with this skill
    avg_learning_weeks: float | None
    opportunity_unlock_count: int  # how many more opportunities become available
    roi_rating: str  # high, medium, low


class MarketInsightsService:
    def compute_market_value(
        self,
        demand_count: int,
        supply_count: int,
        trend_direction: str,
    ) -> SkillMarketValue:
        """Compute market value from demand/supply signals."""
        max(demand_count, 1)
        demand_index = min(demand_count / 10.0 * 100, 100)

        scarcity = 100 * (1 - min(supply_count / max(demand_count, 1), 1.0))
        scarcity_index = max(0, min(scarcity, 100))

        # Composite: 60% demand + 40% scarcity
        composite = 0.6 * demand_index + 0.4 * scarcity_index

        return SkillMarketValue(
            capability_id="",
            capability_name="",
            demand_index=round(demand_index, 1),
            scarcity_index=round(scarcity_index, 1),
            market_value_score=round(composite, 1),
            trend=trend_direction,
            avg_opportunity_count=demand_count,
            qualified_supply=supply_count,
        )

    def compute_compensation_benchmark(
        self,
        opportunity_type: str,
        category: str,
        compensation_values: list[str],
        min_cohort: int = 10,
    ) -> CompensationBenchmark:
        """Compute aggregated compensation benchmark."""
        if len(compensation_values) < min_cohort:
            return CompensationBenchmark(
                opportunity_type=opportunity_type,
                capability_category=category,
                sample_size=len(compensation_values),
                min_display=None,
                max_display=None,
                median_display=None,
                suppressed=True,
            )

        # Sort for percentiles (treating as strings for display)
        sorted_vals = sorted(compensation_values)
        mid = len(sorted_vals) // 2
        return CompensationBenchmark(
            opportunity_type=opportunity_type,
            capability_category=category,
            sample_size=len(sorted_vals),
            min_display=sorted_vals[0],
            max_display=sorted_vals[-1],
            median_display=sorted_vals[mid],
            suppressed=False,
        )

    def compute_employer_reputation(
        self,
        *,
        org_id: str,
        total_placements: int,
        verified_placements: int,
        avg_duration_days: float | None,
        return_candidates: int,
        total_feedback: int,
        avg_response_hours: float | None,
    ) -> EmployerReputation:
        """Compute employer reputation score."""
        ver_rate = verified_placements / max(total_placements, 1)
        return_rate = return_candidates / max(total_feedback, 1)

        # Weighted reputation: 30% verification + 25% return + 25% volume + 20% response
        vol_score = min(total_placements / 20.0, 1.0) * 100
        resp_score = max(0, 100 - (avg_response_hours or 48)) if avg_response_hours else 50

        reputation = (
            0.30 * ver_rate * 100 + 0.25 * return_rate * 100 + 0.25 * vol_score + 0.20 * resp_score
        )

        return EmployerReputation(
            org_id=org_id,
            total_placements=total_placements,
            avg_placement_duration_days=avg_duration_days,
            verification_rate=round(ver_rate, 3),
            candidate_return_rate=round(return_rate, 3),
            response_time_hours=avg_response_hours,
            reputation_score=round(min(reputation, 100), 1),
        )

    def compute_skill_roi(
        self,
        *,
        capability_id: str,
        capability_name: str,
        current_opportunities: int,
        opportunities_with_skill: int,
        avg_learning_weeks: float | None,
    ) -> SkillROI:
        """Estimate ROI of learning a skill."""
        unlock = max(0, opportunities_with_skill - current_opportunities)
        demand_uplift = unlock / max(current_opportunities, 1)

        if demand_uplift > 0.5:
            rating = "high"
        elif demand_uplift > 0.2:
            rating = "medium"
        else:
            rating = "low"

        return SkillROI(
            capability_id=capability_id,
            capability_name=capability_name,
            demand_uplift=round(demand_uplift, 3),
            avg_learning_weeks=avg_learning_weeks,
            opportunity_unlock_count=unlock,
            roi_rating=rating,
        )
