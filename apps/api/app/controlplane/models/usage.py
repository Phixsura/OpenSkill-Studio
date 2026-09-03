"""Append-only usage events (ADR-014 §3).

Loose refs everywhere (String(26), no FKs to business tables) — metering
history outlives packs, runs, and evaluations. Corrections are adjustment
events referencing the original; there is no UPDATE path.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Index, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

# usage_type -> canonical unit (single source of truth)
USAGE_TYPES: dict[str, str] = {
    "llm_input_tokens": "tokens",
    "llm_output_tokens": "tokens",
    "image_generation": "images",
    "image_editing": "images",
    "video_generation_seconds": "seconds",
    "video_processing_seconds": "seconds",
    "voice_generation": "seconds",
    "workflow_run": "runs",
    "multimodal_evaluation": "evaluations",
    "storage_gb_day": "gb_day",
    "active_learner_seat": "seats",
    "api_request": "requests",
    "content_license": "licenses",
}

USAGE_SOURCES = frozenset(
    {
        "workflow_runtime",
        "evaluation",
        "storage_sweep",
        "seat_sweep",
        "api_metering",
        "manual",
        "adjustment",
    }
)


class UsageEvent(Base):
    __tablename__ = "cp_usage_events"
    __table_args__ = (
        # R113[M17]: tenant-scoped — a global key namespace collided across
        # tenants (same class cp11/cp13 fixed for credits/purchases): tenant
        # B's event silently no-op'd against tenant A's key via ON CONFLICT.
        Index(
            "uq_cp_usage_idem_tenant",
            "tenant_id",
            "idempotency_key",
            unique=True,
            postgresql_where="idempotency_key IS NOT NULL",
        ),
        Index("ix_cp_usage_tenant_time", "tenant_id", "occurred_at"),
        Index("ix_cp_usage_org_time", "org_id", "occurred_at"),
        Index("ix_cp_usage_type_time", "usage_type", "occurred_at"),
        # R50[43]: run-terminal settlement selects by workflow_run_id
        Index(
            "ix_cp_usage_workflow_run",
            "workflow_run_id",
            postgresql_where="workflow_run_id IS NOT NULL",
        ),
    )

    id: Mapped[str] = ulid_pk()
    tenant_id: Mapped[str] = mapped_column(String(26), nullable=False)
    org_id: Mapped[str] = mapped_column(String(26), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    project_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    workflow_run_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    evaluation_task_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    provider_connection_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model_or_service: Mapped[str | None] = mapped_column(String(200), nullable=True)
    usage_type: Mapped[str] = mapped_column(String(40), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    adjustment_of_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
