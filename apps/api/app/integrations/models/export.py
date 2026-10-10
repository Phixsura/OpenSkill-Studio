"""Governed warehouse export streams (ADR-018 §16.2)."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

EXPORT_RUN_STATUSES = frozenset({"running", "succeeded", "failed"})
ANONYMIZE_MODES = frozenset({"hash", "drop"})
EXPORT_SCHEDULES = frozenset({"manual", "daily"})
EXPORT_PAGE_ROWS = 1000


class ExportStream(Base):
    __tablename__ = "intg_export_streams"
    __table_args__ = (Index("uq_intg_export_org_name", "org_id", "name", unique=True),)

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    dataset: Mapped[str] = mapped_column(String(50), nullable=False)
    # EXPLICIT allowlist: the writer selects ONLY these fields; anything not
    # listed is structurally absent (R82 total-coverage discipline).
    field_allowlist: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    # {field: "hash"|"drop"} — learner ids hash with a per-org salt by default.
    anonymize: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    schedule: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    cursor: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ExportRun(Base):
    __tablename__ = "intg_export_runs"
    __table_args__ = (Index("ix_intg_export_runs", "stream_id", "created_at"),)

    id: Mapped[str] = ulid_pk()
    stream_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("intg_export_streams.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="running")
    cursor_from: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    cursor_to: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    row_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    parts: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    manifest_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    error: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
