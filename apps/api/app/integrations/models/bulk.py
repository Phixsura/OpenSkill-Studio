"""Bulk import jobs (ADR-018 §16.1). Imports are sessions, not requests:
upload -> validate (dry-run default) -> previewed -> commit (same
fingerprint or 409 IMPORT_DRY_RUN_STALE)."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

IMPORT_KINDS = frozenset({"users"})
IMPORT_MODES = frozenset({"atomic", "partial"})
IMPORT_STATUSES = frozenset(
    {"validating", "previewed", "committing", "succeeded", "failed", "partial"}
)
MAX_IMPORT_BYTES = 52_428_800  # 50 MB
MAX_ROW_ERRORS = 10_000
IMPORT_CHUNK_ROWS = 500


class ImportJob(Base):
    __tablename__ = "intg_import_jobs"
    __table_args__ = (
        Index("ix_intg_import_org", "org_id", "created_at"),
        Index("uq_intg_import_idem", "org_id", "idempotency_key", unique=True),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    template_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    mode: Mapped[str] = mapped_column(String(10), nullable=False, default="partial")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="validating")
    file_key: Mapped[str] = mapped_column(String(500), nullable=False)
    # SHA-256(file bytes + template_version) — commit refuses a stale preview.
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    dry_stats: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    stats: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    idempotency_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ImportRowError(Base):
    __tablename__ = "intg_import_row_errors"
    __table_args__ = (Index("ix_intg_import_errors", "job_id", "row_number"),)

    id: Mapped[str] = ulid_pk()
    job_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("intg_import_jobs.id", ondelete="CASCADE"), nullable=False
    )
    # 1-indexed INCLUDING the header row — matches the user's spreadsheet.
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    column: Mapped[str | None] = mapped_column(String(100), nullable=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(String(300), nullable=False)
    raw_row: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
