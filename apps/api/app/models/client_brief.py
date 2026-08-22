"""Client brief models for commercial production projects."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

# ── Enums ─────────────────────────────────────────────────


class BriefStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"  # published internally, accepting applications
    ASSIGNED = "assigned"  # assigned to cohort/creators
    IN_PRODUCTION = "in_production"  # work underway
    REVIEW = "review"  # deliverables under review
    ACTIVE = "active"  # legacy alias (mapped from convert)
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


# ── Models ────────────────────────────────────────────────


class ClientBrief(Base):
    """A structured commercial production request from an external client.

    Not a CRM entity — only stores what's needed to run the production project.
    The brief can be converted into a Project via ClientBriefService.convert_to_project().
    """

    __tablename__ = "client_briefs"
    __table_args__ = (
        Index("uq_brief_org_slug", "org_id", "slug", unique=True),
        Index("ix_briefs_org_status", "org_id", "status"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), nullable=False)
    client_name: Mapped[str] = mapped_column(String(200), nullable=False)
    client_industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    client_website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    brand_guidelines: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_type: Mapped[str] = mapped_column(String(50), nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    deliverable_specs: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    tone_and_style: Mapped[str | None] = mapped_column(Text, nullable=True)
    references: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    constraints: Mapped[str | None] = mapped_column(Text, nullable=True)
    budget_range: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timeline: Mapped[str | None] = mapped_column(String(200), nullable=True)
    evaluation_criteria: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    status: Mapped[BriefStatus] = mapped_column(
        Enum(BriefStatus, name="brief_status", create_constraint=True),
        default=BriefStatus.DRAFT,
    )
    created_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class BriefApplication(Base):
    """A learner's interest in working on a commercial project (application mode)."""

    __tablename__ = "brief_applications"
    __table_args__ = (
        Index("uq_brief_application", "brief_id", "user_id", unique=True),
        Index("ix_brief_apps_user", "user_id"),
    )

    id: Mapped[str] = ulid_pk()
    brief_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("client_briefs.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    cohort_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("cohorts.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status", create_constraint=True),
        default=ApplicationStatus.PENDING,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
