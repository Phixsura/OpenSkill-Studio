"""Skill Passport — user-owned, privacy-controlled talent identity (ADR-015 D4).

Private by default. Users must explicitly opt in to discoverability and
choose which fields to expose.
"""

from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

# Fields that can appear in visible_fields
PASSPORT_SHAREABLE_FIELDS = frozenset(
    {
        "capabilities",
        "credentials",
        "projects",
        "portfolio",
        "availability",
        "learning_paths",
        "workflow_competencies",
        "commercial_history",
        "verifications",
    }
)


class SkillPassport(Base):
    """User-owned talent passport backed by verified platform evidence."""

    __tablename__ = "skill_passports"

    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    # private | organization_only | share_link | public_subset
    default_visibility: Mapped[str] = mapped_column(
        String(20), default="private", server_default="'private'"
    )
    # Whitelist of fields exposed externally
    visible_fields: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # Self-declared preferences
    preferred_opportunity_types: Mapped[list] = mapped_column(
        JSONB, default=list, server_default="[]"
    )
    # open | not_looking | open_to_offers | NULL
    availability_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    availability_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Opt-in to employer discoverability — THE consent gate
    discoverable: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    # Scoped discoverability: NULL = all employers; list = specific employer org_ids
    discoverable_to: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PassportSnapshot(Base):
    """Immutable point-in-time snapshot for external verification."""

    __tablename__ = "passport_snapshots"

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    # External share token: /verify/passport/{token}
    share_token: Mapped[str] = mapped_column(String(64), unique=True)
    # Frozen capability/credential/evidence summary
    payload: Mapped[dict] = mapped_column(JSONB)
    # SHA-256 of canonical JSON payload — tamper detection
    checksum: Mapped[str] = mapped_column(String(64))
    # Which fields were included (user-selected subset)
    included_fields: Mapped[list] = mapped_column(JSONB)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # active | revoked
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="'active'")

    __table_args__ = (Index("ix_passport_snapshots_user", "user_id", "status"),)
