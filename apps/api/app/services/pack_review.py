"""Pack Review service — create, list, delete, update reviews and maintain aggregate stats."""

from datetime import UTC, datetime
from typing import Literal

import structlog
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.pack_review import PackReview, ReviewHelpfulVote
from app.models.skill_pack import PackStatus, PackVisibility, SkillPack

log = structlog.get_logger()

SortOrder = Literal["newest", "oldest", "highest", "lowest"]


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
        """Recalculate average_rating and review_count atomically.

        Uses correlated subqueries in a single UPDATE to prevent lost updates
        under concurrent review mutations. When the UPDATE acquires the row
        lock, the subqueries re-execute with a fresh READ COMMITTED snapshot.
        """
        count_sq = (
            select(func.count(PackReview.id))
            .where(PackReview.pack_id == pack_id)
            .scalar_subquery()
        )
        avg_sq = (
            select(func.avg(PackReview.rating))
            .where(PackReview.pack_id == pack_id)
            .scalar_subquery()
        )
        await self.db.execute(
            update(SkillPack)
            .where(SkillPack.id == pack_id)
            .values(review_count=count_sq, average_rating=avg_sq)
        )
        await self.db.flush()

    async def create_review(
        self,
        pack_id: str,
        user_id: str,
        rating: int,
        title: str | None = None,
        body: str | None = None,
    ) -> PackReview:
        pack = await self._get_public_pack(pack_id)

        # Prevent self-reviews
        if pack.created_by == user_id:
            raise AppError("SELF_REVIEW_FORBIDDEN", "You cannot review your own pack", 422)

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

    async def update_review(
        self,
        review_id: str,
        user_id: str,
        rating: int | None = None,
        title: str | None = None,
        body: str | None = None,
    ) -> PackReview:
        """Update an existing review. Owner only."""
        review = await self.db.get(PackReview, review_id)
        if review is None:
            raise ReviewNotFoundError()
        if review.user_id != user_id:
            raise AppError("FORBIDDEN", "You can only edit your own reviews", 403)

        if rating is not None:
            review.rating = rating
        if title is not None:
            review.title = title
        if body is not None:
            review.body = body

        # Low ratings require a substantive body so authors get actionable feedback
        effective_rating = review.rating
        effective_body = review.body
        if effective_rating <= 2 and (effective_body is None or len(effective_body) < 20):
            raise AppError(
                "LOW_RATING_NEEDS_BODY",
                "Reviews rated 2 or below need a body of at least 20 characters",
                422,
            )

        await self.db.flush()

        if rating is not None:
            await self._recalculate_stats(review.pack_id)

        log.info("review_updated", review_id=review_id, user_id=user_id)
        return review

    async def list_reviews(
        self,
        pack_id: str,
        page: int = 1,
        per_page: int = 20,
        sort: SortOrder = "newest",
        rating: int | None = None,
    ) -> tuple[list[PackReview], int]:
        await self._get_public_pack(pack_id)  # 404 for private/unpublished
        base = select(PackReview).where(PackReview.pack_id == pack_id)

        if rating is not None:
            base = base.where(PackReview.rating == rating)

        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()

        # Apply sort order
        if sort == "oldest":
            order_clause = PackReview.created_at.asc()
        elif sort == "highest":
            order_clause = PackReview.rating.desc()
        elif sort == "lowest":
            order_clause = PackReview.rating.asc()
        else:  # "newest" (default)
            order_clause = PackReview.created_at.desc()

        offset = (page - 1) * per_page
        result = await self.db.execute(
            base.order_by(order_clause).offset(offset).limit(per_page)
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

    async def reply_to_review(
        self,
        review_id: str,
        pack_id: str,
        user_id: str,
        reply_text: str,
    ) -> PackReview:
        """Add a publisher reply to a review. Only the pack creator can reply."""
        pack = await self._get_public_pack(pack_id)
        if pack.created_by != user_id:
            raise AppError("FORBIDDEN", "Only the pack owner can reply to reviews", 403)

        review = await self.db.get(PackReview, review_id)
        if review is None:
            raise ReviewNotFoundError()
        if review.pack_id != pack_id:
            raise AppError("REVIEW_NOT_FOUND", "Review not found for this pack", 404)

        review.reply_text = reply_text
        review.reply_at = datetime.now(UTC)
        await self.db.flush()

        log.info("review_reply_added", review_id=review_id, pack_id=pack_id)
        return review

    async def get_distribution(self, pack_id: str) -> dict:
        """Return rating distribution for a pack."""
        await self._get_public_pack(pack_id)

        result = await self.db.execute(
            select(
                PackReview.rating,
                func.count(PackReview.id),
            )
            .where(PackReview.pack_id == pack_id)
            .group_by(PackReview.rating)
        )
        rows = result.all()

        distribution = {i: 0 for i in range(1, 6)}
        total = 0
        rating_sum = 0
        for rating_val, count in rows:
            distribution[rating_val] = count
            total += count
            rating_sum += rating_val * count

        average = round(rating_sum / total, 2) if total > 0 else None

        return {
            "average": average,
            "total": total,
            "distribution": distribution,
        }

    async def toggle_helpful(self, review_id: str, user_id: str) -> PackReview:
        """Toggle a helpful vote on a review."""
        review = await self.db.get(PackReview, review_id)
        if review is None:
            raise ReviewNotFoundError()

        # Check if user already voted
        existing = await self.db.get(ReviewHelpfulVote, (user_id, review_id))
        if existing is not None:
            # Remove vote
            await self.db.delete(existing)
            # Atomic decrement to prevent lost updates under concurrent votes
            review.helpful_count = func.greatest(0, PackReview.helpful_count - 1)
        else:
            # Add vote — handle concurrent double-click with IntegrityError
            vote = ReviewHelpfulVote(user_id=user_id, review_id=review_id)
            self.db.add(vote)
            try:
                await self.db.flush()
            except IntegrityError:
                # Vote was already inserted by a concurrent request — treat as remove
                await self.db.rollback()
                existing2 = await self.db.get(ReviewHelpfulVote, (user_id, review_id))
                if existing2:
                    await self.db.delete(existing2)
                    review = await self.db.get(PackReview, review_id)
                    review.helpful_count = func.greatest(0, PackReview.helpful_count - 1)
                    await self.db.flush()
                # Refresh to materialize SQL expressions and avoid MissingGreenlet
                review = await self.db.get(PackReview, review_id)
                if review:
                    await self.db.refresh(review)
                log.info("review_helpful_toggled", review_id=review_id, user_id=user_id)
                return review
            # Atomic increment
            review.helpful_count = PackReview.helpful_count + 1

        await self.db.flush()
        await self.db.refresh(review)
        log.info("review_helpful_toggled", review_id=review_id, user_id=user_id)
        return review

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
