"""Learning Path models — ordered curriculum composition from multiple packs."""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk
from app.models.skill import ContentStatus

# ── Enums ────────────────────────────────────────────────


class PathItemType(str, enum.Enum):
    SKILL = "skill"
    PROJECT = "project"
    SECTION = "section"  # heading only, no FK
    WORKFLOW_PACK = "workflow_pack"  # Issue #21: installed workflow pack reference


# ── Learning Path ────────────────────────────────────────


class LearningPath(Base):
    __tablename__ = "learning_paths"
    __table_args__ = (
        Index("uq_path_org_slug", "org_id", "slug", unique=True),
        Index("ix_paths_org_status", "org_id", "status"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus, name="content_status", create_constraint=True),
        default=ContentStatus.DRAFT,
    )
    estimated_minutes: Mapped[int | None] = mapped_column(Integer)
    created_by: Mapped[str | None] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ── Path Items ───────────────────────────────────────────


class LearningPathItem(Base):
    __tablename__ = "learning_path_items"
    __table_args__ = (
        Index("ix_path_items_order", "path_id", "sort_order"),
        CheckConstraint(
            "(item_type = 'SKILL' AND skill_id IS NOT NULL) OR "
            "(item_type = 'PROJECT' AND project_id IS NOT NULL) OR "
            "(item_type = 'SECTION' AND section_title IS NOT NULL) OR "
            "(item_type = 'WORKFLOW_PACK' AND workflow_pack_id IS NOT NULL)",
            name="ck_path_item_type_ref",
        ),
    )

    id: Mapped[str] = ulid_pk()
    path_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False
    )
    item_type: Mapped[PathItemType] = mapped_column(
        Enum(PathItemType, name="path_item_type", create_constraint=True), nullable=False
    )
    skill_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("skills.id", ondelete="CASCADE")
    )
    project_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE")
    )
    section_title: Mapped[str | None] = mapped_column(String(200))
    # Loose ref to an installed workflow pack (Issue #21) — no FK by design
    workflow_pack_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    unlock_rule: Mapped[str] = mapped_column(String(30), nullable=False, default="previous_required")
    drip_schedule: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


# ── Cohort Assignment ────────────────────────────────────


class CohortLearningPathAssignment(Base):
    """Assign a learning path to a cohort (composite PK)."""

    __tablename__ = "cohort_learning_path_assignments"

    cohort_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cohorts.id", ondelete="CASCADE"), primary_key=True
    )
    path_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("learning_paths.id", ondelete="CASCADE"), primary_key=True
    )
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    assigned_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
