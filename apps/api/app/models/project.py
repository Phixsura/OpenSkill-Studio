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
    # AI visual production media types
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    PROMPT = "prompt"
    REFERENCE = "reference"
    FINAL_OUTPUT = "final_output"


class ItemType(str, enum.Enum):
    FILE = "file"
    TEXT = "text"
    LINK = "link"
    PROMPT = "prompt"
    MARKDOWN = "markdown"


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
    project_type: Mapped[str] = mapped_column(
        String(20), default="general", server_default="general", nullable=False
    )
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
    # Optional links to cohort/brief — NULL means org-wide (backward-compatible).
    client_brief_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("client_briefs.id", ondelete="SET NULL"), nullable=True
    )
    cohort_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("cohorts.id", ondelete="SET NULL"), nullable=True
    )
    created_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
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
    version: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    submission: Mapped["Submission"] = relationship(back_populates="items")


class PeerReviewPhase(str, enum.Enum):
    """Peer review round lifecycle (Moodle Workshop phases, simplified):
    SETUP → learners submit; ASSESSMENT → allocations exist, peers review;
    CLOSED → scores aggregated and visible."""

    SETUP = "setup"
    ASSESSMENT = "assessment"
    CLOSED = "closed"


class PeerAssessmentStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"


class PeerReviewRound(Base):
    """A peer-review cycle on a project.

    Configuration follows the Teachfloor/Moodle model: N reviews per
    reviewer, optional anonymity, optional self-review, reuse of the
    project rubric for structured scoring.
    """

    __tablename__ = "peer_review_rounds"
    __table_args__ = (Index("ix_pr_rounds_project", "project_id"),)

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    num_reviews: Mapped[int] = mapped_column(Integer, default=2)  # per reviewer
    anonymous: Mapped[bool] = mapped_column(Boolean, default=True)
    include_self_review: Mapped[bool] = mapped_column(Boolean, default=False)
    phase: Mapped[PeerReviewPhase] = mapped_column(
        Enum(PeerReviewPhase, name="peer_review_phase", create_constraint=True),
        default=PeerReviewPhase.SETUP,
    )
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PeerAssessment(Base):
    """One reviewer's assessment of one submission within a round."""

    __tablename__ = "peer_assessments"
    __table_args__ = (
        Index("uq_peer_assessment", "round_id", "submission_id", "reviewer_id", unique=True),
        Index("ix_peer_assessments_reviewer", "round_id", "reviewer_id"),
    )

    id: Mapped[str] = ulid_pk()
    round_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("peer_review_rounds.id", ondelete="CASCADE"), nullable=False
    )
    submission_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False
    )
    reviewer_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    is_self_review: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[PeerAssessmentStatus] = mapped_column(
        Enum(PeerAssessmentStatus, name="peer_assessment_status", create_constraint=True),
        default=PeerAssessmentStatus.PENDING,
    )
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Per-rubric-dimension scores: [{criterion, score, max_score}]
    score_breakdown: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CommentAnchorType(str, enum.Enum):
    """How a comment is attached to a submission item (Frame.io semantics):
    GLOBAL = the whole asset; TIME = a video/audio timestamp (with optional
    range duration); REGION = a normalized-coordinate area on an image."""

    GLOBAL = "global"
    TIME = "time"
    REGION = "region"


class SubmissionComment(Base):
    """Anchored, threaded feedback on a single submission item.

    Region geometry follows the Annotorious/W3C Web Annotation convention:
    normalized 0-1 coordinates stored as {type, bounds:{minX,minY,maxX,maxY}}
    so annotations are resolution- and zoom-independent.
    """

    __tablename__ = "submission_comments"
    __table_args__ = (
        Index("ix_comments_item_created", "item_id", "created_at"),
        Index("ix_comments_submission", "submission_id"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    submission_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False
    )
    item_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("submission_items.id", ondelete="CASCADE"), nullable=False
    )
    author_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("submission_comments.id", ondelete="CASCADE"), nullable=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    anchor_type: Mapped[CommentAnchorType] = mapped_column(
        Enum(CommentAnchorType, name="comment_anchor_type", create_constraint=True),
        default=CommentAnchorType.GLOBAL,
    )
    # TIME anchor: position and optional range, in milliseconds
    timestamp_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # REGION anchor: normalized geometry JSON
    region: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SubmissionReview(Base):
    __tablename__ = "submission_reviews"
    __table_args__ = (Index("ix_reviews_sub_created", "submission_id", "created_at"),)

    id: Mapped[str] = ulid_pk()
    submission_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False
    )
    reviewer_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
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
    __table_args__ = (Index("uq_extension_project_user", "project_id", "user_id", unique=True),)

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
    granted_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProjectTemplate(Base):
    """Reusable project blueprint. Deliverables are stored as a JSONB list
    and copied to real ProjectDeliverable rows at instantiation, so editing
    a project created from a template never affects the template."""

    __tablename__ = "project_templates"
    __table_args__ = (Index("ix_templates_org_status", "org_id", "status"),)

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    project_type: Mapped[str] = mapped_column(
        String(20), default="general", server_default="general", nullable=False
    )
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, name="difficulty_level", create_constraint=True),
        default=DifficultyLevel.INTERMEDIATE,
    )
    suggested_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_score: Mapped[int] = mapped_column(Integer, default=100)
    rubric: Mapped[list] = mapped_column(JSONB, nullable=False)
    # list of {name, description, type, required, config, sort_order}
    deliverables: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    skill_names: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus, name="content_status", create_constraint=True),
        default=ContentStatus.PUBLISHED,
    )
    created_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Pack origin tracking
    origin_pack_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    origin_release_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    origin_component_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    locally_modified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")


class ProjectAsset(Base):
    """Instructor-provided reference material attached to a project
    (brand logos, style references, client briefs). Visible to all org
    members; not part of any learner submission."""

    __tablename__ = "project_assets"
    __table_args__ = (Index("ix_assets_project_order", "project_id", "sort_order"),)

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_key: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    uploaded_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProjectCreatorAssignment(Base):
    """Direct assignment of a commercial project to an individual creator.

    Complements CohortProjectAssignment: a project can be exposed to a
    full cohort AND/OR to selected individual creators.
    """

    __tablename__ = "project_creator_assignments"
    __table_args__ = (
        Index("uq_project_creator", "project_id", "user_id", unique=True),
        Index("ix_project_creators_user", "user_id"),
    )

    id: Mapped[str] = ulid_pk()
    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    assigned_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
