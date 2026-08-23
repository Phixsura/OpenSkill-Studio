"""Cohort (class/batch) models for training program operations."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, ulid_pk

# ── Enums ─────────────────────────────────────────────────


class CohortStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class CohortRole(str, enum.Enum):
    LEARNER = "learner"
    INSTRUCTOR = "instructor"


class ParticipationMode(str, enum.Enum):
    ASSIGNED = "assigned"
    APPLICATION = "application"


# ── Models ────────────────────────────────────────────────


class Cohort(Base):
    """A training cohort/class within an organization.

    Examples: "AI Visual Commerce — Fall 2026", "E-commerce AI Bootcamp — Cohort 03".
    """

    __tablename__ = "cohorts"
    __table_args__ = (
        Index("uq_cohort_org_slug", "org_id", "slug", unique=True),
        Index("ix_cohorts_org_status", "org_id", "status"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[CohortStatus] = mapped_column(
        Enum(CohortStatus, name="cohort_status", create_constraint=True),
        default=CohortStatus.DRAFT,
    )
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    max_learners: Mapped[int | None] = mapped_column(Integer, nullable=True)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    created_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    members: Mapped[list["CohortMember"]] = relationship(
        back_populates="cohort", cascade="all, delete-orphan"
    )


class CohortMember(Base):
    """A user enrolled in a cohort as either learner or instructor."""

    __tablename__ = "cohort_members"
    __table_args__ = (
        Index("uq_cohort_member", "cohort_id", "user_id", unique=True),
        Index("ix_cohort_members_user", "user_id"),
    )

    id: Mapped[str] = ulid_pk()
    cohort_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cohorts.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[CohortRole] = mapped_column(
        Enum(CohortRole, name="cohort_role", create_constraint=True),
        default=CohortRole.LEARNER,
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    cohort: Mapped["Cohort"] = relationship(back_populates="members")


class CohortSkillAssignment(Base):
    """Join table: a skill assigned to a cohort for its learners."""

    __tablename__ = "cohort_skill_assignments"

    cohort_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cohorts.id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    assigned_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)


class CohortProjectAssignment(Base):
    """A project assigned to a cohort, with optional deadline/limit overrides.

    Has its own PK (not composite) because override fields make it more than
    a pure join table — it carries per-cohort scheduling data.
    """

    __tablename__ = "cohort_project_assignments"
    __table_args__ = (
        Index("uq_cohort_project", "cohort_id", "project_id", unique=True),
        Index("ix_cohort_projects_project", "project_id"),
    )

    id: Mapped[str] = ulid_pk()
    cohort_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cohorts.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    deadline_override: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    late_deadline_override: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    max_submissions_override: Mapped[int | None] = mapped_column(Integer, nullable=True)
    participation_mode: Mapped[ParticipationMode] = mapped_column(
        Enum(ParticipationMode, name="participation_mode", create_constraint=True),
        default=ParticipationMode.ASSIGNED,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    assigned_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
