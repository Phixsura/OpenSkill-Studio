"""Immutable commercial audit events (ADR-014 §1.4, issue §38).

Append-only: no UPDATE/DELETE API exists anywhere. `before`/`after` carry
whitelisted safe summaries only — never secrets, tokens, or card data.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class CommercialAuditEvent(Base):
    __tablename__ = "cp_audit_events"
    __table_args__ = (
        Index("ix_cp_audit_tenant_created", "tenant_id", "created_at"),
        Index("ix_cp_audit_action_created", "action", "created_at"),
        Index("ix_cp_audit_target", "target_type", "target_id"),
    )

    id: Mapped[str] = ulid_pk()
    actor_user_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    actor_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # platform | tenant | partner | system | impersonated
    action: Mapped[str] = mapped_column(String(60), nullable=False)  # registry-validated
    target_type: Mapped[str] = mapped_column(String(40), nullable=False)
    target_id: Mapped[str] = mapped_column(String(26), nullable=False)
    # Loose refs — audit history outlives everything.
    tenant_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    partner_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    before: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
