"""Candidate-side application analytics (N14).

Gives job seekers insight into their application performance:
- Application success rate
- Average time to first response
- Most common rejection stage
- Response rate (applications that moved past submitted)
- Active applications count
- Breakdown by status and opportunity type
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.application import (
    Application,
    ApplicationEvent,
)

# Statuses that mean "still waiting" (no employer action yet)
_PENDING_STATUSES = frozenset({"submitted"})
# Statuses that mean "active" (in progress)
_ACTIVE_STATUSES = frozenset(
    {"submitted", "screening", "interview", "assessment", "offer"}
)
# Statuses that mean "terminal"
_TERMINAL_STATUSES = frozenset(
    {"accepted", "rejected", "withdrawn", "hired", "completed"}
)


@dataclass(frozen=True, slots=True)
class CandidateApplicationStats:
    """Aggregate application statistics for a candidate."""

    total_applications: int
    active_applications: int
    offers_received: int
    placements: int
    success_rate: float  # offers / total (where total > 0)
    response_rate: float  # (total - still_submitted) / total
    avg_days_to_response: float | None
    most_common_rejection_stage: str | None
    applications_by_status: dict[str, int]
    applications_by_type: dict[str, int]


class CandidateAnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_stats(self, user_id: str) -> CandidateApplicationStats:
        """Compute application analytics for a candidate."""
        # Load all applications
        q = select(Application).where(Application.user_id == user_id)
        result = await self.db.execute(q)
        applications = list(result.scalars().all())

        if not applications:
            return CandidateApplicationStats(
                total_applications=0,
                active_applications=0,
                offers_received=0,
                placements=0,
                success_rate=0.0,
                response_rate=0.0,
                avg_days_to_response=None,
                most_common_rejection_stage=None,
                applications_by_status={},
                applications_by_type={},
            )

        total = len(applications)

        # Count by status
        status_counts: dict[str, int] = Counter()
        type_counts: dict[str, int] = Counter()
        active = 0
        offers = 0
        placements = 0
        still_submitted = 0
        rejection_from_stages: list[str] = []

        for app in applications:
            status_counts[app.status] += 1

            if app.status in _ACTIVE_STATUSES:
                active += 1
            if app.status in ("offer", "accepted", "hired", "completed"):
                offers += 1
            if app.status in ("hired", "completed"):
                placements += 1
            if app.status in _PENDING_STATUSES:
                still_submitted += 1

        # Load events for time-to-response and rejection stage analysis
        app_ids = [a.id for a in applications]
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

        # Compute avg time to first response (first transition from submitted)
        response_days: list[float] = []
        for app in applications:
            app_events = events_by_app.get(app.id, [])
            # Find the first non-submitted transition
            submit_time = None
            first_response_time = None
            for ev in app_events:
                if ev.from_status == "draft" and ev.to_status == "submitted":
                    submit_time = ev.created_at
                elif submit_time and ev.from_status == "submitted":
                    first_response_time = ev.created_at
                    break
            if submit_time and first_response_time:
                delta = (first_response_time - submit_time).total_seconds() / 86400
                response_days.append(delta)

            # Track rejection stages
            if app.status == "rejected":
                for ev in reversed(app_events):
                    if ev.to_status == "rejected":
                        rejection_from_stages.append(ev.from_status)
                        break

        avg_response = (
            round(sum(response_days) / len(response_days), 1)
            if response_days
            else None
        )

        # Most common rejection stage
        rejection_counter = Counter(rejection_from_stages)
        most_common_rejection = (
            rejection_counter.most_common(1)[0][0]
            if rejection_counter
            else None
        )

        success_rate = offers / total if total > 0 else 0.0
        response_rate = (total - still_submitted) / total if total > 0 else 0.0

        return CandidateApplicationStats(
            total_applications=total,
            active_applications=active,
            offers_received=offers,
            placements=placements,
            success_rate=round(success_rate, 3),
            response_rate=round(response_rate, 3),
            avg_days_to_response=avg_response,
            most_common_rejection_stage=most_common_rejection,
            applications_by_status=dict(status_counts),
            applications_by_type=dict(type_counts),
        )
