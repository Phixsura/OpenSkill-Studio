"""Transactional outbox (ADR-014 §cross-cutting).

Business writes insert rows here in the SAME transaction as the business
rows; the control-plane worker consumes them with FOR UPDATE SKIP LOCKED.
"""

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class OutboxMessage(Base):
    __tablename__ = "cp_outbox"
    __table_args__ = (Index("ix_cp_outbox_poll", "status", "available_at"),)

    id: Mapped[str] = ulid_pk()
    topic: Mapped[str] = mapped_column(String(40), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    status: Mapped[str] = mapped_column(
        String(12), default="pending", server_default="pending"
    )  # pending | processing | done | failed
    attempts: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    available_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    locked_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


def enqueue(db, topic: str, payload: dict) -> OutboxMessage:
    """Insert an outbox row in the caller's transaction (no commit here)."""
    msg = OutboxMessage(topic=topic, payload=payload)
    db.add(msg)
    return msg
