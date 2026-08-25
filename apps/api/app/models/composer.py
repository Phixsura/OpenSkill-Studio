"""Composer + creator-matching models (ADR-013).

SolutionDrafts are the single side-effect gate (D5): composers write ONLY
draft rows; a human confirm materializes real entities. CreatorAssignment is
shortlist-as-offer — the platform never auto-assigns.
"""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class SolutionDraft(Base):
    """A machine-composed learning-path or production-solution draft."""

    __tablename__ = "solution_drafts"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    draft_type: Mapped[str] = mapped_column(String(30))  # learning_path | production_solution
    requirement_profile_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    match_run_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    # items + gaps + placeholders + cuts — every omission is a first-class row
    # with a reason code (R8: nothing hidden)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    engine_version: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="draft")
    confirmed_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # The LearningPath / Project created on confirm
    materialized_entity_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_solution_drafts_org", "org_id", "draft_type"),)


class CreatorCapabilityEvidence(Base):
    """Decomposed verified evidence per (user, capability) — auditable (R9/GDPR)."""

    __tablename__ = "creator_capability_evidence"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    capability_key: Mapped[str] = mapped_column(String(64))
    # skill_completed | badge | approved_submission | commercial_project | eval_result | workflow_run
    evidence_type: Mapped[str] = mapped_column(String(30))
    evidence_id: Mapped[str] = mapped_column(String(26))  # loose ref to the source record
    # 1.0 platform-verified / 0.6 self-declared (D5 evidence hierarchy)
    weight: Mapped[float] = mapped_column(Numeric(3, 2), default=1.0)
    score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (Index("ix_evidence_user_cap", "org_id", "user_id", "capability_key"),)


class CreatorAssignment(Base):
    """Shortlist-as-offer: a human assigner offers, the creator responds (R9)."""

    __tablename__ = "creator_assignments"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE")
    )
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    match_run_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="offered", server_default="offered")
    # Always a human user — never a service account (R9). Nullable because
    # ondelete='SET NULL' must be able to fire when the assigner is deleted.
    assigned_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    override_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("uq_creator_assignment", "project_id", "user_id", unique=True),
        Index("ix_creator_assignments_org", "org_id"),
    )
