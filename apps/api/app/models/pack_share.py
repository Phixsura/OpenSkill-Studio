"""Cross-organization content sharing models."""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class PackShare(Base):
    """A sharing record: one pack shared to one target org."""

    __tablename__ = "pack_shares"
    __table_args__ = (
        Index("uq_pack_share", "pack_id", "target_org_id", unique=True),
        Index("ix_pack_shares_target", "target_org_id"),
    )

    id: Mapped[str] = ulid_pk()
    pack_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("skill_packs.id", ondelete="CASCADE"), nullable=False
    )
    target_org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    shared_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    shared_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
