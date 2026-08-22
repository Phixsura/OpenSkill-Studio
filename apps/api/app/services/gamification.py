"""Gamification service — points, levels, leaderboard."""

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gamification import PointsLedger, UserPoints
from app.models.user import User

log = structlog.get_logger()

# Point values per event
POINTS_SKILL_COMPLETION = 10
POINTS_PROJECT_SUBMISSION = 20
POINTS_PATH_COMPLETION = 50
POINTS_REVIEW_POSTED = 5

# Level thresholds: level N requires (N-1)*100 points
_LEVEL_STEP = 100


def _compute_level(total_points: int) -> int:
    """Derive level from total points. Level 1 at 0 pts, level 2 at 100, etc."""
    return max(1, (total_points // _LEVEL_STEP) + 1)


class GamificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def award_points(
        self,
        user_id: str,
        org_id: str,
        points: int,
        reason: str,
        reference_id: str | None = None,
        description: str | None = None,
    ) -> UserPoints:
        """Award points to a user and update their aggregate record."""
        # Append ledger entry
        entry = PointsLedger(
            user_id=user_id,
            org_id=org_id,
            points=points,
            reason=reason,
            reference_id=reference_id,
            description=description,
        )
        self.db.add(entry)

        # Upsert aggregate
        result = await self.db.execute(
            select(UserPoints).where(
                UserPoints.user_id == user_id,
                UserPoints.org_id == org_id,
            )
        )
        user_points = result.scalar_one_or_none()

        if user_points is None:
            user_points = UserPoints(
                user_id=user_id,
                org_id=org_id,
                total_points=points,
                level=_compute_level(points),
            )
            self.db.add(user_points)
            await self.db.flush()
        else:
            # Atomic SQL update — level computed from the DB-side total, not stale Python value
            await self.db.execute(
                update(UserPoints)
                .where(
                    UserPoints.user_id == user_id,
                    UserPoints.org_id == org_id,
                )
                .values(
                    total_points=UserPoints.total_points + points,
                    level=((UserPoints.total_points + points) / _LEVEL_STEP) + 1,
                )
            )
            await self.db.flush()
            # Refresh to get the updated values
            await self.db.refresh(user_points)
        log.info(
            "points_awarded",
            user_id=user_id,
            org_id=org_id,
            points=points,
            reason=reason,
            total=user_points.total_points,
        )
        return user_points

    async def get_leaderboard(
        self, org_id: str, limit: int = 20
    ) -> list[dict]:
        """Top N users by total points in an org."""
        result = await self.db.execute(
            select(
                UserPoints.user_id,
                UserPoints.total_points,
                UserPoints.level,
                User.display_name,
            )
            .join(User, User.id == UserPoints.user_id, isouter=True)
            .where(UserPoints.org_id == org_id)
            .order_by(UserPoints.total_points.desc())
            .limit(limit)
        )
        rows = result.all()
        return [
            {
                "rank": idx + 1,
                "user_id": row.user_id,
                "display_name": row.display_name or "",
                "total_points": row.total_points,
                "level": row.level,
            }
            for idx, row in enumerate(rows)
        ]

    async def get_user_points(self, user_id: str, org_id: str) -> dict:
        """Get a single user's points summary."""
        result = await self.db.execute(
            select(UserPoints).where(
                UserPoints.user_id == user_id,
                UserPoints.org_id == org_id,
            )
        )
        up = result.scalar_one_or_none()
        if up is None:
            return {"total_points": 0, "level": 1}
        return {"total_points": up.total_points, "level": up.level}

    async def get_user_points_history(
        self, user_id: str, org_id: str, limit: int = 50
    ) -> list[dict]:
        """Recent point awards for a user."""
        result = await self.db.execute(
            select(PointsLedger)
            .where(
                PointsLedger.user_id == user_id,
                PointsLedger.org_id == org_id,
            )
            .order_by(PointsLedger.created_at.desc())
            .limit(limit)
        )
        return [
            {
                "id": row.id,
                "points": row.points,
                "reason": row.reason,
                "reference_id": row.reference_id,
                "description": row.description,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in result.scalars().all()
        ]
