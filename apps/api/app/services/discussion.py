"""Pack discussion/comment service — threaded comments on packs."""

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.discussion import PackDiscussion

log = structlog.get_logger()


class DiscussionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_comment(
        self,
        pack_id: str,
        user_id: str,
        body: str,
        parent_id: str | None = None,
    ) -> PackDiscussion:
        if parent_id:
            parent = await self.db.get(PackDiscussion, parent_id)
            if parent is None or parent.pack_id != pack_id:
                raise AppError("PARENT_NOT_FOUND", "Parent comment not found in this pack", 404)

        comment = PackDiscussion(
            pack_id=pack_id,
            user_id=user_id,
            parent_id=parent_id,
            body=body,
        )
        self.db.add(comment)
        await self.db.flush()
        log.info("discussion_comment_created", comment_id=comment.id, pack_id=pack_id)
        return comment

    async def list_comments(
        self,
        pack_id: str,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[dict], int]:
        """Return threaded comments: top-level with nested replies."""
        # Count top-level comments only
        count_q = select(func.count()).where(
            PackDiscussion.pack_id == pack_id,
            PackDiscussion.parent_id.is_(None),
        )
        total_r = await self.db.execute(count_q)
        total = total_r.scalar_one()

        # Get all comments for this pack (top-level + replies) in one query
        result = await self.db.execute(
            select(PackDiscussion)
            .where(PackDiscussion.pack_id == pack_id)
            .order_by(PackDiscussion.created_at.asc())
        )
        all_comments = list(result.scalars().all())

        # Build threaded structure
        by_id: dict[str, dict] = {}
        top_level: list[dict] = []

        for c in all_comments:
            entry = {
                "id": c.id,
                "pack_id": c.pack_id,
                "user_id": c.user_id,
                "parent_id": c.parent_id,
                "body": c.body,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                "replies": [],
            }
            by_id[c.id] = entry
            if c.parent_id is None:
                top_level.append(entry)
            elif c.parent_id in by_id:
                by_id[c.parent_id]["replies"].append(entry)

        # Paginate top-level comments
        offset = (page - 1) * per_page
        paginated = top_level[offset : offset + per_page]
        return paginated, total

    async def delete_comment(
        self,
        comment_id: str,
        user_id: str,
    ) -> None:
        comment = await self.db.get(PackDiscussion, comment_id)
        if comment is None:
            raise AppError("COMMENT_NOT_FOUND", "Comment not found", 404)
        if comment.user_id != user_id:
            raise AppError("NOT_AUTHOR", "Only the author can delete their comment", 403)
        await self.db.delete(comment)
        await self.db.flush()
