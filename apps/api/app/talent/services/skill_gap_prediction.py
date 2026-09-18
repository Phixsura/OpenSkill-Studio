"""Skill gap prediction — forecast future skill needs using demand trends.

Features:
  - Predict which skills will be in demand in 3/6/12 months
  - Identify emerging skill gaps before they become critical
  - Recommend proactive learning investments
  - Time-to-gap-closure estimation
  - Skill supply forecasting from current learner pipelines
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SkillGapForecast:
    capability_id: str
    capability_name: str
    current_demand: int
    current_supply: int
    current_gap: int
    predicted_demand_3m: int
    predicted_demand_6m: int
    predicted_demand_12m: int
    predicted_gap_3m: int
    predicted_gap_6m: int
    predicted_gap_12m: int
    urgency: str  # critical, high, medium, low
    recommended_action: str


@dataclass(frozen=True, slots=True)
class SupplyForecast:
    capability_id: str
    capability_name: str
    current_supply: int
    learners_in_pipeline: int  # users with evidence but below threshold
    estimated_graduates_3m: int
    estimated_graduates_6m: int
    supply_growth_rate: float


@dataclass(frozen=True, slots=True)
class TimeToClosureEstimate:
    capability_id: str
    capability_name: str
    current_gap: int
    monthly_supply_growth: float
    estimated_months_to_close: float | None  # None if gap is growing
    feasible: bool


class SkillGapPredictionService:
    def forecast_demand(
        self,
        *,
        current_demand: int,
        growth_rate_90d: float,  # from skill_trends
    ) -> tuple[int, int, int]:
        """Forecast demand at 3, 6, 12 months using growth rate."""
        monthly_rate = growth_rate_90d / 3.0

        d3 = max(0, round(current_demand * (1 + monthly_rate * 3)))
        d6 = max(0, round(current_demand * (1 + monthly_rate * 6)))
        d12 = max(0, round(current_demand * (1 + monthly_rate * 12)))
        return d3, d6, d12

    def forecast_supply(
        self,
        *,
        capability_id: str,
        capability_name: str,
        current_supply: int,
        learners_below_threshold: int,
        avg_months_to_qualify: float,
    ) -> SupplyForecast:
        """Forecast supply growth from learner pipeline."""
        if avg_months_to_qualify <= 0:
            monthly_graduates = 0.0
        else:
            monthly_graduates = learners_below_threshold / avg_months_to_qualify

        return SupplyForecast(
            capability_id=capability_id,
            capability_name=capability_name,
            current_supply=current_supply,
            learners_in_pipeline=learners_below_threshold,
            estimated_graduates_3m=round(monthly_graduates * 3),
            estimated_graduates_6m=round(monthly_graduates * 6),
            supply_growth_rate=round(monthly_graduates / max(current_supply, 1), 3),
        )

    def estimate_time_to_closure(
        self,
        *,
        capability_id: str,
        capability_name: str,
        current_gap: int,
        monthly_supply_growth: float,
        monthly_demand_growth: float,
    ) -> TimeToClosureEstimate:
        """Estimate how long until a skill gap closes."""
        net_monthly_closure = monthly_supply_growth - monthly_demand_growth

        if net_monthly_closure <= 0:
            return TimeToClosureEstimate(
                capability_id=capability_id,
                capability_name=capability_name,
                current_gap=current_gap,
                monthly_supply_growth=monthly_supply_growth,
                estimated_months_to_close=None,
                feasible=False,
            )

        months = current_gap / net_monthly_closure
        return TimeToClosureEstimate(
            capability_id=capability_id,
            capability_name=capability_name,
            current_gap=current_gap,
            monthly_supply_growth=monthly_supply_growth,
            estimated_months_to_close=round(months, 1),
            feasible=True,
        )

    def build_forecast(
        self,
        *,
        capability_id: str,
        capability_name: str,
        current_demand: int,
        current_supply: int,
        growth_rate_90d: float,
        supply_growth_monthly: float,
    ) -> SkillGapForecast:
        """Build complete gap forecast."""
        current_gap = max(0, current_demand - current_supply)
        d3, d6, d12 = self.forecast_demand(
            current_demand=current_demand, growth_rate_90d=growth_rate_90d,
        )
        # Assume supply grows linearly
        s3 = round(current_supply + supply_growth_monthly * 3)
        s6 = round(current_supply + supply_growth_monthly * 6)
        s12 = round(current_supply + supply_growth_monthly * 12)

        gap3 = max(0, d3 - s3)
        gap6 = max(0, d6 - s6)
        gap12 = max(0, d12 - s12)

        # Urgency
        if gap3 > current_gap * 1.5:
            urgency = "critical"
            action = "Immediate investment in training programs required"
        elif gap6 > current_gap:
            urgency = "high"
            action = "Start new learning pathways within 1-2 months"
        elif gap12 > current_gap:
            urgency = "medium"
            action = "Plan curriculum additions for next quarter"
        else:
            urgency = "low"
            action = "Monitor trends; gap is stable or closing"

        return SkillGapForecast(
            capability_id=capability_id,
            capability_name=capability_name,
            current_demand=current_demand,
            current_supply=current_supply,
            current_gap=current_gap,
            predicted_demand_3m=d3,
            predicted_demand_6m=d6,
            predicted_demand_12m=d12,
            predicted_gap_3m=gap3,
            predicted_gap_6m=gap6,
            predicted_gap_12m=gap12,
            urgency=urgency,
            recommended_action=action,
        )
