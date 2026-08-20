"""Pack Review service — create, list, delete reviews and maintain aggregate stats."""

import structlog
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.pack_review import PackReview
from app.models.skill_pack import PackStatus, PackVisibility, SkillPack

log = structlog.get_logger()


class ReviewNotFoundError(AppError):
    def __init__(self):
        super().__init__("REVIEW_NOT_FOUND", "Review not found", 404)


class PackReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_public_pack(self, pack_id: str) -> SkillPack:
        """Verify pack exists, is published, and is not private."""
        pack = await self.db.get(SkillPack, pack_id)
        if pack is None:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)
        if pack.status != PackStatus.PUBLISHED:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)
        if pack.visibility == PackVisibility.PRIVATE:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)
        return pack

    async def _recalculate_stats(self, pack_id: str) -> None:
        """Recalculate average_rating and review_count on the SkillPack row."""
        result = await self.db.execute(
            select(
                func.count(PackReview.id),
                func.avg(PackReview.rating),
            ).where(PackReview.pack_id == pack_id)
        )
        row = result.one()
        count = row[0]
        avg = float(round(row[1], 2)) if row[1] is not None else None

        pack = await self.db.get(SkillPack, pack_id)
        if pack is not None:
            pack.review_count = count
            pack.average_rating = avg
            await self.db.flush()

    async def create_review(
        self,
        pack_id: str,
        user_id: str,
        rating: int,
        title: str | None = None,
        body: str | None = None,
    ) -> PackReview:
        await self._get_public_pack(pack_id)

        review = PackReview(
            pack_id=pack_id,
            user_id=user_id,
            rating=rating,
            title=title,
            body=body,
        )
        self.db.add(review)
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise AppError(
                "DUPLICATE_REVIEW",
                "You have already reviewed this pack",
                409,
            ) from None

        await self._recalculate_stats(pack_id)

        log.info("review_created", pack_id=pack_id, user_id=user_id, rating=rating)
        return review

    async def list_reviews(
        self,
        pack_id: str,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[PackReview], int]:
        await self._get_public_pack(pack_id)  # 404 for private/unpublished
        base = select(PackReview).where(PackReview.pack_id == pack_id)

        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()

        offset = (page - 1) * per_page
        result = await self.db.execute(
            base.order_by(PackReview.created_at.desc()).offset(offset).limit(per_page)
        )
        return list(result.scalars().all()), total

    async def delete_review(self, review_id: str, user_id: str) -> None:
        review = await self.db.get(PackReview, review_id)
        if review is None:
            raise ReviewNotFoundError()
        if review.user_id != user_id:
            raise AppError("FORBIDDEN", "You can only delete your own reviews", 403)

        pack_id = review.pack_id
        await self.db.delete(review)
        await self.db.flush()

        await self._recalculate_stats(pack_id)
        log.info("review_deleted", review_id=review_id, pack_id=pack_id)

    async def get_stats(self, pack_id: str) -> dict:
        result = await self.db.execute(
            select(
                func.count(PackReview.id),
                func.avg(PackReview.rating),
            ).where(PackReview.pack_id == pack_id)
        )
        row = result.one()
        return {
            "review_count": row[0],
            "average_rating": float(round(row[1], 2)) if row[1] is not None else None,
        }
