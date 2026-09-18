"""Opportunity bookmark service — toggle, list, check (N13)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.bookmark import OpportunityBookmark


class BookmarkService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def toggle_bookmark(
        self,
        user_id: str,
        opportunity_id: str,
        notes: str | None = None,
    ) -> tuple[OpportunityBookmark | None, bool]:
        """Toggle bookmark. Returns (bookmark, created).

        If bookmark exists → removes it and returns (None, False).
        If not → creates it and returns (bookmark, True).
        """
        existing = await self.db.execute(
            select(OpportunityBookmark).where(
                OpportunityBookmark.user_id == user_id,
                OpportunityBookmark.opportunity_id == opportunity_id,
            )
        )
        bookmark = existing.scalar_one_or_none()

        if bookmark:
            await self.db.delete(bookmark)
            await self.db.flush()
            return None, False

        new_bookmark = OpportunityBookmark(
            user_id=user_id,
            opportunity_id=opportunity_id,
            notes=notes,
        )
        self.db.add(new_bookmark)
        await self.db.flush()
        return new_bookmark, True

    async def list_bookmarks(
        self,
        user_id: str,
        *,
        cursor: str | None = None,
        limit: int = 50,
    ) -> tuple[list[OpportunityBookmark], bool]:
        """List user's bookmarked opportunities, newest first."""
        q = select(OpportunityBookmark).where(OpportunityBookmark.user_id == user_id)
        if cursor:
            q = q.where(OpportunityBookmark.id < cursor)

        q = q.order_by(OpportunityBookmark.created_at.desc()).limit(limit + 1)
        result = await self.db.execute(q)
        items = list(result.scalars().all())

        has_more = len(items) > limit
        if has_more:
            items = items[:limit]
        return items, has_more

    async def is_bookmarked(self, user_id: str, opportunity_id: str) -> bool:
        """Check if an opportunity is bookmarked by the user."""
        q = select(OpportunityBookmark.id).where(
            OpportunityBookmark.user_id == user_id,
            OpportunityBookmark.opportunity_id == opportunity_id,
        )
        result = await self.db.execute(q)
        return result.scalar_one_or_none() is not None

    async def update_notes(
        self, user_id: str, bookmark_id: str, notes: str | None
    ) -> OpportunityBookmark | None:
        """Update bookmark notes. Only the bookmark owner can update."""
        bookmark = await self.db.get(OpportunityBookmark, bookmark_id)
        if not bookmark or bookmark.user_id != user_id:
            return None
        bookmark.notes = notes
        await self.db.flush()
        return bookmark
