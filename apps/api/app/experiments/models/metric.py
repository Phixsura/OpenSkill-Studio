"""Metric definitions & provenance-backed snapshots (ADR-017 §4.6–§4.7).

Definitions are the semantic layer over product data (we ARE the warehouse).
Snapshots carry sufficient statistics only — no raw rows ever leave the
snapshot layer — plus CUPED pre-period covariate aggregates and a provenance
JSONB recording the query_version that produced every number.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

METRIC_KINDS = frozenset({"binary", "continuous", "rate", "time_to_event"})
METRIC_SOURCE_KINDS = frozenset({"sql", "service"})
METRIC_PRIVACY_CLASSES = frozenset({"aggregate_only", "k_anonymous"})
METRIC_DIRECTIONS = frozenset({"increase_good", "decrease_good"})


class MetricDefinition(Base):
    __tablename__ = "experiment_metric_definitions"

    id: Mapped[str] = ulid_pk()
    key: Mapped[str] = mapped_column(String(64), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    kind: Mapped[str] = mapped_column(String(16))
    domain: Mapped[str] = mapped_column(String(20))
    source_kind: Mapped[str] = mapped_column(String(10))
    # Bumped whenever the producing query changes — snapshots record the
    # version that computed them, analyses default to same-version windows
    query_version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    # {"source": "<registry key>", ...source params}
    spec: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    privacy_class: Mapped[str] = mapped_column(
        String(16), default="aggregate_only", server_default="aggregate_only"
    )
    direction: Mapped[str] = mapped_column(
        String(16), default="increase_good", server_default="increase_good"
    )
    # v2 robustness knobs — applied at snapshot computation, recorded in provenance
    winsorize_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 3), nullable=True)
    cap_value: Mapped[Decimal | None] = mapped_column(Numeric(24, 6), nullable=True)
    percentile: Mapped[Decimal | None] = mapped_column(Numeric(6, 3), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class MetricSnapshot(Base):
    """Sufficient statistics per (experiment, metric, variant, UTC-day window)."""

    __tablename__ = "experiment_metric_snapshots"

    id: Mapped[str] = ulid_pk()
    experiment_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("experiments.id", ondelete="CASCADE")
    )
    metric_key: Mapped[str] = mapped_column(String(64))
    variant_key: Mapped[str] = mapped_column(String(40))
    # Segment dimension (§4.8 v2): '' = the whole population (the ONLY rows
    # top-level aggregation may read — segment rows would double-count);
    # 'org:<id>' = the per-org breakdown for user-unit experiments
    segment: Mapped[str] = mapped_column(String(64), default="", server_default="")
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    n: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    numerator: Mapped[Decimal | None] = mapped_column(Numeric(24, 6), nullable=True)
    denominator: Mapped[Decimal | None] = mapped_column(Numeric(24, 6), nullable=True)
    sum_value: Mapped[Decimal | None] = mapped_column(Numeric(24, 6), nullable=True)
    sum_sq: Mapped[Decimal | None] = mapped_column(Numeric(30, 6), nullable=True)
    # CUPED pre-period covariate aggregates (§4.7 v2)
    cov_sum: Mapped[Decimal | None] = mapped_column(Numeric(24, 6), nullable=True)
    cov_sum_sq: Mapped[Decimal | None] = mapped_column(Numeric(30, 6), nullable=True)
    cov_xy_sum: Mapped[Decimal | None] = mapped_column(Numeric(30, 6), nullable=True)
    # exp12 (§4.6 v3): per-covariate sufficient stats {key: {sum, sum_sq,
    # xy_sum}}; the cov_* columns above mirror the FIRST covariate so every
    # pre-exp12 reader keeps working
    covariates: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    provenance: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "experiment_id",
            "metric_key",
            "segment",
            "variant_key",
            "window_start",
            name="uq_experiment_metric_snapshots_window",
        ),
        Index("ix_experiment_metric_snapshots_exp_metric", "experiment_id", "metric_key"),
    )
