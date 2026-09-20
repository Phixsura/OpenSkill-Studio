"""Talent activity log — audit history for all talent mutations (ADR-015 upgrade).

Records a structured timeline of all significant talent events per user,
enabling activity feeds, compliance audit trails, and admin oversight.
"""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

ACTIVITY_ACTION_TYPES = frozenset(
    {
        "evidence_added",
        "evidence_voided",
        "credential_issued",
        "credential_revoked",
        "application_submitted",
        "application_transitioned",
        "endorsement_received",
        "endorsement_given",
        "passport_updated",
        "passport_snapshot_created",
        "opportunity_created",
        "opportunity_updated",
        "match_generated",
        "outreach_sent",
        "outreach_responded",
        "pool_joined",
        "pool_left",
        "interview_scheduled",
        "scorecard_submitted",
        "verification_submitted",
    }
)


class TalentActivityLog(Base):
    """Immutable activity log entry for talent audit trail."""

    __tablename__ = "talent_activity_log"


    def __repr__(self) -> str:
        return f"<TalentActivityLog {self.id}>"
    __table_args__ = (
        Index("ix_activity_user_created", "user_id", "created_at"),
        Index("ix_activity_action", "action_type"),
        Index("ix_activity_target", "target_type", "target_id"),
    )

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    action_type: Mapped[str] = mapped_column(String(50))
    target_type: Mapped[str] = mapped_column(String(50))
    target_id: Mapped[str] = mapped_column(String(26))
    extra: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
