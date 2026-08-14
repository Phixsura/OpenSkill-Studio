import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class EvalType(str, enum.Enum):
    EXERCISE_TEXT = "exercise_text"
    EXERCISE_CODE = "exercise_code"
    SUBMISSION_REVIEW = "submission_review"


class EvalStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EvaluationTask(Base):
    __tablename__ = "evaluation_tasks"
    __table_args__ = (
        Index("ix_eval_tasks_org_status", "org_id", "status"),
        Index("ix_eval_tasks_submission", "submission_id"),
        Index("ix_eval_tasks_worker", "status", "priority", "created_at"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    submission_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=True
    )
    attempt_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("exercise_attempts.id", ondelete="CASCADE"), nullable=True
    )
    type: Mapped[EvalType] = mapped_column(
        Enum(EvalType, name="eval_type", create_constraint=True), nullable=False
    )
    status: Mapped[EvalStatus] = mapped_column(
        Enum(EvalStatus, name="eval_status", create_constraint=True),
        default=EvalStatus.PENDING,
    )
    priority: Mapped[int] = mapped_column(Integer, default=5)
    config: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    llm_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    retries: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EvalUsageMonthly(Base):
    __tablename__ = "eval_usage_monthly"
    __table_args__ = (PrimaryKeyConstraint("org_id", "month"),)

    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    month: Mapped[date] = mapped_column(Date, nullable=False)
    total_tasks: Mapped[int] = mapped_column(Integer, default=0)
    total_input_tokens: Mapped[int] = mapped_column(BigInteger, default=0)
    total_output_tokens: Mapped[int] = mapped_column(BigInteger, default=0)
    total_cost_usd: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
