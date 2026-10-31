"""Trust audit events (ADR-017 §P).

Append-only: no UPDATE/DELETE API exists anywhere. Mirrors
CommercialAuditEvent (ADR-014) exactly — loose refs so audit history
outlives everything it references.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class TrustAuditEvent(Base):
    __tablename__ = "trust_audit_events"
    __table_args__ = (
        Index("ix_trust_audit_org_created", "org_id", "created_at"),
        Index("ix_trust_audit_action", "action", "created_at"),
        Index("ix_trust_audit_target", "target_type", "target_id"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(String(26), nullable=False)
    actor_user_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    actor_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # user | system | platform
    action: Mapped[str] = mapped_column(String(60), nullable=False)
    target_type: Mapped[str] = mapped_column(String(40), nullable=False)
    target_id: Mapped[str] = mapped_column(String(26), nullable=False)
    before: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
