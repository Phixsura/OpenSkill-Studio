"""Career goal service — user-side goal tracking with progress (N3).

Users set career aspirations with target capabilities and dates,
then check progress by comparing their current capability levels
against the goal's targets.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.career_goal import MAX_ACTIVE_GOALS, CareerGoal
from app.talent.services.scoring import compute_capability_profile


class CareerGoalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_goal(
        self,
        *,
        user_id: str,
        title: str,
        description: str | None = None,
        target_role: str | None = None,
        target_capabilities: list[dict] | None = None,
        target_date: date | None = None,
    ) -> CareerGoal:
        # Enforce max active goals
        count_q = select(func.count()).select_from(
            select(CareerGoal.id)
            .where(
                CareerGoal.user_id == user_id,
                CareerGoal.status == "active",
            )
            .subquery()
        )
        active_count = (await self.db.execute(count_q)).scalar() or 0
        if active_count >= MAX_ACTIVE_GOALS:
            raise ValueError(
                f"Maximum {MAX_ACTIVE_GOALS} active goals allowed. "
                "Complete or abandon an existing goal first."
            )

        goal = CareerGoal(
            user_id=user_id,
            title=title,
            description=description,
            target_role=target_role,
            target_capabilities=target_capabilities or [],
            target_date=target_date,
        )
        self.db.add(goal)
        await self.db.flush()
        return goal

    async def get_goal(self, goal_id: str) -> CareerGoal | None:
        return await self.db.get(CareerGoal, goal_id)

    async def list_goals(
        self,
        user_id: str,
        *,
        status: str | None = None,
        cursor: str | None = None,
        limit: int = 20,
    ) -> tuple[list[CareerGoal], bool]:
        q = select(CareerGoal).where(CareerGoal.user_id == user_id)
        if status:
            q = q.where(CareerGoal.status == status)
        if cursor:
            q = q.where(CareerGoal.id < cursor)
        q = q.order_by(CareerGoal.created_at.desc()).limit(limit + 1)
        result = await self.db.execute(q)
        items = list(result.scalars().all())
        has_more = len(items) > limit
        if has_more:
            items = items[:limit]
        return items, has_more

    async def update_goal(
        self, goal_id: str, user_id: str, **fields: object
    ) -> CareerGoal | None:
        goal = await self.db.get(CareerGoal, goal_id)
        if not goal or goal.user_id != user_id:
            return None
        for key, value in fields.items():
            if hasattr(goal, key) and value is not None:
                setattr(goal, key, value)
        await self.db.flush()
        return goal

    async def complete_goal(
        self, goal_id: str, user_id: str
    ) -> CareerGoal | None:
        goal = await self.db.get(CareerGoal, goal_id)
        if not goal or goal.user_id != user_id:
            return None
        if goal.status != "active":
            raise ValueError(f"Cannot complete a goal in status '{goal.status}'")
        goal.status = "completed"
        goal.completed_at = datetime.now(UTC)
        await self.db.flush()
        return goal

    async def abandon_goal(
        self, goal_id: str, user_id: str
    ) -> CareerGoal | None:
        goal = await self.db.get(CareerGoal, goal_id)
        if not goal or goal.user_id != user_id:
            return None
        if goal.status != "active":
            raise ValueError(f"Cannot abandon a goal in status '{goal.status}'")
        goal.status = "abandoned"
        await self.db.flush()
        return goal

    async def check_goal_progress(
        self, goal_id: str, user_id: str
    ) -> dict:
        """Check progress toward a goal by comparing current capability levels."""
        goal = await self.db.get(CareerGoal, goal_id)
        if not goal or goal.user_id != user_id:
            return {
                "goal_id": goal_id,
                "title": "",
                "overall_progress": 0.0,
                "target_date": None,
                "days_remaining": None,
                "capabilities": [],
            }

        target_caps = goal.target_capabilities or []
        if not target_caps:
            return {
                "goal_id": goal.id,
                "title": goal.title,
                "overall_progress": 0.0,
                "target_date": goal.target_date.isoformat() if goal.target_date else None,
                "days_remaining": _days_remaining(goal.target_date),
                "capabilities": [],
            }

        # Get current capability profile for target capability IDs
        cap_ids = [tc.get("capability_id") for tc in target_caps if tc.get("capability_id")]
        profile = await compute_capability_profile(self.db, user_id, capability_ids=cap_ids or None)
        current_levels = {s.capability_id: s.level for s in profile}

        cap_progress = []
        total_progress = 0.0
        for tc in target_caps:
            cap_id = tc.get("capability_id", "")
            cap_name = tc.get("capability_name", cap_id)
            target_level = tc.get("target_level", 1)
            current_level = current_levels.get(cap_id, 0)

            if target_level <= 0:
                progress_pct = 100.0
            else:
                progress_pct = min(100.0, (current_level / target_level) * 100)

            cap_progress.append({
                "capability_id": cap_id,
                "capability_name": cap_name,
                "current_level": current_level,
                "target_level": target_level,
                "progress": round(progress_pct, 1),
                "met": current_level >= target_level,
            })
            total_progress += progress_pct

        overall = round(total_progress / max(len(target_caps), 1), 1) if target_caps else 0.0

        return {
            "goal_id": goal.id,
            "title": goal.title,
            "overall_progress": overall,
            "target_date": goal.target_date.isoformat() if goal.target_date else None,
            "days_remaining": _days_remaining(goal.target_date),
            "capabilities": cap_progress,
        }


def _days_remaining(target_date: date | None) -> int | None:
    """Compute days remaining until target date, or None if no date set."""
    if not target_date:
        return None
    today = date.today()
    delta = target_date - today
    return max(0, delta.days)
