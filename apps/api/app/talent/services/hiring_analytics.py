"""Hiring funnel analytics — time-to-hire, conversion rates, pipeline velocity.

Computes enterprise hiring metrics from ApplicationEvent transition data:
  - Time-to-hire (avg/median days from submission to hire)
  - Per-stage conversion rates
  - Per-stage average duration
  - Offer acceptance rate
  - Pipeline velocity (hires per month)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from statistics import median

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.application import Application, ApplicationEvent
from app.talent.models.employer import Opportunity

# Pipeline stages in order
PIPELINE_STAGES = [
    "submitted",
    "screening",
    "interview",
    "assessment",
    "offer",
    "hired",
]


@dataclass(frozen=True, slots=True)
class HiringAnalytics:
    """Hiring funnel metrics for an organization."""

    avg_time_to_hire_days: float | None
    median_time_to_hire_days: float | None
    stage_conversion_rates: dict[str, float]
    avg_time_in_stage: dict[str, float]
    offer_acceptance_rate: float | None
    total_applications: int
    total_hires: int
    total_offers: int
    pipeline_velocity: float | None  # hires per month


class HiringAnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def compute(
        self,
        org_id: str,
        *,
        days_back: int = 90,
    ) -> HiringAnalytics:
        """Compute hiring analytics for an employer org.

        Args:
            org_id: Employer organization ID
            days_back: Look-back window in days (default 90)

        Returns:
            HiringAnalytics with time metrics and conversion rates.
        """
        cutoff = datetime.now(UTC) - timedelta(days=days_back)

        # Get all opportunities for this org
        opp_q = select(Opportunity.id).where(
            Opportunity.employer_org_id == org_id,
        )
        opp_result = await self.db.execute(opp_q)
        opp_ids = [row[0] for row in opp_result.all()]

        if not opp_ids:
            return self._empty_analytics()

        # Get all applications for these opportunities within the window
        app_q = select(Application).where(
            Application.opportunity_id.in_(opp_ids),
            Application.created_at >= cutoff,
        )
        app_result = await self.db.execute(app_q)
        applications = list(app_result.scalars().all())
        total_applications = len(applications)

        if total_applications == 0:
            return self._empty_analytics()

        app_ids = [a.id for a in applications]

        # Get all events for these applications
        event_q = (
            select(ApplicationEvent)
            .where(ApplicationEvent.application_id.in_(app_ids))
            .order_by(ApplicationEvent.created_at)
        )
        event_result = await self.db.execute(event_q)
        events = list(event_result.scalars().all())

        # Group events by application
        events_by_app: dict[str, list[ApplicationEvent]] = {}
        for ev in events:
            events_by_app.setdefault(ev.application_id, []).append(ev)

        # Compute time-to-hire
        hire_times: list[float] = []
        for app in applications:
            app_events = events_by_app.get(app.id, [])
            hire_event = next(
                (e for e in app_events if e.to_status == "hired"),
                None,
            )
            if hire_event and hire_event.created_at and app.created_at:
                days = (hire_event.created_at - app.created_at).total_seconds() / 86400
                hire_times.append(days)

        avg_tth = sum(hire_times) / len(hire_times) if hire_times else None
        median_tth = median(hire_times) if hire_times else None

        # Count applications reaching each stage
        stage_counts: dict[str, int] = {s: 0 for s in PIPELINE_STAGES}
        stage_times: dict[str, list[float]] = {s: [] for s in PIPELINE_STAGES}

        for app in applications:
            app_events = events_by_app.get(app.id, [])
            reached_stages: dict[str, datetime] = {}

            # Track which stages were reached and when
            for ev in app_events:
                if ev.to_status in stage_counts and ev.to_status not in reached_stages:
                    stage_counts[ev.to_status] += 1
                    if ev.created_at:
                        reached_stages[ev.to_status] = ev.created_at

            # Compute time between consecutive stages
            sorted_stages = sorted(reached_stages.items(), key=lambda x: x[1])
            for i in range(1, len(sorted_stages)):
                stage_name = sorted_stages[i][0]
                prev_time = sorted_stages[i - 1][1]
                curr_time = sorted_stages[i][1]
                days = (curr_time - prev_time).total_seconds() / 86400
                stage_times[stage_name].append(days)

        # All submitted applications count
        stage_counts["submitted"] = max(stage_counts["submitted"], total_applications)

        # Conversion rates between consecutive stages
        conversion_rates: dict[str, float] = {}
        for i in range(1, len(PIPELINE_STAGES)):
            prev = PIPELINE_STAGES[i - 1]
            curr = PIPELINE_STAGES[i]
            key = f"{prev}→{curr}"
            if stage_counts[prev] > 0:
                conversion_rates[key] = round(
                    stage_counts[curr] / stage_counts[prev], 4
                )
            else:
                conversion_rates[key] = 0.0

        # Average time in each stage
        avg_stage_time: dict[str, float] = {}
        for stage, times in stage_times.items():
            if times:
                avg_stage_time[stage] = round(sum(times) / len(times), 2)

        # Offer acceptance
        total_offers = stage_counts.get("offer", 0)
        total_hires = stage_counts.get("hired", 0)
        offer_acceptance = (
            round(total_hires / total_offers, 4) if total_offers > 0 else None
        )

        # Pipeline velocity: hires per month
        velocity = None
        if total_hires > 0 and days_back > 0:
            months = days_back / 30.0
            velocity = round(total_hires / months, 2)

        return HiringAnalytics(
            avg_time_to_hire_days=round(avg_tth, 2) if avg_tth is not None else None,
            median_time_to_hire_days=round(median_tth, 2) if median_tth is not None else None,
            stage_conversion_rates=conversion_rates,
            avg_time_in_stage=avg_stage_time,
            offer_acceptance_rate=offer_acceptance,
            total_applications=total_applications,
            total_hires=total_hires,
            total_offers=total_offers,
            pipeline_velocity=velocity,
        )

    @staticmethod
    def _empty_analytics() -> HiringAnalytics:
        return HiringAnalytics(
            avg_time_to_hire_days=None,
            median_time_to_hire_days=None,
            stage_conversion_rates={},
            avg_time_in_stage={},
            offer_acceptance_rate=None,
            total_applications=0,
            total_hires=0,
            total_offers=0,
            pipeline_velocity=None,
        )
