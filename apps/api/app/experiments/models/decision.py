"""Decision registry & policy promotion (ADR-017 §4.9–§4.10, Parts J/K).

DecisionRecords are immutable organizational memory: every experiment ends in
a versioned record with uncertainty, guardrail outcome, approver and evidence
links. A terminal decision (promote/reject) is unique per experiment.

PromotionDrafts carry an approved result toward a TARGET-DOMAIN DRAFT object
— never a direct production mutation. The target whitelist structurally
excludes every employment action (§2.1).
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

DECISIONS = frozenset({"promote", "reject", "inconclusive", "extend"})
TERMINAL_DECISIONS = frozenset({"promote", "reject"})
PROMOTION_STATUSES = frozenset({"draft", "approved", "applied", "rejected"})


class DecisionRecord(Base):
    __tablename__ = "experiment_decision_records"

    id: Mapped[str] = ulid_pk()
    experiment_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("experiments.id", ondelete="CASCADE")
    )
    experiment_version: Mapped[int] = mapped_column(Integer)
    decision: Mapped[str] = mapped_column(String(14))
    summary: Mapped[str] = mapped_column(Text)
    # Denormalized for the decision registry / meta-analysis filters
    domain: Mapped[str] = mapped_column(String(20))
    analysis_type: Mapped[str] = mapped_column(String(14))
    # The analysis this decision references — must match a recorded
    # analysis_look event (no decide-before-analyze)
    analysis_result_hash: Mapped[str] = mapped_column(String(64))
    uncertainty: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    segments: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    guardrail_outcome: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    evidence: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    approver_user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="RESTRICT")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        # One terminal decision per experiment; extend/inconclusive may repeat
        Index(
            "uq_experiment_decision_terminal",
            "experiment_id",
            unique=True,
            postgresql_where="decision IN ('promote', 'reject')",
        ),
        Index("ix_experiment_decision_domain", "domain", "decision"),
    )


class PromotionDraft(Base):
    __tablename__ = "experiment_promotion_drafts"

    id: Mapped[str] = ulid_pk()
    decision_record_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("experiment_decision_records.id", ondelete="CASCADE")
    )
    # Whitelisted in security.PROMOTION_TARGET_TYPES — no employment actions
    target_type: Mapped[str] = mapped_column(String(30))
    target_ref: Mapped[str] = mapped_column(String(64))
    draft_payload: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    status: Mapped[str] = mapped_column(String(10), default="draft", server_default="draft")
    approved_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Reference to the draft object created in the target domain
    applied_ref: Mapped[str | None] = mapped_column(String(64), nullable=True)
    apply_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_experiment_promotion_drafts_status", "status"),
    )
