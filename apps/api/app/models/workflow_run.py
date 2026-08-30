"""Workflow runtime models — runs, step runs, review gates, bindings (ADR-010 D6).

Every state transition is a conditional UPDATE with an expected-status guard
(0 rows updated = lost race). Run history is append-only via WorkflowRunEvent.
"""

import enum
from datetime import datetime

from sqlalchemy import (
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


class RunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_REVIEW = "waiting_review"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepRunStatus(str, enum.Enum):
    PENDING = "pending"  # upstream not finished
    READY = "ready"  # all inputs satisfied, awaiting execution
    RUNNING = "running"  # executing (lease held)
    WAITING_REVIEW = "waiting_review"  # review_gate suspended
    WAITING_RETRY = "waiting_retry"  # failed attempt, will retry
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"  # upstream failed
    CANCELLED = "cancelled"


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    # Loose coupling — run history outlives packs
    pack_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    release_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    installation_id: Mapped[str | None] = mapped_column(
        String(26),
        ForeignKey("workflow_pack_installations.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Frozen at creation — running workflows never observe definition changes (D1)
    definition_snapshot: Mapped[dict] = mapped_column(JSONB)
    inputs: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    outputs: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[RunStatus] = mapped_column(
        Enum(RunStatus, name="workflow_run_status", create_constraint=True),
        default=RunStatus.PENDING,
    )
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    started_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_wfruns_org_status", "org_id", "status"),
        # Run history lists sort by created_at; the status index doesn't help
        Index("ix_wfruns_org_created", "org_id", "created_at"),
        Index(
            "uq_wfrun_idem",
            "org_id",
            "idempotency_key",
            unique=True,
            postgresql_where="idempotency_key IS NOT NULL",
        ),
    )


class WorkflowStepRun(Base):
    __tablename__ = "workflow_step_runs"

    id: Mapped[str] = ulid_pk()
    run_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("workflow_runs.id", ondelete="CASCADE")
    )
    step_id: Mapped[str] = mapped_column(String(64))
    step_type: Mapped[str] = mapped_column(String(30))
    status: Mapped[StepRunStatus] = mapped_column(
        Enum(StepRunStatus, name="workflow_step_run_status", create_constraint=True),
        default=StepRunStatus.PENDING,
    )
    # Retry counter lives at the STEP level (Temporal lesson: retry steps, not runs)
    attempt: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, server_default="3")
    inputs_resolved: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Bounded output (≤48KB enforced in service; media stored as asset refs)
    output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Write-ahead idempotency key for provider calls (R13)
    provider_request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # actual_offering_used — recorded on every provider execution
    offering_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    # Lease for crash detection (R11): expired lease + RUNNING = crashed executor
    lease_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("uq_steprun", "run_id", "step_id", unique=True),
        Index("ix_stepruns_status", "status", "lease_expires_at"),
    )


class WorkflowStepReview(Base):
    """Durable review-gate decision row (REV-4).

    The decision is persisted state, not an ephemeral event — a decision can
    never be "sent before anyone was listening" (Inngest race lesson).
    """

    __tablename__ = "workflow_step_reviews"

    id: Mapped[str] = ulid_pk()
    step_run_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("workflow_step_runs.id", ondelete="CASCADE")
    )
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Mandatory due date — no unbounded waits (SFN 1-year-hang lesson)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    decision: Mapped[str | None] = mapped_column(String(20), nullable=True)  # approved|rejected
    decision_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        # One OPEN review per step run — concurrent decisions get a deterministic 409
        Index(
            "uq_open_review",
            "step_run_id",
            unique=True,
            postgresql_where="decision IS NULL",
        ),
        Index("ix_step_reviews_org_due", "org_id", "due_at"),
    )


class WorkflowRunEvent(Base):
    """Append-only run audit trail."""

    __tablename__ = "workflow_run_events"

    id: Mapped[str] = ulid_pk()
    run_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("workflow_runs.id", ondelete="CASCADE")
    )
    step_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    event_type: Mapped[str] = mapped_column(String(30))
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_runevents_run", "run_id", "created_at"),)


class WorkflowStepBinding(Base):
    """Org-level resolved provider choice for a provider_action step.

    Human-confirmed; revalidated at execution time (BINDING_STALE).
    """

    __tablename__ = "workflow_step_bindings"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    installation_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("workflow_pack_installations.id", ondelete="CASCADE")
    )
    step_id: Mapped[str] = mapped_column(String(64))
    binding_mode: Mapped[str] = mapped_column(
        String(20), default="auto", server_default="auto"
    )  # auto | preferred | pinned
    offering_id: Mapped[str | None] = mapped_column(
        String(26),
        ForeignKey("provider_model_offerings.id", ondelete="SET NULL"),
        nullable=True,
    )
    reasons: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    gaps: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    confirmed_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("uq_binding", "installation_id", "step_id", unique=True),)
