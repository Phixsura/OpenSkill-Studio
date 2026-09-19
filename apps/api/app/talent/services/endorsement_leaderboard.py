"""Endorsement leaderboard — top endorsed users and capabilities (N12).

Provides org-level and platform-level leaderboards for social proof
and gamification of skill endorsements.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.capability import Capability
from app.talent.models.endorsement import SkillEndorsement
from app.talent.models.passport import SkillPassport


@dataclass(frozen=True, slots=True)
class LeaderboardEntry:
    """A single user entry in the endorsement leaderboard."""

    user_id: str
    total_endorsements: int
    unique_endorsers: int


@dataclass(frozen=True, slots=True)
class CapabilityLeaderboardEntry:
    """A single capability entry in the endorsement leaderboard."""

    capability_id: str
    capability_name: str
    endorsement_count: int
    unique_users: int


@dataclass(frozen=True, slots=True)
class EndorsementStats:
    """Platform/org-wide endorsement statistics."""

    total_endorsements: int
    total_endorsers: int
    total_endorsed_users: int
    avg_per_user: float


class EndorsementLeaderboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_top_endorsed_users(
        self,
        *,
        limit: int = 20,
    ) -> list[LeaderboardEntry]:
        """Top users by endorsement count.

        Only counts users with discoverable=true passport.
        """
        q = (
            select(
                SkillEndorsement.user_id,
                func.count(SkillEndorsement.id).label("total"),
                func.count(func.distinct(SkillEndorsement.endorser_id)).label("unique_endorsers"),
            )
            .join(
                SkillPassport,
                SkillPassport.user_id == SkillEndorsement.user_id,
            )
            .where(SkillPassport.discoverable.is_(True))
            .group_by(SkillEndorsement.user_id)
            .order_by(func.count(SkillEndorsement.id).desc())
            .limit(limit)
        )
        result = await self.db.execute(q)
        return [
            LeaderboardEntry(
                user_id=row.user_id,
                total_endorsements=row.total,
                unique_endorsers=row.unique_endorsers,
            )
            for row in result.all()
        ]

    async def get_top_endorsed_capabilities(
        self,
        *,
        limit: int = 20,
    ) -> list[CapabilityLeaderboardEntry]:
        """Top capabilities by endorsement count."""
        q = (
            select(
                SkillEndorsement.capability_id,
                func.count(SkillEndorsement.id).label("total"),
                func.count(func.distinct(SkillEndorsement.user_id)).label("unique_users"),
            )
            .group_by(SkillEndorsement.capability_id)
            .order_by(func.count(SkillEndorsement.id).desc())
            .limit(limit)
        )
        result = await self.db.execute(q)
        rows = result.all()

        # Load capability names
        cap_ids = [r.capability_id for r in rows]
        if cap_ids:
            cap_q = select(Capability.id, Capability.canonical_name).where(
                Capability.id.in_(cap_ids)
            )
            cap_result = await self.db.execute(cap_q)
            names = dict(cap_result.all())
        else:
            names = {}

        return [
            CapabilityLeaderboardEntry(
                capability_id=row.capability_id,
                capability_name=names.get(row.capability_id, ""),
                endorsement_count=row.total,
                unique_users=row.unique_users,
            )
            for row in rows
        ]

    async def get_endorsement_stats(self) -> EndorsementStats:
        """Platform-wide endorsement statistics."""
        total_q = select(func.count(SkillEndorsement.id))
        total = (await self.db.execute(total_q)).scalar() or 0

        endorsers_q = select(func.count(func.distinct(SkillEndorsement.endorser_id)))
        total_endorsers = (await self.db.execute(endorsers_q)).scalar() or 0

        endorsed_q = select(func.count(func.distinct(SkillEndorsement.user_id)))
        total_endorsed = (await self.db.execute(endorsed_q)).scalar() or 0

        avg = total / total_endorsed if total_endorsed > 0 else 0.0

        return EndorsementStats(
            total_endorsements=total,
            total_endorsers=total_endorsers,
            total_endorsed_users=total_endorsed,
            avg_per_user=round(avg, 2),
        )
