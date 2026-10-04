"""Append-only experiment audit trail (ADR-017 §4.11, Part M).

Every lifecycle transition, amendment, ramp change, guardrail action and
analysis look lands one row. There is no UPDATE or DELETE path.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

EXPERIMENT_EVENT_TYPES = frozenset(
    {
        "created",
        "version_created",
        "transition",
        "ramp_changed",
        "guardrail_paused",
        "guardrail_alerted",
        "analysis_look",
        "decision_recorded",
        "promotion_drafted",
    }
)


class ExperimentEvent(Base):
    __tablename__ = "experiment_events"

    id: Mapped[str] = ulid_pk()
    experiment_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("experiments.id", ondelete="CASCADE")
    )
    # null actor = platform worker
    actor_user_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(String(40))
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (Index("ix_experiment_events_exp_created", "experiment_id", "created_at"),)
