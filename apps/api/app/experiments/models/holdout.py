"""Global holdout groups (ADR-017 §4.12 v2, Statsig-style).

Units hashing into an ACTIVE group's band are excluded from NEW enrollment
into every experiment of the group's domain/scope for the period — measuring
the cumulative impact of everything shipped. Membership is computed (a
deterministic salt), never stored; existing sticky assignments keep serving
(a holdout group only blocks NEW entries, it never yanks an experience).
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

HOLDOUT_GROUP_STATUSES = frozenset({"active", "released"})
HOLDOUT_GROUP_MAX_BP = 2000  # at most 20% of a domain withheld


class HoldoutGroup(Base):
    __tablename__ = "experiment_holdout_groups"

    id: Mapped[str] = ulid_pk()
    # unique among ACTIVE groups only (the round-3 one-shot-key lesson:
    # a released group must not hold its key hostage forever)
    key: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(200))
    domain: Mapped[str] = mapped_column(String(20))
    # null = platform-wide; set = applies to that org's experiments only
    scope_org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    holdout_bp: Mapped[int] = mapped_column(Integer)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(10), default="active", server_default="active")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_experiment_holdout_groups_domain", "domain", "status"),
        Index(
            "uq_experiment_holdout_groups_active_key",
            "key",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )
