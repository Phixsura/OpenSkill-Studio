"""Personalized opportunity recommendation feed (N19).

Combines multiple signals to produce a ranked feed of opportunities
tailored to each user:
  1. Capability match — how well user's skills fit required capabilities
  2. Type preference — from passport preferred_opportunity_types
  3. Goal alignment — boosts opportunities aligned with career goals
  4. Recency — newer opportunities ranked higher
  5. Engagement — bookmarked similar opportunities boost score
  6. Already applied — excluded from results

Signal weights:
  capability_match  0.40
  type_preference   0.15
  goal_alignment    0.20
  recency           0.15
  engagement        0.10
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.application import Application
from app.talent.models.bookmark import OpportunityBookmark
from app.talent.models.career_goal import CareerGoal
from app.talent.models.employer import Opportunity
from app.talent.models.passport import SkillPassport
from app.talent.services.scoring import compute_capability_profile

# Signal weights
_W_CAPABILITY = 0.40
_W_TYPE_PREF = 0.15
_W_GOAL = 0.20
_W_RECENCY = 0.15
_W_ENGAGEMENT = 0.10

# Recency decay: opportunities older than this get 0 recency score
_RECENCY_WINDOW_DAYS = 90


@dataclass(frozen=True, slots=True)
class RecommendedOpportunity:
    """A scored opportunity recommendation for a user."""

    opportunity_id: str
    title: str
    opportunity_type: str
    employer_org_id: str
    match_score: float
    match_reasons: list[str]
    is_bookmarked: bool
    already_applied: bool
    closes_in_days: int | None


class RecommendationFeedService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_feed(
        self,
        user_id: str,
        *,
        limit: int = 20,
        cursor: str | None = None,
        opportunity_type: str | None = None,
    ) -> tuple[list[RecommendedOpportunity], bool]:
        """Generate personalized opportunity feed."""
        now = datetime.now(UTC)

        # 1. Load user context
        passport = await self.db.get(SkillPassport, user_id)
        preferred_types = set(passport.preferred_opportunity_types) if passport else set()

        profile = await compute_capability_profile(self.db, user_id)
        user_cap_ids = {s.capability_id for s in profile}
        user_cap_levels: dict[str, int] = {s.capability_id: s.level for s in profile}

        # Career goal target capabilities
        goal_q = select(CareerGoal).where(
            CareerGoal.user_id == user_id,
            CareerGoal.status == "active",
        )
        goal_result = await self.db.execute(goal_q)
        goal_cap_ids: set[str] = set()
        for goal in goal_result.scalars().all():
            for tc in goal.target_capabilities or []:
                cap_id = tc.get("capability_id")
                if cap_id:
                    goal_cap_ids.add(cap_id)

        # Bookmarked opportunity IDs
        bk_q = select(OpportunityBookmark.opportunity_id).where(
            OpportunityBookmark.user_id == user_id
        )
        bk_result = await self.db.execute(bk_q)
        bookmarked_ids = {row[0] for row in bk_result.all()}

        # Already applied opportunity IDs
        app_q = select(Application.opportunity_id).where(
            Application.user_id == user_id
        )
        app_result = await self.db.execute(app_q)
        applied_ids = {row[0] for row in app_result.all()}

        # 2. Query open opportunities
        opp_q = select(Opportunity).where(Opportunity.status == "open")
        if opportunity_type:
            opp_q = opp_q.where(Opportunity.opportunity_type == opportunity_type)
        if cursor:
            opp_q = opp_q.where(Opportunity.id < cursor)
        opp_q = opp_q.order_by(Opportunity.created_at.desc()).limit(limit * 3)

        opp_result = await self.db.execute(opp_q)
        opportunities = list(opp_result.scalars().all())

        # 3. Score each opportunity
        scored: list[RecommendedOpportunity] = []

        for opp in opportunities:
            is_applied = opp.id in applied_ids
            # Skip already-applied by default
            if is_applied:
                continue

            reasons: list[str] = []

            # Capability match
            required_caps = opp.required_capabilities or []
            cap_score = 0.0
            if required_caps:
                met = 0
                for req in required_caps:
                    cap_id = req.get("capability_id", "")
                    min_level = req.get("min_level", 1)
                    if cap_id in user_cap_ids and user_cap_levels.get(cap_id, 0) >= min_level:
                        met += 1
                cap_score = met / len(required_caps)
                if cap_score >= 0.8:
                    reasons.append("Strong capability match")
                elif cap_score >= 0.5:
                    reasons.append("Partial capability match")

            # Type preference
            type_score = 1.0 if opp.opportunity_type in preferred_types else 0.0
            if type_score > 0:
                reasons.append(f"Preferred type: {opp.opportunity_type}")

            # Goal alignment
            goal_score = 0.0
            if goal_cap_ids and required_caps:
                goal_overlap = sum(
                    1 for req in required_caps
                    if req.get("capability_id") in goal_cap_ids
                )
                goal_score = min(goal_overlap / max(len(required_caps), 1), 1.0)
                if goal_score > 0:
                    reasons.append("Aligns with career goals")

            # Recency
            if opp.created_at:
                age_days = (now - opp.created_at).total_seconds() / 86400
                recency_score = max(0.0, 1.0 - age_days / _RECENCY_WINDOW_DAYS)
            else:
                recency_score = 0.5

            if recency_score > 0.8:
                reasons.append("Recently posted")

            # Engagement (bookmarked = boost)
            engagement_score = 1.0 if opp.id in bookmarked_ids else 0.0
            if engagement_score > 0:
                reasons.append("Bookmarked")

            # Composite score
            composite = (
                _W_CAPABILITY * cap_score
                + _W_TYPE_PREF * type_score
                + _W_GOAL * goal_score
                + _W_RECENCY * recency_score
                + _W_ENGAGEMENT * engagement_score
            )

            # Deadline
            closes_in: int | None = None
            if opp.application_deadline:
                delta = opp.application_deadline - now
                closes_in = max(0, int(delta.total_seconds() / 86400))

            if not reasons:
                reasons.append("Open opportunity")

            scored.append(RecommendedOpportunity(
                opportunity_id=opp.id,
                title=opp.title,
                opportunity_type=opp.opportunity_type,
                employer_org_id=opp.employer_org_id,
                match_score=round(composite, 3),
                match_reasons=reasons,
                is_bookmarked=opp.id in bookmarked_ids,
                already_applied=is_applied,
                closes_in_days=closes_in,
            ))

        # Sort by score descending
        scored.sort(key=lambda r: r.match_score, reverse=True)

        # Apply limit
        has_more = len(scored) > limit
        result = scored[:limit]

        return result, has_more
