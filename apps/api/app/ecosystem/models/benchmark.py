"""Benchmark Lab (ADR-016 Part F).

Dimensional scoring only — there is deliberately NO overall_score column.
Blind review hides model/provider identity behind alias labels until every
reviewer in a batch has submitted.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

# Initial AI-visual benchmark families (issue #35 Part F)
BENCHMARK_FAMILIES = frozenset(
    {
        "ecommerce_hero",
        "product_consistency",
        "character_consistency",
        "chinese_text_render",
        "storyboard_adherence",
        "i2v_motion",
        "temporal_consistency",
        "commercial_ad_15s",
        "background_replacement",
        "multimodal_qa",
    }
)

SUITE_STATUSES = frozenset({"draft", "active", "archived"})
RUN_STATUSES = frozenset({"queued", "running", "completed", "failed", "cancelled"})

# Preserved score dimensions (never collapsed into one number)
SCORE_DIMENSIONS = frozenset(
    {
        "quality",
        "brief_adherence",
        "consistency",
        "text_accuracy",
        "motion_quality",
        "temporal_quality",
        "speed_p50_ms",
        "cost_per_case_usd",
        "reliability",
        "commercial_readiness",
    }
)


class BenchmarkSuite(Base):
    """A reusable benchmark suite for one AI-visual scenario family."""

    __tablename__ = "eco_benchmark_suites"

    id: Mapped[str] = ulid_pk()
    key: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    family: Mapped[str] = mapped_column(String(40))
    capability_key: Mapped[str] = mapped_column(String(64))
    # [{"dimension": "quality", "weight": 0.3, "anchors": {...}}, ...]
    rubric: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # {"required": true, "blind": true, "min_reviewers": 2}
    human_review_policy: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # Names of automated metrics valid for this family (e.g. ["ocr_text_accuracy"])
    automated_metrics: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    budget_usd_cap: Mapped[float] = mapped_column(Numeric(10, 2), default=10.0)
    repeat_count: Mapped[int] = mapped_column(Integer, default=3, server_default="3")
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="draft")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_eco_bench_suites_family", "family", "status"),)


class BenchmarkCase(Base):
    """One test case inside a suite."""

    __tablename__ = "eco_benchmark_cases"

    id: Mapped[str] = ulid_pk()
    suite_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_benchmark_suites.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(200))
    prompt: Mapped[str] = mapped_column(Text)
    # Asset references (URIs/ids), never blobs
    reference_assets: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    constraints: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    weight: Mapped[float] = mapped_column(Numeric(4, 3), default=1.0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_eco_bench_cases_suite", "suite_id", "sort_order"),)


class BenchmarkRun(Base):
    """One execution of a suite against one target model/offering."""

    __tablename__ = "eco_benchmark_runs"

    id: Mapped[str] = ulid_pk()
    suite_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_benchmark_suites.id", ondelete="RESTRICT")
    )
    # queued | running | completed | failed | cancelled
    status: Mapped[str] = mapped_column(String(20), default="queued", server_default="queued")
    # {"entity_kind": "model_version", "entity_id": ..., "offering_id": ...,
    #  "provider_key": ...}
    target: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # Adapter versions, config — reproducibility snapshot
    environment_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    seed_settings: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    budget_usd_cap: Mapped[float] = mapped_column(Numeric(10, 2), default=10.0)
    total_cost_usd: Mapped[float] = mapped_column(Numeric(12, 6), default=0)
    # Aggregated per-dimension scores — NO overall_score by design
    dimension_scores: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    triggered_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_eco_bench_runs_suite", "suite_id", "created_at"),
        Index("ix_eco_bench_runs_status", "status"),
    )


class BenchmarkResult(Base):
    """One case × repeat execution result within a run."""

    __tablename__ = "eco_benchmark_results"

    id: Mapped[str] = ulid_pk()
    run_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_benchmark_runs.id", ondelete="CASCADE")
    )
    case_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_benchmark_cases.id", ondelete="RESTRICT")
    )
    repeat_index: Mapped[int] = mapped_column(Integer, default=0)
    input_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    output_assets: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    usage: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    cost_usd: Mapped[float] = mapped_column(Numeric(12, 6), default=0)
    retries: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    failed: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    # {"text_accuracy": 0.91, ...} — automated metrics only
    automated_scores: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("run_id", "case_id", "repeat_index", name="uq_eco_bench_result"),
        Index("ix_eco_bench_results_run", "run_id"),
    )


class ReviewBatch(Base):
    """A blind human-review batch over results from multiple runs.

    alias_map ({run_id: "Model A"}) is server-side only and MUST NOT appear in
    reviewer-facing responses until the batch is fully submitted + revealed.
    """

    __tablename__ = "eco_review_batches"

    id: Mapped[str] = ulid_pk()
    suite_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_benchmark_suites.id", ondelete="RESTRICT")
    )
    run_ids: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # {run_id: alias_label} — the blind mapping; excluded from reviewer responses
    alias_map: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    reviewer_ids: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    blind: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    # open | complete | revealed
    status: Mapped[str] = mapped_column(String(20), default="open", server_default="open")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_eco_review_batches_suite", "suite_id"),)


class BenchmarkReview(Base):
    """One reviewer's blind scores for one result."""

    __tablename__ = "eco_benchmark_reviews"

    id: Mapped[str] = ulid_pk()
    batch_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_review_batches.id", ondelete="CASCADE")
    )
    run_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_benchmark_runs.id", ondelete="CASCADE")
    )
    result_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_benchmark_results.id", ondelete="CASCADE")
    )
    reviewer_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    # Reviewer-facing identity ("Model A") — never the real target
    alias_label: Mapped[str] = mapped_column(String(8))
    # {"quality": 4, "brief_adherence": 5, ...} keyed by rubric dimensions
    scores: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("result_id", "reviewer_id", name="uq_eco_bench_review"),
        Index("ix_eco_bench_reviews_batch", "batch_id"),
    )
