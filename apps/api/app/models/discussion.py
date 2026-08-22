"""Pack Discussion models — threaded comments on published skill packs."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class PackDiscussion(Base):
    """A comment (or reply) on a skill pack. Self-referencing parent_id for threads."""

    __tablename__ = "pack_discussions"
    __table_args__ = (
        Index("ix_discussions_pack_created", "pack_id", "created_at"),
        Index("ix_discussions_parent", "parent_id"),
    )

    id: Mapped[str] = ulid_pk()
    pack_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("skill_packs.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    parent_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("pack_discussions.id", ondelete="CASCADE"), nullable=True
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
