"""Sticky assignments & append-only exposures (ADR-017 §4.4–§4.5).

Assignments are written with INSERT ... ON CONFLICT DO NOTHING and re-read —
never SELECT-then-INSERT (the R128/R88 race class). Exposures are an
append-only audit surface: assignment ≠ exposure, integration points record
an exposure at the moment the variant actually takes effect.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class ExperimentAssignment(Base):
    __tablename__ = "experiment_assignments"

    id: Mapped[str] = ulid_pk()
    experiment_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("experiments.id", ondelete="CASCADE")
    )
    unit_type: Mapped[str] = mapped_column(String(24))
    unit_id: Mapped[str] = mapped_column(String(26))
    variant_key: Mapped[str] = mapped_column(String(40))
    # Spec version live at assignment time — variants never change mid-run
    assigned_version: Mapped[int] = mapped_column(Integer)
    # Layer bucket the unit hashed to (diagnostics / SRM)
    bucket: Mapped[int] = mapped_column(Integer)
    is_holdout: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "experiment_id", "unit_type", "unit_id", name="uq_experiment_assignments_unit"
        ),
        Index("ix_experiment_assignments_unit", "unit_type", "unit_id"),
        Index("ix_experiment_assignments_exp_variant", "experiment_id", "variant_key"),
    )


class ExperimentExposure(Base):
    """Append-only: no UPDATE/DELETE path exists (ADR-017 §2.6)."""

    __tablename__ = "experiment_exposures"

    id: Mapped[str] = ulid_pk()
    assignment_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("experiment_assignments.id", ondelete="CASCADE")
    )
    # Denormalized to keep the hot funnel query join-free
    experiment_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("experiments.id", ondelete="CASCADE")
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Surface identifiers only — never PII bodies
    context: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # Idempotency handle for at-least-once callers (partial unique below)
    dedup_key: Mapped[str | None] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index("ix_experiment_exposures_exp_occurred", "experiment_id", "occurred_at"),
        # Defect #58 (exp11): dedup is PER ASSIGNMENT — scoping it to the
        # experiment made units sharing a natural key (per-day client keys)
        # collide, and ON CONFLICT silently dropped every unit after the
        # first each day.
        Index(
            "uq_experiment_exposures_dedup",
            "assignment_id",
            "dedup_key",
            unique=True,
            postgresql_where=text("dedup_key IS NOT NULL"),
        ),
    )


class ExperimentIdentityLink(Base):
    """§4.17 (round 210): a GLOBAL anonymous->user identity link. One anon
    id links to exactly one user, ever — first link wins; rebinding is a
    422 at the service. The link is the forwarding table resolution
    follows; assignment history migrates in place at link time."""

    __tablename__ = "experiment_identity_links"

    anonymous_id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
