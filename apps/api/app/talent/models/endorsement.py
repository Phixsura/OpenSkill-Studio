"""Skill endorsements — peer verification flow (ADR-015 upgrade).

Allows users to endorse another user's capability, creating a structured
peer_verified evidence record. Prevents self-endorsement and duplicates.
"""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

ENDORSEMENT_RELATIONSHIPS = frozenset(
    {
        "colleague",
        "manager",
        "instructor",
        "client",
        "peer",
        "mentor",
        "mentee",
    }
)


class SkillEndorsement(Base):
    """A peer endorsement of a user's capability."""

    __tablename__ = "talent_skill_endorsements"
    __table_args__ = (
        Index("ix_endorse_user", "user_id"),
        Index("ix_endorse_endorser", "endorser_id"),
        Index("ix_endorse_cap", "capability_id"),
        Index(
            "ix_endorse_unique",
            "user_id",
            "endorser_id",
            "capability_id",
            unique=True,
        ),
    )

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    endorser_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    capability_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("capabilities.id", ondelete="CASCADE")
    )
    relationship: Mapped[str] = mapped_column(String(30))
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="accepted")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
