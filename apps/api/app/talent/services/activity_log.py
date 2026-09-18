"""Talent activity log service — audit trail for all talent mutations.

Records structured activity entries for user timeline, admin audit,
and compliance export. Entries are immutable.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.activity import (
    ACTIVITY_ACTION_TYPES,
    TalentActivityLog,
)


class ActivityLogService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        *,
        user_id: str,
        action_type: str,
        target_type: str,
        target_id: str,
        metadata: dict | None = None,
    ) -> TalentActivityLog:
        """Record an activity log entry. Fail-safe: invalid action_type
        is logged with 'unknown' prefix rather than raising."""
        if action_type not in ACTIVITY_ACTION_TYPES:
            action_type = f"unknown:{action_type}"

        entry = TalentActivityLog(
            user_id=user_id,
            action_type=action_type,
            target_type=target_type,
            target_id=target_id,
            extra=metadata or {},
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def list_activities(
        self,
        user_id: str,
        *,
        action_type: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> tuple[list[TalentActivityLog], bool]:
        """List activity entries for a user, newest first."""
        q = select(TalentActivityLog).where(TalentActivityLog.user_id == user_id)
        if action_type:
            q = q.where(TalentActivityLog.action_type == action_type)
        if cursor:
            q = q.where(TalentActivityLog.id < cursor)

        q = q.order_by(TalentActivityLog.created_at.desc()).limit(limit + 1)
        result = await self.db.execute(q)
        items = list(result.scalars().all())

        has_more = len(items) > limit
        if has_more:
            items = items[:limit]
        return items, has_more

    async def list_org_activities(
        self,
        org_id: str,
        *,
        action_type: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> tuple[list[TalentActivityLog], bool]:
        """List activity entries for an organization (admin audit trail).

        Scoped to users who are members of the org to prevent cross-tenant
        data leakage.
        """
        from app.models.organization import OrgMember

        q = (
            select(TalentActivityLog)
            .join(
                OrgMember,
                OrgMember.user_id == TalentActivityLog.user_id,
            )
            .where(OrgMember.org_id == org_id)
        )
        if action_type:
            q = q.where(TalentActivityLog.action_type == action_type)
        if cursor:
            q = q.where(TalentActivityLog.id < cursor)

        q = q.order_by(TalentActivityLog.created_at.desc()).limit(limit + 1)
        result = await self.db.execute(q)
        items = list(result.scalars().all())

        has_more = len(items) > limit
        if has_more:
            items = items[:limit]
        return items, has_more
