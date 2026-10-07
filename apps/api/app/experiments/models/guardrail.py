"""Guardrail events (ADR-017 §4.8, Part D).

A breach can only auto-PAUSE the experiment — there is no auto-promote code
path anywhere in this package (asserted by a source-scan test). SRM and other
health alerts land here too, under reserved __srm__/__incident__ keys.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

GUARDRAIL_ACTIONS = frozenset({"paused", "alerted"})

# Reserved guardrail keys (not spec-defined metrics)
SRM_GUARDRAIL_KEY = "__srm__"
# Defect #90: time-sliced SRM — a late randomization break is diluted by the
# healthy cumulative mass, so the last-24h slice gets its own chi-square
SRM_WINDOW_GUARDRAIL_KEY = "__srm_window__"
INCIDENT_GUARDRAIL_KEY = "__incident__"
# §4.13 v2: per-variant exposure ratios diverging from assignment ratios flag
# trigger bias (the exposure decision is being affected by the treatment)
EXPOSURE_SRM_GUARDRAIL_KEY = "__exposure_srm__"
# Cross-experiment interaction alert (§4.13 v2) — weekly sweep, both sides
INTERACTION_GUARDRAIL_KEY = "__interaction__"


class GuardrailEvent(Base):
    __tablename__ = "experiment_guardrail_events"

    id: Mapped[str] = ulid_pk()
    experiment_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("experiments.id", ondelete="CASCADE")
    )
    guardrail_key: Mapped[str] = mapped_column(String(64))
    metric_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    observed: Mapped[Decimal | None] = mapped_column(Numeric(24, 6), nullable=True)
    threshold: Mapped[Decimal | None] = mapped_column(Numeric(24, 6), nullable=True)
    window_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    window_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    action: Mapped[str] = mapped_column(String(10))
    auto: Mapped[bool] = mapped_column(default=True, server_default="true")
    detail: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_experiment_guardrail_events_exp_created", "experiment_id", "created_at"),
    )
