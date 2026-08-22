"""Pack Review model — user ratings and reviews for published skill packs."""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class PackReview(Base):
    """One review per user per pack. Rating 1-5 with optional title/body."""

    __tablename__ = "pack_reviews"
    __table_args__ = (
        Index("uq_review_pack_user", "pack_id", "user_id", unique=True),
        Index("ix_reviews_pack_created", "pack_id", "created_at"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
    )

    id: Mapped[str] = ulid_pk()
    pack_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("skill_packs.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String(200))
    body: Mapped[str | None] = mapped_column(Text)
    helpful_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    reply_text: Mapped[str | None] = mapped_column(String(1000))
    reply_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ReviewHelpfulVote(Base):
    """Tracks which users found a review helpful. Composite PK on (user_id, review_id)."""

    __tablename__ = "review_helpful_votes"

    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    review_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("pack_reviews.id", ondelete="CASCADE"), primary_key=True
    )
