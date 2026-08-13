import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, ulid_pk
from app.models.skill import ContentStatus, DifficultyLevel

# ── Enums ─────────────────────────────────────────────────


class DeliverableType(str, enum.Enum):
    FILE = "file"
    TEXT = "text"
    LINK = "link"
    MARKDOWN = "markdown"


class ItemType(str, enum.Enum):
    FILE = "file"
    TEXT = "text"
    LINK = "link"


class SubmissionStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    REVISION_REQUESTED = "revision_requested"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReviewStatus(str, enum.Enum):
    APPROVED = "approved"
    REVISION_REQUESTED = "revision_requested"
    REJECTED = "rejected"


class ReviewerType(str, enum.Enum):
    INSTRUCTOR = "instructor"
    AI = "ai"


# ── Models ────────────────────────────────────────────────


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        Index("uq_project_org_slug", "org_id", "slug", unique=True),
        Index("ix_projects_org_status_deadline", "org_id", "status", "deadline"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, name="difficulty_level", create_constraint=True),
        default=DifficultyLevel.INTERMEDIATE,
    )
    max_score: Mapped[int] = mapped_column(Integer, default=100)
    rubric: Mapped[dict] = mapped_column(JSONB, nullable=False)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    late_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    late_penalty_pct: Mapped[int] = mapped_column(Integer, default=0)
    max_submissions: Mapped[int] = mapped_column(Integer, default=0)  # 0 = unlimited
    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus, name="content_status", create_constraint=True),
        default=ContentStatus.DRAFT,
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    deliverables: Mapped[list["ProjectDeliverable"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class ProjectSkill(Base):
    __tablename__ = "project_skills"

    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True
    )


class ProjectDeliverable(Base):
    __tablename__ = "project_deliverables"
    __table_args__ = (Index("ix_deliverables_project_order", "project_id", "sort_order"),)

    id: Mapped[str] = ulid_pk()
    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[DeliverableType] = mapped_column(
        Enum(DeliverableType, name="deliverable_type", create_constraint=True), nullable=False
    )
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    project: Mapped["Project"] = relationship(back_populates="deliverables")


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        Index("ix_submissions_project_user_ver", "project_id", "user_id", "version"),
        Index("ix_submissions_org_status", "org_id", "status"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus, name="submission_status", create_constraint=True),
        default=SubmissionStatus.DRAFT,
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_late: Mapped[bool] = mapped_column(Boolean, default=False)
    final_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["Project"] = relationship(back_populates="submissions")
    items: Mapped[list["SubmissionItem"]] = relationship(
        back_populates="submission", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["SubmissionReview"]] = relationship(
        back_populates="submission", cascade="all, delete-orphan"
    )


class SubmissionItem(Base):
    __tablename__ = "submission_items"
    __table_args__ = (Index("ix_submission_items_sub", "submission_id"),)

    id: Mapped[str] = ulid_pk()
    submission_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False
    )
    deliverable_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("project_deliverables.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[ItemType] = mapped_column(
        Enum(ItemType, name="item_type", create_constraint=True), nullable=False
    )
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    submission: Mapped["Submission"] = relationship(back_populates="items")


class SubmissionReview(Base):
    __tablename__ = "submission_reviews"
    __table_args__ = (Index("ix_reviews_sub_created", "submission_id", "created_at"),)

    id: Mapped[str] = ulid_pk()
    submission_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False
    )
    reviewer_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id"), nullable=True
    )
    reviewer_type: Mapped[ReviewerType] = mapped_column(
        Enum(ReviewerType, name="reviewer_type", create_constraint=True), nullable=False
    )
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, name="review_status", create_constraint=True), nullable=False
    )
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_breakdown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    submission: Mapped["Submission"] = relationship(back_populates="reviews")


class SubmissionExtension(Base):
    __tablename__ = "submission_extensions"
    __table_args__ = (
        Index("uq_extension_project_user", "project_id", "user_id", unique=True),
    )

    id: Mapped[str] = ulid_pk()
    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    original_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    extended_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    granted_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
