"""Consent audit log model — tracks all consent-related changes (N20).

Records every consent decision a user makes: passport visibility changes,
discoverable toggles, pool membership responses, outreach responses,
data deletion requests, and data exports.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

CONSENT_TYPES = frozenset(
    {
        "passport_visibility",
        "discoverable",
        "pool_consent",
        "outreach_response",
        "deletion_request",
        "data_export",
        "snapshot_share",
        "endorsement_opt_in",
    }
)

CONSENT_ACTIONS = frozenset({"granted", "revoked", "updated"})


class ConsentLog(Base):
    __tablename__ = "talent_consent_log"

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    consent_type: Mapped[str] = mapped_column(String(50), index=True)
    action: Mapped[str] = mapped_column(String(20))
    details: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
