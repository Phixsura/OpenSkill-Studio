"""Talent CRM — consent-based pools and outreach (ADR-015 D13).

Rule-suggested pool membership requires explicit user consent before data
is visible. Anti-spam rate limiting enforced at service level.
"""

from datetime import UTC, datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class TalentPool(Base):
    """Consent-based talent pool for grouping candidates."""

    __tablename__ = "talent_pools"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # manual | rule_suggested | candidate_opt_in
    membership_mode: Mapped[str] = mapped_column(
        String(20), default="manual", server_default="'manual'"
    )
    # For rule_suggested: {"min_level": 3, "capabilities": ["01J..."], ...}
    rule_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # internal | shared (visible to member candidates)
    visibility: Mapped[str] = mapped_column(String(20), default="internal", server_default="'internal'")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_talent_pools_org", "org_id"),)


class TalentPoolMembership(Base):
    """Membership in a talent pool — requires consent for rule-suggested."""

    __tablename__ = "talent_pool_memberships"

    id: Mapped[str] = ulid_pk()
    pool_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("talent_pools.id", ondelete="CASCADE")
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    # manual_added | rule_suggested | opted_in
    source: Mapped[str] = mapped_column(String(20))
    # pending_consent | accepted | declined
    consent_status: Mapped[str] = mapped_column(
        String(20), default="accepted", server_default="'accepted'"
    )
    added_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC), server_default=func.now())

    __table_args__ = (
        Index("uq_pool_member", "pool_id", "user_id", unique=True),
        Index("ix_pool_memberships_user", "user_id"),
    )


class TalentOutreach(Base):
    """Opportunity invitation or talent-pool invitation."""

    __tablename__ = "talent_outreach"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    # opportunity_invitation | pool_invitation
    outreach_type: Mapped[str] = mapped_column(String(30))
    target_type: Mapped[str] = mapped_column(String(20))
    target_id: Mapped[str] = mapped_column(String(26))
    # sent | viewed | accepted | declined | expired
    status: Mapped[str] = mapped_column(String(20), default="sent", server_default="'sent'")
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now())
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC), server_default=func.now())

    __table_args__ = (
        Index("ix_outreach_user", "user_id", "status"),
        Index("ix_outreach_org", "org_id"),
    )
