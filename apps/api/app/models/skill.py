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
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, ulid_pk

# ── Enums ─────────────────────────────────────────────────


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ExerciseType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TEXT_ANSWER = "text_answer"
    CODE_SUBMISSION = "code_submission"
    FILE_UPLOAD = "file_upload"


class ProgressStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class GradingMethod(str, enum.Enum):
    AUTO = "auto"
    MANUAL = "manual"
    AI = "ai"


# ── Models ────────────────────────────────────────────────


class SkillCategory(Base):
    __tablename__ = "skill_categories"
    __table_args__ = (Index("uq_category_org_slug", "org_id", "slug", unique=True),)

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus, name="content_status", create_constraint=True),
        default=ContentStatus.DRAFT,
    )
    created_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Pack origin tracking (set when installed from a pack)
    origin_pack_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    origin_release_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    origin_component_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    locally_modified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    skills: Mapped[list["Skill"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )


class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = (
        Index("uq_skill_org_slug", "org_id", "slug", unique=True),
        Index("ix_skills_org_category_order", "org_id", "category_id", "sort_order"),
        Index("ix_skills_org_status", "org_id", "status"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("skill_categories.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    learning_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, name="difficulty_level", create_constraint=True),
        default=DifficultyLevel.BEGINNER,
    )
    estimated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, server_default="{}")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus, name="content_status", create_constraint=True),
        default=ContentStatus.DRAFT,
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Pack origin tracking
    origin_pack_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    origin_release_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    origin_component_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    locally_modified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # Interactive sandbox placeholder (URL to external sandbox environment)
    sandbox_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    category: Mapped["SkillCategory"] = relationship(back_populates="skills")
    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates="skill", cascade="all, delete-orphan"
    )


class SkillPrerequisite(Base):
    __tablename__ = "skill_prerequisites"
    __table_args__ = (CheckConstraint("skill_id != prerequisite_id", name="ck_no_self_prereq"),)

    skill_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True
    )
    prerequisite_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True
    )


class Exercise(Base):
    __tablename__ = "exercises"
    __table_args__ = (Index("ix_exercises_skill_order", "skill_id", "sort_order"),)

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[ExerciseType] = mapped_column(
        Enum(ExerciseType, name="exercise_type", create_constraint=True), nullable=False
    )
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    max_score: Mapped[int] = mapped_column(Integer, default=100)
    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus, name="content_status", create_constraint=True),
        default=ContentStatus.DRAFT,
    )
    created_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Interactive sandbox placeholder (JSONB config for sandbox environment)
    sandbox_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Pack origin tracking
    origin_pack_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    origin_release_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    origin_component_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    locally_modified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    skill: Mapped["Skill"] = relationship(back_populates="exercises")
    attempts: Mapped[list["ExerciseAttempt"]] = relationship(
        back_populates="exercise", cascade="all, delete-orphan"
    )


class ExerciseAttempt(Base):
    __tablename__ = "exercise_attempts"
    __table_args__ = (
        Index("ix_attempts_exercise_user", "exercise_id", "user_id", "created_at"),
        Index("ix_attempts_user_org", "user_id", "org_id"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    answer: Mapped[dict] = mapped_column(JSONB, nullable=False)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    graded_by: Mapped[GradingMethod | None] = mapped_column(
        Enum(GradingMethod, name="grading_method", create_constraint=True), nullable=True
    )
    graded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    exercise: Mapped["Exercise"] = relationship(back_populates="attempts")


class SkillProgress(Base):
    __tablename__ = "skill_progress"
    __table_args__ = (
        Index("uq_skill_progress", "skill_id", "user_id", unique=True),
        Index("ix_skill_progress_user_org", "user_id", "org_id", "status"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[ProgressStatus] = mapped_column(
        Enum(ProgressStatus, name="progress_status", create_constraint=True),
        default=ProgressStatus.NOT_STARTED,
    )
    exercises_total: Mapped[int] = mapped_column(Integer, default=0)
    exercises_done: Mapped[int] = mapped_column(Integer, default=0)
    best_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
