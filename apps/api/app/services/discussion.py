"""Pack discussion/comment service — threaded comments on packs."""

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.discussion import PackDiscussion
from app.models.skill_pack import PackStatus, PackVisibility, SkillPack

log = structlog.get_logger()


class DiscussionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _require_public_pack(self, pack_id: str) -> SkillPack:
        """Verify the pack exists and is public/published before allowing comments."""
        pack = await self.db.get(SkillPack, pack_id)
        if pack is None:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)
        if pack.status != PackStatus.PUBLISHED:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)
        if pack.visibility == PackVisibility.PRIVATE:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)
        return pack

    async def create_comment(
        self,
        pack_id: str,
        user_id: str,
        body: str,
        parent_id: str | None = None,
    ) -> PackDiscussion:
        # Validate pack exists and is public
        await self._require_public_pack(pack_id)

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
        """Return threaded comments: paginated top-level with nested replies."""
        # Verify pack is public/published (same check as create_comment)
        await self._require_public_pack(pack_id)

        # Count top-level comments only
        count_q = select(func.count()).where(
            PackDiscussion.pack_id == pack_id,
            PackDiscussion.parent_id.is_(None),
        )
        total_r = await self.db.execute(count_q)
        total = total_r.scalar_one()

        # Step 1: Get paginated top-level comments (SQL-level pagination)
        offset = (page - 1) * per_page
        top_q = (
            select(PackDiscussion)
            .where(
                PackDiscussion.pack_id == pack_id,
                PackDiscussion.parent_id.is_(None),
            )
            .order_by(PackDiscussion.created_at.asc())
            .offset(offset)
            .limit(per_page)
        )
        top_result = await self.db.execute(top_q)
        top_comments = list(top_result.scalars().all())

        if not top_comments:
            return [], total

        # Step 2: Fetch replies only for the paginated top-level comment IDs
        top_ids = [c.id for c in top_comments]
        replies_q = (
            select(PackDiscussion)
            .where(
                PackDiscussion.pack_id == pack_id,
                PackDiscussion.parent_id.in_(top_ids),
            )
            .order_by(PackDiscussion.created_at.asc())
        )
        replies_result = await self.db.execute(replies_q)
        replies = list(replies_result.scalars().all())

        # Build threaded structure
        def _to_dict(c: PackDiscussion) -> dict:
            return {
                "id": c.id,
                "pack_id": c.pack_id,
                "user_id": c.user_id,
                "parent_id": c.parent_id,
                "body": c.body,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                "replies": [],
            }

        by_id: dict[str, dict] = {}
        result_list: list[dict] = []

        for c in top_comments:
            entry = _to_dict(c)
            by_id[c.id] = entry
            result_list.append(entry)

        for r in replies:
            entry = _to_dict(r)
            if r.parent_id in by_id:
                by_id[r.parent_id]["replies"].append(entry)

        return result_list, total

    async def delete_comment(
        self,
        comment_id: str,
        user_id: str,
        pack_id: str | None = None,
    ) -> None:
        comment = await self.db.get(PackDiscussion, comment_id)
        if comment is None:
            raise AppError("COMMENT_NOT_FOUND", "Comment not found", 404)
        if pack_id and comment.pack_id != pack_id:
            raise AppError("COMMENT_NOT_FOUND", "Comment not found in this pack", 404)
        if comment.user_id != user_id:
            raise AppError("NOT_AUTHOR", "Only the author can delete their comment", 403)
        await self.db.delete(comment)
        await self.db.flush()
