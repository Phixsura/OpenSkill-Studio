"""Skill trending and obsolescence detection (ADR-015 world-class upgrade I7).

Analyzes evidence creation patterns over time windows to identify:
  - rising   — accelerating evidence creation (growth_rate > 0.2)
  - stable   — consistent evidence creation (-0.2 ≤ growth_rate ≤ 0.2)
  - cooling  — declining evidence creation (growth_rate < -0.2)
  - emerging — new skill, small but fast-growing (total < 10, recent > 0)

Uses 90-day rolling windows: current vs prior period.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.capability import Capability
from app.talent.models.employer import Opportunity
from app.talent.models.evidence import CapabilityEvidence


@dataclass(frozen=True, slots=True)
class SkillTrend:
    """Trend analysis for a single capability."""

    capability_id: str
    capability_name: str
    category: str
    trend_direction: str  # rising, stable, cooling, emerging
    current_period_count: int  # evidence created in last 90 days
    prior_period_count: int  # evidence created in prior 90 days
    growth_rate: float  # (current - prior) / max(prior, 1)
    demand_count: int  # open opportunities requiring this skill
    supply_count: int  # distinct users with active evidence


TREND_WINDOW_DAYS = 90


def _classify_trend(
    current: int, prior: int, total_all_time: int
) -> tuple[str, float]:
    """Classify trend direction and compute growth rate."""
    if prior == 0 and current == 0:
        return "stable", 0.0

    growth = (current - prior) / max(prior, 1)

    if total_all_time < 10 and current > 0:
        return "emerging", round(growth, 3)
    if growth > 0.2:
        return "rising", round(growth, 3)
    if growth < -0.2:
        return "cooling", round(growth, 3)
    return "stable", round(growth, 3)


async def compute_skill_trends(
    db: AsyncSession,
    *,
    direction: str | None = None,
    category: str | None = None,
    limit: int = 50,
) -> list[SkillTrend]:
    """Compute skill trends across the platform.

    Args:
        direction: Filter by trend direction (rising/stable/cooling/emerging)
        category: Filter by capability category
        limit: Max results
    """
    now = datetime.now(UTC)
    current_start = now - timedelta(days=TREND_WINDOW_DAYS)
    prior_start = now - timedelta(days=TREND_WINDOW_DAYS * 2)

    # Load active capabilities
    cap_q = select(Capability).where(Capability.status == "active")
    if category:
        cap_q = cap_q.where(Capability.category == category)
    cap_result = await db.execute(cap_q)
    capabilities = {c.id: c for c in cap_result.scalars().all()}

    if not capabilities:
        return []

    cap_ids = list(capabilities.keys())

    # Batch query: evidence counts per capability per time window
    # Current period
    current_q = (
        select(
            CapabilityEvidence.capability_id,
            func.count(CapabilityEvidence.id).label("cnt"),
        )
        .where(
            CapabilityEvidence.capability_id.in_(cap_ids),
            CapabilityEvidence.status == "active",
            CapabilityEvidence.created_at >= current_start,
        )
        .group_by(CapabilityEvidence.capability_id)
    )
    current_result = await db.execute(current_q)
    current_counts = dict(current_result.all())

    # Prior period
    prior_q = (
        select(
            CapabilityEvidence.capability_id,
            func.count(CapabilityEvidence.id).label("cnt"),
        )
        .where(
            CapabilityEvidence.capability_id.in_(cap_ids),
            CapabilityEvidence.status == "active",
            CapabilityEvidence.created_at >= prior_start,
            CapabilityEvidence.created_at < current_start,
        )
        .group_by(CapabilityEvidence.capability_id)
    )
    prior_result = await db.execute(prior_q)
    prior_counts = dict(prior_result.all())

    # All-time counts
    total_q = (
        select(
            CapabilityEvidence.capability_id,
            func.count(CapabilityEvidence.id).label("cnt"),
        )
        .where(
            CapabilityEvidence.capability_id.in_(cap_ids),
            CapabilityEvidence.status == "active",
        )
        .group_by(CapabilityEvidence.capability_id)
    )
    total_result = await db.execute(total_q)
    total_counts = dict(total_result.all())

    # Supply: distinct users with evidence per capability
    supply_q = (
        select(
            CapabilityEvidence.capability_id,
            func.count(func.distinct(CapabilityEvidence.user_id)).label("cnt"),
        )
        .where(
            CapabilityEvidence.capability_id.in_(cap_ids),
            CapabilityEvidence.status == "active",
        )
        .group_by(CapabilityEvidence.capability_id)
    )
    supply_result = await db.execute(supply_q)
    supply_counts = dict(supply_result.all())

    # Demand: count open opportunities requiring each capability
    # This requires searching the JSONB required_capabilities array
    demand_q = (
        select(Opportunity)
        .where(Opportunity.status == "open")
    )
    demand_result = await db.execute(demand_q)
    demand_counts: dict[str, int] = {}
    for opp in demand_result.scalars().all():
        for req in (opp.required_capabilities or []):
            cid = req.get("capability_id", "")
            if cid in capabilities:
                demand_counts[cid] = demand_counts.get(cid, 0) + 1

    # Build trends
    trends: list[SkillTrend] = []
    for cap_id, cap in capabilities.items():
        current = current_counts.get(cap_id, 0)
        prior = prior_counts.get(cap_id, 0)
        total = total_counts.get(cap_id, 0)

        trend_dir, growth = _classify_trend(current, prior, total)

        # Apply direction filter
        if direction and trend_dir != direction:
            continue

        trends.append(SkillTrend(
            capability_id=cap_id,
            capability_name=cap.canonical_name,
            category=cap.category,
            trend_direction=trend_dir,
            current_period_count=current,
            prior_period_count=prior,
            growth_rate=growth,
            demand_count=demand_counts.get(cap_id, 0),
            supply_count=supply_counts.get(cap_id, 0),
        ))

    # Sort: rising first, then by growth rate descending
    direction_order = {"rising": 0, "emerging": 1, "stable": 2, "cooling": 3}
    trends.sort(key=lambda t: (direction_order.get(t.trend_direction, 9), -t.growth_rate))
    return trends[:limit]
